"""Follow L1 through forced rounds: at each G-form snapshot after a rebuild, cut list to 1 item, d2=d1=1, acc=(3,3)."""
import sys, subprocess, re
sys.path.insert(0, '..'); import idle  # noqa
MS = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
M = '1RB---_1RC1RD_0LD1LC_1RF0LE_0LG1LC_0RB0RG_0RA1LD'
cfg = open(sys.argv[1]).read().splitlines()[1]
for rnd in range(int(sys.argv[2])):
    p = subprocess.Popen([MS, M, '6', '6000000', 'p2000', 'i'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    p.stdin.write(cfg + '\n'); p.stdin.close()
    nxt = None; stage = 0
    for l in p.stdout:
        if l.startswith('H'): print('round', rnd, 'HALT', l.strip()); sys.exit()
        if not l.startswith('T '): continue
        a, st = l.split('|', 1); toks = st.split()
        npair = max(sum(1 for i in range(len(toks) - 1) if toks[i] == x and toks[i + 1] == y) for x, y in [(toks[i], toks[i+1]) for i in range(len(toks)-1)] or [(0, 0)]) if len(toks) > 1 else 0
        if stage == 0 and npair <= 2: stage = 1          # old list gone (consumed)
        dd = any(toks[i].startswith('010011') and re.match(r'100100\^3[0-9]{3}$', toks[i+1]) for i in range(len(toks)-1))
        if stage == 1 and npair >= 3 and dd and toks[0] == '[000000]' and toks[1].startswith('000100') and a.split()[3] == 'G':
            nxt = (a, toks); p.kill(); break
    if not nxt: print('round', rnd, 'no rebuild seen within budget'); break
    a, toks = nxt
    # list = most frequent adjacent pair; keep one copy
    pairs = {}
    for i in range(len(toks) - 1): pairs[(toks[i], toks[i + 1])] = pairs.get((toks[i], toks[i + 1]), 0) + 1
    (x, y), n = max(pairs.items(), key=lambda kv: kv[1])
    i0 = next(i for i in range(len(toks) - 1) if toks[i] == x and toks[i + 1] == y)
    j = i0
    while j + 1 < len(toks) and toks[j] == x and toks[j + 1] == y: j += 2
    print(f"round {rnd}: rebuilt list {x} {y} x{n}  head={' '.join(toks[:i0])[:120]}  tail={' '.join(toks[j:])}")
    t2 = toks[:i0] + [x, y] + toks[j:]
    # edit counts: b,a (first two counted tokens after 000100) -> 3; d2,d1 (first two counted tokens after 010011) -> 1
    def setc(k, v): t2[k] = t2[k].split('^')[0] + f'^{v}'
    cnt = [k for k, t in enumerate(t2) if '^' in t and int(t.split('^')[1]) > 1 and k < i0]
    for k in cnt[:2]: setc(k, 3)
    for k in cnt[2:4]: setc(k, 1)
    cfg = 'G 1 | ' + ' '.join(t2)
    print('   next cfg:', cfg[:200])
