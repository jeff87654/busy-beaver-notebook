"""q.py WAITPID -- cmd1 ;; cmd2 ;; ... : wait for WAITPID to exit, then run each command (stdin/stdout redirect via '< f' '> f' tokens) at Idle; log PIDs."""
import idle, subprocess, sys, os, time, ctypes
def alive(pid):
    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
    if not h: return False
    code = ctypes.c_ulong(); ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code)); ctypes.windll.kernel32.CloseHandle(h)
    return code.value == 259
wp = int(sys.argv[1]); cmds = ' '.join(sys.argv[3:]).split(';;')
while wp and alive(wp): time.sleep(20)
for c in cmds:
    toks = c.split(); fin = fout = None; args = []
    i = 0
    while i < len(toks):
        if toks[i] == '<': fin = open(toks[i+1]); i += 2
        elif toks[i] == '>': fout = open(toks[i+1], 'w'); i += 2
        else: args.append(toks[i]); i += 1
    if args[0].endswith('.exe'): args[0] = os.path.abspath(args[0])
    p = subprocess.Popen(args, stdin=fin, stdout=fout, creationflags=0x40)
    with open('pids.txt', 'a') as fp: fp.write(f"{time.strftime('%F %H:%M')} {p.pid} {c.strip()}\n")
    p.wait()
