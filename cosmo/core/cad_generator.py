import cadquery as cq
import json
import os

def generate_casing(od_mm, length_mm, layers, output_file="casing.step"):
    """
    Generates a multi-layered concentric cylinder casing.
    
    Args:
        od_mm: Outer diameter of the outermost layer.
        length_mm: Length of the casing.
        layers: List of dictionaries defining each layer from OUTSIDE to INSIDE.
                e.g., [{'name': 'Casing', 'material': 'SS316', 'thickness': 2.0}, ...]
        output_file: Path to save the resulting STEP file.
        
    Returns:
        A list of generated cadquery Workplanes (the solid layers).
    """
    
    current_od = od_mm
    solids = []
    
    # We want to export an assembly so that Gmsh recognizes them as distinct volumes
    # that can be fragmented and meshed with different materials.
    assembly = cq.Assembly()
    
    for i, layer in enumerate(layers):
        thickness = layer['thickness']
        name = layer.get('name', f'Layer_{i}')
        
        # Calculate ID for this layer
        current_id = current_od - (2 * thickness)
        
        if current_id < 0:
            raise ValueError(f"Layer {name} thickness {thickness} is too large for remaining OD {current_od}")
            
        # Handle solid core (ID == 0) first
        if current_id == 0:
            solid = cq.Workplane("XY").circle(current_od / 2.0).extrude(length_mm)
        else:
            solid = (
                cq.Workplane("XY")
                .circle(current_od / 2.0)
                .circle(current_id / 2.0)
                .extrude(length_mm)
            )
            
        solids.append(solid)
        assembly.add(solid, name=name, color=cq.Color(0.5, 0.5, 0.5, 0.5)) # Just a default color
        
        current_od = current_id

    # Export to STEP
    if output_file:
        assembly.save(output_file)
        print(f"Geometry generated and saved to {output_file}")
    
    return solids

if __name__ == "__main__":
    # Test generation
    test_layers = [
        {'name': 'OuterCasing', 'material': 'SS316', 'thickness': 2.0},
        {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 5.0},
        {'name': 'InnerChassis', 'material': 'PEEK', 'thickness': 1.8}
    ]
    generate_casing(43.0, 300.0, test_layers, "test_casing.step")
