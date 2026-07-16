import cadquery as cq
import math

def create_adapter(detailed=True):
    """
    Creates a 7/16-20 UNF-2A male adapter with an O-ring groove.
    detailed=True includes the helical thread geometry.
    detailed=False returns a defeatured cylinder for meshing.
    """
    major_dia = 0.4375 * 25.4 # 11.1125 mm
    pitch = (1.0 / 20.0) * 25.4 # 1.27 mm
    thread_len = 15.0
    
    body_dia = 20.0 # Flange/shoulder
    body_len = 10.0
    
    minor_dia = major_dia - 1.082532 * pitch # ~9.7 mm
    
    # O-ring groove behind the thread
    groove_dia = minor_dia - 0.5
    groove_width = 2.0
    groove_pos = 3.0 # distance from shoulder
    
    # Base geometry: body flange + cylinder for thread
    adapter = (
        cq.Workplane("XY")
        .circle(body_dia / 2.0).extrude(body_len)
        .faces(">Z").workplane()
        .circle(minor_dia / 2.0 if detailed else major_dia / 2.0).extrude(thread_len)
    )
    
    # Cut O-ring groove
    adapter = (
        adapter.faces(">Z").workplane(offset=-thread_len + groove_pos)
        .circle(major_dia/2.0 + 1.0).circle(groove_dia/2.0)
        .extrude(groove_width, combine="cut")
    )
    
    if detailed:
        # Create helical thread using sweep
        # We sweep a V-profile along a helix
        try:
            helix_path = cq.Wire.makeHelix(
                pitch=pitch, 
                height=thread_len - groove_pos - groove_width - 1.0, 
                radius=major_dia/2.0
            )
            
            # The helix starts at (radius, 0, 0)
            # Create a triangle profile in XZ plane
            half_p = pitch / 2.0
            h = (major_dia - minor_dia) / 2.0
            
            # Profile must be positioned at the start of the helix
            profile = (
                cq.Workplane("XZ")
                .center(major_dia/2.0, 0)
                .lineTo(0, half_p*0.8)
                .lineTo(-h, 0)
                .lineTo(0, -half_p*0.8)
                .close()
            )
            
            # Sweep the profile along the helix
            # isFrenet=True keeps the profile aligned with the path tangent
            thread = profile.sweep(helix_path, isFrenet=True)
            
            # Move thread to sit on top of the flange
            thread = thread.translate((0, 0, body_len + groove_pos + groove_width + 0.5))
            
            # Combine
            adapter = adapter.union(thread)
        except Exception as e:
            print(f"Warning: Helical thread sweep failed ({e}). Returning simplified thread.")
            
    return adapter

if __name__ == "__main__":
    adapter_detailed = create_adapter(detailed=True)
    cq.exporters.export(adapter_detailed, "adapter_detailed.step")
    
    adapter_defeatured = create_adapter(detailed=False)
    cq.exporters.export(adapter_defeatured, "adapter_defeatured.step")
    print("Exported detailed and defeatured adapter models.")
