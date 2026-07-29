import gmsh
import os
from pathlib import Path

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
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.ElementOrder", element_order)
        gmsh.option.setNumber("Mesh.Optimize", 1)
        gmsh.option.setNumber("Mesh.OptimizeNetgen", 1)
        gmsh.option.setNumber("Mesh.SaveGroupsOfNodes", 1)
        gmsh.option.setNumber("Mesh.SaveAll", 0)

        vols = gmsh.model.occ.importShapes(step_file)
        if len(vols) != len(layers):
            raise ValueError(f"STEP solids ({len(vols)}) do not match layers ({len(layers)})")
        if len(vols) == 1:
            fragment_map = [vols]
        else:
            _, fragment_map = gmsh.model.occ.fragment(vols, [])
        gmsh.model.occ.synchronize()
        volume_rank = {
            tag: index + 1
            for index, (_, tag) in enumerate(sorted(gmsh.model.getEntities(3)))
        }
        exported_sets = {}
        for i, mapped in enumerate(fragment_map):
            layer_name = layers[i].get('name', f'Layer_{i}')
            tags = sorted({tag for dim, tag in mapped if dim == 3})
            if not tags:
                raise ValueError(f"No meshed volume remains for layer {layer_name}")
            group = gmsh.model.addPhysicalGroup(3, tags)
            gmsh.model.setPhysicalName(3, group, layer_name)
            exported_sets[layer_name] = tags

        gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size_max)
        gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_size_min)
        gmsh.model.mesh.generate(3)
        gmsh.write(output_inp_file)
        path = Path(output_inp_file)
        inp = path.read_text(encoding="utf-8")
        for layer_name, tags in exported_sets.items():
            for tag in tags:
                inp = inp.replace(
                    f"ELSET=Volume{volume_rank[tag]}", f"ELSET={layer_name}"
                )
        path.write_text(inp, encoding="utf-8")
    finally:
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
