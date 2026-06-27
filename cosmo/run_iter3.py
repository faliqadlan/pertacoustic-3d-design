import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cosmo_runner import run_cosmo_iteration

# Iteration 2 Reasoning
reasoning_iter2 = {
    "iteration": 2,
    "config": {"od": 43.0, "layers": [
        {'name': 'Outer', 'material': 'Titanium', 'thickness': 3.0},
        {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 8.0},
        {'name': 'Chassis', 'material': 'PEEK', 'thickness': 3.0}
    ]},
    "result": {"max_temp": 105.87},
    "constraints": {"thermal": {"threshold": 70.0, "satisfied": False}},
    "reasoning": "Temperature 105.87°C is still 35.87°C above the 70°C threshold. The 8.0 mm Aerogel layer significantly improved thermal resistance compared to Iteration 1, but is insufficient to keep the temperature below 70°C for an hour at 43 mm OD. Since the user allowed increasing the OD, we will increase the OD to 60.0 mm to accommodate a much thicker Aerogel insulation layer (14.0 mm) while maintaining sufficient ID.",
    "proposed_next": {
        "od": 60.0,
        "layers": [
            {'name': 'Outer', 'material': 'Titanium', 'thickness': 3.0},
            {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 14.0},
            {'name': 'Chassis', 'material': 'PEEK', 'thickness': 3.0}
        ]
    }
}

# Run Iteration 3
layers_iter3 = reasoning_iter2["proposed_next"]["layers"]
od_iter3 = reasoning_iter2["proposed_next"]["od"]
max_temp = run_cosmo_iteration(3, od_iter3, 100.0, layers_iter3, bht=150.0, time_seconds=3600, animate=False)
print(f"ITER3_MAX_TEMP: {max_temp}")
