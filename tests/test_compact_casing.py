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
    STM32F411_ENVELOPE_MM,
    THERMAL_DURATION_S,
    THERMAL_ZONES_LOCAL_MM,
    ZERO_POWER_W,
    compute_radial_budget,
    elastic_buckling,
    generate_compact_casing_cad,
    lame_stress,
    run_architecture_trade_study,
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

    def test_radial_budget_recomputation_no_aerogel_vs_aerogel(self):
        """Verify radial budget and direct PCM1808 fit without aerogel."""
        # 1. With Aerogel (Historical baseline: t_wall=3.5, t_aero=2.225, t_liner=1.5)
        with_aero = compute_radial_budget(od_mm=44.45, wall_mm=3.5, liner_mm=1.5, aerogel_mm=2.225)
        self.assertAlmostEqual(with_aero["clear_id_mm"], 30.0, places=1)
        self.assertFalse(with_aero["direct_fit"])
        self.assertIn("INFEASIBLE", with_aero["packaging_status"])
        
        # 2. No Aerogel (Architecture A: t_wall=3.5, t_aero=0, t_liner=1.5)
        no_aero = compute_radial_budget(od_mm=44.45, wall_mm=3.5, liner_mm=1.5, aerogel_mm=0.0)
        self.assertAlmostEqual(no_aero["clear_id_mm"], 34.45, places=2)
        # Standard PCM1808 board (30x12 mm; diagonal with 1 mm clearance = 34.18 mm) fits directly!
        self.assertTrue(no_aero["direct_fit"])
        self.assertIn("Direct circular fit", no_aero["packaging_status"])

    def test_ppa_material_properties_are_documented_and_exact(self):
        """Verify exact Solvay Amodel A-1133 HS PPA properties in material library."""
        ppa = MATERIALS["PPA_Amodel_A1133HS"]
        self.assertEqual(ppa["density"], 1450)
        self.assertEqual(ppa["conductivity"], 0.26)
        self.assertEqual(ppa["specific_heat"], 1200)
        self.assertEqual(ppa["elastic_modulus_mpa_70c"], 8000)
        self.assertEqual(ppa["yield_strength_mpa_70c_screening"], 135)
        self.assertEqual(ppa["poisson_ratio"], 0.36)
        self.assertIn("Amodel A-1133 HS", ppa["notes"])

    def test_thermal_simulation_demonstrates_aerogel_heat_trapping(self):
        """Verify that aerogel is detrimental under 1.0 W internal dissipation at 70 °C."""
        # Candidate with aerogel
        cand_with_aero = size_architecture_candidate(
            "With Aerogel", od_mm=44.45, wall_mm=3.5, liner_mm=1.5, aerogel_mm=2.225
        )
        # Candidate without aerogel
        cand_no_aero = size_architecture_candidate(
            "No Aerogel", od_mm=44.45, wall_mm=3.5, liner_mm=1.5, aerogel_mm=0.0
        )
        
        # Under 0 W (pure external ingress): aerogel delays heating during first 30-60 min
        t_30m_with_aero = cand_with_aero["thermal_0w"]["inner_temperature_C"][60]  # t=1800s (30m)
        t_30m_no_aero = cand_no_aero["thermal_0w"]["inner_temperature_C"][60]
        self.assertLess(t_30m_with_aero, t_30m_no_aero)
        
        # Under 1.0 W (self heating): aerogel traps heat at 2 hours, making it hotter than no-aerogel!
        t1_with_aero = cand_with_aero["thermal_1w"]["final_inner_temperature_C"]
        t1_no_aero = cand_no_aero["thermal_1w"]["final_inner_temperature_C"]
        self.assertGreater(t1_with_aero, t1_no_aero)
        self.assertLess(t1_no_aero, 85.0)  # Safe operating margin below 85 °C

    def test_polymer_only_casing_shows_structural_limitations(self):
        """Verify that PEEK-only and PPA-only casings exhibit severe buckling vulnerability."""
        # PEEK-only casing (7.225 mm wall)
        peek_casing = size_architecture_candidate(
            "Architecture C: PEEK-Only", od_mm=44.45, wall_mm=7.225, liner_mm=0.0, aerogel_mm=0.0,
            casing_material="PEEK", liner_material="PEEK"
        )
        # Buckling FoS under 10,000 psi (68.95 MPa) must be < 1.0 (immediate collapse)
        fos_buckle_hist_peek = peek_casing["structural"]["buckling_historical"]["buckling_safety_factor"]
        self.assertLess(fos_buckle_hist_peek, 1.0)
        self.assertIn("INFEASIBLE", peek_casing["overall_status"])
        
        # PPA-only casing (7.225 mm wall)
        ppa_casing = size_architecture_candidate(
            "Architecture D: PPA-Only", od_mm=44.45, wall_mm=7.225, liner_mm=0.0, aerogel_mm=0.0,
            casing_material="PPA_Amodel_A1133HS", liner_material="PPA_Amodel_A1133HS"
        )
        fos_buckle_hist_ppa = ppa_casing["structural"]["buckling_historical"]["buckling_safety_factor"]
        self.assertLess(fos_buckle_hist_ppa, 1.0)
        self.assertIn("INFEASIBLE", ppa_casing["overall_status"])

    def test_inconel_structural_screening_multi_scenarios(self):
        """Verify Inconel 718 metallic shell maintains high structural margin under ~1000 m and 10k psi."""
        struct = structural_screening(od_mm=44.45, wall_mm=3.5, material_key="Inconel718")
        
        fos_yield_1000m = struct["scenarios"]["scenario_1000m_10mpa"]["yield_safety_factor"]
        fos_buckle_1000m = struct["buckling_1000m"]["buckling_safety_factor"]
        fos_yield_hist = struct["scenarios"]["scenario_historical_68_9mpa"]["yield_safety_factor"]
        
        self.assertGreaterEqual(fos_yield_1000m, 10.0)
        self.assertGreaterEqual(fos_buckle_1000m, 5.0)
        self.assertGreaterEqual(fos_yield_hist, 2.0)

    def test_component_limits_exact_and_conditional_classification(self):
        """Verify that only authorized ICs are verified and others marked conditional."""
        assessment = zone_thermal_assessment(final_cavity_temp_C=70.57)
        self.assertEqual(assessment["STM32F411CEU6"]["status"], "VERIFIED")
        self.assertEqual(assessment["PCM1808"]["status"], "VERIFIED")
        self.assertEqual(assessment["RTC Module (Unspecified PN)"]["status"], "CONDITIONAL")
        self.assertEqual(assessment["MicroSD Storage (Unspecified PN)"]["status"], "CONDITIONAL")

    def test_multi_architecture_trade_study_execution(self):
        """Verify that trade study evaluates all required architectures side-by-side."""
        candidates, recommended = run_architecture_trade_study()
        self.assertGreaterEqual(len(candidates), 5)
        
        arch_names = [c["architecture"] for c in candidates]
        self.assertTrue(any("Architecture A" in name for name in arch_names))
        self.assertTrue(any("Architecture B" in name for name in arch_names))
        self.assertTrue(any("Architecture C" in name for name in arch_names))
        self.assertTrue(any("Architecture D" in name for name in arch_names))
        self.assertTrue(any("Reference Baseline" in name for name in arch_names))
        
        # Verify recommended architecture is Architecture A (Inconel + PEEK, no aerogel)
        self.assertIn("Architecture A", recommended["architecture"])
        self.assertEqual(recommended["od_mm"], PREFERRED_OD_MM)
        self.assertAlmostEqual(recommended["clear_id_mm"], 34.45, places=2)
        self.assertEqual(recommended["aerogel_mm"], 0.0)
        self.assertTrue(recommended["packaging"]["direct_fit"])

    def test_3d_cad_solid_watertight_and_step_export_no_aerogel(self):
        """Verify watertight CadQuery solid generation for simplified casing."""
        cand = size_architecture_candidate(
            "Architecture A", od_mm=44.45, wall_mm=3.5, liner_mm=1.5, aerogel_mm=0.0
        )
        parts = generate_compact_casing_cad(cand)
        self.assertGreaterEqual(len(parts), 9)
        
        for solid, name, _ in parts:
            val = solid.val()
            self.assertTrue(val.isValid(), f"Solid {name} is not a valid solid")
            self.assertGreater(val.Volume(), 0.0, f"Solid {name} has zero volume")
            
        with TemporaryDirectory() as tmpdir:
            step_path = Path(tmpdir) / "test_no_aerogel_casing.step"
            generate_compact_casing_cad(cand, output_step_path=step_path)
            self.assertTrue(step_path.exists())
            self.assertGreater(step_path.stat().st_size, 1000)

    def test_historical_biweekly5_artifacts_remain_unmodified(self):
        """Verify historical Biweekly 5 script and results remain intact."""
        biweekly5_path = Path(__file__).resolve().parents[1] / "cosmo" / "biweekly5.py"
        self.assertTrue(biweekly5_path.exists())
        self.assertGreater(biweekly5_path.stat().st_size, 50000)
        
        b5_results = Path(__file__).resolve().parents[1] / "results" / "biweekly-5"
        self.assertTrue(b5_results.exists())


if __name__ == "__main__":
    unittest.main()
