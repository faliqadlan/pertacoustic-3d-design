import json
import os

results_dir = "results"
for iter_name in os.listdir(results_dir):
    if not iter_name.startswith("iteration_"):
        continue
    summary_file = os.path.join(results_dir, iter_name, "summary.json")
    if os.path.exists(summary_file):
        with open(summary_file, "r") as f:
            data = json.load(f)
        data["iteration"] = int(iter_name.split("_")[1])
        with open(summary_file, "w") as f:
            json.dump(data, f, indent=4)
