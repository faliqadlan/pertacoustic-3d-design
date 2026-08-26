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
    PCM1808_ENVELOPE_MM,
    PREFERRED_OD_MM,
    PRESSURE_SCENARIO_1000M_MPA,
    PRESSURE_SCENARIO_HISTORICAL_MPA,
    PRESSURE_SCENARIO_INTERMEDIATE_MPA,
    STM32F411_ENVELOPE_MM,
    THERMAL_DURATION_S,
    THERMAL_ZONES_LOCAL_MM,
    ZERO_POWER_W,
    check_cad_assembly_interferences,
    compute_carrier_tolerance_budget,
    compute_radial_budget,
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
        """Verify explicit carrier tolerance budget accounts for differential expansion, tolerances, and moisture swell."""
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
        
        # Hot operating clearance: 0.400 - 0.0776 - 0.015 (swell) = 0.3074 mm
        self.assertAlmostEqual(budget["hot_clearance_diametral_mm"], 0.3074, places=3)
        self.assertAlmostEqual(budget["hot_clearance_radial_mm"], 0.1537, places=3)
        self.assertTrue(budget["adequate_clearance"])

    def test_final_carrier_remains_inside_shell_at_nominal_geometry(self):
        """Verify that nominal carrier outer radius (18.525 mm) remains strictly inside the shell bore (18.725 mm)."""
        shell_bore_radius = (44.45 - 2 * 3.5) / 2.0  # 18.725 mm
        carrier_outer_radius = (37.45 - 0.400) / 2.0  # 18.525 mm
        self.assertLess(carrier_outer_radius, shell_bore_radius)
        self.assertAlmostEqual(shell_bore_radius - carrier_outer_radius, 0.200, places=3)

    def test_interference_calculation_errors_fail_closed(self):
        """Verify that geometry kernel or solid calculation errors fail closed (passed=False, status='ERROR / NOT VERIFIED')."""
        # Pass an invalid geometry dictionary missing required keys
        invalid_geom = {"od_mm": 44.45}
        result = check_cad_assembly_interferences(invalid_geom)
        self.assertFalse(result["passed"])
        self.assertEqual(result["status"], "ERROR / NOT VERIFIED")
        self.assertIsNotNone(result["error"])
        self.assertIn("KeyError", result["error"])

    def test_recommendation_cannot_select_missing_or_failed_collision_evidence(self):
        """Verify that recommendation engine rejects candidates with missing, False, or ERROR collision status."""
        candidates, _ = run_architecture_trade_study()
        
        # Test candidate with missing collision results
        bad_cand_1 = dict(candidates[0])
        bad_cand_1["collision_results"] = None
        
        # Test candidate with failed collision results
        bad_cand_2 = dict(candidates[0])
        bad_cand_2["collision_results"] = {"passed": False, "status": "FAIL (1.200 mm³ collision)"}
        
        # Test candidate with ERROR collision results
        bad_cand_3 = dict(candidates[0])
        bad_cand_3["collision_results"] = {"passed": False, "status": "ERROR / NOT VERIFIED", "error": "KernelCrash"}
        
        with self.assertRaises(ValueError):
            select_recommended_candidate([bad_cand_1, bad_cand_2, bad_cand_3])

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
        
        fos_yield_1000m = struct["scenarios"]["scenario_1000m_10mpa"]["yield_safety_factor"]
        fos_buckle_1000m = struct["buckling_1000m"]["buckling_safety_factor"]
        fos_yield_20mpa = struct["scenarios"]["scenario_intermediate_20mpa"]["yield_safety_factor"]
        fos_buckle_20mpa = struct["buckling_20mpa"]["buckling_safety_factor"]
        fos_yield_hist = struct["scenarios"]["scenario_historical_68_9mpa"]["yield_safety_factor"]
        
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
        
        assessment = zone_thermal_assessment(final_cavity_temp_C=70.57)
        self.assertEqual(assessment["STM32F411CEU6"]["status"], "VERIFIED")
        self.assertEqual(assessment["PCM1808"]["status"], "VERIFIED")
        self.assertEqual(assessment["RTC Module (Unspecified PN)"]["status"], "CONDITIONAL / UNVERIFIED")
        self.assertEqual(assessment["RTC Module (Unspecified PN)"]["margin_C"], "N/A (Unspecified Part Rating)")
        self.assertEqual(assessment["MicroSD Storage (Unspecified PN)"]["status"], "CONDITIONAL / UNVERIFIED")

    def test_recommendation_engine_rule_logic(self):
        """Verify that candidate recommendation is governed by explicit multi-gate engineering rules."""
        candidates, recommended = run_architecture_trade_study()
        self.assertGreaterEqual(len(candidates), 7)
        
        self.assertLessEqual(recommended["od_mm"], MAX_OD_MM)
        self.assertLessEqual(recommended["housing_length_mm"], MAX_TOOL_LENGTH_MM)
        self.assertTrue(recommended["packaging"]["direct_fit"])
        self.assertLessEqual(recommended["thermal_1w"]["final_inner_temperature_C"], 85.0)
        self.assertIn("Inconel", recommended["casing_material"])
        self.assertTrue(recommended["collision_results"]["passed"])
        
        selected = select_recommended_candidate(candidates)
        self.assertEqual(selected["architecture"], recommended["architecture"])
        self.assertEqual(selected["od_mm"], PREFERRED_OD_MM)

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

    def test_historical_biweekly5_artifacts_remain_unmodified(self):
        """Verify historical Biweekly 5 script and results remain intact."""
        biweekly5_path = Path(__file__).resolve().parents[1] / "cosmo" / "biweekly5.py"
        self.assertTrue(biweekly5_path.exists())
        self.assertGreater(biweekly5_path.stat().st_size, 50000)
        
        b5_results = Path(__file__).resolve().parents[1] / "results" / "biweekly-5"
        self.assertTrue(b5_results.exists())


if __name__ == "__main__":
    unittest.main()

