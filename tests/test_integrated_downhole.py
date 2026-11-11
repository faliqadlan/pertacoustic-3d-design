"""Boundary checks for the integrated conceptual assembly and exchange geometry."""

from dataclasses import replace
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

import cadquery as cq

from cosmo.integrated_downhole import (
    BASELINE, ROOT, Design, Parameters, block, bounds, build_design, cylinder,
    engineering_scenarios, export_all, export_step, generate,
    intersection_volume, representation, shapes, tube, verify_design, volume,
)


class IntegratedDownholeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design = build_design()
        cls.observed = verify_design(cls.design)

    def clone_design(self):
        return Design(self.design.parameters, [replace(part) for part in self.design.parts], list(self.design.components))

    def test_complete_geometry_and_all_part_interferences(self):
        result = self.observed
        self.assertAlmostEqual(result["overall_length_mm"], 863.0, places=5)
        self.assertLessEqual(result["maximum_od_mm"], 44.45)
        self.assertGreater(result["solid_count"], result["part_count"])
        n = len(self.design.parts)
        self.assertEqual(result["all_pair_count"], n * (n - 1) // 2)
        self.assertGreater(result["boolean_pairs_after_bbox_pruning"], 30)
        self.assertLessEqual(result["maximum_prohibited_interference_mm3"], 1e-4)
        self.assertEqual(result["collision_exclusions"], [])
        self.assertLessEqual(result["outside_envelope_volume_mm3"], 1e-4)
        self.assertEqual(len({p.name for p in self.design.parts}), n)

    def test_shell_geometry_has_actual_specified_wall_and_bore(self):
        p = self.design.parameters
        shell = self.design.by_name("electronics_barrel").solid
        measured = bounds(shell)
        self.assertAlmostEqual(measured["xmax"] - measured["xmin"], p.od_mm, places=5)
        expected = math.pi * ((p.od_mm / 2) ** 2 - (p.bore_mm / 2) ** 2) * p.electronics_barrel_mm
        self.assertAlmostEqual(volume(shell), expected, places=5)
        self.assertAlmostEqual(p.bore_mm, 37.45)
        margin = self.observed["clearances_mm"]["adc_reserved_diametral_margin"]
        self.assertAlmostEqual(margin, 37.45 - math.hypot(32, 14), places=6)

    def test_parameter_validation_rejects_infeasible_or_changed_governing_envelopes(self):
        for changes in ({"od_mm": 58}, {"wall_mm": 30}, {"od_mm": 40},
                        {"electronics_barrel_mm": 380}, {"battery_barrel_mm": 120},
                        {"cell_diameter_mm": 37}, {"sensor_length_mm": 120},
                        {"electronics_barrel_mm": 1800}, {"external_c": 150},
                        {"duration_s": 3600}, {"wall_mm": float("nan")}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                Parameters(**changes).validate()

    def test_nondefault_feasible_parameters_generate_consistent_geometry(self):
        params = Parameters(od_mm=47.625, wall_mm=4, electronics_barrel_mm=420, battery_barrel_mm=220)
        observed = verify_design(build_design(params))
        self.assertAlmostEqual(observed["overall_length_mm"], 913)
        self.assertAlmostEqual(observed["shell_bore_mm"], 39.625)
        self.assertAlmostEqual(observed["maximum_od_mm"], 47.625)
        self.assertEqual(self.design.parameters, Parameters())

    def test_boundary_is_covered_in_ideal_cad_and_guard_has_open_paths(self):
        self.assertLessEqual(self.observed["nominal_boundary_uncovered_volume_mm3"], 1e-4)
        self.assertEqual(self.observed["wet_to_dry_transition_z_mm"], [153, 165])
        self.assertEqual(len(self.observed["open_guard_rays"]), 6)
        self.assertTrue(all(row["guard_intersection_mm3"] < 1e-4 for row in self.observed["open_guard_rays"]))

    def test_a_real_component_collision_is_rejected(self):
        design = self.clone_design()
        design.by_name("adc").solid = design.by_name("mcu").solid
        with self.assertRaisesRegex(ValueError, "Prohibited part interference"):
            verify_design(design)

    def test_open_feedthrough_path_is_rejected(self):
        design = self.clone_design()
        part = design.by_name("sealed_feedthrough_reserve")
        part.solid = part.solid.cut(cylinder(1.5, 152, 15))
        with self.assertRaisesRegex(ValueError, "CAD barrier has an open path"):
            verify_design(design)

    def test_closed_acoustic_windows_are_rejected(self):
        design = self.clone_design()
        p = design.parameters
        guard = design.by_name("open_sensor_guard")
        guard.solid = guard.solid.union(tube(p.od_mm / 2, p.od_mm / 2 - 2, 70, 10))
        with self.assertRaisesRegex(ValueError, "acoustic exposure window"):
            verify_design(design)

    def test_empty_and_invalid_boolean_results_fail_closed(self):
        with self.assertRaises(ValueError):
            shapes(cq.Workplane("XY"))
        malformed = Mock(objects=[object()])
        malformed.val.return_value = None
        with patch.object(cq.Workplane, "intersect", return_value=malformed):
            with self.assertRaisesRegex(ValueError, "Invalid Boolean"):
                intersection_volume(cylinder(2, 0, 1), cylinder(2, 0, 1))
        with patch("cosmo.integrated_downhole.intersection_volume", side_effect=RuntimeError("kernel failed")):
            with self.assertRaisesRegex(RuntimeError, "kernel failed"):
                verify_design(self.design)

    def test_views_preserve_part_identity_and_explosion_is_only_translation(self):
        before = {part.name: bounds(part.solid) for part in self.design.parts}
        complete = representation(self.design, "complete")
        section = representation(self.design, "sectional")
        exploded = representation(self.design, "exploded")
        self.assertEqual([p.name for p, _ in complete], [p.name for p, _ in section])
        self.assertEqual([p.name for p, _ in complete], [p.name for p, _ in exploded])
        for part, solid in exploded:
            self.assertAlmostEqual(volume(solid), volume(part.solid), places=5)
            actual = bounds(solid)
            for axis, delta in zip(("x", "y", "z"), part.exploded_offset_mm):
                for endpoint in ("min", "max"):
                    self.assertAlmostEqual(actual[axis + endpoint], before[part.name][axis + endpoint] + delta, places=5)
        for part, solid in section:
            self.assertLessEqual(volume(solid), volume(part.solid) + 1e-4)
        self.assertEqual(before, {part.name: bounds(part.solid) for part in self.design.parts})

    def test_all_step_exports_round_trip_without_losing_modules(self):
        with TemporaryDirectory() as folder:
            records = export_all(self.design, Path(folder))
            self.assertEqual(len(records), 8)
            self.assertTrue(all(record["status"] == "PASS" for record in records))
            complete = next(row for row in records if row["file"] == "integrated_complete.step")
            self.assertEqual(set(complete["part_names"]), {part.name for part in self.design.parts})
            self.assertEqual(complete["solid_count"], self.observed["solid_count"])
            for record in records:
                self.assertLess(record["volume_relative_error"], 1e-7)
                self.assertEqual(record["units"], "mm")
                self.assertTrue((Path(folder) / record["file"]).is_file())

    def test_corrupt_step_import_cannot_be_reported_as_success(self):
        part = self.design.by_name("hti_reference")
        with TemporaryDirectory() as folder, patch("cadquery.importers.importStep", return_value=cylinder(1, 0, 1)):
            with self.assertRaisesRegex(ValueError, "STEP round trip changed"):
                export_step([(part, part.solid)], Path(folder) / "corrupt.step")

    def test_removable_retention_parts_allow_module_loading(self):
        # An open battery sleeve accepts a cell axially before removable stops are fitted.
        p = self.design.parameters
        sleeve = self.design.by_name("battery_holder").solid
        cell_column = cylinder(p.cell_diameter_mm / 2, p.stations["battery_start"], p.battery_barrel_mm)
        self.assertLess(intersection_volume(sleeve, cell_column), 1e-4)
        for name in ("battery_lower_end_support", "battery_upper_end_support", "removable_card_keepers"):
            self.assertIsNotNone(self.design.by_name(name))
        # Removing top keepers permits radial loading onto the ADC saddle.
        adc = self.design.by_name("adc").solid
        lifted = adc.translate((0, 1, 0))
        self.assertLess(intersection_volume(lifted, self.design.by_name("carrier_and_card_saddles").solid), 1e-4)

    def test_power_and_storage_are_explicit_scenarios_not_qualification(self):
        result = engineering_scenarios(self.design.parameters)
        self.assertIn("UNRESOLVED", result["pressure_rating"])
        self.assertEqual(result["battery_limits"]["runtime_at_70c"], "NOT VERIFIED")
        scenario = result["power_scenarios"][1]
        self.assertAlmostEqual(scenario["nominal_current_a"], 2 / 0.85 / 7.2)
        self.assertAlmostEqual(scenario["two_hour_input_wh"], 4 / 0.85)
        self.assertEqual(result["storage_scenarios"][1]["raw_bytes"], 5_529_600_000)

    def test_historical_directories_cannot_be_output_targets(self):
        for folder in (ROOT / "results" / "biweekly-5", ROOT / "results" / "compact-casing" / "new"):
            with self.subTest(folder=folder), self.assertRaisesRegex(ValueError, "historical"):
                generate(folder)


if __name__ == "__main__":
    unittest.main()
