import numpy as np

def parse_frd_temperatures(frd_file):
    """
    Parses a CalculiX .frd file and extracts nodal temperatures for all time steps.
    
    Returns:
        nodes: dictionary of {node_id: (x, y, z)}
        steps: list of dictionaries, one per time step. 
               Each step has:
               - 'time': float time value
               - 'temperatures': dict of {node_id: temp_val}
    """
    nodes = {}
    steps = []
    
    with open(frd_file, "r") as f:
        lines = f.readlines()
        
    current_time = 0.0
    in_nodes = False
    in_temp = False
    current_temps = {}
    
    for line in lines:
        if line.startswith("    2C") or line.startswith(" 2C") or line.strip().startswith("2C"):
            # Start of node coordinates block
            in_nodes = True
            in_temp = False
            continue
        elif line.startswith("    3") or line.startswith(" 3") or line.strip() == "3":
            # End of block
            in_nodes = False
            in_temp = False
            continue
        elif "100CL" in line:
            # Temperature block header
            # E.g. "  100CL  101 60.00000000       90829                     1    1           1"
            parts = line.split()
            if len(parts) >= 3:
                try:
                    current_time = float(parts[2])
                except (IndexError, ValueError):
                    pass
            in_temp = True
            in_nodes = False
            current_temps = {}
            steps.append({'time': current_time, 'temperatures': current_temps})
            continue
            
        if in_nodes:
            # Node line: ' -1  node_id  x  y  z'
            # Strict FRD fixed-width format for nodes: 
            #  -1 (3 chars), id (10 chars), x,y,z (12 chars each)
            try:
                if line.startswith(" -1"):
                    nid = int(line[3:13])
                    x = float(line[13:25])
                    y = float(line[25:37])
                    z = float(line[37:49])
                    nodes[nid] = (x, y, z)
            except ValueError:
                pass
                
        if in_temp:
            # Temperature line: ' -1  node_id  temp'
            # Strict FRD format: -1 (3), id (10), val (12)
            try:
                if line.startswith(" -1"):
                    nid = int(line[3:13])
                    t_val = float(line[13:25])
                    current_temps[nid] = t_val
            except ValueError:
                pass
                
    return nodes, steps

def extract_max_internal_temperature(frd_file, target_time=14400, r_inner=12.7, z_bounds=None):
    """
    Finds the maximum temperature on the inner surface at a given time.
    r_inner is the inner radius (25.4 mm / 2).
    """
    nodes, steps = parse_frd_temperatures(frd_file)
    
    if not steps:
        raise ValueError(f"No temperature steps found in {frd_file}")
        
    # Find the step closest to target_time
    closest_step = min(steps, key=lambda x: abs(x['time'] - target_time))
    if abs(closest_step['time'] - target_time) > max(1.0, target_time * 0.01):
        raise ValueError(
            f"Closest FRD time {closest_step['time']} is not within 1% of {target_time}"
        )
    
    # Filter nodes that are on the inner boundary (r ~ r_inner)
    inner_nodes = []
    tol = 0.5 # mm tolerance
    for nid, (x, y, z) in nodes.items():
        r = (x**2 + y**2)**0.5
        if abs(r - r_inner) < tol and (z_bounds is None or z_bounds[0] <= z <= z_bounds[1]):
            inner_nodes.append(nid)
            
    if not inner_nodes:
        raise ValueError(f"No nodes found at requested inner radius {r_inner} mm")
        
    max_t = -999.0
    temps = closest_step['temperatures']
    for nid in inner_nodes:
        if nid in temps:
            if temps[nid] > max_t:
                max_t = temps[nid]
                
    if max_t == -999.0:
        raise ValueError("Inner-boundary nodes have no temperatures in the selected FRD step")
    return max_t
