import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cosmo_runner import run_cosmo_iteration

# Iteration 5 Reasoning
reasoning_iter5 = {
    "iteration": 5,
    "config": {"od": 68.0, "layers": [
        {'name': 'Outer', 'material': 'Titanium', 'thickness': 3.0},
        {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 18.0},
        {'name': 'Chassis', 'material': 'PEEK', 'thickness': 3.0}
    ]},
    "result": {"max_temp": 70.53},
    "constraints": {"thermal": {"threshold": 70.0, "satisfied": False}},
    "reasoning": "Temperature 70.53°C is almost exactly on the threshold (0.53°C over). A tiny increase in OD to 70.0 mm (Aerogel to 19.0 mm) will safely clear the 70.0°C constraint while maintaining all material constraints.",
    "proposed_next": {
        "od": 70.0,
        "layers": [
            {'name': 'Outer', 'material': 'Titanium', 'thickness': 3.0},
            {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 19.0},
            {'name': 'Chassis', 'material': 'PEEK', 'thickness': 3.0}
        ]
    }
}

# Run Iteration 6
layers_iter6 = reasoning_iter5["proposed_next"]["layers"]
od_iter6 = reasoning_iter5["proposed_next"]["od"]
max_temp = run_cosmo_iteration(6, od_iter6, 100.0, layers_iter6, bht=150.0, time_seconds=3600, animate=False)
print(f"ITER6_MAX_TEMP: {max_temp}")
