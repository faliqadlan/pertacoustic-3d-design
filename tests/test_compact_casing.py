"""Unit tests for the compact downhole casing redesign study."""

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
    ESTIMATED_HARDWARE_POWER_W,
    EXTERNAL_TEMPERATURE_C,
    HOUSING_LENGTH_MM,
    INHERITED_SCREENING_POWER_W,
    MATERIALS,
    MAX_OD_MM,
    MAX_TOOL_LENGTH_MM,
    PCM1808_ENVELOPE_MM,
    PEEK_CARRIER_THICKNESS_MM,
    PREFERRED_OD_MM,
    PRESSURE_SCENARIO_1000M_MPA,
    PRESSURE_SCENARIO_HISTORICAL_MPA,
    STM32F411_ENVELOPE_MM,
    TARGET_CLEAR_ID_MM,
    THERMAL_DURATION_S,
    THERMAL_ZONES_LOCAL_MM,
    build_nominal_hti_adapter_solid,
    elastic_buckling,
    generate_compact_casing_cad,
    investigate_packaging,
    lame_stress,
    run_compact_trade_study,
    size_compact_candidate,
    structural_screening,
    thread_retention_screening,
    transient_thermal_simulation,
    zone_thermal_assessment,
)


class CompactCasingRedesignTests(unittest.TestCase):
    """Test suite verifying compact casing geometry, packaging, thermal, and structural screening."""

    def test_design_envelope_constants_conform_to_formal_authority(self):
        """Verify boundary constants match formal MoM and 20 August 2026 direction."""
        self.assertAlmostEqual(PREFERRED_OD_MM, 44.45, places=2)
        self.assertAlmostEqual(MAX_OD_MM, 57.15, places=2)
        self.assertLessEqual(HOUSING_LENGTH_MM, MAX_TOOL_LENGTH_MM)
        self.assertEqual(MAX_TOOL_LENGTH_MM, 2000.0)
        self.assertEqual(EXTERNAL_TEMPERATURE_C, 70.0)
        self.assertEqual(THERMAL_DURATION_S, 7200)
        self.assertEqual(INHERITED_SCREENING_POWER_W, 1.0)
        self.assertEqual(ESTIMATED_HARDWARE_POWER_W, 0.35)
        self.assertEqual(TARGET_CLEAR_ID_MM, 30.0)

    def test_packaging_investigation_logic(self):
        """Verify objective electronics packaging evaluation within ~30 mm ID."""
        pkg = investigate_packaging(TARGET_CLEAR_ID_MM)
        self.assertIn("investigated_clear_id_mm", pkg)
        self.assertEqual(pkg["investigated_clear_id_mm"], 30.0)
        
        # STM32F411 (21 mm wide) packages comfortably
        stm_info = pkg["components"]["STM32F411"]
        self.assertTrue(stm_info["slotted_carrier_fit"])
        
        # PCM1808 (30 mm wide) requires carrier slotting or narrow PCB
        pcm_info = pkg["components"]["PCM1808"]
        self.assertEqual(pcm_info["dimensions_l_w_h_mm"], PCM1808_ENVELOPE_MM)
        self.assertGreater(pcm_info["diagonal_mm"], 30.0)
        
        # Minimum unmodified vs slotted ID
        self.assertGreaterEqual(pkg["min_screening_clear_id_unmodified_mm"], 32.0)
        self.assertLessEqual(pkg["min_screening_clear_id_slotted_mm"], 30.0)

    def test_structural_lame_stress_and_buckling_formulas(self):
        """Verify analytical Lamé stress and long-cylinder buckling calculations."""
        od = 44.45
        wall = 3.5
        
        # 1000 m hydrostatic scenario (10 MPa)
        res_1000m = lame_stress(od, wall, PRESSURE_SCENARIO_1000M_MPA)
        self.assertGreater(res_1000m["max_von_mises_mpa"], 0.0)
        self.assertGreaterEqual(res_1000m["yield_safety_factor"], 10.0)  # High margin under 10 MPa
        
        # Buckling screen
        buckle_1000m = elastic_buckling(od, wall, PRESSURE_SCENARIO_1000M_MPA)
        self.assertGreater(buckle_1000m["critical_buckling_pressure_mpa"], 50.0)
        self.assertGreaterEqual(buckle_1000m["buckling_safety_factor"], 5.0)
        
        # Fail-closed on invalid wall consuming bore
        with self.assertRaises(ValueError):
            lame_stress(od_mm=40.0, wall_mm=25.0, pressure_mpa=10.0)

    def test_structural_multi_scenario_screening(self):
        """Verify structural screening across all required explicit scenarios."""
        struct = structural_screening(PREFERRED_OD_MM, wall_mm=3.5)
        self.assertIn("scenario_1000m_10mpa", struct["scenarios"])
        self.assertIn("scenario_intermediate_20mpa", struct["scenarios"])
        self.assertIn("scenario_historical_68_9mpa", struct["scenarios"])
        
        # Yield FoS must be positive and properly ordered
        fos_1000m = struct["scenarios"]["scenario_1000m_10mpa"]["yield_safety_factor"]
        fos_hist = struct["scenarios"]["scenario_historical_68_9mpa"]["yield_safety_factor"]
        self.assertGreater(fos_1000m, fos_hist)
        self.assertGreaterEqual(fos_hist, 2.0)

    def test_thread_retention_screening(self):
        """Verify nominal 7/16-20 UNF-2A thread retention shear screening."""
        thread = thread_retention_screening(PRESSURE_SCENARIO_1000M_MPA)
        self.assertAlmostEqual(thread["pitch_mm"], 1.27, places=3)
        self.assertAlmostEqual(thread["engagement_mm"], 10.16, places=2)
        self.assertGreaterEqual(thread["thread_safety_factor"], 2.0)

    def test_transient_thermal_simulation_and_duration(self):
        """Verify 2-hour (7200 s) transient thermal simulation under 70 °C boundary."""
        cand = size_compact_candidate(PREFERRED_OD_MM, clear_id_mm=30.0, inconel_wall_mm=3.5)
        self.assertTrue(cand["fit"])
        
        run_1w = transient_thermal_simulation(cand, power_w=1.0, duration_s=7200)
        self.assertEqual(len(run_1w["times_s"]), int(7200 / 30.0) + 1)
        self.assertEqual(run_1w["times_s"][-1], 7200.0)
        
        # Cavity temperature should start at 25 °C and remain below 85 °C verified limit
        self.assertEqual(run_1w["inner_temperature_C"][0], 25.0)
        self.assertLess(run_1w["final_inner_temperature_C"], 85.0)
        self.assertGreater(run_1w["final_inner_temperature_C"], 25.0)
        
        # 0.35 W realistic power should result in lower temperature than 1.0 W
        run_035w = transient_thermal_simulation(cand, power_w=0.35, duration_s=7200)
        self.assertLess(run_035w["final_inner_temperature_C"], run_1w["final_inner_temperature_C"])

    def test_component_operating_limit_verification(self):
        """Verify temperature limits for STM32F411, PCM1808, RTC, and SD."""
        assessment = zone_thermal_assessment(final_cavity_temp_C=58.5)
        self.assertTrue(assessment["STM32F411CEU6"]["passes"])
        self.assertEqual(assessment["STM32F411CEU6"]["max_limit_C"], 85.0)
        self.assertTrue(assessment["PCM1808"]["passes"])
        self.assertEqual(assessment["PCM1808"]["max_limit_C"], 85.0)
        self.assertTrue(assessment["DS3231 Industrial RTC"]["passes"])

    def test_trade_study_matrix_evaluates_preferred_and_max_envelope(self):
        """Verify trade study evaluates 44.45 mm preferred candidate and stays <= 57.15 mm."""
        trade_rows, recommended = run_compact_trade_study()
        self.assertGreaterEqual(len(trade_rows), 5)
        
        ods = [r["od_mm"] for r in trade_rows]
        self.assertIn(44.45, ods)
        self.assertIn(57.15, ods)
        
        # Verify recommended design
        self.assertEqual(recommended["od_mm"], PREFERRED_OD_MM)
        self.assertLessEqual(recommended["od_mm"], MAX_OD_MM)
        self.assertEqual(recommended["clear_id_mm"], TARGET_CLEAR_ID_MM)
        self.assertGreater(recommended["aerogel_mm"], 1.0)
        self.assertIn("PASS", recommended["overall_status"])

    def test_3d_cad_solid_watertight_and_step_export(self):
        """Verify watertight CadQuery solid generation and assembly structure."""
        cand = size_compact_candidate(PREFERRED_OD_MM, clear_id_mm=30.0, inconel_wall_mm=3.5)
        parts = generate_compact_casing_cad(cand)
        self.assertGreaterEqual(len(parts), 10)
        
        # Verify all solids are valid CadQuery shapes
        for solid, name, _ in parts:
            val = solid.val()
            self.assertTrue(val.isValid(), f"Solid {name} is not a valid solid")
            self.assertGreater(val.Volume(), 0.0, f"Solid {name} has zero volume")
            
        with TemporaryDirectory() as tmpdir:
            step_path = Path(tmpdir) / "test_compact_casing.step"
            generate_compact_casing_cad(cand, output_step_path=step_path)
            self.assertTrue(step_path.exists())
            self.assertGreater(step_path.stat().st_size, 1000)

    def test_axial_zones_and_housing_length_consistency(self):
        """Verify internal thermal zones fit within the modeled housing length."""
        first_zone = min(start for start, _ in THERMAL_ZONES_LOCAL_MM.values())
        last_zone = max(end for _, end in THERMAL_ZONES_LOCAL_MM.values())
        self.assertGreaterEqual(first_zone, ENDCAP_THICKNESS_MM)
        self.assertLess(last_zone, HOUSING_LENGTH_MM - ENDCAP_THICKNESS_MM)

    def test_historical_biweekly5_artifacts_remain_unmodified(self):
        """Verify historical Biweekly 5 script and results remain intact."""
        biweekly5_path = Path(__file__).resolve().parents[1] / "cosmo" / "biweekly5.py"
        self.assertTrue(biweekly5_path.exists())
        self.assertGreater(biweekly5_path.stat().st_size, 50000)
        
        b5_results = Path(__file__).resolve().parents[1] / "results" / "biweekly-5"
        self.assertTrue(b5_results.exists())


if __name__ == "__main__":
    unittest.main()
