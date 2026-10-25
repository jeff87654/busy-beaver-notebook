"""exprobe.py IN.tsv OUT.tsv [grades] : exhaustion probes K(0^n; 0; b) built from each row's dlscan3 template,
n = parent's start length (p0/p1 30, p2/p3 11, c35/c35h 35) and n = 3, b in 5,10,20,40; literal sim9 (Idle), cap 2e8.
Reports H<ones> or T per probe."""
import re, subprocess, sys
SIM = r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb9_from_bb8/sim9.exe'
NST = {'p0': 30, 'p1': 30, 'p2': 11, 'p3': 11, 'c35': 35, 'c35h': 35}
def word(t, n, b):
    f = dict(kv.split('=') for kv in t.split(',')[2:])
    al, be = map(int, re.fullmatch(r'(\d+)d\+(\d+)', f['d']).groups())
    aB, bB = map(int, re.fullmatch(r'(\d+)b\+(\d+)', f['b']).groups())
    return f['P'] + (f['u'] * be + f['s']) * (n + 1) + f['u'] * (aB * b + bB) + f['S'], t.split(',')[1]
def main():
  grades = sys.argv[3].split(',') if len(sys.argv) > 3 else None
  out = open(sys.argv[2], 'w')
  for l in open(sys.argv[1]):
      r = l.rstrip('\n').split('\t')
      if grades and r[6] not in grades: continue
      res = []
      for n in (3, NST[r[0]]):
          for b in (5, 10, 20, 40):
              w, q = word(r[7], n, b)
              p = subprocess.run([SIM, r[3], w, str(len(w)), q, '200000000', '10'], capture_output=True, text=True,
                                 creationflags=0x40).stdout
              m = re.search(r'HALT at step (\d+) in state (\w) reading (\d): ones (\d+)', p)
              res.append(f'n{n}b{b}:' + (f'H{m.group(4)}@{m.group(2)}{m.group(3)}' if m else 'T'))
      out.write('\t'.join(r[:4] + [r[6], ' '.join(res)]) + '\n'); out.flush()
  
if __name__ == "__main__":
    main()
