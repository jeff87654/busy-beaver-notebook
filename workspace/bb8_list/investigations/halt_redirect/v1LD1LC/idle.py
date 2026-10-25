"""run a python script at Idle priority: python idle.py SCRIPT ARGS..."""
import ctypes, sys, runpy, threading
k = ctypes.windll.kernel32
k.SetPriorityClass(k.GetCurrentProcess(), 0x40)
sys.setrecursionlimit(1000000)
threading.stack_size(256*1024*1024 - 4096)
sys.argv = sys.argv[1:]
def main():
    runpy.run_path(sys.argv[0], run_name='__main__')
t = threading.Thread(target=main); t.start(); t.join()
