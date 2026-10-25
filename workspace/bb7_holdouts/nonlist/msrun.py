"""msrun.py MACHINE K DUMPFILE MAXMACRO PRINTEVERY [edits...]: run ms.exe from a dumped tape (nlp7v --dumpat) with
count edits 'IDX=VAL' (IDX = token index in the dump line, 0 = first token after '|', '[..]' counted) or 'LIST=n'
(keep n repeats of the longest repeated 2-token pattern); prints compressed snapshots ((pat)xN)."""
import re, subprocess, sys
m, K, dump, mm, pe = sys.argv[1:6]; edits = [e for e in sys.argv[6:] if not e.startswith('--')]
line = open(dump).read().splitlines()[1]
head, toks = line.split('|', 1); toks = toks.split()
for e in edits:
    k, v = e.split('=')
    if k == 'LIST':
        # find longest run of a repeated 2-token pattern
        best = (0, 0)
        i = 0
        while i + 3 < len(toks):
            j = i
            while j + 3 < len(toks) and toks[j] == toks[j + 2] and toks[j + 1] == toks[j + 3]: j += 2
            if (j - i) // 2 + 1 > best[1]: best = (i, (j - i) // 2 + 1)
            i = j + 1 if j > i else i + 1
        s, r = best; n = int(v)
        toks = toks[:s + 2 * n] + toks[s + 2 * r:]
    else:
        i = int(k); b = toks[i].split('^')[0]; toks[i] = f'{b}^{v}'
inp = head + '| ' + ' '.join(toks) + '\n'
ms = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
p = subprocess.Popen([ms, m, K, mm, 'p' + pe, 'i'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, creationflags=0x40)
p.stdin.write(inp); p.stdin.close()
DIG = '--digits' in sys.argv
DIGKEY = [e.split('=')[1] for e in sys.argv if e.startswith('--key=')][0] if any(e.startswith('--key=') for e in sys.argv) else '011100'
def comp(ts):
    out = []; i = 0
    while i < len(ts):
        if i + 3 < len(ts) and ts[i] == ts[i + 2] and ts[i + 1] == ts[i + 3]:
            j = i
            while j + 3 < len(ts) and ts[j] == ts[j + 2] and ts[j + 1] == ts[j + 3]: j += 2
            out.append(f'({ts[i]} {ts[i+1]})x{(j - i) // 2 + 1}'); i = j + 2
        else: out.append(ts[i]); i += 1
    return ' '.join(out)
prev = None
for l in p.stdout:
    l = l.rstrip('\n')
    if DIG and l.startswith('T '):
        a, st = l.split('|', 1)
        if ']' not in st: continue
        tail = st.split(']', 1)[1].split()
        ks = [i for i, t in enumerate(tail) if t.startswith(DIGKEY)]
        if not ks: continue
        dig = comp(tail[ks[0]:]).replace('^1 ', ' ')
        if dig != prev:
            print(a.split()[1], a.split()[2], '| acc:', ' '.join(tail[:ks[0]])[:70], '|', dig[:220]); prev = dig
        continue
    if l.startswith('T '):
        a, b = l.split('|', 1)
        c = comp(b.split()).replace('^1 ', ' ')
        key = re.sub(r'\^\d+', '', c)
        print(a.split()[1], a.split()[2], a.split()[3], '|', c[:300])
    else: print(l)
