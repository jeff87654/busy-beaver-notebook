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

import json
CFG = json.loads((HERE / 'R3s336.json').read_text())
AXIOMORDER = CFG['order']
CNAMES = CFG['clauses']
# element notations by subroutine name
ENAMES = {'pushwff().0': 'E_v0', 'v_1().0': 'E_v1', 'v_2().0': 'E_v2', 'v_3().0': 'E_v3', 'v_4().0': 'E_v4',
          'par1().0': 'E_par1', 'par2().0': 'E_par2', 'par3().0': 'E_par3', 'weq().0': 'E_weq',
          'wel().0': 'E_wel', 'wim().0': 'E_wim', 'wn().0': 'E_wn', 'wal().0': 'E_wal', 'wex().0': 'E_wex',
          'wa().0': 'E_wa', 'select().0': 'E_select', 'cparam(param1).0': 'E_cparam1',
          'cparam(param2).0': 'E_cparam2', 'cparam(param3).0': 'E_cparam3', 'cparam(scratch3).0': 'E_cparam_s3'}
NAMES = {n: ENAMES[names[n]] for n in names if names[n] in ENAMES}
ATOM_HEADS = {'while_decnz', 'pair', 'unpair', 'cparam', 'if_eq', 'if_not_decnz', 'select', 'pushwff', 'v_1',
              'v_2', 'v_3', 'v_4', 'par1', 'par2', 'par3', 'weq', 'wel', 'wim', 'wal', 'wn', 'wex', 'wa'}

def atom_list():
    out = []
    for n in sorted(nodes):
        m = re.fullmatch(r'(\w+)\(.*\)\.0', names[n])
        if m and m.group(1) in ATOM_HEADS:
            out.append(n)
        elif names[n].startswith('main().') and nodes[n][0].startswith('EDecnz'):
            out.append(n)            # the final halt check
    return out

def atoms():
    return 'Definition atoms : list nat := [' + '; '.join(map(str, atom_list())) + '].'

def flatten(n, A):
    # same flattening as Coq's [expand]: every non-atom node is expanded
    if n in A: return [n]
    out = []
    for e in nodes[n]:
        m = re.fullmatch(r'ENode (\d+)', e)
        assert m, (n, e)
        out += flatten(int(m.group(1)), A)
    return out

def notations():
    return chr(10).join(f'Local Notation {NAMES[n]} := (ENode {n}) (only parsing).' for n in sorted(NAMES, key=lambda n: NAMES[n]))

def clauses():
    import sys; sys.path.insert(0, str(HERE / 'tools'))
    from prog_flat import expand
    A = set(atom_list())
    flat = [x for e in expand('ENode 0') for x in flatten(int(e.split()[1]), A)]
    v0 = next(n for n in NAMES if NAMES[n] == 'E_v0'); sel = next(n for n in NAMES if NAMES[n] == 'E_select')
    k = flat.index(v0)
    body = flat[k + 1:-1]; segs = []; cur = []
    for n in body:
        cur.append(n)
        if n == sel: segs.append(cur); cur = []
    N = len(CNAMES)
    assert not cur and len(segs) == N == len(AXIOMORDER)
    cl = {}
    for c, seg in zip(AXIOMORDER, segs):
        assert cl.get(c, seg) == seg; cl[c] = seg
    out = ['Definition CL (c : nat) : list edge :=', '  match c with']
    for c in range(N):
        items = '; '.join(NAMES.get(n, f'ENode {n}') for n in cl[c])
        out.append(f'  | {c if c < N - 1 else "_"} => (* {CNAMES[c]} *) [{items}]')
    out.append('  end.')
    pre = '; '.join(f'ENode {n}' for n in flat[:k])
    out.append(f'Definition prefix : list edge := [{pre}].')
    out.append(f'Definition check_node : nat := {flat[-1]}.')
    return chr(10).join(out)

def wrap(s):
    return s if s == 'm' else f'({s})'

def replace_region(src, tag, body):
    a = f'(* BEGIN GENERATED {tag} *)\n'; b = f'(* END GENERATED {tag} *)'
    if a not in src:
        return src
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
    src = replace_region(src, 'atoms', atoms())
    src = replace_region(src, 'notations', notations())
    p.write_text(src, encoding='utf-8', newline='\n')
