"""Generate the mechanical parts of coq/Prog.v from coq/ZF2Dag.v (rewrites the GENERATED regions).
Usage: python tools/gen_prog.py"""
import re
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
txt = (HERE / 'coq' / 'ZF2Dag.v').read_text()
nodes, names = {}, {}
for m in re.finditer(r'\| (\d+) => \((.*?), (E\w+(?: \d+)?)\)\s+\(\* (.*?) \*\)', txt):
    nodes[int(m.group(1))] = (m.group(2), m.group(3)); names[int(m.group(1))] = m.group(4)

def num(e, kind):
    m = re.fullmatch(kind + r' (\d+)', e); return int(m.group(1)) if m else None

def loops():
    out = []
    for n in sorted(nodes):
        if not names[n].startswith('while_decnz(') or not names[n].endswith(').0'):
            continue
        car, cdr = nodes[n]
        r = num(car, 'EDecnz'); assert r is not None, n
        if cdr == 'EContinue 1':
            targets = []
        else:
            b = num(cdr, 'ENode'); bc, bd = nodes[b]; assert bd == 'EContinue 2', n
            if num(bc, 'EInc') is not None:
                targets = [num(bc, 'EInc')]
            else:
                b2 = num(bc, 'ENode'); x, y = nodes[b2]
                targets = [num(x, 'EInc'), num(y, 'EInc')]
        assert None not in targets and r not in targets and len(set(targets)) == len(targets)
        post = 'm'
        for t in targets:
            post = f'set {wrap(post)} {t} (get m {t} + get m {r})'
        post = f'set {wrap(post)} {r} 0'
        g = 'fun m : St => m' if not targets else ' '.join(f'inc {t} (' for t in reversed(targets)).strip() + ' m' + ')' * len(targets)
        if len(targets) == 1: g = f'inc {targets[0]}'
        if len(targets) == 2: g = f'fun m : St => inc {targets[1]} (inc {targets[0]} m)'
        out.append(f'(* {names[n]} *)\nLemma w{n} m : sem (ENode {n}) m XNormal ({post}).\n'
                   f'Proof. revert m; while_tac ({g}) (fun m : St => {post}). Qed.')
    return '\n'.join(out)

NAMES = {235: 'E_v0', 250: 'E_v1', 251: 'E_v2', 252: 'E_v3', 253: 'E_v4', 229: 'E_par1', 231: 'E_par2',
         233: 'E_par3', 260: 'E_weq', 258: 'E_wel', 321: 'E_wim', 323: 'E_wn', 256: 'E_wal', 262: 'E_wex',
         254: 'E_wa', 236: 'E_select', 11: 'E_cparam2', 13: 'E_cparam3'}
AXIOMORDER = [16, 17, 3, 18, 4, 7, 8, 9, 11, 5, 12, 13, 14, 2, 15, 0, 1, 6, 10, 19]
CNAMES = ['DET', 'GEN', 'B1', 'B2', 'B3', 'B4', 'B6b', 'B8b', 'B6a', 'B6b', 'B6c', 'B7', 'B8a', 'B8b', 'B8c',
          'EXT', 'REP', 'POW', 'UNI', 'INF']

def clauses():
    import sys; sys.path.insert(0, str(HERE / 'tools'))
    from prog_flat import expand
    flat = [int(e.split()[1]) for e in expand('ENode 0')]
    assert flat[17] == 235 and flat[-1] == 58
    body = flat[18:-1]; segs = []; cur = []
    for n in body:
        cur.append(n)
        if n == 236: segs.append(cur); cur = []
    assert not cur and len(segs) == 20
    cl = {}
    for c, seg in zip(AXIOMORDER, segs):
        assert cl.get(c, seg) == seg; cl[c] = seg
    out = ['Definition CL (c : nat) : list edge :=', '  match c with']
    for c in range(20):
        items = '; '.join(NAMES.get(n, f'ENode {n}') for n in cl[c])
        out.append(f'  | {c if c < 19 else "_"} => (* {CNAMES[c]} *) [{items}]')
    out.append('  end.')
    pre = '; '.join(f'ENode {n}' for n in flat[:17])
    out.append(f'Definition prefix : list edge := [{pre}].')
    return chr(10).join(out)

def wrap(s):
    return s if s == 'm' else f'({s})'

def replace_region(src, tag, body):
    a = f'(* BEGIN GENERATED {tag} *)\n'; b = f'(* END GENERATED {tag} *)'
    i = src.index(a) + len(a); j = src.index(b)
    return src[:i] + body + '\n' + src[j:]

if __name__ == '__main__':
    p = HERE / 'coq' / 'ProgLib.v'
    src = p.read_text(encoding='utf-8')
    src = replace_region(src, 'loops', loops())
    ws = re.findall(r'Lemma (w\d+) m', loops())
    body = 'Ltac elem_w := match goal with' + chr(10)
    body += ''.join('  | |- sem (ENode %s) _ _ _ => apply %s' % (w[1:], w) + chr(10) for w in ws) + '  end.'
    src = replace_region(src, 'elem_w', body)
    src = replace_region(src, 'clauses', clauses())
    p.write_text(src, encoding='utf-8', newline='\n')
