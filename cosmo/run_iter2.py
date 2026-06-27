import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cosmo_runner import run_cosmo_iteration

# Iteration 1 Reasoning
reasoning_iter1 = {
    "iteration": 1,
    "config": {"od": 43.0, "layers": [
        {'name': 'Outer', 'material': 'Titanium', 'thickness': 5.0},
        {'name': 'Chassis', 'material': 'PEEK', 'thickness': 5.0}
    ]},
    "result": {"max_temp": 150.0},
    "constraints": {"thermal": {"threshold": 70.0, "satisfied": False}},
    "reasoning": "Temperature 150.0°C is 114% above the threshold of 70°C. The internal chassis reached thermal equilibrium with the BHT. PEEK alone does not provide enough thermal resistance for 1 hour. No metals other than Titanium are allowed, and no vacuum is allowed.",
    "proposed_next": {
        "od": 43.0,
        "layers": [
            {'name': 'Outer', 'material': 'Titanium', 'thickness': 3.0},
            {'name': 'Insulation', 'material': 'Aerogel', 'thickness': 8.0},
            {'name': 'Chassis', 'material': 'PEEK', 'thickness': 3.0}
        ]
    }
}

# Run Iteration 2
layers_iter2 = reasoning_iter1["proposed_next"]["layers"]
max_temp = run_cosmo_iteration(2, 43.0, 100.0, layers_iter2, bht=150.0, time_seconds=3600, animate=False)
print(f"ITER2_MAX_TEMP: {max_temp}")
