import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from cosmo.biweekly5 import (
    ENDCAP_THICKNESS_MM,
    FRONT_AXIAL_INSULATION_MM,
    MATERIALS,
    HOUSING_LENGTH_MM,
    REAR_AXIAL_INSULATION_MM,
    REQUIRED_CLEAR_ID_MM,
    THERMAL_ZONES_LOCAL_MM,
    _outer_faces,
    _parse_buckling_factor,
    _zone_max_temperatures,
    axial_heat_leak_screen,
    choose_wall,
    engineering_status,
    lame_screen,
    parse_inp,
    pressure_vessel_solid,
    revised_geometry,
    run_screening_matrix,
    thermal_simulation,
    thread_retention_screen,
)
from cosmo.core.result_extractor import extract_max_internal_temperature
from cosmo.core.solver_interface import setup_and_run_calculix


class Biweekly5StudyTests(unittest.TestCase):
    def test_geometry_and_pressure_screens(self):
        self.assertEqual(REQUIRED_CLEAR_ID_MM, 41)
        self.assertFalse(choose_wall(50)["fit"])
        candidate = choose_wall(65)
        self.assertTrue(candidate["fit"])
        self.assertGreaterEqual(candidate["yield_safety_factor"], 2)
        self.assertGreaterEqual(candidate["buckling_factor"], 2)
        self.assertGreater(lame_screen(65, 5)["max_von_mises_MPa"], 0)

    def test_thermal_model_and_thread_datum(self):
        candidate = choose_wall(65)
        run = thermal_simulation(candidate, power_w=0, cells_per_layer=4, duration_s=600)
        self.assertEqual(len(run["times_s"]), 11)
        self.assertGreater(run["inner_temperature_C"][-1], 25)
        self.assertLess(run["inner_temperature_C"][-1], 150)
        thread = thread_retention_screen()
        self.assertAlmostEqual(thread["pitch_mm"], 1.27, places=6)
        self.assertAlmostEqual(thread["engagement_mm"], 10.16, places=6)

    def test_revised_candidate_replaces_the_old_radial_only_selection(self):
        selected = run_screening_matrix()[2]
        self.assertEqual(selected["od_mm"], 200)
        self.assertEqual(selected["endcap_thickness_mm"], ENDCAP_THICKNESS_MM)

    def test_calculix_conductivity_keeps_w_per_mk_numeric_value(self):
        with TemporaryDirectory() as directory:
            inp = Path(directory) / "probe.inp"
            inp.write_text("*NODE\n1, 10, 0, 0\n", encoding="utf-8")
            layers = [{"name": "Outer", "material": "Inconel718", "thickness": 1.0}]
            with patch("cosmo.core.solver_interface.subprocess.run"):
                self.assertTrue(
                    setup_and_run_calculix(
                        str(inp), layers, od_mm=20, ccx_path="ccx", time_seconds=60
                    )
                )
            generated = inp.read_text(encoding="utf-8")
            self.assertIn("*CONDUCTIVITY\n1.470000E+01", generated)

    def test_calculix_fatal_text_is_not_success(self):
        with TemporaryDirectory() as directory:
            inp = Path(directory) / "fatal_probe.inp"
            inp.write_text("*NODE\n1, 10, 0, 0\n", encoding="utf-8")
            layers = [{"name": "Outer", "material": "Inconel718", "thickness": 1.0}]
            completed = SimpleNamespace(stdout="*ERROR invalid element set", stderr="", returncode=0)
            with patch("cosmo.core.solver_interface.subprocess.run", return_value=completed):
                self.assertFalse(
                    setup_and_run_calculix(
                        str(inp), layers, od_mm=20, ccx_path="ccx", time_seconds=60
                    )
                )

    def test_pressure_model_is_closed_and_materials_match_library(self):
        candidate = revised_geometry()
        vessel = pressure_vessel_solid(candidate).val()
        outer = candidate["od_mm"] / 2
        inner = outer - candidate["inconel_wall_mm"]
        cap = candidate["endcap_thickness_mm"]
        expected = 3.141592653589793 * (
            outer**2 * HOUSING_LENGTH_MM - inner**2 * (HOUSING_LENGTH_MM - 2 * cap)
        )
        self.assertTrue(vessel.isValid())
        self.assertGreater(vessel.Volume(), expected)
        self.assertEqual(MATERIALS["Aerogel"]["density"], 200)
        self.assertEqual(MATERIALS["Aerogel"]["conductivity"], 0.024)

    def test_revised_geometry_and_status_gate_are_consistent(self):
        candidate = revised_geometry()
        first_zone = min(start for start, _ in THERMAL_ZONES_LOCAL_MM.values())
        last_zone = max(end for _, end in THERMAL_ZONES_LOCAL_MM.values())
        self.assertEqual(first_zone, ENDCAP_THICKNESS_MM + FRONT_AXIAL_INSULATION_MM)
        self.assertEqual(
            last_zone + REAR_AXIAL_INSULATION_MM,
            HOUSING_LENGTH_MM - ENDCAP_THICKNESS_MM,
        )
        self.assertEqual(candidate["clear_id_mm"], 41)
        self.assertEqual(engineering_status("PASS", "PASS"), "PASS")
        self.assertNotEqual(engineering_status("PASS", "FAIL"), "PASS")

    def test_second_order_tetrahedron_keeps_pressure_face_detection(self):
        with TemporaryDirectory() as directory:
            inp = Path(directory) / "quadratic.inp"
            inp.write_text(
                "*NODE\n"
                "1, 1, 0, 0\n2, 0, 1, 0\n3, -1, 0, 0\n4, 0, 0, 1\n"
                "5, 0, 0, 0\n6, 0, 0, 0\n7, 0, 0, 0\n8, 0, 0, 0\n9, 0, 0, 0\n10, 0, 0, 0\n"
                "*ELEMENT, TYPE=C3D10, ELSET=Outer\n1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10\n"
                "*NODE FILE\nU\n",
                encoding="utf-8",
            )
            nodes, elements = parse_inp(inp)
            self.assertEqual(len(elements[1]), 10)
            self.assertIn((1, 1), _outer_faces(nodes, elements, outer_radius=1))

    def test_buckling_parser_and_temperature_extractor_fail_closed(self):
        with TemporaryDirectory() as directory:
            dat = Path(directory) / "buckling.dat"
            dat.write_text(" BUCKLING FACTOR = 2.1250E+00\n", encoding="utf-8")
            self.assertAlmostEqual(_parse_buckling_factor(dat), 2.125)
        with patch(
            "cosmo.core.result_extractor.parse_frd_temperatures",
            return_value=({1: (0.0, 0.0, 0.0)}, [{"time": 3600.0, "temperatures": {1: 42.0}}]),
        ):
            with self.assertRaises(ValueError):
                extract_max_internal_temperature("unused.frd", target_time=3600, r_inner=20.5)

    def test_component_temperature_zones_do_not_mix_endcaps(self):
        nodes = {
            1: (20.5, 0, 0),
            2: (20.5, 0, 110),
            3: (20.5, 0, 140),
            4: (20.5, 0, 200),
            5: (20.5, 0, 260),
        }
        temperatures = {1: 150, 2: 120, 3: 90, 4: 70, 5: 80}
        self.assertEqual(
            _zone_max_temperatures(nodes, temperatures, 20.5),
            {"Analog front-end": 120, "PCM1808": 90, "STM32F411": 70, "RTC/SD/power": 80},
        )
        axial = axial_heat_leak_screen(revised_geometry())
        self.assertLess(axial["front_initial_heat_W"], 0.3)
        self.assertLess(axial["rear_initial_heat_W"], 1.0)


if __name__ == "__main__":
    unittest.main()
