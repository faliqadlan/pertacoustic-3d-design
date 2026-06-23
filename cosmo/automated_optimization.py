import os
import json
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cosmo_runner import run_cosmo_iteration

def run_automated_optimization():
    print("Starting automated COSMO optimization loop (2 Complex Configurations)")
    
    os.makedirs("results", exist_ok=True)
    
    configs = [
        # Config 1: Titanium outer, Air insulation, PEEK inner
        [{'name': 'Outer', 'material': 'Titanium', 'thickness': 5.0},
         {'name': 'Insulation', 'material': 'Air', 'thickness': 3.0},
         {'name': 'Inner', 'material': 'PEEK', 'thickness': 2.0}],
         
        # Config 2: Stainless Steel outer, Teflon insulation, PEEK inner
        [{'name': 'Outer', 'material': 'SS316', 'thickness': 5.0},
         {'name': 'Insulation', 'material': 'PTFE', 'thickness': 3.0},
         {'name': 'Inner', 'material': 'PEEK', 'thickness': 2.0}]
    ]
    
    od = 70.0
    length = 100.0
    bht = 150.0
    time_seconds = 14400 # 4 hours
    
    for i, layers in enumerate(configs, 1):
        # We will only animate the final iteration
        do_animate = (i == len(configs))
        
        max_temp = run_cosmo_iteration(i, od, length, layers, bht=bht, time_seconds=time_seconds, animate=do_animate)
        
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

if __name__ == "__main__":
    run_automated_optimization()
