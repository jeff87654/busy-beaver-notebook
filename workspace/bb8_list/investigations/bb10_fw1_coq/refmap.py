import subprocess, sys
LOW = 0x40
def run(n, w=20000, C=30, R=1):
    Z = n - 9 - 4 * R
    x = 4 * w + 13
    args = [str(__import__('pathlib').Path(__file__).resolve().parent / 'cpp' / 'hsim.exe'), '20000000000', '6', '6', '6', '3', str(C), str(x), '0', '1*%d' % Z, '1', str(R), '2']
    o = subprocess.run(args, capture_output=True, text=True, creationflags=LOW).stdout.split('\n')
    seq = [int(l.split('zeros=')[1].split()[0]) for l in o if l.startswith('W0')]
    stk = [int(l.split('stackblocks=')[1]) for l in o if l.startswith('W0')]
    fin = [l for l in o if l.startswith('HALT') or l.startswith('LIMIT') or l.startswith('WIDE')][0]
    return seq, stk, fin
if __name__ == '__main__':
    for n in range(int(sys.argv[1]), int(sys.argv[2])):
        seq, stk, fin = run(n, w=int(sys.argv[3]) if len(sys.argv) > 3 else 20000)
        print(n, n % 5, seq, stk[-1] if stk else None, fin.split()[0], fin.split()[1], flush=True)
