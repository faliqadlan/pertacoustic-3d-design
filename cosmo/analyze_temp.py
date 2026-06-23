import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from result_extractor import parse_frd_temperatures
import numpy as np

nodes, steps = parse_frd_temperatures("casing_iter2.frd")

# Get the last step
last_step = steps[-1]
temps = last_step['temperatures']

# Group nodes by radius
radii = []
t_vals = []
for nid, temp in temps.items():
    x, y, z = nodes[nid]
    r = (x**2 + y**2)**0.5
    radii.append(r)
    t_vals.append(temp)

import collections
r_bins = collections.defaultdict(list)
for r, t in zip(radii, t_vals):
    # bin by 1 mm
    bin_r = round(r, 0)
    r_bins[bin_r].append(t)

for bin_r in sorted(r_bins.keys()):
    arr = np.array(r_bins[bin_r])
    print(f"Radius ~{bin_r} mm: Min Temp = {arr.min():.2f}, Max Temp = {arr.max():.2f}, Mean = {arr.mean():.2f}")
