import os
import json
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cosmo_runner import run_cosmo_iteration

def run_quick_test():
    print("Starting QUICK VERIFICATION Test...")
    
    os.makedirs("results", exist_ok=True)
    
    # 1. Simple PEEK casing (thick)
    layers = [{'name': 'Casing', 'material': 'PEEK', 'thickness': 10.0}]
    
    od = 70.0
    length = 100.0
    bht = 150.0
    time_seconds = 600 # 10 minutes for fast verification
    
    print(f"Configuration: {layers}")
    print(f"Simulation Time: {time_seconds} seconds")
    
    max_temp = run_cosmo_iteration(1, od, length, layers, bht=bht, time_seconds=time_seconds, animate=True)
    
    if max_temp is not None:
        iter_dir = os.path.join("results", "iteration_01")
        os.makedirs(iter_dir, exist_ok=True)
        
        summary = {
            'iteration': 1,
            'layers': layers,
            'od': od,
            'length': length,
            'max_temp': max_temp
        }
        with open(os.path.join(iter_dir, "summary.json"), "w") as f:
            json.dump(summary, f, indent=2)
            
        print(f"Quick test successful! Max internal temperature reached: {max_temp:.2f} C")
    else:
        print("Quick test failed.")

if __name__ == "__main__":
    run_quick_test()
