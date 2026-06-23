import os
import sys
import json
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("matplotlib not found, installing...")
    import subprocess
    subprocess.check_call([os.sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt

from result_extractor import parse_frd_temperatures

def plot_all_results(results_dir="results"):
    print("Generating Temperature-Time Plots and CSV Data...")
    
    csv_data = []
    
    plt.figure(figsize=(10, 6))
    
    for iter_name in sorted(os.listdir(results_dir)):
        if not iter_name.startswith("iteration_"):
            continue
            
        iter_dir = os.path.join(results_dir, iter_name)
        summary_file = os.path.join(iter_dir, "summary.json")
        
        if not os.path.exists(summary_file):
            continue
            
        with open(summary_file, "r") as f:
            summary = json.load(f)
            
        iter_num = summary['iteration']
        od = summary['od']
        layers = summary['layers']
        
        inner_radius = (od / 2.0) - sum(l['thickness'] for l in layers)
        
        frd_file = f"casing_iter{iter_num}.frd"
        if not os.path.exists(frd_file):
            print(f"Skipping {iter_name}: {frd_file} not found.")
            continue
            
        print(f"Parsing {frd_file} for iteration {iter_num}...")
        nodes, steps = parse_frd_temperatures(frd_file)
        
        if not nodes or not steps:
            continue
            
        inner_nodes = []
        tol = 0.5
        for nid, (x, y, z) in nodes.items():
            r = (x**2 + y**2)**0.5
            if abs(r - inner_radius) < tol:
                inner_nodes.append(nid)
                
        if not inner_nodes:
            inner_nodes = list(nodes.keys())
            
        times = []
        temps = []
        
        for step in steps:
            time_s = step['time']
            max_t = -999.0
            for nid in inner_nodes:
                t = step['temperatures'].get(nid, -999.0)
                if t > max_t:
                    max_t = t
                    
            times.append(time_s / 3600.0) # convert to hours
            temps.append(max_t)
            
            # Save for CSV (Iter, Time_h, Temp_C)
            csv_data.append({
                "Iteration": iter_num,
                "Time_Hours": round(time_s / 3600.0, 4),
                "Max_Inner_Temp_C": round(max_t, 4)
            })
            
        label = "Iter " + str(iter_num) + ": " + " + ".join([l['material'] for l in layers])
        linestyle = '-' if iter_num == 1 else '--'
        marker = 'o' if iter_num == 1 else 's'
        plt.plot(times, temps, marker=marker, linestyle=linestyle, label=label, alpha=0.8)
        
    plt.title("Internal Electronics Temperature over 4 Hours (150°C Ambient)")
    plt.xlabel("Time (Hours)")
    plt.ylabel("Maximum Internal Temperature (°C)")
    plt.axhline(y=40, color='r', linestyle='--', label='Critical Threshold (40°C)')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid(True)
    plt.tight_layout()
    
    # Save PNG
    plt.savefig("temperature_plot.png", dpi=300, bbox_inches='tight')
    print("Saved plot to temperature_plot.png")
    
    # Save CSV
    if csv_data:
        keys = csv_data[0].keys()
        with open("numerical_data.csv", "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(csv_data)
        print("Saved numeric data to numerical_data.csv")

if __name__ == "__main__":
    plot_all_results()
