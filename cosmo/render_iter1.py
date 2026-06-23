import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from thermal_animator import animate_results
animate_results("casing_iter1.inp", "casing_iter1.frd", "thermal_anim_iter1.mp4")
