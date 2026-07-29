import os
import json
import csv

import matplotlib.pyplot as plt

from .result_extractor import parse_frd_temperatures

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
        
        frd_file = os.path.join(iter_dir, f"casing_iter{iter_num}.frd")
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
            
        label = "Iter " + str(iter_num) + ": " + " + ".join([f"{l['material']} ({l['thickness']}mm)" for l in layers])
        
        linestyles = ['-', '--', '-.', ':']
        markers = ['o', 's', '^', 'D', 'v', 'x']
        linestyle = linestyles[(iter_num - 1) % len(linestyles)]
        marker = markers[(iter_num - 1) % len(markers)]
        
        cut_times = []
        cut_temps = []
        for time_h, t in zip(times, temps):
            cut_times.append(time_h)
            cut_temps.append(t)
            if iter_num == 1 and t >= 149.9:
                break
        
        plt.plot(cut_times, cut_temps, marker=marker, linestyle=linestyle, label=label, alpha=0.8)
        
    plt.title("Internal Electronics Temperature over 1 Hour (150°C Ambient)")
    plt.xlabel("Time (Hours)")
    plt.ylabel("Maximum Internal Temperature (°C)")
    # plt.axhline(y=40, color='r', linestyle='--', label='Critical Threshold (40°C)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=1)
    plt.grid(True)
    
    # Save PNG
    plot_path = os.path.join(results_dir, "temperature_plot.png")
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {plot_path}")
    
    # Save CSV
    if csv_data:
        keys = csv_data[0].keys()
        csv_path = os.path.join(results_dir, "numerical_data.csv")
        with open(csv_path, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(csv_data)
        print(f"Saved numeric data to {csv_path}")
