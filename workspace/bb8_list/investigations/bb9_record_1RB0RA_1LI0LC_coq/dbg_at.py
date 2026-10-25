"""python dbg_at.py SCRIPT N : run the exploration script's first N stages, then debug the loop search."""
import sys, io, contextlib
script, N = sys.argv[1], sys.argv[2]
sys.argv = ['x', N]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    mod = __import__(script)
import mexp
mexp.debug_loop(mod.cfg)
