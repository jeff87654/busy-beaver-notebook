import idle, subprocess, sys
ms = [l.split('\t')[0] for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\low34.txt') if l.strip()]
out = open('batch1e10.txt', 'w')
for m in ms:
    p = subprocess.Popen([r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\low\run.exe', m, sys.argv[1]], stdout=subprocess.PIPE, text=True, creationflags=0x40)
    open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\pids.txt', 'a').write('%d run.exe batch %s\n' % (p.pid, m))
    o, _ = p.communicate(); out.write(o); out.flush()
