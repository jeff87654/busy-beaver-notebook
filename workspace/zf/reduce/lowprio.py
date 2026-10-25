"""Import to drop this process to Windows IDLE priority and pin it to cores 0-3 (bb8 CPU policy)."""
import ctypes
from ctypes import wintypes
try:
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.GetCurrentProcess.restype = wintypes.HANDLE
    k.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    k.SetProcessAffinityMask.argtypes = [wintypes.HANDLE, ctypes.c_size_t]
    h = k.GetCurrentProcess()
    if not k.SetPriorityClass(h, 0x40):          # IDLE_PRIORITY_CLASS
        raise OSError(ctypes.get_last_error())
    k.SetProcessAffinityMask(h, 0xF)
except Exception as e:
    import sys; print('lowprio failed:', e, file=sys.stderr)
