"""d9f.py: follower for 10-state extensions of the D9-counter machine, started from the base's literal halting tape
(state I on a 0, closed form in mkhalt.py).  Same literal-stage server (stage35g, family GH) and abstract jumps
(follow2.jump) as fable/gh_run.py, plus:
  * every stage reports whether slot I0 (the redirect) or a J slot was used (U mask from the server);
  * policy 'switch': new huge accumulators get rep 19+2520*BIGK until a K-moment has more than TH tokens
    (the rebuild), then the standard rep 19 (so rebuilt lists have realistic size, later stages stay cheap);
  * --stop-i0 N: stop when the N-th stage using I0 begins (the run came back to the redirect).
usage: python d9f.py MACHINE A:r [--policy switch] [--bigk 1] [--th 300] [--stages N] [--maxs S] [--stop-i0 2]"""
import sys, os, argparse, re, hashlib, time
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mf35g, mf35
from follow2 import Aff, Fail, jump
from mkhalt import halt_word
from accel import Accelerator
ACCEL = True
FAM = 'GH'; F = mf35g.FAMILIES[FAM]; E = F['E']; LB = 19; MM = 2520
BIGREP = 2539; LOOKTH = 30

def stage(M, word, head, state, maxs, rcap=600):
    sv = mf35g._server()
    q = 'ABCDEFGHIJ'.index(F['Q'])
    sv.stdin.write(f"{M} {state} {head} {maxs} {max(4*len(word)+20000, 30000000)} {rcap} {q} {F['SUF']} {F['E']}\n{word}\n")
    sv.stdin.flush()
    line = sv.stdout.readline().strip()
    out, _, u = line.rpartition(' | U=')
    if not _:
        raise RuntimeError('server output without U mask: ' + line[:200])
    return out, int(u, 16)

def rle(v):
    out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]: j += 1
        out.append(f'{v[i]}^{j-i}' if j - i > 1 else str(v[i])); i = j
    return ' '.join(out)

def cfar(f):
    return re.sub(r'(?:10){4,}', lambda m: f'(10)^{len(m.group())//2}', f)

def follow(M, A, r, policy='switch', bigk=1, th=300, stages=1000, maxs=10**9, stop_i0=0, log=print, word=None):
    if word is None:
        w, h = halt_word(A, r); word, head, state = w, h, 'I'
    else:
        word, head, state = word
    switched = policy == 'std'
    n_i0 = 0
    acc = Accelerator(); voff = 0
    seen = {}
    for s in range(stages):
        out, um = stage(M, word, head, state, maxs)
        flags = ('I0 ' if um >> 16 & 1 else '') + ('J0 ' if um >> 18 & 1 else '') + ('J1 ' if um >> 19 & 1 else '')
        if um >> 16 & 1:
            n_i0 += 1
            if stop_i0 and n_i0 >= stop_i0:
                log(f'{s} STOP_I0 (I0 used in stage {s}, {n_i0}-th time) {flags}'); return 'I0AGAIN', s
        f = out.split()
        if f[0] == 'H':
            log(f'{s} HALT {f[2]}{f[3]} ones={f[4]} step={f[1]} {flags}'); return 'HALT', s
        if f[0] in ('T', 'W'):
            log(f'{s} {f[0]} {out[:100]} {flags}'); return f[0], s
        parts = out.split('|')
        toks = [int(x) for x in parts[1].split()]
        far = parts[2].strip() if len(parts) > 2 else ''
        digits = toks[2:][::-1]
        ntok = len(toks)
        log(f'{s} K: {rle(digits)} | a={toks[1]} r={toks[0]}' + (f' far={cfar(far)}' if far else '') + f' n={ntok} st={f[1]} {flags}')
        if not switched and ntok > th:
            switched = True; log(f'{s} SWITCH to std reps (n={ntok} > {th})')
        ent = []
        for m in digits:
            if ent and ent[-1][1] == m: ent[-1][2] += 1
            else: ent.append(['D', m, 1])
        left = [('D', Aff(m), Aff(c)) for _, m, c in ent] + [('D', Aff(toks[1]), Aff(1)), ('D', Aff(toks[0]), Aff(1))]
        try:
            items, newp, info = jump(left, [], {}, E)
        except (Fail, AssertionError, RuntimeError, RecursionError) as ex:
            log(f'{s} JUMPFAIL {ex}'); return 'FAIL', s
        def build(big):
            vals = {}
            for p, v in newp.items():
                base = mf35.rep(v, MM, LB)
                if v.exact:
                    vals[p] = base
                elif policy == 'look':
                    vals[p] = base + (BIGREP - LB if big else 0)
                elif policy == 'allbig':
                    vals[p] = base + (BIGREP - LB)
                else:
                    vals[p] = base if switched else base + MM * bigk
            new = []
            for e in items:
                m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
                c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
                new += [m] * c
            if (switched or policy == 'look') and len(new) >= 2 and new[-1] > 2000 and not big:
                new[-1] = LB + ((new[-1] - LB) % MM)
            return vals, new
        vals, new = build(False)
        if policy == 'look' and any(not v.exact for v in newp.values()):
            # lookahead: does the next literal stage turn the new huge accumulator into a list?
            w2 = far + mf35.word_of_tokens(new) + F['SUF']
            o2, _ = stage(M, w2, len(w2), F['Q'], maxs)
            if o2.startswith('J'):
                n2 = len(o2.split('|')[1].split())
                if n2 > len(new) + LOOKTH:
                    vals, new = build(True)
                    log(f'{s} LOOK: next stage builds {n2 - len(new)} new tokens from the accumulator; rep -> {BIGREP} class')
        nz = 0
        for m in new[:-2][::-1]:
            if m != 1: break
            nz += 1
        log(f'{s} J: ev={info.get("event")} zeros={nz} newr={",".join(f"{p}={v}" for p, v in vals.items())} '
            f'hd={info.get("huge_depth")} -> {rle(new[:-2])} | a={new[-2]} r={new[-1]}')
        if ACCEL:
            got = acc.push(s, new, far)
            if got:
                k, p, new, dl = got; voff += k * p
                log(f'{s} ACCEL {k} periods of {p} stages (virtual stage {s + voff}); deltas {dl} -> {rle(new[:-2])[:300]} | a={new[-2]} r={new[-1]}')
        word = far + mf35.word_of_tokens(new) + F['SUF']
        head, state = len(word), F['Q']
        key = hashlib.sha1(word.encode()).digest()
        if key in seen:
            log(f'{s} REPCYCLE: configuration of stage {seen[key]} repeats (period {s - seen[key]} actual stages)')
            return 'REPCYCLE', s
        seen[key] = s
    return 'MAXSTAGES', stages

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('machine'); ap.add_argument('Ar')
    ap.add_argument('--policy', default='switch'); ap.add_argument('--bigk', type=int, default=1)
    ap.add_argument('--th', type=int, default=300); ap.add_argument('--stages', type=int, default=1000)
    ap.add_argument('--maxs', type=int, default=10**9); ap.add_argument('--stop-i0', type=int, default=0)
    ap.add_argument('--log', default=None); ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--bigrep', type=int, default=2539, help="policy look: rep of a rebuilt accumulator (= 19 mod 840 or 2520)")
    ap.add_argument('--lookth', type=int, default=30)
    ap.add_argument('--noaccel', action='store_true')
    ap.add_argument('--mm', type=int, default=2520, help='modulus of the standard representatives (2520: rep 19; 5040: 2539; 10080: 7579)')
    a = ap.parse_args()
    A, r = map(int, a.Ar.split(':'))
    _cfg = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'd9f_cfg.json')
    if os.path.exists(_cfg):
        import json
        _c = json.load(open(_cfg))
        if 'max_stages' in _c: a.stages = min(a.stages, int(_c['max_stages']))
    BIGREP = a.bigrep; LOOKTH = a.lookth; ACCEL = not a.noaccel; MM = a.mm
    lf = open(a.log, 'w') if a.log else None
    t0 = time.time()
    def log(s):
        if not a.quiet: print(s, flush=True)
        if lf: lf.write(s + '\n'); lf.flush()
    import threading
    sys.setrecursionlimit(400_000); threading.stack_size(255 * 1024 * 1024)
    box = {}
    def go():
        box['r'] = follow(a.machine, A, r, a.policy, a.bigk, a.th, a.stages, a.maxs, a.stop_i0, log)
    th = threading.Thread(target=go); th.start(); th.join()
    res, s = box.get('r', ('CRASH', -1))
    log(f'RESULT {res} stage={s} time={time.time()-t0:.0f}s')
