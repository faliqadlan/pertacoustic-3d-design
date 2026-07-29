import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from cosmo.biweekly5 import (
    MATERIALS,
    HOUSING_LENGTH_MM,
    REQUIRED_CLEAR_ID_MM,
    _parse_buckling_factor,
    _zone_max_temperatures,
    axial_heat_leak_screen,
    choose_wall,
    lame_screen,
    pressure_vessel_solid,
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

    def test_minimum_integer_od_for_one_hour_conditional_target(self):
        at_145 = thermal_simulation(choose_wall(145), 1, 16)["inner_temperature_C"][-1]
        at_146 = thermal_simulation(choose_wall(146), 1, 16)["inner_temperature_C"][-1]
        self.assertGreater(at_145, 70)
        self.assertLessEqual(at_146, 70)
        self.assertEqual(run_screening_matrix()[2]["od_mm"], 146)

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
        candidate = choose_wall(150)
        vessel = pressure_vessel_solid(candidate).val()
        outer = candidate["od_mm"] / 2
        inner = outer - candidate["inconel_wall_mm"]
        cap = candidate["inconel_wall_mm"]
        expected = 3.141592653589793 * (
            outer**2 * HOUSING_LENGTH_MM - inner**2 * (HOUSING_LENGTH_MM - 2 * cap)
        )
        self.assertTrue(vessel.isValid())
        self.assertAlmostEqual(vessel.Volume(), expected, delta=expected * 1e-6)
        self.assertEqual(MATERIALS["Aerogel"]["density"], 200)
        self.assertEqual(MATERIALS["Aerogel"]["conductivity"], 0.024)

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
            2: (20.5, 0, 20),
            3: (20.5, 0, 50),
            4: (20.5, 0, 110),
            5: (20.5, 0, 170),
        }
        temperatures = {1: 150, 2: 120, 3: 90, 4: 70, 5: 80}
        self.assertEqual(
            _zone_max_temperatures(nodes, temperatures, 20.5),
            {"Analog front-end": 120, "PCM1808": 90, "STM32F411": 70, "RTC/SD/power": 80},
        )
        axial = axial_heat_leak_screen(choose_wall(146))
        self.assertGreater(axial["front_initial_heat_W"], 2.0)
        self.assertLess(axial["rear_initial_heat_W"], 1.0)


if __name__ == "__main__":
    unittest.main()
