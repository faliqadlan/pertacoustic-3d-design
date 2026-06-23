import os
import json
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cosmo_runner import run_cosmo_iteration

def run_automated_optimization():
    print("Starting automated COSMO optimization loop (2 Complex Configurations)")
    
    os.makedirs("results", exist_ok=True)
    
    configs = [
        # Config 1: Titanium outer, Aerogel insulation, PEEK inner
        [{'name': 'Outer', 'material': 'Titanium', 'thickness': 5.0},
         {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 5.0},
         {'name': 'Inner', 'material': 'PEEK', 'thickness': 3.0}],
         
        # Config 2: SS316 outer, Vacuum insulation, PEEK inner
        [{'name': 'Outer', 'material': 'SS316', 'thickness': 5.0},
         {'name': 'Insulation', 'material': 'Vacuum', 'thickness': 5.0},
         {'name': 'Inner', 'material': 'PEEK', 'thickness': 3.0}]
    ]
    
    od = 70.0
    length = 100.0
    bht = 150.0
    time_seconds = 3600 # 1 hour
    
    for i, layers in enumerate(configs, 1):
        # Animate every iteration
        max_temp = run_cosmo_iteration(i, od, length, layers, bht=bht, time_seconds=time_seconds, animate=True)
        
        if max_temp is not None:
            # Save summary
            iter_dir = os.path.join("results", f"iteration_{i:02d}")
            os.makedirs(iter_dir, exist_ok=True)
            
            summary = {
                'iteration': i,
                'layers': layers,
                'od': od,
                'length': length,
                'max_temp': max_temp
            }
            with open(os.path.join(iter_dir, "summary.json"), "w") as f:
                json.dump(summary, f, indent=2)
                
    # Run compiler
    from results_compiler import compile_results
    compile_results(results_dir="results", output_md="comparison_table.md")
    
    # Generate numerical data and plots
    from plot_results import plot_all_results
    plot_all_results(results_dir="results")

if __name__ == "__main__":
    run_automated_optimization()
