# exprobe2.py: enhanced counter-exhaustion probe that handles any active symbol X_k (not just X0)
# and handles <Q adjacent to a symbolic run w^H{rr} by peeling 1 copy of w (reducing rr by 1 mod MG).
import sys, re, subprocess, os

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MG = 38918880

T_MAP = {}
for l in open(os.path.join(B, 'kg', 'fitted.tsv')):
    f = l.rstrip('\r\n').split('\t')
    if len(f) >= 4:
        T_MAP[f[0]] = f[3]

def probe_one(m, b0='20000', b1='100000', exe='symsim_v14g.exe'):
    T = T_MAP.get(m, '')
    opts = ['--memcap', '2000', '--sigwin', '0', '--mg', str(MG), '--canon', '--multi', '--dom'] + (['--tmpl', T] if T else [])
    r = subprocess.run([os.path.join(B, exe), 'run', '--budget', b0, '--tlimit', '200', '--tape', '--tapeall', '400'] + opts,
                       input=f'{m} A\n', capture_output=True, text=True).stdout.split('\n')
    tape = [l for l in r if l.startswith('TAPE ')]
    syms = [l for l in r if l.startswith('TAPESYMS')]
    if not tape:
        return f'{m} NOTAPE'
    tape = tape[0][5:]
    syms = syms[0] if syms else ''
    if tape.startswith('...'):
        return f'{m} TAPE-TRUNCATED'
    res = {k: int(v) for k, v in re.findall(r'X(\d+)=[^\[]*\[r(\d+)\]', syms)}

    def lin_res(e):
        if '/' in e:
            return None
        tot = 0
        for sign, coef, var, const in re.findall(r'([+-]?)(?:(\d+)\*)?(?:X(\d+)|(\d+))', e):
            sg = -1 if sign == '-' else 1
            if var:
                if var not in res:
                    return None
                tot += sg * (int(coef) if coef else 1) * res[var]
            elif const:
                tot += sg * int(const)
        return tot % MG

    toks = tape.split()
    # Find all symbolic runs on the tape
    sym_indices = []
    for i, t in enumerate(toks):
        mm = re.match(r'([01]+)\^\{(.*)\}$', t)
        if mm and 'X' in mm.group(2):
            sym_indices.append(i)
    if not sym_indices:
        return f'{m} NOSYMRUNS {tape[:160]}'

    all_out = []
    for bi in sym_indices:
        out = []
        for cval in (0, 1, 2):
            nt = []
            for i, t in enumerate(toks):
                mm = re.match(r'([01]+)\^\{(.*)\}$', t)
                if i == bi:
                    nt.append(f'{mm.group(1)}^{cval}' if cval > 0 else '')
                    continue
                if mm:
                    rr = lin_res(mm.group(2))
                    if rr is None:
                        nt = None
                        break
                    nt.append(f'{mm.group(1)}^H{rr}')
                else:
                    nt.append(t)
            if nt is None:
                out.append(f'c={cval}:NORES')
                continue
            spec = ' '.join(x for x in nt if x)
            if re.search(r'<[A-P]', spec):
                parts = spec.split()
                j = [k for k, x in enumerate(parts) if re.fullmatch(r'<[A-P]', x)][0]
                q = parts[j][1]
                left = parts[:j]
                lw = left[-1]
                w, _, cnt = lw.partition('^')
                if cnt and cnt.startswith('H'):
                    rr = (int(cnt[1:]) - 1) % MG
                    peeled = [f'{w}^H{rr}'] + ([w[:-1]] if len(w) > 1 else [])
                    left = left[:-1] + peeled
                    spec = ' '.join(left + [q + '>', w[-1]] + parts[j + 1:])
                else:
                    n = int(cnt) if cnt else 1
                    cells = w * n
                    left = left[:-1] + ([cells[:-1]] if len(cells) > 1 else [])
                    spec = ' '.join(left + [q + '>', cells[-1]] + parts[j + 1:])
            o = subprocess.run([os.path.join(B, exe), 'run', '--budget', b1, '--tlimit', '200', '--hlb', '1000000'] + opts,
                               input=f'{m} A {spec}\n', capture_output=True, text=True).stdout
            R = [l for l in o.split('\n') if l.startswith('R ')]
            if not R:
                out.append(f'c={cval}:NOR')
                continue
            p = R[0].split()
            jl = R[0].split('|')[1].strip() if '|' in R[0] else ''
            kj = [x for x in p if x.startswith('kj=')]
            out.append(f'c={cval}:{p[3]}:{kj[0] if kj else ""}[{jl[:60]}]')
        all_out.append(f'tok[{bi}]={toks[bi]} -> ' + ' '.join(out))
    return f'{m} | ' + ' || '.join(all_out)

if __name__ == '__main__':
    for fn in ['ep14/out_a.txt', 'ep14/out_b.txt']:
        for ln in open(os.path.join(B, fn)):
            if 'NOCOUNTER' in ln or 'HEADSYM' in ln:
                m = ln.split()[0]
                res = probe_one(m)
                print(res, flush=True)
