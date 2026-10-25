"""helpers: build run-spec from family parameters, run fsnap, parse output"""
import subprocess, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
M = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE"
def word_of(Qword, toks, r, h, tail):
    """Qword: binary string ending in '00' or ''; list D(t1)..D(tk) (10)^r 1^h ; tail: list of 1-run lengths each preceded by 00"""
    w = Qword + ''.join('10'*t + '1' for t in toks) + '10'*r + '1'*h
    for x in tail: w += '00' + '1'*x
    return w
def spec_of_word(w):
    w = w.lstrip('0').rstrip('0'); out = []; i = 0
    while i < len(w):
        j = i
        while j < len(w) and w[j] == '1': j += 1
        k = j
        while k < len(w) and w[k] == '0': k += 1
        z = k - j; o = j - i
        out.append(f"{o}" if z == 1 else (f"{o}." if z == 0 else (f"{o}|" if z == 2 else f"{o}|{z}|")))
        i = k
    return ' '.join(out)
FAM = re.compile(r'^(\d+) \[(\d+)\] Q\[(.*?)\] g=(\d+) T\[(.*?)\] r=(\d+) h=(\d+) tail\[(.*?)\]')
def expand_list(s):
    out = []
    for part in s.split(','):
        if not part: continue
        if '^' in part:
            v, c = part.split('^'); out += [int(v)]*int(c)
        else: out.append(int(part))
    return out
def run(w, nsteps=10**9, ncfg=1, hmin=3, maxQ=100000):
    spec = spec_of_word(w)
    p = subprocess.run([os.path.join(HERE, 'fsnap.exe'), M, spec, str(nsteps), str(hmin), str(maxQ), str(ncfg)], capture_output=True, text=True)
    res = []
    for line in p.stdout.splitlines():
        m = FAM.match(line)
        if m:
            res.append(dict(step=int(m.group(1)), Q=m.group(3).strip(), g=int(m.group(4)), toks=expand_list(m.group(5)), r=int(m.group(6)), h=int(m.group(7)), tail=expand_list(m.group(8))))
        elif line.startswith('HALT'):
            res.append(dict(halt=line))
        elif line.startswith('RAW'):
            res.append(dict(raw=line))
    return res
def cl(v):
    out=[]; i=0
    while i < len(v):
        j=i
        while j < len(v) and v[j]==v[i]: j+=1
        out.append(f"{v[i]}" + (f"^{j-i}" if j-i>1 else "")); i=j
    return '[' + ','.join(out) + ']'
def fmt(c):
    if 'halt' in c: return c['halt']
    if 'raw' in c: return c['raw'][:200]
    q = c['Q']; q = q if len(q) < 120 else q[:50]+' ... '+q[-60:]
    return f"{c['step']}: Q[{q}] {cl(c['toks'])} r={c['r']} h={c['h']} tail{cl(c['tail'])}"
