"""
Dimension and Assumption Register for HTI-02-DHPC/D
"""
import json
from pathlib import Path

DIMENSIONS = {
    "hydrophone_envelope": {
        "length_inches": 3.5,
        "length_mm": 88.9,
        "diameter_inches": 0.688,
        "diameter_mm": 17.4752,
        "source": "HTI Product Page and Mechanical Outline (02-001-25-00-00)",
        "notes": "Envelope dimensions only. Internal geometry is proprietary and not modeled."
    },
    "mounting_interface": {
        "thread_spec": "7/16-20 UNF",
        "hydrophone_thread": "7/16-20 UNF-2B (female)",
        "adapter_thread": "7/16-20 UNF-2A (male)",
        "source": "HTI Mechanical Outline",
        "notes": "Thread provides mechanical retention only."
    },
    "pressure_seal": {
        "type": "Radial O-ring",
        "location": "Adapter body (male part) sealing against hydrophone bore",
        "assumption": True,
        "requires_hti_confirmation": True,
        "notes": "Assuming standard radial O-ring groove on the 7/16-20 adapter plug. Dimensions to be confirmed by HTI for 10,000 psi rating."
    }
}

def export_register(output_dir):
    out_path = Path(output_dir) / "dimension_and_assumption_register.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(DIMENSIONS, f, indent=4)
    print(f"Exported dimension register to {out_path}")

if __name__ == "__main__":
    export_register(".")
