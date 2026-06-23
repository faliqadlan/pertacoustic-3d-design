import pyvista as pv
import numpy as np
import os
import vtk

# Fallback to software rendering if needed
os.environ["PYVISTA_OFF_SCREEN"] = "true"
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"

def read_inp_to_pyvista(inp_file):
    """
    Parses a simple Gmsh-generated CalculiX .inp file 
    and creates a PyVista UnstructuredGrid.
    Assumes C3D10 (quadratic tetrahedrons).
    """
    nodes = {}
    elements = []
    
    in_node = False
    in_elem = False
    
    with open(inp_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.upper().startswith("*NODE"):
                in_node = True
                in_elem = False
                continue
            elif line.upper().startswith("*ELEMENT"):
                in_node = False
                if "C3D10" in line.upper():
                    in_elem = True
                else:
                    in_elem = False
                continue
            elif line.startswith("*"):
                in_node = False
                in_elem = False
                continue
                
            if in_node:
                try:
                    parts = line.split(",")
                    nid = int(parts[0])
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    nodes[nid] = (x, y, z)
                except:
                    pass
            elif in_elem:
                try:
                    parts = line.split(",")
                    eid = int(parts[0])
                    # C3D10 has 10 nodes. 
                    node_ids = [int(p) for p in parts[1:11]]
                    elements.append(node_ids)
                except:
                    pass

    # Create VTK arrays
    # VTK needs nodes starting from index 0
    node_id_to_idx = {}
    points = np.zeros((len(nodes), 3))
    
    for idx, (nid, coords) in enumerate(nodes.items()):
        node_id_to_idx[nid] = idx
        points[idx] = coords
        
    # Cells array for VTK_QUADRATIC_TETRA (type 24)
    # Format: [n_points, p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, ...]
    cells = []
    cell_types = []
    for elem_nodes in elements:
        cells.append(10) # Number of points
        for nid in elem_nodes:
            cells.append(node_id_to_idx[nid])
        cell_types.append(vtk.VTK_QUADRATIC_TETRA)
        
    grid = pv.UnstructuredGrid(cells, np.array(cell_types), points)
    
    # Store the node id mapping so we can attach temperatures later
    return grid, node_id_to_idx

def animate_results(inp_file, frd_file, output_mp4="thermal_animation.mp4"):
    from result_extractor import parse_frd_temperatures
    
    print(f"Loading mesh from {inp_file}...")
    mesh, node_id_to_idx = read_inp_to_pyvista(inp_file)
    
    print(f"Loading temperatures from {frd_file}...")
    nodes_frd, steps = parse_frd_temperatures(frd_file)
    
    if not steps:
        print("No temperature data found.")
        return
        
    # We will slice the mesh in half to see inside
    sliced_mesh = mesh.clip(normal='y', origin=(0, 0, 0), invert=False)
    
    print(f"Generating animation with {len(steps)} frames...")
    
    # Set up plotter
    plotter = pv.Plotter(off_screen=True)
    plotter.open_movie(output_mp4, framerate=5, quality=8) # H264 mp4
    
    # Add initial mesh with first step data
    temp_array = np.zeros(mesh.n_points)
    initial_temps = steps[0]['temperatures']
    for nid, temp in initial_temps.items():
        if nid in node_id_to_idx:
            temp_array[node_id_to_idx[nid]] = temp
            
    mesh.point_data["Temperature (°C)"] = temp_array
    
    # Update sliced mesh
    sliced_mesh = mesh.clip(normal='y', origin=(0, 0, 0), invert=False)
    
    plotter.add_mesh(sliced_mesh, scalars="Temperature (°C)", cmap="coolwarm", 
                     clim=[25, 150], show_scalar_bar=True, lighting=True)
                     
    plotter.camera_position = 'iso'
    # Start writing frames
    plotter.show(auto_close=False)
    
    for i, step in enumerate(steps):
        time_val = step['time']
        temps = step['temperatures']
        
        # Update point data
        temp_array = np.zeros(mesh.n_points)
        for nid, temp in temps.items():
            if nid in node_id_to_idx:
                temp_array[node_id_to_idx[nid]] = temp
                
        mesh.point_data["Temperature (°C)"] = temp_array
        sliced_mesh_t = mesh.clip(normal='y', origin=(0, 0, 0), invert=False)
        
        # Replace the dataset in the plotter
        plotter.clear()
        plotter.add_mesh(sliced_mesh_t, scalars="Temperature (°C)", cmap="coolwarm", 
                         clim=[25, 150], show_scalar_bar=True)
        plotter.add_text(f"Time: {time_val/3600:.2f} hours", position='upper_left')
        
        # Slight camera orbit
        plotter.camera.Azimuth(1.0)
        
        plotter.write_frame()
        print(f"Wrote frame {i+1}/{len(steps)}")
        
    plotter.close()
    print(f"Animation saved to {output_mp4}")

if __name__ == "__main__":
    pass
