import idle, subprocess, sys
# runw.py MACHINEFILE STEPS : width.exe on each machine (idle), print last span line
exe = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_fw1_counter\width.exe'
for l in open(sys.argv[1]):
    m = l.split()[0]
    p = subprocess.Popen([exe, m, sys.argv[2]], stdout=subprocess.PIPE, text=True, creationflags=0x40)
    with open('pids.txt', 'a') as f: f.write(f'{p.pid} width {m}\n')
    o = p.communicate()[0].strip().splitlines()
    print(m, '|', o[-2] if len(o) > 1 else '', '|', o[-1], flush=True)
