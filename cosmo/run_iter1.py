import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cosmo_runner import run_cosmo_iteration

layers = [
    {'name': 'Outer', 'material': 'Titanium', 'thickness': 5.0},
    {'name': 'Chassis', 'material': 'PEEK', 'thickness': 5.0}
]

max_temp = run_cosmo_iteration(1, 43.0, 100.0, layers, bht=150.0, time_seconds=3600, animate=False)
print(f"ITER1_MAX_TEMP: {max_temp}")
