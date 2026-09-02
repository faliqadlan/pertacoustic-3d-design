"""Unit tests for the simplified compact downhole casing redesign study."""

import math
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import cadquery as cq
import numpy as np

from cosmo.compact_casing import (
    BOARD_ASSEMBLY_CLEARANCE_MM,
    COMPONENT_LIMITS,
    ENDCAP_THICKNESS_MM,
    EXTERNAL_TEMPERATURE_C,
    HOUSING_LENGTH_MM,
    INHERITED_SCREENING_POWER_W,
    MATERIALS,
    MAX_OD_MM,
    MAX_TOOL_LENGTH_MM,
    MIN_USABLE_ID_MM,
    PCM1808_ENVELOPE_MM,
    PREFERRED_OD_MM,
    PRESSURE_SCENARIO_1000M_MPA,
    PRESSURE_SCENARIO_HISTORICAL_MPA,
    PRESSURE_SCENARIO_INTERMEDIATE_MPA,
    STM32F411_ENVELOPE_MM,
    THERMAL_DURATION_S,
    THERMAL_ZONES_LOCAL_MM,
    ZERO_POWER_W,
    build_carrier_material_trade_matrix,
    build_id_od_envelope_study,
    check_cad_assembly_interferences,
    compute_carrier_dimensional_sensitivity,
    compute_carrier_tolerance_budget,
    compute_radial_budget,
    compute_required_circular_diameter,
    elastic_buckling,
    generate_compact_casing_cad,
    lame_stress,
    render_transverse_pcm1808_cross_section,
    run_architecture_trade_study,
    select_recommended_candidate,
    size_architecture_candidate,
    structural_screening,
    transient_thermal_simulation,
    zone_thermal_assessment,
    future_custom_pcb_envelope,
    is_id_od_candidate_viable,
    select_id_od_preliminary_configuration,
)


class SimplifiedCompactCasingTests(unittest.TestCase):
    """Test suite verifying no-aerogel compact casing architectures, packaging, thermal, and structural screening."""

    def test_design_envelope_constants_conform_to_formal_authority(self):
        """Verify boundary constants match formal MoM and design direction."""
        self.assertAlmostEqual(PREFERRED_OD_MM, 44.45, places=2)
        self.assertAlmostEqual(MAX_OD_MM, 57.15, places=2)
        self.assertLessEqual(HOUSING_LENGTH_MM, MAX_TOOL_LENGTH_MM)
        self.assertEqual(MAX_TOOL_LENGTH_MM, 2000.0)
        self.assertEqual(EXTERNAL_TEMPERATURE_C, 70.0)
        self.assertEqual(THERMAL_DURATION_S, 7200)
        self.assertEqual(INHERITED_SCREENING_POWER_W, 1.0)
        self.assertEqual(ZERO_POWER_W, 0.0)
        self.assertEqual(MIN_USABLE_ID_MM, 30.0)

    def test_id_floor_is_not_target_and_envelope_study_is_parametric(self):
        self.assertGreater(PREFERRED_OD_MM - 2 * 3.5, MIN_USABLE_ID_MM)
        self.assertNotIn("target_id_mm", build_id_od_envelope_study()[0])
        rows = build_id_od_envelope_study()
        self.assertEqual(len(rows), 10)
        self.assertEqual({r["od_mm"] for r in rows}, {44.45, 47.625, 50.8, 53.975, 57.15})
        self.assertEqual({r["wall_mm"] for r in rows}, {3.5, 4.0})
        selected = next(r for r in rows if r["od_mm"] == 44.45 and r["wall_mm"] == 3.5)
        self.assertAlmostEqual(selected["id_mm"], 37.45, places=2)
        self.assertEqual(selected["id_floor_status"], "PASS")
        self.assertEqual(selected["electronics_packaging_status"], "PASS")

    def test_exact_30mm_id_fails_strict_floor_rule(self):
        """1. Exactly 30.0 mm ID fails the strict ID > 30 mm floor rule."""
        rows = build_id_od_envelope_study(od_values=(36.0,), wall_values=(3.0,))
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertAlmostEqual(r["id_mm"], 30.0, places=2)
        self.assertEqual(r["id_floor_status"], "FAIL")
        self.assertAlmostEqual(r["margin_above_min_id_mm"], 0.0, places=2)
        self.assertFalse(is_id_od_candidate_viable(r))

    def test_required_diameter_is_derived_and_floor_can_pass_while_packaging_fails(self):
        """2 & 9. Derived required diameter and floor pass while packaging fails."""
        self.assertAlmostEqual(compute_required_circular_diameter(30.0, 12.0), math.hypot(32.0, 14.0), places=6)
        floor_only = next(r for r in build_id_od_envelope_study(od_values=(34.1,), wall_values=(2.0,)))
        self.assertEqual(floor_only["id_floor_status"], "PASS")
        self.assertEqual(floor_only["electronics_packaging_status"], "FAIL")
        self.assertFalse(is_id_od_candidate_viable(floor_only))
        self.assertEqual(compute_radial_budget(od_mm=32.0, wall_mm=1.0, is_discrete_carrier=True)["direct_fit"], False)

    def test_structural_status_explicitly_states_10mpa_screening_basis(self):
        """3. Structural status explicitly states the 10 MPa screening basis."""
        rows = build_id_od_envelope_study()
        for r in rows:
            self.assertIn("10 MPa SCREENING", r["structural_10mpa_screening_status"])
            self.assertIn(r["structural_10mpa_screening_status"], {"PASS @ 10 MPa SCREENING", "FAIL @ 10 MPa SCREENING"})
            self.assertEqual(r["structural_screening_status"], r["structural_10mpa_screening_status"])

    def test_structural_authority_remains_conditional_design_pressure_unresolved(self):
        """4. Structural authority remains CONDITIONAL — DESIGN PRESSURE UNRESOLVED."""
        rows = build_id_od_envelope_study()
        for r in rows:
            self.assertEqual(r["structural_authority_status"], "CONDITIONAL — DESIGN PRESSURE UNRESOLVED")

    def test_20mpa_and_historical_10kpsi_metrics_included_in_envelope(self):
        """5. 20 MPa and historical 10k psi values are included in the envelope result."""
        rows = build_id_od_envelope_study()
        for r in rows:
            self.assertIn("strength_ratio_10mpa", r)
            self.assertIn("buckling_fos_10mpa", r)
            self.assertIn("strength_ratio_20mpa", r)
            self.assertIn("buckling_fos_20mpa", r)
            self.assertIn("strength_ratio_historical_10kpsi", r)
            self.assertIn("buckling_fos_historical_10kpsi", r)
            self.assertIsInstance(r["strength_ratio_20mpa"], float)
            self.assertIsInstance(r["buckling_fos_20mpa"], float)
            self.assertIsInstance(r["strength_ratio_historical_10kpsi"], float)
            self.assertIsInstance(r["buckling_fos_historical_10kpsi"], float)
            # Clearance naming check per Section D
            self.assertEqual(r["board_assembly_clearance_per_side_mm"], BOARD_ASSEMBLY_CLEARANCE_MM)
            self.assertEqual(r["carrier_manufacturing_allowance"], "UNRESOLVED")
            self.assertNotIn("carrier_allowance_mm", r)

        # FoS trend visibility: increasing OD at fixed wall thickness reduces buckling margin
        wall_35_rows = [r for r in rows if r["wall_mm"] == 3.5]
        buckling_10mpa = [r["buckling_fos_10mpa"] for r in wall_35_rows]
        self.assertEqual(buckling_10mpa, sorted(buckling_10mpa, reverse=True))

    def test_recommendation_selector_derives_44_45_with_current_inputs(self):
        """6. The recommendation selector derives 44.45/3.5 with current inputs."""
        rows = build_id_od_envelope_study()
        rec = select_id_od_preliminary_configuration(rows)
        self.assertIsNotNone(rec)
        self.assertAlmostEqual(rec["od_mm"], 44.45, places=2)
        self.assertAlmostEqual(rec["wall_mm"], 3.50, places=2)
        self.assertAlmostEqual(rec["id_mm"], 37.45, places=2)
        self.assertEqual(rec["overall_preliminary_recommendation"], "RECOMMENDED PRELIMINARY CONFIGURATION")

    def test_selector_picks_next_smallest_viable_od_when_44_45_infeasible(self):
        """7. If 44.45 becomes infeasible in a synthetic test, the next smallest viable OD is selected."""
        import copy
        rows = build_id_od_envelope_study()
        synthetic_rows = copy.deepcopy(rows)
        # Mark all 44.45 mm OD candidates as failing packaging
        for r in synthetic_rows:
            if math.isclose(r["od_mm"], 44.45):
                r["electronics_packaging_status"] = "FAIL"
                r["packaging_diametral_margin_mm"] = -1.0
        rec = select_id_od_preliminary_configuration(synthetic_rows)
        self.assertIsNotNone(rec)
        self.assertAlmostEqual(rec["od_mm"], 47.625, places=3)
        self.assertAlmostEqual(rec["wall_mm"], 3.50, places=2)

    def test_selector_returns_none_if_no_od_viable(self):
        """8. If no OD is viable, no false recommendation is produced."""
        import copy
        rows = build_id_od_envelope_study()
        synthetic_rows = copy.deepcopy(rows)
        for r in synthetic_rows:
            r["electronics_packaging_status"] = "FAIL"
        rec = select_id_od_preliminary_configuration(synthetic_rows)
        self.assertIsNone(rec)

    def test_current_electronics_requirement_derived_from_source_dimensions(self):
        """9. Current electronics requirement remains derived from source dimensions."""
        w_pcm, h_pcm = PCM1808_ENVELOPE_MM[1], PCM1808_ENVELOPE_MM[2]
        self.assertEqual(w_pcm, 30.0)
        self.assertEqual(h_pcm, 12.0)
        expected_d = math.hypot(w_pcm + 2.0 * BOARD_ASSEMBLY_CLEARANCE_MM, h_pcm + 2.0 * BOARD_ASSEMBLY_CLEARANCE_MM)
        derived_d = compute_required_circular_diameter(w_pcm, h_pcm, BOARD_ASSEMBLY_CLEARANCE_MM)
        self.assertAlmostEqual(derived_d, expected_d, places=6)
        self.assertAlmostEqual(derived_d, 34.928, places=3)

    def test_future_custom_pcb_dimensions_are_input_driven(self):
        """10. Future custom-PCB dimensions remain input-driven."""
        unresolved = future_custom_pcb_envelope()
        self.assertEqual(unresolved["status"], "INPUT REQUIRED / UNRESOLVED")
        self.assertIsNone(unresolved["required_diameter_mm"])
        measured = future_custom_pcb_envelope(width_mm=20.0, height_mm=10.0)
        self.assertAlmostEqual(measured["required_diameter_mm"], math.hypot(22.0, 12.0), places=6)

    def test_pcm1808_exact_geometry_and_packaging_clearance(self):
        """Verify exact PCM1808 nominal dimensions, clearance calculation, and direct circular fit rules."""
        self.assertEqual(PCM1808_ENVELOPE_MM[1], 30.0)
        self.assertEqual(PCM1808_ENVELOPE_MM[2], 12.0)
        self.assertEqual(BOARD_ASSEMBLY_CLEARANCE_MM, 1.0)
        
        eff_w = 30.0 + 2.0 * BOARD_ASSEMBLY_CLEARANCE_MM  # 32.0
        eff_h = 12.0 + 2.0 * BOARD_ASSEMBLY_CLEARANCE_MM  # 14.0
        expected_diagonal = math.hypot(eff_w, eff_h)  # sqrt(32^2 + 14^2) = sqrt(1220) ≈ 34.928 mm
        self.assertAlmostEqual(expected_diagonal, 34.928, places=3)
        
        # 1. Full circumferential 1.5 mm PEEK liner (Clear ID = 34.45 mm < 34.93 mm -> INFEASIBLE)
        full_liner = compute_radial_budget(od_mm=44.45, wall_mm=3.5, liner_mm=1.5, aerogel_mm=0.0, is_discrete_carrier=False)
        self.assertAlmostEqual(full_liner["clear_id_mm"], 34.45, places=2)
        self.assertFalse(full_liner["direct_fit"])
        self.assertIn("INFEASIBLE", full_liner["packaging_status"])
        
        # 2. Conformal carrier rails in 3.5 mm Inconel shell bore (Shell Bore ID = 37.45 mm >= 34.93 mm -> FEASIBLE)
        discrete_carrier = compute_radial_budget(od_mm=44.45, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True)
        self.assertAlmostEqual(discrete_carrier["shell_bore_id_mm"], 37.45, places=2)
        self.assertAlmostEqual(discrete_carrier["clear_id_mm"], 37.45, places=2)
        self.assertTrue(discrete_carrier["direct_fit"])
        self.assertAlmostEqual(discrete_carrier["clearance_margin_mm"], (37.45 - expected_diagonal) / 2.0, places=2)
        self.assertIn("FEASIBLE", discrete_carrier["packaging_status"])

    def test_carrier_tolerance_budget_includes_thermal_expansion(self):
        """Verify explicit carrier tolerance budget accounts for differential expansion, tolerances, and assumed screening allowance."""
        budget = compute_carrier_tolerance_budget(
            shell_bore_nom_mm=37.450, carrier_od_nom_mm=37.050, carrier_material_key="PEEK", t_assembly_c=20.0, t_max_c=70.0
        )
        self.assertEqual(budget["shell_bore_nom_mm"], 37.450)
        self.assertEqual(budget["carrier_od_nom_mm"], 37.050)
        self.assertAlmostEqual(budget["cold_clearance_diametral_mm"], 0.400, places=3)
        self.assertAlmostEqual(budget["cold_clearance_radial_mm"], 0.200, places=3)
        
        # Differential expansion: Inconel 13 ppm/K, PEEK 55 ppm/K, Delta T = 50 K
        # Inconel bore expansion: 37.45 * 13e-6 * 50 = +0.0243 mm
        # PEEK carrier expansion: 37.05 * 55e-6 * 50 = +0.1019 mm
        # Diff growth: 0.1019 - 0.0243 = +0.0776 mm diametral (+0.0388 mm radial)
        self.assertAlmostEqual(budget["diff_thermal_growth_diametral_mm"], 0.0776, places=3)
        self.assertAlmostEqual(budget["diff_thermal_growth_radial_mm"], 0.0388, places=3)
        self.assertAlmostEqual(budget["dim_uncertainty_allowance_diametral_mm"], 0.020, places=3)
        self.assertAlmostEqual(budget["hot_clearance_diametral_mm"], 0.3024, places=3)
        self.assertAlmostEqual(budget["hot_clearance_radial_mm"], 0.1512, places=3)
        self.assertTrue(budget["adequate_clearance"])

    def test_carrier_tolerance_budget_returns_complete_dict(self):
        budget = compute_carrier_tolerance_budget()
        self.assertIsInstance(budget, dict)
        self.assertIn("cold_clearance_diametral_mm", budget)
        self.assertIn("worst_case_hot_diametral_mm", budget)
        self.assertAlmostEqual(budget["cold_clearance_diametral_mm"], 0.4, places=3)

    def test_radial_budget_returns_dict_with_nested_tolerance_budget(self):
        budget = compute_radial_budget(44.45, 3.5, is_discrete_carrier=True)
        tol = budget["tolerance_budget"]
        self.assertIsInstance(budget, dict)
        self.assertIsInstance(tol, dict)
        self.assertAlmostEqual(budget["shell_bore_id_mm"], 37.45, places=2)
        self.assertIn("dim_uncertainty_allowance_diametral_mm", tol)
        self.assertIn("hot_clearance_diametral_mm", tol)
        self.assertIn("hot_clearance_radial_mm", tol)
        self.assertIn("adequate_clearance", tol)
        self.assertAlmostEqual(tol["hot_clearance_diametral_mm"], 0.3024, places=3)
        self.assertAlmostEqual(tol["hot_clearance_radial_mm"], 0.1512, places=3)
        self.assertTrue(tol["adequate_clearance"])

    def test_final_carrier_remains_inside_shell_at_nominal_geometry(self):
        """Verify that nominal carrier outer radius (18.525 mm) remains strictly inside the shell bore (18.725 mm)."""
        shell_bore_radius = (44.45 - 2 * 3.5) / 2.0  # 18.725 mm
        carrier_outer_radius = (37.45 - 0.400) / 2.0  # 18.525 mm
        self.assertLess(carrier_outer_radius, shell_bore_radius)
        self.assertAlmostEqual(shell_bore_radius - carrier_outer_radius, 0.200, places=3)

    def test_interference_calculation_errors_fail_closed(self):
        """Verify that geometry kernel or solid calculation errors fail closed (passed=False, status='ERROR / NOT VERIFIED')."""
        # 1. Missing keys / exception
        invalid_geom = {"od_mm": 44.45}
        result = check_cad_assembly_interferences(invalid_geom)
        self.assertFalse(result["passed"])
        self.assertEqual(result["status"], "ERROR / NOT VERIFIED")
        self.assertIsNotNone(result["error"])
        self.assertIn("KeyError", result["error"])

    def test_invalid_boolean_shape_fails_closed(self):
        """Verify that an invalid OCC Boolean result shape fails closed rather than silently returning 0.0."""
        from unittest.mock import MagicMock, patch
        
        cand = size_architecture_candidate(
            "Architecture A", od_mm=44.45, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True
        )
        
        # Mock an invalid CadQuery shape (val is not None, but isValid() is False)
        mock_shape = MagicMock()
        mock_shape.isValid.return_value = False
        mock_shape.Volume.return_value = 0.0
        
        mock_workplane = MagicMock()
        mock_workplane.objects = [mock_shape]
        mock_workplane.val.return_value = mock_shape
        
        with patch.object(cq.Workplane, "intersect", return_value=mock_workplane):
            res = check_cad_assembly_interferences(cand)
            self.assertFalse(res["passed"])
            self.assertEqual(res["status"], "ERROR / NOT VERIFIED")
            self.assertIn("ValueError", res["error"])

    def test_non_empty_boolean_result_with_val_none_fails_closed(self):
        """Verify that a non-empty Boolean objects list with val() == None fails closed."""
        from unittest.mock import MagicMock, patch
        
        cand = size_architecture_candidate(
            "Architecture A", od_mm=44.45, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True
        )
        
        # Mock non-empty objects list, but val() is None
        mock_workplane = MagicMock()
        mock_workplane.objects = [MagicMock()]
        mock_workplane.val.return_value = None
        
        with patch.object(cq.Workplane, "intersect", return_value=mock_workplane):
            res = check_cad_assembly_interferences(cand)
            self.assertFalse(res["passed"])
            self.assertEqual(res["status"], "ERROR / NOT VERIFIED")
            self.assertIn("ValueError", res["error"])

    def test_current_shell_thermal_result_is_not_labeled_cavity_temperature(self):
        """Verify that 1D thermal simulation explicitly labels its result as inner shell surface temperature."""
        cand = size_architecture_candidate(
            "Architecture A", od_mm=44.45, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True
        )
        t_res = cand["thermal_1w"]
        self.assertIn("thermal_metric_label", t_res)
        self.assertIn("INNER SHELL SURFACE", t_res["thermal_metric_label"])
        self.assertIn("inner_shell_temperature_C", t_res)
        self.assertAlmostEqual(t_res["final_inner_shell_temperature_C"], 70.00, places=1)

    def test_internal_thermal_resistance_budget_derived_from_live_results(self):
        """Verify allowable internal thermal resistance budget calculation: (85 - T_shell) / P."""
        from cosmo.compact_casing import compute_internal_thermal_resistance_budget
        budget = compute_internal_thermal_resistance_budget(inner_shell_temp_c=70.00, power_w=1.0)
        
        # For STM32F411CEU6 (limit 85 C): allowable delta T = 15 K, allowable R_internal = 15 K/W
        stm = budget["STM32F411CEU6"]
        self.assertEqual(stm["operating_limit_status"], "VERIFIED (-40...+85 C)")
        self.assertEqual(stm["allowable_delta_T_K"], 15.00)
        self.assertEqual(stm["allowable_r_internal_K_per_W"], 15.00)
        self.assertEqual(stm["thermal_model_status"], "CONDITIONAL / WITHIN INNER-SHELL-BASED SCREENING BUDGET")
        self.assertEqual(stm["junction_temperature"], "NOT ESTABLISHED")
        
        # Unspecified ICs remain CONDITIONAL / UNVERIFIED
        rtc = budget["RTC Module (Unspecified PN)"]
        self.assertEqual(rtc["operating_limit_status"], "UNSPECIFIED")
        self.assertEqual(rtc["thermal_model_status"], "CONDITIONAL / UNVERIFIED")
        self.assertEqual(rtc["junction_temperature"], "NOT ESTABLISHED")

    def test_internal_thermal_sensitivity_sweep(self):
        """Verify lumped parameter sweep across R_internal."""
        from cosmo.compact_casing import compute_internal_thermal_sensitivity
        rows = compute_internal_thermal_sensitivity(inner_shell_temp_c=70.00, power_w=1.0, r_values=[0.0, 5.0, 10.0, 15.0, 20.0])
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["t_electronics_screen_C"], 70.00)
        self.assertEqual(rows[0]["status"], "WITHIN 85C BOUND")
        self.assertEqual(rows[3]["t_electronics_screen_C"], 85.00)
        self.assertEqual(rows[3]["status"], "WITHIN 85C BOUND")
        self.assertEqual(rows[4]["t_electronics_screen_C"], 90.00)
        self.assertEqual(rows[4]["status"], "EXCEEDS 85C BOUND")

    def test_recommendation_cannot_select_missing_or_failed_collision_evidence(self):
        """Verify that recommendation engine rejects candidates with missing, False, or ERROR collision status."""
        candidates, _ = run_architecture_trade_study()
        
        bad_cand_1 = dict(candidates[0])
        bad_cand_1["collision_results"] = None
        
        bad_cand_2 = dict(candidates[0])
        bad_cand_2["collision_results"] = {"passed": False, "status": "FAIL (1.200 mm³ collision)"}
        
        bad_cand_3 = dict(candidates[0])
        bad_cand_3["collision_results"] = {"passed": False, "status": "ERROR / NOT VERIFIED", "error": "KernelCrash"}
        
        with self.assertRaises(ValueError):
            select_recommended_candidate([bad_cand_1, bad_cand_2, bad_cand_3])

    def test_tolerance_budget_gate_in_recommendation_engine(self):
        """Verify that discrete-carrier candidates with missing or inadequate tolerance budget are disqualified."""
        candidates, _ = run_architecture_trade_study()
        
        # Inadequate clearance
        bad_cand_tol = dict(candidates[0])
        bad_cand_tol["packaging"] = dict(candidates[0]["packaging"])
        bad_cand_tol["packaging"]["tolerance_budget"] = {"adequate_clearance": False}
        
        # Missing tolerance budget
        bad_cand_no_tol = dict(candidates[0])
        bad_cand_no_tol["packaging"] = dict(candidates[0]["packaging"])
        bad_cand_no_tol["packaging"]["tolerance_budget"] = None
        
        with self.assertRaises(ValueError):
            select_recommended_candidate([bad_cand_tol, bad_cand_no_tol])

    def test_total_tool_length_gate_in_recommendation_engine(self):
        """Verify that candidate exceeding total modeled tool length of 2000 mm is disqualified."""
        cand_long = size_architecture_candidate(
            "Architecture A: Long Housing", od_mm=44.45, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True
        )
        cand_long["total_tool_length_mm"] = 2050.0  # Exceeds 2000 mm gate
        
        with self.assertRaises(ValueError):
            select_recommended_candidate([cand_long])

    def test_wall_selection_not_list_order_dependent(self):
        """Verify that 3.5 mm baseline wall selection is governed by explicit packaging rule and not list order."""
        candidates, _ = run_architecture_trade_study()
        # Find 3.5mm and 4.0mm candidates
        c_35 = next(c for c in candidates if "3.5 mm Wall" in c["architecture"])
        c_40 = next(c for c in candidates if "4.0 mm Wall" in c["architecture"])
        
        # Put 4.0 mm first
        reversed_order = [c_40, c_35]
        selected = select_recommended_candidate(reversed_order)
        self.assertEqual(selected["wall_mm"], 3.5)
        self.assertIn("3.5 mm Wall", selected["architecture"])
        self.assertIn("PRELIMINARY PACKAGING-FAVORABLE SCREENING BASELINE", selected["wall_status"])

    def test_only_one_candidate_marked_recommended(self):
        """Verify that exactly one candidate in the trade study has is_recommended_baseline == True."""
        candidates, recommended = run_architecture_trade_study()
        rec_flags = [c.get("is_recommended_baseline", False) for c in candidates]
        self.assertEqual(sum(rec_flags), 1)
        self.assertTrue(recommended["is_recommended_baseline"])

    def test_report_and_csv_consistency_for_recommended_candidate(self):
        """Verify that generated Markdown report and CSV match 100% numerically for the recommended baseline."""
        candidates, recommended = run_architecture_trade_study()
        
        with TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            from cosmo.compact_casing import export_trade_study_csv_and_report
            export_trade_study_csv_and_report(candidates, recommended, out_dir)
            
            csv_path = out_dir / "compact_casing_trade_study.csv"
            md_path = out_dir / "compact_casing_redesign_report.md"
            
            self.assertTrue(csv_path.exists())
            self.assertTrue(md_path.exists())
            
            md_text = md_path.read_text(encoding="utf-8")
            
            # Read CSV recommended row
            import csv
            with open(csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
            rec_csv = next(r for r in rows if r["architecture"] == recommended["architecture"])
            
            # Verify OD, shell bore, wall thickness, 2h 1W temp in report text
            self.assertIn(f"{float(rec_csv['od_mm']):.2f} mm", md_text)
            self.assertIn(f"{float(rec_csv['wall_mm']):.2f} mm", md_text)
            self.assertIn(f"{float(rec_csv['shell_bore_id_mm']):.2f} mm", md_text)
            self.assertIn(f"{float(rec_csv['inner_shell_temp_2h_1w_C']):.2f} °C", md_text)
            self.assertEqual(rec_csv["is_recommended_baseline"], "True")
            self.assertEqual(rec_csv["strength_basis"], "YIELD")

    def test_polymer_csv_strength_values_not_mislabeled_as_yield(self):
        """Verify that CSV output columns do not mislabel polymer strength as yield."""
        candidates, recommended = run_architecture_trade_study()
        with TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            from cosmo.compact_casing import export_trade_study_csv_and_report
            export_trade_study_csv_and_report(candidates, recommended, out_dir)
            
            csv_path = out_dir / "compact_casing_trade_study.csv"
            import csv
            with open(csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                fieldnames = reader.fieldnames
                
            self.assertNotIn("fos_yield_1000m", fieldnames)
            self.assertIn("strength_basis", fieldnames)
            self.assertIn("strength_ratio_10mpa", fieldnames)
            
            inconel_row = next(r for r in rows if "Architecture A" in r["architecture"])
            self.assertEqual(inconel_row["strength_basis"], "YIELD")
            
            ppa_only_row = next(r for r in rows if "Architecture G" in r["architecture"])
            self.assertEqual(ppa_only_row["strength_basis"], "TENSILE_STRESS_AT_BREAK_SCREENING")
            
            peek_only_row = next(r for r in rows if "Architecture F" in r["architecture"])
            self.assertEqual(peek_only_row["strength_basis"], "TENSILE_STRENGTH_SCREENING")

    def test_cad_assembly_bounding_extent_matches_total_length(self):
        """Verify that CAD solid assembly axial extent matches modeled length <= 2000 mm."""
        cand = size_architecture_candidate(
            "Architecture A", od_mm=44.45, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True
        )
        parts = generate_compact_casing_cad(cand)
        z_min = min(solid.val().BoundingBox().zmin for solid, _, _ in parts)
        z_max = max(solid.val().BoundingBox().zmax for solid, _, _ in parts)
        cad_span = round(z_max - z_min, 1)
        self.assertAlmostEqual(cad_span, 656.9, places=1)
        self.assertLessEqual(cad_span, MAX_TOOL_LENGTH_MM)

    def test_wall_thickness_sensitivity_included_in_trade_study(self):
        """Verify that 4.0 mm wall sensitivity candidate is evaluated and achieves higher buckling margin."""
        candidates, _ = run_architecture_trade_study()
        wall_4mm_cand = next((c for c in candidates if "4.0 mm Wall" in c["architecture"]), None)
        self.assertIsNotNone(wall_4mm_cand)
        self.assertEqual(wall_4mm_cand["wall_mm"], 4.0)
        self.assertEqual(wall_4mm_cand["packaging"]["shell_bore_id_mm"], 36.45)
        self.assertTrue(wall_4mm_cand["packaging"]["direct_fit"])
        
        # Buckling safety factor at 10k psi for 4.0mm wall should exceed 2.0 (2.45)
        fos_buckle_10k = wall_4mm_cand["structural"]["buckling_historical"]["buckling_safety_factor"]
        self.assertGreaterEqual(fos_buckle_10k, 2.0)
        self.assertAlmostEqual(fos_buckle_10k, 2.45, places=2)

    def test_pcm1808_reserved_envelope_and_assembly_zero_prohibited_interference(self):
        """Verify automated Boolean intersection interference checks pass with zero collision volume."""
        cand = size_architecture_candidate(
            "Architecture A", od_mm=44.45, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True
        )
        collision = check_cad_assembly_interferences(cand)
        self.assertTrue(collision["passed"], f"Interference check failed: {collision}")
        self.assertEqual(collision["carrier_vs_shell_vol_mm3"], 0.0)
        self.assertEqual(collision["carrier_vs_pcm_general_envelope_vol_mm3"], 0.0)
        self.assertEqual(collision["pcm_nominal_vs_shell_vol_mm3"], 0.0)
        self.assertEqual(collision["pcm_nominal_vs_buffer_vol_mm3"], 0.0)
        self.assertEqual(collision["max_interference_vol_mm3"], 0.0)

    def test_ppa_strength_basis_is_explicit_and_not_mislabeled_as_yield(self):
        """Verify that PPA strength basis is explicitly labeled as tensile stress at break and not yield."""
        ppa_stress = lame_stress(od_mm=44.45, wall_mm=3.5, pressure_mpa=10.0, material_key="PPA_Amodel_A1133HS")
        self.assertEqual(ppa_stress["strength_basis"], "TENSILE_STRESS_AT_BREAK_SCREENING")
        self.assertEqual(ppa_stress["screening_strength_mpa"], 181.0)
        self.assertNotIn("yield_strength_mpa_70c_screening", MATERIALS["PPA_Amodel_A1133HS"])

    def test_ppa_derived_70c_properties_match_solvay_source_and_interpolation(self):
        """Verify Solvay Amodel technical design guide source data and exact linear interpolation at 70 °C."""
        ppa = MATERIALS["PPA_Amodel_A1133HS"]
        self.assertIn("provenance", ppa)
        self.assertEqual(ppa["density"], 1480)
        self.assertEqual(ppa["elastic_modulus_mpa_23c"], 13400)
        self.assertEqual(ppa["elastic_modulus_mpa_100c"], 10800)
        self.assertEqual(ppa["tensile_strength_mpa_23c"], 233)
        self.assertEqual(ppa["tensile_strength_mpa_100c"], 148)
        self.assertEqual(ppa["poisson_ratio"], 0.41)
        self.assertEqual(ppa["water_absorption_24h_percent"], 0.20)
        self.assertEqual(ppa["water_absorption_sat_percent"], 1.80)
        
        # Modulus at 70 °C: 13400 - (47/77)*(13400 - 10800) = 11812.99 MPa ≈ 11813 MPa
        expected_e_70 = round(13400.0 - (47.0 / 77.0) * (13400.0 - 10800.0))
        self.assertEqual(ppa["elastic_modulus_mpa_70c"], expected_e_70)
        self.assertEqual(ppa["elastic_modulus_mpa_70c"], 11813)
        
        # Tensile strength at 70 °C: 233 - (47/77)*(233 - 148) = 181.12 MPa ≈ 181 MPa
        expected_sigma_70 = round(233.0 - (47.0 / 77.0) * (233.0 - 148.0))
        self.assertEqual(ppa["screening_tensile_strength_mpa_70c"], expected_sigma_70)
        self.assertEqual(ppa["screening_tensile_strength_mpa_70c"], 181)

    def test_unsupported_material_values_not_marked_verified(self):
        """Verify that assumed/screening values like PPA conductivity are NOT marked VERIFIED."""
        ppa = MATERIALS["PPA_Amodel_A1133HS"]
        self.assertNotIn("VERIFIED", ppa["provenance"]["conductivity"])
        self.assertIn("ASSUMED SCREENING VALUE", ppa["provenance"]["conductivity"])
        self.assertIn("ASSUMED SCREENING VALUE", ppa["provenance"]["specific_heat"])

    def test_peek_provenance_and_clte(self):
        """Verify Victrex 450G PEEK provenance and CLTE data."""
        peek = MATERIALS["PEEK"]
        self.assertEqual(peek["thermal_expansion_per_c"], 0.000045)
        self.assertEqual(peek["thermal_expansion_cross_flow_per_c"], 0.000055)
        self.assertIn("VERIFIED MANUFACTURER VALUE", peek["provenance"]["thermal_expansion_per_c"])
        self.assertIn("VERIFIED MANUFACTURER VALUE", peek["provenance"]["thermal_expansion_cross_flow_per_c"])
        self.assertIn("VERIFIED MANUFACTURER VALUE", peek["provenance"]["density"])
        self.assertIn("VERIFIED MANUFACTURER VALUE", peek["provenance"]["conductivity"])
        self.assertIn("ASSUMED SCREENING VALUE", peek["provenance"]["specific_heat"])

    def test_thermal_simulation_demonstrates_aerogel_heat_trapping(self):
        """Verify that aerogel is detrimental under 1.0 W internal dissipation at 70 °C."""
        cand_with_aero = size_architecture_candidate(
            "With Aerogel", od_mm=44.45, wall_mm=3.5, liner_mm=1.5, aerogel_mm=2.225, is_discrete_carrier=False
        )
        cand_no_aero = size_architecture_candidate(
            "No Aerogel Conformal PEEK", od_mm=44.45, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True
        )
        
        t_30m_with_aero = cand_with_aero["thermal_0w"]["inner_temperature_C"][60]
        t_30m_no_aero = cand_no_aero["thermal_0w"]["inner_temperature_C"][60]
        self.assertLess(t_30m_with_aero, t_30m_no_aero)
        
        t1_with_aero = cand_with_aero["thermal_1w"]["final_inner_temperature_C"]
        t1_no_aero = cand_no_aero["thermal_1w"]["final_inner_temperature_C"]
        self.assertGreater(t1_with_aero, t1_no_aero)
        self.assertLess(t1_no_aero, 85.0)

    def test_polymer_only_casing_shows_structural_limitations(self):
        """Verify that PEEK-only and PPA-only casings exhibit severe buckling vulnerability."""
        peek_casing = size_architecture_candidate(
            "Architecture F: PEEK-Only", od_mm=44.45, wall_mm=7.225, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=False,
            casing_material="PEEK", liner_material="PEEK"
        )
        fos_buckle_hist_peek = peek_casing["structural"]["buckling_historical"]["buckling_safety_factor"]
        self.assertLess(fos_buckle_hist_peek, 1.0)
        self.assertIn("EXPLORATORY", peek_casing["overall_status"])
        
        ppa_casing = size_architecture_candidate(
            "Architecture G: PPA-Only", od_mm=44.45, wall_mm=7.225, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=False,
            casing_material="PPA_Amodel_A1133HS", liner_material="PPA_Amodel_A1133HS"
        )
        fos_buckle_hist_ppa = ppa_casing["structural"]["buckling_historical"]["buckling_safety_factor"]
        self.assertLess(fos_buckle_hist_ppa, 1.0)
        self.assertIn("EXPLORATORY", ppa_casing["overall_status"])

    def test_inconel_structural_screening_multi_scenarios(self):
        """Verify Inconel 718 metallic shell maintains high structural margin under ~1000 m and 20 MPa."""
        struct = structural_screening(od_mm=44.45, wall_mm=3.5, material_key="Inconel718")
        
        fos_yield_1000m = struct["scenarios"]["scenario_1000m_10mpa"]["screening_strength_ratio"]
        fos_buckle_1000m = struct["buckling_1000m"]["buckling_safety_factor"]
        fos_yield_20mpa = struct["scenarios"]["scenario_intermediate_20mpa"]["screening_strength_ratio"]
        fos_buckle_20mpa = struct["buckling_20mpa"]["buckling_safety_factor"]
        fos_yield_hist = struct["scenarios"]["scenario_historical_68_9mpa"]["screening_strength_ratio"]
        
        self.assertGreaterEqual(fos_yield_1000m, 10.0)
        self.assertGreaterEqual(fos_buckle_1000m, 5.0)
        self.assertGreaterEqual(fos_yield_20mpa, 5.0)
        self.assertGreaterEqual(fos_buckle_20mpa, 2.5)
        self.assertGreaterEqual(fos_yield_hist, 2.0)

    def test_component_limits_exact_and_conditional_classification(self):
        """Verify that only authorized ICs are verified and unspecified parts are unverified."""
        self.assertIsNone(COMPONENT_LIMITS["RTC Module (Unspecified PN)"]["min_C"])
        self.assertIsNone(COMPONENT_LIMITS["RTC Module (Unspecified PN)"]["max_C"])
        self.assertEqual(COMPONENT_LIMITS["RTC Module (Unspecified PN)"]["status"], "CONDITIONAL / UNVERIFIED")
        
        assessment = zone_thermal_assessment(final_inner_shell_temp_C=70.00)
        self.assertEqual(assessment["STM32F411CEU6"]["operating_limit_status"], "VERIFIED (-40...+85 C)")
        self.assertEqual(assessment["STM32F411CEU6"]["thermal_model_status"], "CONDITIONAL / WITHIN INNER-SHELL-BASED SCREENING BUDGET")
        self.assertEqual(assessment["PCM1808"]["operating_limit_status"], "VERIFIED (-40...+85 C)")
        self.assertEqual(assessment["PCM1808"]["thermal_model_status"], "CONDITIONAL / WITHIN INNER-SHELL-BASED SCREENING BUDGET")
        self.assertEqual(assessment["RTC Module (Unspecified PN)"]["thermal_model_status"], "CONDITIONAL / UNVERIFIED")
        self.assertEqual(assessment["RTC Module (Unspecified PN)"]["margin_C"], "N/A (Unspecified Part Rating)")
        self.assertEqual(assessment["MicroSD Storage (Unspecified PN)"]["thermal_model_status"], "CONDITIONAL / UNVERIFIED")

    def test_recommendation_engine_rule_logic(self):
        """Verify that candidate recommendation is governed by explicit multi-gate engineering rules."""
        candidates, recommended = run_architecture_trade_study()
        self.assertGreaterEqual(len(candidates), 7)
        
        self.assertLessEqual(recommended["od_mm"], MAX_OD_MM)
        self.assertLessEqual(recommended.get("total_tool_length_mm", 0.0), MAX_TOOL_LENGTH_MM)
        self.assertTrue(recommended["packaging"]["direct_fit"])
        self.assertLessEqual(recommended["thermal_1w"]["final_inner_temperature_C"], 85.0)
        self.assertIn("Inconel", recommended["casing_material"])
        self.assertTrue(recommended["collision_results"]["passed"])
        
        selected = select_recommended_candidate(candidates)
        self.assertEqual(selected["architecture"], recommended["architecture"])
        self.assertEqual(selected["od_mm"], PREFERRED_OD_MM)
        self.assertTrue(selected["is_recommended_baseline"])

    def test_3d_cad_solid_watertight_and_step_export_conformal_carrier(self):
        """Verify watertight CadQuery solid generation for conformal carrier casing."""
        cand = size_architecture_candidate(
            "Architecture A", od_mm=44.45, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True
        )
        parts = generate_compact_casing_cad(cand)
        self.assertGreaterEqual(len(parts), 9)
        
        for solid, name, _ in parts:
            val = solid.val()
            self.assertTrue(val.isValid(), f"Solid {name} is not a valid solid")
            self.assertGreater(val.Volume(), 0.0, f"Solid {name} has zero volume")
            
        with TemporaryDirectory() as tmpdir:
            step_path = Path(tmpdir) / "test_conformal_carrier_casing.step"
            generate_compact_casing_cad(cand, output_step_path=step_path)
            self.assertTrue(step_path.exists())
            self.assertGreater(step_path.stat().st_size, 1000)

    def test_transverse_cross_section_render_succeeds(self):
        """Verify transverse PCM1808 clearance cross-section figure is rendered properly."""
        with TemporaryDirectory() as tmpdir:
            out_png = Path(tmpdir) / "test_transverse.png"
            render_transverse_pcm1808_cross_section(out_png)
            self.assertTrue(out_png.exists())
            self.assertGreater(out_png.stat().st_size, 5000)

    def test_pa66_material_properties_and_datasheet_exactness(self):
        """Verify BASF Ultramid A3WG6 HRX BK23591 PA66-GF30 properties match verified datasheet values."""
        pa66 = MATERIALS["PA66_Ultramid_A3WG6_HRX"]
        
        self.assertEqual(pa66["grade"], "Ultramid A3WG6 HRX BK23591")
        self.assertEqual(pa66["polymer_family"], "PA66-GF30")
        self.assertEqual(pa66["density"], 1370)
        self.assertEqual(pa66["conductivity"], 0.36)
        self.assertEqual(pa66["specific_heat"], 1260)
        self.assertEqual(pa66["melting_temperature_c"], 260)
        self.assertEqual(pa66["hdt_a_1_8mpa_c"], 245)
        self.assertEqual(pa66["hdt_b_0_45mpa_c"], 260)
        
        # Dry vs Conditioned Mechanical Properties
        self.assertEqual(pa66["elastic_modulus_mpa_23c_dry"], 9500)
        self.assertEqual(pa66["elastic_modulus_mpa_23c_cond"], 6000)
        self.assertEqual(pa66["tensile_stress_at_break_mpa_23c_dry"], 185)
        self.assertEqual(pa66["tensile_stress_at_break_mpa_23c_cond"], 110)
        self.assertEqual(pa66["strength_basis"], "TENSILE_STRESS_AT_BREAK_SCREENING")
        self.assertEqual(pa66["flexural_modulus_mpa_23c_dry"], 9200)
        self.assertEqual(pa66["flexural_modulus_mpa_23c_cond"], 5800)
        self.assertEqual(pa66["tensile_creep_modulus_1000h_cond_mpa"], 4800)
        
        # Moisture absorption ranges
        self.assertEqual(pa66["moisture_absorption_equilibrium_range_percent"], "1.5 - 1.9%")
        self.assertEqual(pa66["water_absorption_sat_range_percent"], "5.6 - 6.3%")
        self.assertEqual(pa66["moisture_absorption_equilibrium_23c_50rh_min_percent"], 1.5)
        self.assertEqual(pa66["moisture_absorption_equilibrium_23c_50rh_max_percent"], 1.9)
        self.assertEqual(pa66["water_absorption_sat_23c_min_percent"], 5.6)
        self.assertEqual(pa66["water_absorption_sat_23c_max_percent"], 6.3)
        
        # 70 C status
        self.assertEqual(pa66["elastic_modulus_mpa_70c_status"], "CONDITIONAL — EXACT 70 C CONDITIONED PROPERTY NOT VERIFIED")
        self.assertEqual(pa66["screening_tensile_strength_mpa_70c_status"], "CONDITIONAL — EXACT 70 C CONDITIONED PROPERTY NOT VERIFIED")
        
        # Electrical insulation (BASF Feb 2026 Product Information)
        self.assertEqual(pa66["volume_resistivity_ohm_m"], 8e10)
        self.assertEqual(pa66["surface_resistivity_ohm"], 8e12)
        self.assertIsNone(pa66["volume_resistivity_ohm_m_dry"])
        self.assertIsNone(pa66["volume_resistivity_ohm_m_cond"])
        self.assertIsNone(pa66["surface_resistivity_ohm_dry"])
        self.assertIsNone(pa66["surface_resistivity_ohm_cond"])
        
        # Processing parameters (BASF Processing Data Sheet)
        proc = pa66["processing"]
        self.assertEqual(proc["predrying_temperature_c"], 80)
        self.assertEqual(proc["predrying_time_hours"], 4)
        self.assertEqual(proc["recommended_pellet_moisture_range_percent"], [0.025, 0.045])
        self.assertEqual(proc["recommended_pellet_moisture_range_str"], "0.025 - 0.045%")
        self.assertNotIn("max_moisture_content_percent", proc)

    def test_carrier_material_trade_matrix_content(self):
        """Verify carrier material trade matrix contains all three material families with correct classification."""
        matrix = build_carrier_material_trade_matrix()
        self.assertEqual(len(matrix), 3)
        
        families = [m["polymer_family"] for m in matrix]
        self.assertIn("PEEK (Unfilled)", families)
        self.assertIn("PPA (Polyphthalamide)", families)
        self.assertIn("PA66-GF30", families)
        
        peek = next(m for m in matrix if "PEEK" in m["exact_grade"] or "450G" in m["exact_grade"])
        ppa = next(m for m in matrix if "Amodel" in m["exact_grade"])
        pa66 = next(m for m in matrix if "Ultramid" in m["exact_grade"])
        
        self.assertEqual(peek["overall_screening_classification"], "ENGINEERING BENCHMARK / REFERENCE — STRONGEST CURRENT EVIDENCE")
        self.assertEqual(ppa["overall_screening_classification"], "HIGHER-PERFORMANCE POLYAMIDE ALTERNATIVE / SECONDARY VALIDATION CANDIDATE — procurement and exact carrier validation pending")
        self.assertEqual(pa66["overall_screening_classification"], "PRIMARY NYLON PROTOTYPE / VALIDATION CANDIDATE — exact 70 C wet properties and downhole-fluid compatibility unresolved")
        self.assertIn("DERIVED / INTERPOLATED SCREENING — DAM", ppa["property_70c_confidence"])
        
        self.assertEqual(peek["relative_cost_class"], "HIGH COST CLASS")
        self.assertEqual(ppa["relative_cost_class"], "EXPECTED LOWER-COST CANDIDATE — PROCUREMENT UNVERIFIED")
        self.assertEqual(pa66["relative_cost_class"], "EXPECTED LOWER-COST CANDIDATE — PROCUREMENT UNVERIFIED")
        
        for item in matrix:
            self.assertNotIn("$", item["relative_cost_class"])
            self.assertNotIn("/kg", item["relative_cost_class"])

    def test_carrier_dimensional_sensitivity_sweep(self):
        """Verify carrier dimensional sensitivity sweep across assumed swelling allowances."""
        rows = compute_carrier_dimensional_sensitivity(shell_bore_nom_mm=37.450)
        self.assertGreaterEqual(len(rows), 6)
        
        # PEEK nominal (0.020 mm allowance)
        peek_nom = next(r for r in rows if r["material"] == "PEEK" and r["assumed_conditioning_allowance_mm"] == 0.020)
        self.assertGreater(peek_nom["worst_case_hot_diametral_mm"], 0.25)
        self.assertEqual(peek_nom["sliding_status"], "FREE SLIDING")
        
        # PPA nominal (0.030 mm allowance)
        ppa_nom = next(r for r in rows if r["material"] == "PPA_Amodel_A1133HS" and r["assumed_conditioning_allowance_mm"] == 0.030)
        self.assertGreater(ppa_nom["worst_case_hot_diametral_mm"], 0.25)
        self.assertEqual(ppa_nom["sliding_status"], "FREE SLIDING")
        
        # PA66 nominal allowance (0.080 mm)
        pa66_nom = next(r for r in rows if r["material"] == "PA66_Ultramid_A3WG6_HRX" and r["carrier_od_nom_mm"] == 37.050 and r["assumed_conditioning_allowance_mm"] == 0.080)
        self.assertGreater(pa66_nom["worst_case_hot_diametral_mm"], 0.15)
        self.assertEqual(pa66_nom["sliding_status"], "FREE SLIDING")
        
        # PA66 extreme saturation swell (0.300 mm allowance on 37.05 mm carrier)
        pa66_sat = next(r for r in rows if r["material"] == "PA66_Ultramid_A3WG6_HRX" and r["carrier_od_nom_mm"] == 37.050 and r["assumed_conditioning_allowance_mm"] == 0.300)
        self.assertLess(pa66_sat["worst_case_hot_diametral_mm"], 0.0)
        self.assertEqual(pa66_sat["sliding_status"], "RISK OF BINDING / INTERFERENCE")

    def test_pa66_not_eligible_as_current_pressure_shell_baseline(self):
        """Verify PA66 is not eligible as the current pressure-shell baseline."""
        pa66_shell = size_architecture_candidate(
            "Architecture G2: PA66-Only", od_mm=44.45, wall_mm=7.225, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=False,
            casing_material="PA66_Ultramid_A3WG6_HRX", liner_material="PA66_Ultramid_A3WG6_HRX"
        )
        fos_buckle_hist_pa66 = pa66_shell["structural"]["buckling_historical"]["buckling_safety_factor"]
        self.assertLess(fos_buckle_hist_pa66, 1.0)
        self.assertIn("EXPLORATORY", pa66_shell["overall_status"])

    def test_generated_trade_study_report_and_csv_contain_three_materials(self):
        """Verify exported report and CSV contain all required sections and data for PEEK, PPA, and PA66."""
        report_path = Path(__file__).resolve().parents[1] / "results" / "compact-casing" / "compact_casing_redesign_report.md"
        csv_path = Path(__file__).resolve().parents[1] / "results" / "compact-casing" / "compact_casing_trade_study.csv"
        
        self.assertTrue(report_path.exists())
        self.assertTrue(csv_path.exists())
        
        content = report_path.read_text(encoding="utf-8")
        self.assertIn("BASF Ultramid A3WG6 HRX BK23591", content)
        self.assertIn("Victrex 450G PEEK", content)
        self.assertIn("Solvay Amodel A-1133 HS", content)
        self.assertIn("CONDITIONAL — EXACT 70 C CONDITIONED PROPERTY NOT VERIFIED", content)
        self.assertIn("STRONGEST CURRENT MATERIAL EVIDENCE", content)
        self.assertIn("0.025 – 0.045 %", content)
        self.assertIn("NOT ELIGIBLE AS THE CURRENT PRESSURE-SHELL BASELINE", content)
        self.assertIn("Proposed Future Physical Validation Plan", content)
        self.assertIn("Which material should we manufacture for the first physical carrier prototype?", content)
        
        # Verify no unsourced numeric cost assertions in report
        self.assertNotIn("~$100–150+/kg", content)
        self.assertNotIn("~$15–25/kg", content)
        self.assertNotIn("~$4–8/kg", content)
        self.assertNotIn("zero-risk", content)
        
        csv_content = csv_path.read_text(encoding="utf-8")
        self.assertIn("Architecture B2", csv_content)
        self.assertIn("PA66_Ultramid_A3WG6_HRX", csv_content)

    def test_nylon_prototype_report_preserves_evidence_boundaries(self):
        """The generated report must distinguish prototype screening from qualification evidence."""
        report_path = Path(__file__).resolve().parents[1] / "results" / "compact-casing" / "compact_casing_redesign_report.md"
        content = report_path.read_text(encoding="utf-8")

        self.assertIn("PRIMARY NYLON PROTOTYPE / VALIDATION CANDIDATE", content)
        self.assertIn("HIGHER-PERFORMANCE POLYAMIDE ALTERNATIVE / SECONDARY VALIDATION CANDIDATE", content)
        self.assertIn("Elnusa", content)
        self.assertIn("UNVERIFIED", content)
        self.assertIn("PROPOSED SCREENING TEST CONDITIONS — NOT AUTHORITATIVE QUALIFICATION REQUIREMENTS", content)
        self.assertNotIn("QUALIFIED PRELIMINARY SCREENING CANDIDATE", content)
        self.assertNotIn("pa66 is qualified", content.lower())
        self.assertNotIn("pa66 downhole-qualified", content.lower())

    def test_pa66_dimensional_report_values_are_generated_from_live_rows(self):
        """PA66 sizing prose must reflect the same live sensitivity rows as the table."""
        rows = compute_carrier_dimensional_sensitivity(37.45)
        nominal = next(r for r in rows if r["material"] == "PA66_Ultramid_A3WG6_HRX" and r["carrier_od_nom_mm"] == 37.05 and r["assumed_conditioning_allowance_mm"] == 0.08)
        saturation = next(r for r in rows if r["material"] == "PA66_Ultramid_A3WG6_HRX" and r["carrier_od_nom_mm"] == 37.05 and r["assumed_conditioning_allowance_mm"] == 0.30)
        report = (Path(__file__).resolve().parents[1] / "results" / "compact-casing" / "compact_casing_redesign_report.md").read_text(encoding="utf-8")
        self.assertIn(f"{nominal['worst_case_hot_diametral_mm']:+.4f} mm", report)
        self.assertIn(f"{saturation['worst_case_hot_diametral_mm']:+.4f} mm", report)

    def test_pa66_cad_variant_names_carrier_material(self):
        """The explicit PA66 prototype CAD variant must be identifiable in metadata."""
        candidate = size_architecture_candidate(
            "PA66 prototype", od_mm=44.45, wall_mm=3.5, is_discrete_carrier=True,
            casing_material="Inconel718", liner_material="PA66_Ultramid_A3WG6_HRX"
        )
        names = [name for _, name, _ in generate_compact_casing_cad(candidate)]
        self.assertIn("PA66-GF30_Prototype_Carrier_Rails", names)

    def test_yield_safety_factor_only_exists_for_yield_strength_basis(self):
        """Generic polymer tensile screening must not be reported as yield safety factor."""
        inconel = lame_stress(44.45, 3.5, 10.0, "Inconel718")
        pa66 = lame_stress(44.45, 3.5, 10.0, "PA66_Ultramid_A3WG6_HRX")
        self.assertEqual(inconel["strength_basis"], "YIELD")
        self.assertIn("yield_safety_factor", inconel)
        self.assertNotEqual(pa66["strength_basis"], "YIELD")
        self.assertNotIn("yield_safety_factor", pa66)

    def test_report_separates_ppa_dam_temperatures_and_first_prototype(self):
        """PPA interpolations and the PA66-first decision must be explicit in generated prose."""
        content = (Path(__file__).resolve().parents[1] / "results" / "compact-casing" / "compact_casing_redesign_report.md").read_text(encoding="utf-8")
        self.assertIn("PPA 23 °C DAM", content)
        self.assertIn("PPA 100 °C DAM", content)
        self.assertIn("PPA 70 °C", content)
        self.assertIn("DERIVED / INTERPOLATED SCREENING — DAM", content)
        self.assertIn("First physical carrier prototype", content)
        self.assertIn("PA66-GF30", content)
        self.assertIn("first prototype path", content)
        self.assertNotIn("PA66-GF30 (or Solvay Amodel", content)
        self.assertNotIn("directly into the wellbore fluid", content.lower())

    def test_historical_biweekly5_artifacts_remain_unmodified(self):
        """Verify historical Biweekly 5 script and results remain intact."""
        biweekly5_path = Path(__file__).resolve().parents[1] / "cosmo" / "biweekly5.py"
        self.assertTrue(biweekly5_path.exists())
        self.assertGreater(biweekly5_path.stat().st_size, 50000)
        
        b5_results = Path(__file__).resolve().parents[1] / "results" / "biweekly-5"
        self.assertTrue(b5_results.exists())


if __name__ == "__main__":
    unittest.main()
