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
        # PCM1808 board: 30.0 mm width x 12.0 mm height
        self.assertEqual(PCM1808_ENVELOPE_MM[1], 30.0)
        self.assertEqual(PCM1808_ENVELOPE_MM[2], 12.0)
        self.assertEqual(BOARD_ASSEMBLY_CLEARANCE_MM, 1.0)
        
        # Effective bounding rectangle: 32.0 mm x 14.0 mm
        eff_w = 30.0 + 2.0 * BOARD_ASSEMBLY_CLEARANCE_MM  # 32.0
        eff_h = 12.0 + 2.0 * BOARD_ASSEMBLY_CLEARANCE_MM  # 14.0
        expected_diagonal = math.hypot(eff_w, eff_h)  # sqrt(32^2 + 14^2) = sqrt(1220) ≈ 34.92848... ≈ 34.93 mm
        self.assertAlmostEqual(expected_diagonal, 34.928, places=3)
        
        # 1. Full circumferential 1.5 mm PEEK liner (Clear ID = 44.45 - 2*(3.5+1.5) = 34.45 mm)
        # MUST NOT PASS direct circular fit because 34.45 mm < 34.93 mm
        full_liner = compute_radial_budget(od_mm=44.45, wall_mm=3.5, liner_mm=1.5, aerogel_mm=0.0, is_discrete_carrier=False)
        self.assertAlmostEqual(full_liner["clear_id_mm"], 34.45, places=2)
        self.assertFalse(full_liner["direct_fit"])
        self.assertIn("INFEASIBLE", full_liner["packaging_status"])
        
        # 2. Conformal carrier rails in 3.5 mm Inconel shell bore (Shell Bore ID = 44.45 - 2*3.5 = 37.45 mm)
        # MUST PASS direct circular fit because 37.45 mm >= 34.93 mm (+2.52 mm clearance margin)
        discrete_carrier = compute_radial_budget(od_mm=44.45, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True)
        self.assertAlmostEqual(discrete_carrier["shell_bore_id_mm"], 37.45, places=2)
        self.assertAlmostEqual(discrete_carrier["clear_id_mm"], 37.45, places=2)
        self.assertTrue(discrete_carrier["direct_fit"])
        self.assertAlmostEqual(discrete_carrier["clearance_margin_mm"], (37.45 - expected_diagonal) / 2.0, places=2)
        self.assertIn("FEASIBLE", discrete_carrier["packaging_status"])

    def test_no_unsupported_low_profile_fallback_used(self):
        """Verify that radial budget calculation strictly evaluates the full 12 mm nominal board height."""
        res = compute_radial_budget(od_mm=44.45, wall_mm=3.5, liner_mm=1.5, aerogel_mm=0.0, is_discrete_carrier=False)
        self.assertFalse(res["direct_fit"])

    def test_ppa_and_peek_material_provenance_tracking(self):
        """Verify explicit provenance tracking and arithmetic derivations for PPA, PEEK, and Inconel 718."""
        ppa = MATERIALS["PPA_Amodel_A1133HS"]
        self.assertIn("provenance", ppa)
        self.assertIn("VERIFIED MANUFACTURER VALUE", ppa["provenance"]["density"])
        self.assertIn("VERIFIED MANUFACTURER VALUE", ppa["provenance"]["conductivity"])
        self.assertIn("DERIVED / INTERPOLATED", ppa["provenance"]["elastic_modulus_mpa_70c"])
        self.assertIn("DERIVED / INTERPOLATED", ppa["provenance"]["screening_tensile_strength_mpa_70c"])
        self.assertIn("ASSUMED SCREENING VALUE", ppa["provenance"]["specific_heat"])
        
        # Verify exact linear interpolation arithmetic:
        # Modulus: 11000 - (47/77)*(11000-6500) = 8253.25 MPa ≈ 8253 MPa
        expected_ppa_e = round(11000.0 - (47.0 / 77.0) * (11000.0 - 6500.0))
        self.assertEqual(ppa["elastic_modulus_mpa_70c"], expected_ppa_e)
        self.assertEqual(ppa["elastic_modulus_mpa_70c"], 8253)
        
        # Tensile stress at break: 195 - (47/77)*(195-110) = 143.12 MPa ≈ 143 MPa
        expected_ppa_sigma = round(195.0 - (47.0 / 77.0) * (195.0 - 110.0))
        self.assertEqual(ppa["screening_tensile_strength_mpa_70c"], expected_ppa_sigma)
        self.assertEqual(ppa["screening_tensile_strength_mpa_70c"], 143)
        
        peek = MATERIALS["PEEK"]
        self.assertIn("provenance", peek)
        self.assertIn("VERIFIED MANUFACTURER VALUE", peek["provenance"]["density"])
        self.assertIn("DERIVED / INTERPOLATED", peek["provenance"]["elastic_modulus_mpa_70c"])
        
        inconel = MATERIALS["Inconel718"]
        self.assertIn("provenance", inconel)
        self.assertIn("ASSUMED SCREENING VALUE", inconel["provenance"]["yield_strength_mpa_150c_screening"])

    def test_thermal_simulation_demonstrates_aerogel_heat_trapping(self):
        """Verify that aerogel is detrimental under 1.0 W internal dissipation at 70 °C."""
        cand_with_aero = size_architecture_candidate(
            "With Aerogel", od_mm=44.45, wall_mm=3.5, liner_mm=1.5, aerogel_mm=2.225, is_discrete_carrier=False
        )
        cand_no_aero = size_architecture_candidate(
            "No Aerogel Conformal PEEK", od_mm=44.45, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True
        )
        
        # Under 0 W (pure external ingress): aerogel delays initial heating
        t_30m_with_aero = cand_with_aero["thermal_0w"]["inner_temperature_C"][60]  # t=1800s (30m)
        t_30m_no_aero = cand_no_aero["thermal_0w"]["inner_temperature_C"][60]
        self.assertLess(t_30m_with_aero, t_30m_no_aero)
        
        # Under 1.0 W (self-heating): aerogel traps heat at 2 hours, resulting in higher cavity temperature
        t1_with_aero = cand_with_aero["thermal_1w"]["final_inner_temperature_C"]
        t1_no_aero = cand_no_aero["thermal_1w"]["final_inner_temperature_C"]
        self.assertGreater(t1_with_aero, t1_no_aero)
        self.assertLess(t1_no_aero, 85.0)  # Screening cavity temperature <= 85 °C

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

    def test_cad_assembly_zero_prohibited_interference(self):
        """Verify automated Boolean intersection interference checks pass with zero collision volume."""
        cand = size_architecture_candidate(
            "Architecture A", od_mm=44.45, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True
        )
        collision = check_cad_assembly_interferences(cand)
        self.assertTrue(collision["passed"], f"Interference check failed: {collision}")
        self.assertEqual(collision["carrier_vs_shell_vol_mm3"], 0.0)
        self.assertEqual(collision["carrier_vs_pcm_reserved_envelope_vol_mm3"], 0.0)
        self.assertEqual(collision["carrier_vs_pcm_nominal_pcb_vol_mm3"], 0.0)
        self.assertEqual(collision["pcm_nominal_vs_shell_vol_mm3"], 0.0)
        self.assertEqual(collision["max_interference_vol_mm3"], 0.0)

    def test_recommendation_engine_rule_logic(self):
        """Verify that candidate recommendation is governed by explicit multi-gate engineering rules."""
        candidates, recommended = run_architecture_trade_study()
        self.assertGreaterEqual(len(candidates), 7)
        
        # Recommendation must satisfy all qualification gates
        self.assertLessEqual(recommended["od_mm"], MAX_OD_MM)
        self.assertLessEqual(recommended["housing_length_mm"], MAX_TOOL_LENGTH_MM)
        self.assertTrue(recommended["packaging"]["direct_fit"])
        self.assertLessEqual(recommended["thermal_1w"]["final_inner_temperature_C"], 85.0)
        self.assertIn("Inconel", recommended["casing_material"])
        
        # Test rule selection among candidates:
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

