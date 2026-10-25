"""idle.py: import first; sets this process (and so its children) to IDLE priority on Windows, with correct HANDLE types."""
import sys
if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes
    _k = ctypes.windll.kernel32
    _k.GetCurrentProcess.restype = wintypes.HANDLE
    _k.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    _k.SetPriorityClass(_k.GetCurrentProcess(), 0x40)
