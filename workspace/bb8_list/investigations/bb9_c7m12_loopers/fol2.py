"""fol2.py: mini-follower for 9-state c7m12 machines (C7 family: BB(7) champion engine, K-moment = state B on the
blank right of ...1 11001, accumulator offset E = 2), with per-stage slot usage and the stage start configurations.
Same stage/jump loop as halt_redirect/mf/ord_run.follow (literal stage35g.exe stage to a K-moment whose champion
process is big, then follow2.jump = abstract R1-R3 to the next event; new huge accumulators -> representative
LB + (R - LB mod 2520) [std]).  Records for each stage: start word/head/state, used-slot mask, K tokens, event,
zeros (= the list the jump clears), new reps.
  python fol2.py MACHINE [--b0 6] [--stages 30] [--maxs 1e8] [--start "0^2 1^89 1 20"] [--slope] [--json F]
--slope: at every stage whose input carries a fresh huge accumulator r, rerun the literal stage with r + 42 (b + 14)
and print the change of the K-moment token count and of the near zero run (slope ~ 4/3 per unit of r: the next cleared
list ~ accumulator: f_(omega+1) shape; 0: fixed)."""
import sys, argparse, threading, subprocess, json
HR = r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect'
sys.path.insert(0, HR + '/c7'); sys.path.insert(0, HR + '/mf')
import c7fam, mf35, mf35g
from follow2 import Aff, Fail, jump
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
STAGE = HR + '/mf/stage35g.exe'
SL = ['A0','A1','B0','B1','C0','C1','D0','D1','E0','E1','F0','F1','G0','G1','H0','H1','I0','I1','J0','J1']
Q, SUF, E = 'B', '11001', 2
LB, MM = 20, 2520
_sv = None


def server():
    global _sv
    if _sv is None or _sv.poll() is not None:
        _sv = subprocess.Popen([STAGE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
                               creationflags=LOW)
    return _sv


def stage(m, word, head, state, maxs, rcap=600):
    sv = server(); maxw = 4 * len(word) + 20000
    sv.stdin.write(f"{m} {state} {head} {int(maxs)} {maxw} {rcap} {'ABCDEFGHIJ'.index(Q)} {SUF} {E}\n{word}\n")
    sv.stdin.flush()
    line = sv.stdout.readline().strip()
    out, sep, u = line.rpartition(' | U=')
    if not sep:
        raise RuntimeError(f'stage35g output not understood: {line[:200]}')
    return out, int(u, 16)


def pad(m):
    while m.count('_') < 9:
        m += '_------'
    return m


def undef_slots(m):
    p = pad(m).split('_')
    return [SL[2 * q + c] for q in range(9) for c in range(2) if p[q][3 * c] == '-']


def rle(v):
    out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]:
            j += 1
        out.append(f'{v[i]}^{j-i}' if j - i > 1 else str(v[i])); i = j
    return ' '.join(out)


def expand(s):
    v = []
    for t in s.split():
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        else:
            v.append(int(t))
    return v


def parseJ(out):
    parts = out.split('|')
    if len(parts) < 2:
        raise RuntimeError(f'bad J line {out[:200]}')
    toks = [int(x) for x in parts[1].split()]
    far = parts[2].strip() if len(parts) > 2 else ''
    return toks, far


def do_jump(toks):
    digits = toks[2:][::-1]
    ent = []
    for x in digits:
        if ent and ent[-1][1] == x:
            ent[-1][2] += 1
        else:
            ent.append(['D', x, 1])
    left = [('D', Aff(x), Aff(c)) for _, x, c in ent] + [('D', Aff(toks[1]), Aff(1)), ('D', Aff(toks[0]), Aff(1))]
    items, newp, info = jump(left, [], {}, E)
    vals = {p: mf35.rep(v, MM, LB) for p, v in newp.items()}
    new = []
    for e in items:
        x = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
        c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
        new += [x] * c
    if len(new) >= 2 and new[-1] > 2000:
        new[-1] = LB + ((new[-1] - LB) % MM)
    nz = 0
    for x in new[:-2][::-1]:
        if x != 1:
            break
        nz += 1
    return new, vals, info, nz


def near_zeros(toks):
    """zeros (token 1) next to a/r at a K-moment: the list the next borrow would cross"""
    nz = 0
    for x in toks[2:]:
        if x != 1:
            break
        nz += 1
    return nz


def follow(m, word, head, state, stages=30, maxs=1e8, slope=False, log=print):
    m = pad(m); hist = []
    used = 0
    for s in range(stages):
        out, u = stage(m, word, head, state, maxs)
        used |= u
        rec = {'s': s, 'start': [word, head, state], 'U': u}
        f = out.split()
        if not f:
            rec['kind'] = 'FAIL'; hist.append(rec); log(f'{s} FAIL'); break
        if f[0] == 'H':
            rec.update(kind='H', step=int(f[1]), slot=f[2] + f[3], ones=int(f[4]))
            hist.append(rec); log(f'{s} HALT {f[2]}{f[3]} step={f[1]} ones={f[4]}'); break
        if f[0] in ('T', 'W'):
            rec.update(kind=f[0], step=int(f[1])); hist.append(rec); log(f'{s} {f[0]} {f[1]}'); break
        if f[0] != 'J':
            raise RuntimeError(f'unexpected stage output {out[:200]}')
        toks, far = parseJ(out)
        digits = toks[2:][::-1]
        rec.update(kind='J', step=int(f[1]), K=rle(digits) + f' | a={toks[1]} r={toks[0]}', far=len(far),
                   ntok=len(toks), nzK=near_zeros(toks))
        msg = f'{s} K(step {f[1]}, far {len(far)}b): {rle(digits)} | a={toks[1]} r={toks[0]}'
        if slope and hist and hist[-1].get('next_alt'):
            w0, h0, q0 = hist[-1]['next_alt']
            out2, _ = stage(m, w0, h0, q0, maxs)
            if out2.split()[0] == 'J':
                t2, _f2 = parseJ(out2)
                rec['slope'] = (len(t2) - len(toks), near_zeros(t2) - near_zeros(toks))
                msg += f'  [r+42: tokens {len(t2) - len(toks):+d}, near zeros {near_zeros(t2) - near_zeros(toks):+d}]'
            else:
                msg += f'  [r+42: {out2[:40]}]'
        log(msg)
        try:
            new, vals, info, nz = do_jump(toks)
        except (Fail, AssertionError, RuntimeError, RecursionError) as ex:
            rec['kind'] = 'JUMPFAIL'; rec['err'] = str(ex)[:200]; hist.append(rec); log(f'{s} JUMPFAIL {ex}'); break
        rec.update(ev=info.get('event'), zeros=nz, level=info.get('level'), newr=vals)
        log(f'{s} J: ev={info.get("event")} cleared_zeros={nz} lvl={info.get("level")} newr={vals} -> '
            f'{rle(new[:-2])} | a={new[-2]} r={new[-1]}')
        word = far + mf35.word_of_tokens(new) + SUF
        head, state = len(word), Q
        if vals and new[-1] in vals.values():
            alt = new[:-1] + [new[-1] + 42]
            w2 = far + mf35.word_of_tokens(alt) + SUF
            rec['next_alt'] = [w2, len(w2), Q]
        hist.append(rec)
    usedl = [SL[i] for i in range(20) if used >> i & 1]
    return hist, usedl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('machine'); ap.add_argument('--b0', type=int, default=6); ap.add_argument('--stages', type=int, default=30)
    ap.add_argument('--maxs', type=float, default=1e8); ap.add_argument('--start', default=None)
    ap.add_argument('--slope', action='store_true'); ap.add_argument('--log', default=None); ap.add_argument('--json', default=None)
    a = ap.parse_args()
    lf = open(a.log, 'w') if a.log else None

    def log(x):
        print(x, flush=True)
        if lf:
            lf.write(x + '\n'); lf.flush()
    toks = expand(a.start) if a.start else [0, 0] + [1] * 12 + [3 * a.b0 + 2]
    w = mf35.word_of_tokens(toks) + SUF
    log(f'# {a.machine} undefined={undef_slots(a.machine)} b0={a.b0} start={a.start or "K(0^11;0;b0)"}')
    sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
    res = []
    t = threading.Thread(target=lambda: res.append(follow(a.machine, w, len(w), Q, a.stages, a.maxs, a.slope, log)))
    t.start(); t.join()
    if not res:
        log('RESULT CRASH'); return
    hist, usedl = res[0]
    last = hist[-1]['kind'] if hist else 'NONE'
    log(f'RESULT {last} stages={len(hist)} used={",".join(usedl)} '
        f'undefined_used={[x for x in undef_slots(a.machine) if x in usedl]}')
    if a.json:
        json.dump({'machine': a.machine, 'b0': a.b0, 'hist': hist, 'used': usedl}, open(a.json, 'w'))


if __name__ == '__main__':
    main()
