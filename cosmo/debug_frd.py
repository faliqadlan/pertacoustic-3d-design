import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from result_extractor import parse_frd_temperatures

nodes, steps = parse_frd_temperatures("casing_iter1.frd")
print(f"Parsed {len(nodes)} nodes and {len(steps)} steps.")
if len(nodes) > 0:
    first_nid = list(nodes.keys())[0]
    print(f"First node: {first_nid} -> {nodes[first_nid]}")
    
if not steps:
    print("No steps parsed.")
else:
    print(f"First step temps: {len(steps[0]['temperatures'])}")
