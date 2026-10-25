"""t1enum.py: residue-targeted lazy TNF enumeration of eaters (J0 + new states K,L,M) for Tier 1 (route 3).
Start = round-1 end of n1's real run in the follower world (far_17 + [0 1^329 | 1 | 19], stage-37 input, b0 = 6).
Phase 1: follow until a round restart 'P 2 5 1^c 0^3 9 1^z' (c >= --cmin) with no far bits (c2 = 4R+3+delta).
  Leaves: NORESTART (no restart within --sa stages), HALT1 (undefined slot read before any restart; branched further),
  T/W/JF.  Every restart (any class) is followed into the next phase (no class pruning).
Phase 2+: every other restart is followed (--s2 stages per round) with further branching on unread slots;
  HALT2 / HALT3.. = halt after a full restarted round (TIER-1 CANDIDATE), RESTART again -> next phase.
usage: python t1enum.py --j0 0LK|free --ns 2 [--fix K0=0LC,..] --out x.tsv"""
import sys, threading, argparse, time
from t1lib import N1, stage, far_of, word_of, rsig, rle
ap = argparse.ArgumentParser()
ap.add_argument('--j0', default='free'); ap.add_argument('--j0list', default=''); ap.add_argument('--ns', type=int, default=2)
ap.add_argument('--k', type=int, default=17); ap.add_argument('--n', type=int, default=329); ap.add_argument('--R', type=int, default=19)
ap.add_argument('--sa', type=int, default=16); ap.add_argument('--s2', type=int, default=110)
ap.add_argument('--maxs', type=float, default=2e7); ap.add_argument('--out', required=True); ap.add_argument('--fix', default='')
ap.add_argument('--maxphase', type=int, default=4); ap.add_argument('--kchk', default='29,41'); ap.add_argument('--maxdef', type=int, default=99); ap.add_argument('--cmin', type=int, default=40); ap.add_argument('--keepfree', default=''); ap.add_argument('--stopat', type=int, default=0)
a = ap.parse_args()
NEW = 'KLMN'[:a.ns]
KF = set(x for x in a.keepfree.split(',') if x)

def mstr(sl):
    parts = N1.split('_')
    parts[9] = sl.get('J0', '---') + '0LC'
    for q in NEW:
        parts.append(sl.get(q + '0', '---') + sl.get(q + '1', '---'))
    return '_'.join(parts)

def options(sl):
    used = [q for q in NEW if any(v[2] == q for v in sl.values())]
    nxt = [q for q in NEW if q not in used][:1]
    tg = list('ABCDEFGHIJ') + used + nxt
    return [w + d + q for w in '01' for d in 'LR' for q in tg]

KS = [int(x) for x in a.kchk.split(',') if x]
def kcheck(sl, c):
    """eater from far_k + [0 1^n|1|R] for the extra k's (same class mod 12 as 17): same restart counter?"""
    M = mstr(sl)
    for k in KS:
        word = far_of(k) + word_of([0] + [1] * a.n + [1, a.R]) + '1010'
        res = None
        for st in range(a.sa + 6):
            kind, d = stage(M, word, int(a.maxs))
            if kind == 'H':
                q, sym = d[0], d[1]; slot = f'{q}{sym}'
                if slot in KF: return ('fail', f'k{k}:KF{slot}')
                if (slot == 'J0' or q in NEW) and slot not in sl and len(sl) < a.maxdef: return ('undef', slot)
                res = 'halt'; break
            if kind != 'K': res = kind; break
            toks, far = d[0], d[1]
            s_ = rsig(toks[:-2]) if not far else None
            if s_ and st > 0 and s_[1] >= a.cmin:
                res = 'ok' if s_[1] == c else f'c{s_[1]}'; break
            word = d[2]
        if res != 'ok': return ('fail', f'k{k}:{res}')
    return ('ok', '')

fo = open(a.out, 'w'); nodes = [0]; t0 = time.time(); stats = {}
def leaf(sl, kind, st, ph, info=''):
    stats[kind] = stats.get(kind, 0) + 1
    fo.write(f'{mstr(sl)}\t{kind}\t{st}\t{ph}\t{info}\n'); fo.flush()

def dfs(sl, word, st, ph, lim, hist):
    nodes[0] += 1
    if a.stopat and nodes[0] > a.stopat: return
    if nodes[0] % 200 == 0:
        print('nodes', nodes[0], stats, '%.0fs' % (time.time() - t0), flush=True)
    M = mstr(sl)
    while True:
        if st >= lim:
            leaf(sl, 'NORESTART' if ph == 1 else f'MAX{ph}', st, ph, hist); return
        kind, d = stage(M, word, int(a.maxs))
        if kind == 'H':
            q, sym, steps, ones = d
            slot = f'{q}{sym}'
            if slot in KF and ph == 1:
                leaf(sl, 'KF1', st, ph, f'{slot} {hist}'); return
            leaf(sl, f'HALT{ph}', st, ph, f'{slot} ones={ones} {hist}')
            if slot in KF: return
            if (slot == 'J0' or q in NEW) and slot not in sl and len(sl) < a.maxdef:
                for o in options(sl):
                    s2 = dict(sl); s2[slot] = o
                    dfs(s2, word, st, ph, lim, hist)
            return
        if kind != 'K':
            leaf(sl, kind, st, ph, hist); return
        toks, far, newword, ev, nz, new = d
        s = rsig(toks[:-2]) if not far else None
        if s and st > 0 and s[1] >= a.cmin:
            P, c, z = s
            tag = f'R{ph}:c={c},d={c - 79},c42={c % 42},P={" ".join(map(str, P))},z={z},st={st}'
            h2 = (hist + ' ' + tag).strip()
            if ph == 1 and KS:
                kc = kcheck(sl, c)
                while kc[0] == 'undef':
                    slot = kc[1]
                    for o in options(sl):
                        s2 = dict(sl); s2[slot] = o
                        dfs(s2, word, st, ph, lim, hist)
                    return
                if kc[0] == 'fail':
                    leaf(sl, 'KFAIL', st, ph, h2 + ' ' + kc[1]); return
            if ph >= a.maxphase:
                leaf(sl, f'RESTART{ph}', st, ph, h2); return
            ph += 1; lim = st + a.s2; hist = h2
        word = newword; st += 1

def go():
    if a.j0list:
        for j in a.j0list.split(','):
            sl0 = {'J0': j}
            for kv in filter(None, a.fix.split(',')):
                k_, v_ = kv.split('='); sl0[k_] = v_
            w = far_of(a.k) + word_of([0] + [1] * a.n + [1, a.R]) + '1010'
            dfs(sl0, w, 0, 1, a.sa, '')
            print('DONE J0', j, nodes[0], stats, 'time %.0f' % (time.time() - t0), flush=True)
        return
    w = far_of(a.k) + word_of([0] + [1] * a.n + [1, a.R]) + '1010'
    sl0 = {}
    if a.j0 != 'free': sl0['J0'] = a.j0
    for kv in filter(None, a.fix.split(',')):
        k_, v_ = kv.split('='); sl0[k_] = v_
    dfs(sl0, w, 0, 1, a.sa, '')
    print('DONE nodes', nodes[0], stats, 'time %.0f' % (time.time() - t0), flush=True)
sys.setrecursionlimit(100000); threading.stack_size(128 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
