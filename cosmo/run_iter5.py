import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cosmo_runner import run_cosmo_iteration

# Iteration 4 Reasoning
reasoning_iter4 = {
    "iteration": 4,
    "config": {"od": 66.0, "layers": [
        {'name': 'Outer', 'material': 'Titanium', 'thickness': 3.0},
        {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 17.0},
        {'name': 'Chassis', 'material': 'PEEK', 'thickness': 3.0}
    ]},
    "result": {"max_temp": 72.81},
    "constraints": {"thermal": {"threshold": 70.0, "satisfied": False}},
    "reasoning": "Temperature 72.81°C is incredibly close to the 70°C threshold (only 2.81°C over). A small additional increment in the Aerogel thickness will likely achieve convergence. We will increase the OD to 68.0 mm and the Aerogel layer to 18.0 mm.",
    "proposed_next": {
        "od": 68.0,
        "layers": [
            {'name': 'Outer', 'material': 'Titanium', 'thickness': 3.0},
            {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 18.0},
            {'name': 'Chassis', 'material': 'PEEK', 'thickness': 3.0}
        ]
    }
}

# Run Iteration 5
layers_iter5 = reasoning_iter4["proposed_next"]["layers"]
od_iter5 = reasoning_iter4["proposed_next"]["od"]
max_temp = run_cosmo_iteration(5, od_iter5, 100.0, layers_iter5, bht=150.0, time_seconds=3600, animate=False)
print(f"ITER5_MAX_TEMP: {max_temp}")
