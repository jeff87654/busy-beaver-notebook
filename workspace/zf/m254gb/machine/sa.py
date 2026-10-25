"""Simulated-annealing (sa.py) / hill-climbing search over structural options and role labels for an NG' family.

Usage: python hc.py <module> <builder> <worker> <seconds> [labels=0..7] [fix=k=v,...]
Writes runs/hc_<module>_<worker>.jsonl (every improvement) and prints the best.
"""
import sys, os, json, random, time, importlib, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ngdsl

def main():
    if os.name == 'nt':
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
    modname, bname, wk, secs = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
    labels = list(range(0, 8))
    fixed = {}
    for a in sys.argv[5:]:
        if a.startswith('labels='):
            lo, hi = a[7:].split('..'); labels = list(range(int(lo), int(hi) + 1))
        if a.startswith('fix='):
            for kv in a[4:].split(','):
                k, v = kv.split('='); fixed[k] = int(v)
    mod = importlib.import_module(modname)
    build = getattr(mod, bname)
    rng = random.Random(1000 + wk)
    name = f'sa_{modname}_{wk}'
    out = open(os.path.join(HERE, 'runs', f'{name}.jsonl'), 'a')

    def evaluate(o, lab):
        f = build(o)
        if not ngdsl.check(f, lab): return None
        st = ngdsl.compile_tokens(ngdsl.bundle_tokens(ngdsl.rpn(f, lab), o.get('place', 'after')), name)
        return st

    seed = None
    for a in sys.argv[5:]:
        if a.startswith('seed='):
            import glob
            rs = [json.loads(l) for fn in glob.glob(a[5:]) for l in open(fn)]
            seed = min(rs, key=lambda r: r['states'])
    def fresh_start():
        if seed is not None and rng.random() < 0.7:
            o = dict(mod.DEFAULT); o.update(seed['o']); o.update(fixed)
            lab = dict(seed['lab'])
            for r in ngdsl.roles(build(o)):
                if r not in lab: lab[r] = rng.choice(labels)
            if ngdsl.check(build(o), lab): return o, lab
        o = dict(mod.DEFAULT)
        if wk % 2 == 1:
            for k, n in mod.OPTS.items(): o[k] = rng.randrange(n)
        o.update(fixed)
        f = build(o)
        rs = ngdsl.roles(f)
        lab = ngdsl.greedy_labels(f, order=rng.sample(rs, len(rs)) if wk % 3 else None,
                                  labels=labels, rng=rng if wk % 3 == 2 else None)
        return o, lab

    t0 = time.time()
    best_all = None
    while time.time() - t0 < secs:
        o, lab = fresh_start()
        cur = evaluate(o, lab)
        stale = 0
        while cur is not None and stale < 3000 and time.time() - t0 < secs:
            o2, lab2 = dict(o), dict(lab)
            if rng.random() < 0.35:
                k = rng.choice([k for k in mod.OPTS if k not in fixed])
                o2[k] = rng.randrange(mod.OPTS[k])
                f2 = build(o2)
                for r in ngdsl.roles(f2):        # roles new to this structure
                    if r not in lab2: lab2[r] = rng.choice(labels)
            else:
                f2 = build(o2)
                rs = ngdsl.roles(f2)
                for _ in range(rng.choice([1, 1, 1, 2, 3])):
                    lab2[rng.choice(rs)] = rng.choice(labels)
            if not ngdsl.check(build(o2), lab2):
                stale += 1; continue
            st = evaluate(o2, lab2)
            if st is None: stale += 1; continue
            T = max(0.05, 2.5 * (1 - (time.time() - t0) / secs))
            if st <= cur or rng.random() < math.exp(-(st - cur) / T):
                stale = 0 if st < cur else stale + 1
                if best_all is None or st < best_all:
                    best_all = st
                    out.write(json.dumps({'states': st, 'o': o2, 'lab': lab2}) + '\n'); out.flush()
                    print('best', st, flush=True)
                o, lab, cur = o2, lab2, st
            else:
                stale += 1
        if cur is not None and (best_all is None or cur < best_all):
            best_all = cur
            out.write(json.dumps({'states': cur, 'o': o, 'lab': lab}) + '\n'); out.flush()
    print('done best', best_all)

if __name__ == '__main__':
    main()
