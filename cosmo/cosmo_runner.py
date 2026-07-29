import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.cad_generator import generate_casing
from core.mesh_generator import generate_mesh
from core.solver_interface import setup_and_run_calculix
from core.result_extractor import extract_max_internal_temperature

def run_cosmo_iteration(iteration_num, od_mm, length_mm, layers, bht=150.0, time_seconds=14400):
    """
    Executes a single COSMO CAD-CAE loop iteration.
    
    Returns:
        max_temp: Maximum internal temperature at the end of the simulation.
    """
    
    print(f"\n{'='*50}")
    print(f"Starting COSMO Iteration {iteration_num}")
    print(f"OD: {od_mm} mm, Length: {length_mm} mm")
    print(f"Layers: {[l['name'] + '(' + l['material'] + ')' for l in layers]}")
    print(f"{'='*50}\n")
    
    # Define file names
    step_file = f"casing_iter{iteration_num}.step"
    inp_file = f"casing_iter{iteration_num}.inp"
    frd_file = f"casing_iter{iteration_num}.frd"
    
    # Step 1: CAD Generation
    try:
        generate_casing(od_mm, length_mm, layers, output_file=step_file)
    except Exception as e:
        print(f"CAD Generation failed: {e}")
        return None
        
    # Step 2: Meshing
    try:
        generate_mesh(step_file, inp_file, layers)
    except Exception as e:
        print(f"Meshing failed: {e}")
        return None
        
    # Step 3: Solver Execution
    try:
        success = setup_and_run_calculix(inp_file, layers, od_mm=od_mm, bht=bht, time_seconds=time_seconds)
        if not success:
            return None
    except Exception as e:
        print(f"Solver failed: {e}")
        return None
        
    # Step 4: Result Extraction
    try:
        # Assuming inner radius is the ID of the innermost layer
        # ID = OD - sum(thicknesses)
        total_thickness = sum([l['thickness'] for l in layers])
        inner_r = (od_mm / 2.0) - total_thickness
        
        max_temp = extract_max_internal_temperature(frd_file, target_time=time_seconds, r_inner=inner_r)
        print(f"\n>>> Max Internal Temperature at t={time_seconds}s: {max_temp:.2f} C <<<\n")
    except Exception as e:
        print(f"Result extraction failed: {e}")
        return None
        
    return max_temp

if __name__ == "__main__":
    # Test Run
    test_layers = [
        {'name': 'OuterCasing', 'material': 'SS316', 'thickness': 2.0},
        {'name': 'Insulation1', 'material': 'Silicone', 'thickness': 2.0},
        {'name': 'Insulation2', 'material': 'Aerogel', 'thickness': 3.0},
        {'name': 'InnerChassis', 'material': 'PEEK', 'thickness': 1.8}
    ]
    
    run_cosmo_iteration(0, 43.0, 100.0, test_layers, time_seconds=3600)
