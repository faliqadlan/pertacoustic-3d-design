import cadquery as cq

def create_hydrophone_envelope():
    """
    Creates a simplified, defeatured envelope of the HTI-02-DHPC/D hydrophone.
    Dimensions from mechanical outline:
    Length: 3.5 inches = 88.9 mm
    Diameter: 0.688 inches = 17.4752 mm
    """
    length_mm = 88.9
    dia_mm = 17.4752
    
    # We create a simple cylinder representing the external envelope.
    # The actual internal geometry is proprietary and not modeled.
    envelope = cq.Workplane("XY").circle(dia_mm / 2.0).extrude(length_mm)
    return envelope

if __name__ == "__main__":
    env = create_hydrophone_envelope()
    cq.exporters.export(env, "hti02_envelope.step")
    print("Exported hti02_envelope.step")
