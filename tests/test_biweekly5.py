import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from cosmo.biweekly5 import (
    REQUIRED_CLEAR_ID_MM,
    choose_wall,
    lame_screen,
    thermal_simulation,
    thread_retention_screen,
)
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


if __name__ == "__main__":
    unittest.main()
