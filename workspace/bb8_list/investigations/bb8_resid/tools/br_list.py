"""br_list.py LIST [DEPTH] : backref_s.check on every machine of LIST (lines 'name machine'); prints name, verdicts."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location('br', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backref_s.py'))
