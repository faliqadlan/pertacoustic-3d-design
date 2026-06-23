import os
import json
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cosmo_runner import run_cosmo_iteration

def run_automated_optimization():
    print("Starting automated COSMO optimization loop (2 Complex Configurations)")
    
    os.makedirs("results", exist_ok=True)
    
    config = [
        # Iteration 5: Thinner Outer Casing, Thicker Vacuum Gap
        {'name': 'Outer', 'material': 'Inconel718', 'thickness': 4.0},
        {'name': 'Vacuum', 'material': 'Vacuum_Gap', 'thickness': 8.0},
        {'name': 'InnerWall', 'material': 'Titanium', 'thickness': 2.0},
        {'name': 'Chassis', 'material': 'Thermal_Mass_CuBe', 'thickness': 6.0}
    ]
    
    od = 70.0
    length = 100.0
    bht = 150.0
    time_seconds = 3600 # 1 hour
    
    # Determine the next iteration number
    existing_iters = [d for d in os.listdir("results") if d.startswith("iteration_")]
    next_i = 1
    if existing_iters:
        next_i = max([int(d.split("_")[1]) for d in existing_iters]) + 1
        
    print(f"Running Iteration {next_i}...")
    
    # Run the single iteration
    max_temp = run_cosmo_iteration(next_i, od, length, config, bht=bht, time_seconds=time_seconds, animate=True)
    
    if max_temp is not None:
        # Save summary
        iter_dir = os.path.join("results", f"iteration_{next_i:02d}")
        os.makedirs(iter_dir, exist_ok=True)
        
        summary = {
            'iteration': next_i,
            'layers': config,
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
