import os
import json
import glob

def compile_results(results_dir="results", output_md="comparison_table.md"):
    """
    Reads the results from all COSMO iterations and generates a comparison table.
    Expects a JSON file in each iteration folder containing the summary metrics.
    """
    
    table_header = "| Iteration | Configuration | OD (mm) | Length (mm) | Max Temp (C) | Time to 40C (h) | Status |\n"
    table_header += "|:---|:---|:---|:---|:---|:---|:---|\n"
    
    table_rows = []
    
    # Check all iteration folders
    iter_folders = sorted(glob.glob(os.path.join(results_dir, "iteration_*")))
    
    for folder in iter_folders:
        summary_file = os.path.join(folder, "summary.json")
        if os.path.exists(summary_file):
            with open(summary_file, "r") as f:
                data = json.load(f)
                
            iter_name = os.path.basename(folder)
            config_str = " + ".join([l['material'] for l in data['layers']])
            od = data['od']
            length = data['length']
            max_temp = data['max_temp']
            time_to_40 = data.get('time_to_40', '> 4.0')
            status = "PASS" if max_temp <= 70.0 else "FAIL"
            
            row = f"| {iter_name} | {config_str} | {od} | {length} | {max_temp:.2f} | {time_to_40} | {status} |\n"
            table_rows.append((max_temp, row))
            
    # Sort by max_temp (ascending)
    table_rows.sort(key=lambda x: x[0])
    
    with open(output_md, "w") as f:
        f.write("# COSMO-Agent Transient Thermal Results\n\n")
        f.write(table_header)
        for _, row in table_rows:
            f.write(row)
            
    print(f"Comparison table generated: {output_md}")

if __name__ == "__main__":
    pass
