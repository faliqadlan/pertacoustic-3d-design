import sys

def check_duplicate_nodes(inp_file):
    nodes = []
    in_node = False
    with open(inp_file, "r") as f:
        for line in f:
            if line.upper().startswith("*NODE"):
                in_node = True
                continue
            elif line.startswith("*"):
                in_node = False
                continue
            
            if in_node:
                parts = line.split(",")
                try:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    nodes.append((x,y,z))
                except:
                    pass
                    
    print(f"Total nodes: {len(nodes)}")
    unique_nodes = set(nodes)
    print(f"Unique coordinates: {len(unique_nodes)}")
    print(f"Duplicates: {len(nodes) - len(unique_nodes)}")

check_duplicate_nodes("casing_iter2.inp")
