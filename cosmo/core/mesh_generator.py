import gmsh
import os

def generate_mesh(
    step_file,
    output_inp_file,
    layers,
    mesh_size_min=0.5,
    mesh_size_max=2.0,
    element_order=2,
):
    """
    Loads a STEP file assembly, fragments it to ensure conformal interfaces,
    meshes it, and exports to CalculiX .inp format.
    
    Args:
        step_file: Path to input STEP geometry.
        output_inp_file: Path to save the Abaqus/CalculiX .inp mesh.
        layers: The list of layer dictionaries (must match the order/number in the STEP file).
    """
    
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    
    # We want second-order tetrahedral elements for better thermal/stress accuracy
    gmsh.option.setNumber("Mesh.ElementOrder", element_order)
    # High quality mesh optimization
    gmsh.option.setNumber("Mesh.Optimize", 1)
    gmsh.option.setNumber("Mesh.OptimizeNetgen", 1)
    # Save node sets for boundary conditions
    gmsh.option.setNumber("Mesh.SaveGroupsOfNodes", 1)
    
    # Load STEP
    vols = gmsh.model.occ.importShapes(step_file)
    
    # Fragment all volumes to ensure conformal meshes at the interfaces
    # This guarantees that nodes align perfectly across layer boundaries
    gmsh.model.occ.fragment(vols, [])
    gmsh.model.occ.synchronize()
    
    # Get all the resulting volumes
    # The order of volumes in gmsh might change after fragment. 
    # For a concentric cylinder starting from OD to ID, we can sort volumes by their center of mass or max radius.
    # A robust way is to compute the bounding box or center of mass for each volume.
    
    volume_tags = gmsh.model.getEntities(3)
    
    # Sort volumes from outermost to innermost based on their maximum X coordinate (which is radius if centered at 0,0)
    def get_max_r(tag):
        bounds = gmsh.model.getBoundingBox(3, tag[1])
        # bounds = (xmin, ymin, zmin, xmax, ymax, zmax)
        return bounds[3] # xmax is the outer radius
        
    sorted_vols = sorted(volume_tags, key=get_max_r, reverse=True)
    
    if len(sorted_vols) != len(layers):
        print(f"Warning: Number of meshed volumes ({len(sorted_vols)}) != number of layers ({len(layers)})")
    
    # Assign physical groups for materials
    for i, (dim, tag) in enumerate(sorted_vols):
        if i < len(layers):
            layer_name = layers[i].get('name', f'Layer_{i}')
            # We must use Physical Groups to export sets to .inp
            pg_tag = gmsh.model.addPhysicalGroup(3, [tag], name=layer_name)
            
    # Assign physical groups for boundary conditions
    # We will NOT create a 2D physical group in Gmsh because Gmsh will export 2D plane stress elements
    # which crashes CalculiX. Instead, solver_interface.py will find the outer nodes and create a *NSET.
        
    # Generate 3D Mesh
    # Set a characteristic length (mesh size). 
    # Since casing thickness is ~1-5mm, mesh size should be ~1mm to get elements across the thickness.
    gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size_max)
    gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_size_min)
    
    gmsh.model.mesh.generate(3)
    
    # Save as Abaqus INP format (which CalculiX reads)
    gmsh.write(output_inp_file)
    
    gmsh.finalize()
    print(f"Mesh generated and saved to {output_inp_file}")

if __name__ == "__main__":
    test_layers = [
        {'name': 'OuterCasing', 'material': 'SS316', 'thickness': 2.0},
        {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 5.0},
        {'name': 'InnerChassis', 'material': 'PEEK', 'thickness': 1.8}
    ]
    if os.path.exists("test_casing.step"):
        generate_mesh("test_casing.step", "test_casing.inp", test_layers)
    else:
        print("Run cad_generator.py first to create test_casing.step")
