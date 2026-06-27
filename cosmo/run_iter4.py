import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cosmo_runner import run_cosmo_iteration

# Iteration 3 Reasoning
reasoning_iter3 = {
    "iteration": 3,
    "config": {"od": 60.0, "layers": [
        {'name': 'Outer', 'material': 'Titanium', 'thickness': 3.0},
        {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 14.0},
        {'name': 'Chassis', 'material': 'PEEK', 'thickness': 3.0}
    ]},
    "result": {"max_temp": 80.51},
    "constraints": {"thermal": {"threshold": 70.0, "satisfied": False}},
    "reasoning": "Temperature 80.51°C is only 10.51°C above the threshold. The 14.0 mm Aerogel layer at 60 mm OD is very close to achieving the target. To bridge the final 10.5°C gap without using other metals (like CuBe) for thermal mass, we must slightly increase the insulation thickness. We will increase the OD to 66.0 mm and the Aerogel layer to 17.0 mm.",
    "proposed_next": {
        "od": 66.0,
        "layers": [
            {'name': 'Outer', 'material': 'Titanium', 'thickness': 3.0},
            {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 17.0},
            {'name': 'Chassis', 'material': 'PEEK', 'thickness': 3.0}
        ]
    }
}

# Run Iteration 4
layers_iter4 = reasoning_iter3["proposed_next"]["layers"]
od_iter4 = reasoning_iter3["proposed_next"]["od"]
max_temp = run_cosmo_iteration(4, od_iter4, 100.0, layers_iter4, bht=150.0, time_seconds=3600, animate=False)
print(f"ITER4_MAX_TEMP: {max_temp}")
