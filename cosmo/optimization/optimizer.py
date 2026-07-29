import os
import json
import sys
import copy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cosmo_runner import run_cosmo_iteration

def validate_geometry(od, layers, min_id=10.0):
    total_thickness = sum(l['thickness'] for l in layers)
    return (od - 2 * total_thickness) >= min_id

def propose_next_config(current_config, max_temp, threshold):
    """
    Proposes the next design configuration based on the temperature overshoot.
    """
    od = current_config['od']
    layers = copy.deepcopy(current_config['layers'])
    
    overshoot = max_temp - threshold
    overshoot_pct = (overshoot / threshold) * 100.0
    
    reasoning = f"Temperature {max_temp:.2f}C is {overshoot_pct:.1f}% above {threshold}C threshold. "
    
    if max_temp > 90.0:
        # Major intervention
        reasoning += "Major intervention. Adding 5.0mm Aerogel and increasing OD by 10.0mm."
        od += 10.0
        for layer in layers:
            if layer['material'] == 'Aerogel':
                layer['thickness'] += 5.0
    elif max_temp > 60.0:
        # Moderate intervention
        reasoning += "Moderate intervention. Adding 3.0mm Aerogel and increasing OD by 6.0mm."
        od += 6.0
        for layer in layers:
            if layer['material'] == 'Aerogel':
                layer['thickness'] += 3.0
    else:
        # Micro-adjustment
        reasoning += "Micro-adjustment. Adding 1.0mm Aerogel and increasing OD by 2.0mm."
        od += 2.0
        for layer in layers:
            if layer['material'] == 'Aerogel':
                layer['thickness'] += 1.0

    if not validate_geometry(od, layers, 10.0):
        reasoning += " Proposed thicknesses violate 10mm minimum ID. Increasing OD further."
        od += 5.0
        
    proposed_config = {
        'od': od,
        'layers': layers
    }
    
    return proposed_config, reasoning

def run_automated_optimization():
    print("Starting automated thermal optimization loop")
    
    results_dir = os.path.join("results", "hti-02-dhpc-d-20260716")
    os.makedirs(results_dir, exist_ok=True)
    
    # Clean up old log if restarting
    log_file = os.path.join(results_dir, "optimization_log.json")
    if os.path.exists(log_file):
        os.remove(log_file)
        
    log_data = {"iterations": []}
    
    # Initial Configuration
    current_config = {
        'od': 43.0,
        'layers': [
            {'name': 'Outer', 'material': 'SS316', 'thickness': 3.0},
            {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 5.0},
            {'name': 'Chassis', 'material': 'PEEK', 'thickness': 3.0}
        ]
    }
    
    length = 100.0
    bht = 150.0
    time_seconds = 3600
    threshold = 50.0
    max_iterations = 10
    
    best_temp = float('inf')
    
    for i in range(1, max_iterations + 1):
        print(f"\n--- Running Iteration {i} ---")
        od = current_config['od']
        layers = current_config['layers']
        
        max_temp = run_cosmo_iteration(i, od, length, layers, bht=bht, time_seconds=time_seconds)
        
        if max_temp is None:
            print(f"Iteration {i} failed to complete. Stopping optimization.")
            break
            
        if max_temp < best_temp:
            best_temp = max_temp
            
        # Save summary and move artifacts
        iter_dir = os.path.join(results_dir, f"iteration_{i:02d}")
        os.makedirs(iter_dir, exist_ok=True)
        
        import shutil
        for ext in ['.step', '.inp', '.frd', '.cvg', '.dat', '.sta']:
            src = f"casing_iter{i}{ext}"
            dst = os.path.join(iter_dir, src)
            if os.path.exists(src):
                if os.path.exists(dst):
                    os.remove(dst)
                shutil.move(src, dst)
                
        summary = {
            'iteration': i,
            'layers': layers,
            'od': od,
            'length': length,
            'max_temp': max_temp
        }
        with open(os.path.join(iter_dir, "summary.json"), "w") as f:
            json.dump(summary, f, indent=2)
            
        # Logging structure
        iter_log = {
            "iteration": i,
            "config": copy.deepcopy(current_config),
            "result": {"max_temp": max_temp, "converged": max_temp <= threshold},
            "constraints": {
                "thermal": {
                    "threshold": threshold,
                    "satisfied": max_temp <= threshold,
                    "overshoot_pct": max(0, ((max_temp - threshold) / threshold) * 100)
                }
            }
        }
        
        if max_temp <= threshold:
            print(f"\nSUCCESS! Target met at Iteration {i}. Max Temp: {max_temp:.2f}C")
            iter_log["reasoning"] = f"Temperature {max_temp:.2f}C satisfies the {threshold}C threshold. Optimization complete."
            iter_log["proposed_next"] = None
            log_data["iterations"].append(iter_log)
            with open(log_file, "w") as f:
                json.dump(log_data, f, indent=2)
            break
            
        # Determine next configuration
        next_config, reasoning = propose_next_config(current_config, max_temp, threshold)
        print(f"Optimization reasoning: {reasoning}")
        
        iter_log["reasoning"] = reasoning
        iter_log["proposed_next"] = next_config
        log_data["iterations"].append(iter_log)
        
        # Save log after every step
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=2)
            
        current_config = next_config

    else:
        print(f"\nBudget exhausted after {max_iterations} iterations.")
        print(f"Best candidate achieved: {best_temp:.2f}C")
        
    # Run compiler
    from core.results_compiler import compile_results
    compile_results(
        results_dir=results_dir,
        output_md=os.path.join(results_dir, "comparison_table.md"),
        threshold=threshold,
    )
    
    # Generate numerical data and plots
    try:
        from core.plot_results import plot_all_results
        plot_all_results(results_dir=results_dir)
    except Exception as e:
        print(f"Could not plot results: {e}")

if __name__ == "__main__":
    run_automated_optimization()
