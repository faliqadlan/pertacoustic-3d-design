import os
import shutil
from pathlib import Path

def restructure():
    root = Path(r"c:\Users\faliq\Desktop\project-user\pertacoustic\cosmo")
    
    # Create new directories
    (root / "core").mkdir(exist_ok=True)
    (root / "hydrophone").mkdir(exist_ok=True)
    (root / "optimization").mkdir(exist_ok=True)
    (root / "results" / "legacy").mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files
    (root / "__init__.py").touch()
    (root / "core" / "__init__.py").touch()
    (root / "hydrophone" / "__init__.py").touch()
    (root / "optimization" / "__init__.py").touch()
    
    # Move core modules
    core_modules = [
        "cad_generator.py",
        "mesh_generator.py",
        "solver_interface.py",
        "result_extractor.py",
        "plot_results.py",
        "results_compiler.py",
        "thermal_animator.py"
    ]
    
    for mod in core_modules:
        src = root / mod
        dst = root / "core" / mod
        if src.exists():
            shutil.move(str(src), str(dst))
            
    # Move optimizer
    optimizer_src = root / "automated_optimization.py"
    if optimizer_src.exists():
        shutil.move(str(optimizer_src), str(root / "optimization" / "optimizer.py"))
        
    # Archive legacy results
    for i in range(1, 7):
        iter_dir = root / "results" / f"iteration_{i:02d}"
        if iter_dir.exists():
            shutil.move(str(iter_dir), str(root / "results" / "legacy" / f"iteration_{i:02d}"))
            
    # Move orphaned output files
    for ext in [".12d", ".cvg", ".dat", ".sta", ".step", ".inp", ".frd"]:
        for f in root.glob(f"*{ext}"):
            shutil.move(str(f), str(root / "results" / "legacy" / f.name))
            
    # Remove one-off scripts
    scripts_to_remove = [
        "debug_frd.py", "debug_frd2.py", "debug_frd3.py", 
        "check_nodes.py", "fix_summary.py", "quick_test.py", 
        "analyze_temp.py", "generate_deliverables.py", "render_iter1.py"
    ]
    for i in range(1, 7):
        scripts_to_remove.append(f"run_iter{i}.py")
        
    for script in scripts_to_remove:
        f = root / script
        if f.exists():
            f.unlink()
            
    print("Restructure complete.")

if __name__ == "__main__":
    restructure()
