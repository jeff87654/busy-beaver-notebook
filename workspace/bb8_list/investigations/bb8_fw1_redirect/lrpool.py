import idle, subprocess, os, time
f = open('lr_rep.out', 'w')
q = subprocess.Popen([os.path.abspath('lrun.exe'), 'lr_rep.txt', '1000000'], stdout=f, creationflags=0x40)
open('pids.txt', 'a').write(f"{q.pid} lrun lr_rep 1e6\n"); q.wait()
open('notes.txt', 'a').write(time.strftime('%H:%M') + ' lrun 1e6 on non-K representative leaves done (lr_rep.out)\n')
