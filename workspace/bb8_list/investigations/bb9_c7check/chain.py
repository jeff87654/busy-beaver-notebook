# chain.py: run C7 phase by phase with the exact macro simulator (c7m90); at every CL apply the record's rule
#   Kt(ctx, X, 1^k; 1; r; t) -> Kt(ctx, 1^(k+1); 1; 3R+2; t)   with R from a policy (list, then default).
# Counter acceleration (like wsim R4.c, only with cnt=True): when three consecutive CLs have the same X, k, t and the
# same ctx except its last token C, which drops by 3 each time, set C := 6 + C mod 3 (the last rounds run literally).
import idle, sys
from gm import run
def split_ctx(ctx):
    items = ctx.split() if ctx else []
    if items and '*' in items[-1] and not items[-1].startswith('('):
        v, c = items[-1].split('*'); c = int(c)
        items = items[:-1] + ([f'{v}*{c-1}'] if c > 2 else [v]) + [v]
    return items
def chain(kt, Rlist, Rdef, maxcl=10**9, log=print, stop=None, cnt=True, multi=True):
    i = 0; hist = []
    while i < maxcl:
        r = run(kt)
        if r['kind'] != 'CL':
            log(f'END {r["kind"]} ' + (f'{r["state"]} ones={r["ones"]} step={r["step"]} | {r["tape"][:800]}' if r['kind'] == 'HALT' else str(r)))
            hist.append(r); return hist
        R = Rlist[i] if i < len(Rlist) else Rdef(i, r)
        i += 1
        items = split_ctx(r['ctx'])
        log(f'J{i} r_in={r["r_in"]} t={r["t"]} k={r["k"]} X={r["X"]} C={r["C"]} R={R} | {r["view"][:800]}')
        hist.append(dict(r, items=items))
        if stop and stop(r): return hist
        if cnt and len(hist) >= 3:
            a, b, c = hist[-3], hist[-2], hist[-1]
            try:
                ok = all(h['kind'] == 'CL' for h in (a, b)) and a['X'] == b['X'] == c['X'] and a['k'] == b['k'] == c['k'] and a['t'] == b['t'] == c['t'] \
                     and a['items'][:-1] == b['items'][:-1] == c['items'][:-1] and int(a['items'][-1]) == int(b['items'][-1]) + 3 == int(c['items'][-1]) + 6 \
                     and int(c['items'][-1]) >= 12
            except (ValueError, KeyError, IndexError):
                ok = False
            if ok:
                C = int(c['items'][-1]); nc = 6 + C % 3
                items = items[:-1] + [str(nc)]
                log(f'   CNT C={C} -> {nc} ({(C - nc)//3} rounds skipped)')
                hist[-1] = dict(c, items=items)
        kk = r['k'] + 1
        if multi:
            # the digits equal to X directly left of X are cleared next, one CL each (record CDP, any accumulator):
            # clear the whole run at once (each CL turns one digit token into one more zero digit).
            c = 0
            while items:
                last = items[-1]
                if '*' in last and not last.startswith('('):
                    v, n = last.split('*')
                    if v == str(r['X']): c += int(n); items = items[:-1]; continue
                elif last == str(r['X']): c += 1; items = items[:-1]; continue
                break
            if c:
                log(f'   MULTI {c} more digits {r["X"]} cleared (list {kk} -> {kk + c})')
                kk += c
        ctxs = ','.join(items)
        kt = (ctxs + ',' if ctxs else '') + f'1*{kk};1;{3*R+2};{r["t"]}'
    return hist
if __name__ == '__main__':
    kt = sys.argv[1]; Rl = [int(x) for x in sys.argv[2].split(',')] if sys.argv[2] else []; Rd = int(sys.argv[3]); mx = int(sys.argv[4])
    chain(kt, Rl, lambda i, r: Rd, mx, log=lambda s: print(s, flush=True))
