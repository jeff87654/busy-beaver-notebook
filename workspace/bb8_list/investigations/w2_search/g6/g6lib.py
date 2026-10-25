"""g6lib.py: 13-state (up to 16) versions of the GH-family literal stage runner and the verbose follower.
run_stage(machine, word, head, state, maxs) -> raw stage13 output line (without U), slots read
stage(machine, tokens, far='') -> same from a token configuration (GH family: Q = G, SUF = 1010, E = 1)
follow(machine, b0=6, policy='std'|'big'|'shrink', stages, maxs, log, start=None) -> result kind
Machines are standard-format strings with any number of states (A..P)."""
import sys, subprocess, os, hashlib, threading
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import mf35g, mf35
from follow2 import Aff, Fail, jump
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
STAGE = os.path.join(HERE, 'stage13.exe')
ST = 'ABCDEFGHIJKLMNOP'
Q, SUF, E = 'G', '1010', 1
_LOCAL = threading.local()
_CACHE = {}


def slots_of(machine):
    return [q[i:i + 3] for q in machine.split('_') for i in (0, 3)]


def slot_names(n):
    return [ST[q] + str(s) for q in range(n) for s in (0, 1)]


def _server():
    sv = getattr(_LOCAL, 'sv', None)
    if sv is None or sv.poll() is not None:
        sv = subprocess.Popen([STAGE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
                              creationflags=LOW)
        _LOCAL.sv = sv
    return sv


def run_stage(machine, word, head, state, maxs=50_000_000, rcap=600):
    """returns (out, used-slot-name list); results cached by input + values of the slots read"""
    key = (hashlib.sha1(word.encode()).digest(), head, state, maxs)
    sl = slots_of(machine)
    for mask, vals, out in _CACHE.get(key, ()):
        if all(i < len(sl) and sl[i] == v for i, v in zip(mask, vals)):
            return out, [slot_names(16)[i] for i in mask]
    sv = _server()
    sv.stdin.write(f"{machine} {state} {head} {maxs} {4 * len(word) + 20000} {rcap} {ST.index(Q)} {SUF} {E}\n{word}\n")
    sv.stdin.flush()
    line = sv.stdout.readline().strip()
    out, _, u = line.rpartition(' | U=')
    if not _:
        return line, []
    um = int(u, 16)
    mask = tuple(i for i in range(32) if um >> i & 1)
    if len(_CACHE) > 60000:
        _CACHE.clear()
    _CACHE.setdefault(key, []).append((mask, tuple(sl[i] if i < len(sl) else None for i in mask), out))
    return out, [slot_names(16)[i] for i in mask]


def expand(s):
    v = []
    for t in s.split():
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        else:
            v.append(int(t))
    return v


def rle(v):
    out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]:
            j += 1
        out.append(f'{v[i]}^{j-i}' if j - i > 1 else str(v[i])); i = j
    return ' '.join(out)


def word_of_tokens(toks):
    return ''.join('10' * m + '1' for m in toks)


def stage(machine, tokens, far='', maxs=50_000_000):
    if isinstance(tokens, str):
        tokens = expand(tokens)
    word = far + word_of_tokens(tokens) + SUF
    return run_stage(machine, word, len(word), Q, maxs)


def fmt(out):
    f = out.split()
    if f[0] == 'H':
        return f'HALT {f[2]}{f[3]} ones={f[4]} step={f[1]}'
    if f[0] in ('T', 'W'):
        return out[:60]
    parts = out.split('|'); toks = [int(x) for x in parts[1].split()]; far = parts[2].strip() if len(parts) > 2 else ''
    return f'K: {rle(toks[2:][::-1])} | a={toks[1]} r={toks[0]}' + (f' far={far}' if far else '') + f' step={f[1]}'


def key(out):
    return fmt(out).rsplit(' step=', 1)[0]


def xstart(b):
    return mf35g.xstart('GH', b)


def follow(machine, b0=6, policy='std', stages=80, maxs=200_000_000, bigk=1, log=print, start=None, startfar='',
           hist=None, fixr=None):
    """ord_run.follow with stage13. hist (list) receives (kind, data) records: ('K', digits, a, r, far) per stage,
    ('J', event, zeros, newtokens) per jump, ('H', state+sym, ones). fixr: replace every huge parameter by this."""
    LB = 19; MM = 2520
    if start is not None:
        if isinstance(start, str):
            start = expand(start)
        word = startfar + word_of_tokens(start) + SUF; head, state = len(word), Q
    else:
        word, head, state = xstart(b0)
    for s in range(stages):
        out, used = run_stage(machine, word, head, state, maxs)
        if not out:
            log(f'{s} FAIL no output'); return 'FAIL'
        f = out.split()
        if f[0] == 'H':
            log(f'{s} HALT {f[2]}{f[3]} ones={f[4]} step={f[1]}')
            if hist is not None: hist.append(('H', f[2] + f[3], int(f[4])))
            return 'HALT'
        if f[0] in ('T', 'W'):
            log(f'{s} {f[0]} {out[:100]}'); return f[0]
        parts = out.split('|')
        toks = [int(x) for x in parts[1].split()]
        far = parts[2].strip() if len(parts) > 2 else ''
        digits = toks[2:][::-1]
        log(f'{s} K: {rle(digits)} | a={toks[1]} r={toks[0]}' + (f' far={far}' if far else ''))
        if hist is not None: hist.append(('K', digits, toks[1], toks[0], far))
        ent = []
        for m in digits:
            if ent and ent[-1][1] == m:
                ent[-1][2] += 1
            else:
                ent.append(['D', m, 1])
        left = [('D', Aff(m), Aff(c)) for _, m, c in ent] + [('D', Aff(toks[1]), Aff(1)), ('D', Aff(toks[0]), Aff(1))]
        try:
            items, newp, info = jump(left, [], {}, E)
        except (Fail, AssertionError, RuntimeError, RecursionError) as ex:
            log(f'{s} JUMPFAIL {ex}'); return 'FAIL'
        vals = {}
        for p, v in newp.items():
            base = mf35.rep(v, MM, LB)
            if v.exact:
                vals[p] = base
            elif fixr is not None:
                vals[p] = fixr
            elif policy == 'std':
                vals[p] = base
            else:
                vals[p] = base + MM * bigk
        new = []
        for e in items:
            m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
            c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
            new += [m] * c
        if len(new) >= 2 and new[-1] > 2000 and policy == 'std' and fixr is None:
            new[-1] = LB + ((new[-1] - LB) % MM)
        if policy == 'shrink':
            for i in range(len(new) - 1):
                if new[i] > 2539:
                    new[i] = LB + ((new[i] - LB) % MM)
            if new[-1] > 2000:
                new[-1] = LB + ((new[-1] - LB) % MM) + MM * bigk
        nz = 0
        for m in new[:-2][::-1]:
            if m != 1:
                break
            nz += 1
        log(f'{s} J: ev={info.get("event")} zeros={nz} newr={",".join(f"{p}={v}" for p, v in vals.items())} '
            f'-> {rle(new[:-2])} | a={new[-2]} r={new[-1]}')
        if hist is not None: hist.append(('J', info.get('event'), nz, new))
        word = far + word_of_tokens(new) + SUF
        head, state = len(word), Q
    return 'MAXSTAGES'
