"""Run coq/build.py at Windows IDLE priority (bb8 CPU policy).  Usage: python tools/build_idle.py File.v"""
import ctypes, runpy, sys
from pathlib import Path
k = ctypes.WinDLL('kernel32')
k.SetPriorityClass(k.GetCurrentProcess(), 0x40)   # IDLE_PRIORITY_CLASS, inherited by coqc
sys.argv = ['build.py'] + sys.argv[1:]
runpy.run_path(str(Path(__file__).resolve().parent.parent / 'coq' / 'build.py'), run_name='__main__')
