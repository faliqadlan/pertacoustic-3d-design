import os
import sys
import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.cad_generator import generate_casing
from hydrophone.hti02_geometry import create_hydrophone_envelope
from hydrophone.adapter_thread import create_adapter

def generate_full_assembly(od_mm, length_mm, layers, output_file="assembly.step", detailed=True):
    """
    Generates the full assembly: Thermal Housing + Adapter + Hydrophone
    """
    assembly = cq.Assembly()
    
    # 1. Thermal Housing (Cold Zone)
    # The housing is generated starting from Z=0 and going to Z=length_mm
    housing_solids = generate_casing(od_mm, length_mm, layers, output_file=None)
    for i, solid in enumerate(housing_solids):
        layer_name = layers[i].get('name', f'Layer_{i}')
        # We need to extract the actual CQ solid from the returned Workplane/list
        # If generate_casing returns Workplanes, we can just add them.
        assembly.add(solid, name=layer_name, color=cq.Color(0.2, 0.5, 0.8, 0.5))
        
    # 2. Adapter
    # The adapter body length is 10mm, thread is 15mm.
    adapter = create_adapter(detailed=detailed)
    # Position the adapter at the end of the housing (Z = length_mm)
    adapter = adapter.translate((0, 0, length_mm))
    assembly.add(adapter, name="Threaded_Adapter", color=cq.Color(0.8, 0.8, 0.2, 1.0))
    
    # 3. Hydrophone Envelope
    # The hydrophone mates with the thread. 
    # Thread starts at Z = length_mm + body_len (10mm).
    # Hydrophone length is 88.9 mm. We'll position it just covering the thread.
    hydrophone = create_hydrophone_envelope()
    hydrophone = hydrophone.translate((0, 0, length_mm + 10.0))
    assembly.add(hydrophone, name="HTI-02-DHPC_D", color=cq.Color(0.2, 0.2, 0.2, 1.0))
    
    if output_file:
        assembly.save(output_file)
        print(f"Assembly saved to {output_file}")
        
    return assembly

if __name__ == "__main__":
    layers = [
        {'name': 'Outer', 'material': 'SS316', 'thickness': 3.0},
        {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 5.0},
        {'name': 'Chassis', 'material': 'PEEK', 'thickness': 3.0}
    ]
    generate_full_assembly(43.0, 100.0, layers, "assembly_detailed.step", detailed=True)
    generate_full_assembly(43.0, 100.0, layers, "assembly_defeatured.step", detailed=False)
