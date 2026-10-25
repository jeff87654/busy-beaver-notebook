import idle, subprocess, sys
# rungeo.py PART OUT STEPS: run geo.exe at idle priority on a pool part; record pid
part, out, steps = sys.argv[1], sys.argv[2], sys.argv[3]
with open(part) as fi, open(out, 'w') as fo:
    p = subprocess.Popen([r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_fw1_counter\geo.exe', steps], stdin=fi, stdout=fo, creationflags=0x40)
    with open('pids.txt', 'a') as pf: pf.write(f'{p.pid} geo.exe {part}\n')
    p.wait()
