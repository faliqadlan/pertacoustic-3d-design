import json
import tempfile
import unittest
from pathlib import Path

from cosmo.core.results_compiler import compile_results


class ResultsCompilerTest(unittest.TestCase):
    def test_uses_run_threshold_without_inventing_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = Path(tmp)
            iteration = results / "iteration_01"
            iteration.mkdir()
            (iteration / "summary.json").write_text(
                json.dumps(
                    {
                        "iteration": 1,
                        "layers": [{"material": "SS316"}],
                        "od": 43.0,
                        "length": 100.0,
                        "max_temp": 60.0,
                    }
                ),
                encoding="utf-8",
            )
            output = results / "comparison.md"

            compile_results(results, output, threshold=50.0)

            table = output.read_text(encoding="utf-8")
            self.assertNotIn("Time to 40C", table)
            self.assertIn("Pass threshold: 50.00 C.", table)
            self.assertIn("| FAIL |", table)


if __name__ == "__main__":
    unittest.main()
