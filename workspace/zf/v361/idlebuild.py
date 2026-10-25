"""Run coq/build.py (cwd-relative) at Windows Idle priority; children inherit it."""
import ctypes, runpy, sys
k = ctypes.windll.kernel32
k.SetPriorityClass(k.GetCurrentProcess(), 0x40)  # IDLE_PRIORITY_CLASS
sys.argv = ['build.py'] + sys.argv[1:]
runpy.run_path('coq/build.py', run_name='__main__')
