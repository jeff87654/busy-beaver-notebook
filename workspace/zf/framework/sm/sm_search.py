"""Simulated annealing over (prefix-code tree shape, axiom -> leaf assignment, param orders,
GEN style) minimising the DAG cell count.  Usage: python -I sm_search.py SEED ITERS
Prints the best configuration as a Python literal (to paste into sm_config.py)."""
import sys, random, math, itertools, json
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\framework\sm')
import sm_prog as P

BASE_PARAMS = {a[0]: a[1] for a in P.AXIOMS}


def codes_of(shape, assign):
    """shape: nested 2-tuples (X, Y) with None leaves; assign: list of axiom names (leaf order)."""
    out = {}
    it = iter(assign)

    def rec(t, pre):
        if t is None:
            out[next(it)] = pre
        else:
            rec(t[0], pre + '1'); rec(t[1], pre + '0')
    rec(shape, '')
    return out


def nleaves(t):
    return 1 if t is None else nleaves(t[0]) + nleaves(t[1])


def random_shape(n, rng):
    if n == 1:
        return None
    k = rng.randrange(1, n)
    return (random_shape(k, rng), random_shape(n - k, rng))


def internal_paths(t, pre=()):
    if t is None:
        return []
    return [pre] + internal_paths(t[0], pre + (0,)) + internal_paths(t[1], pre + (1,))


def get(t, path):
    for p in path:
        t = t[p]
    return t


def put(t, path, v):
    if not path:
        return v
    l = list(t)
    l[path[0]] = put(t[path[0]], path[1:], v)
    return tuple(l)


def mutate_shape(shape, rng):
    paths = internal_paths(shape)
    p = rng.choice(paths)
    node = get(shape, p)
    r = rng.random()
    if r < 0.5:
        new = (node[1], node[0])                     # swap children (changes ones counts)
    else:
        # rotation
        if node[0] is not None and rng.random() < 0.5:
            a, b = node[0]
            new = (a, (b, node[1]))
        elif node[1] is not None:
            a, b = node[1]
            new = ((node[0], a), b)
        else:
            new = (node[1], node[0])
    return put(shape, p, new)


def evaluate(cfg):
    shape, assign, porders, gen = cfg
    for a, o in porders.items():
        P.AXDICT[a] = (a, o, P.AXDICT[a][2])
    try:
        b, n = P.build(codes_of(shape, assign), gen_style=gen)
    finally:
        for a in porders:
            P.AXDICT[a] = (a, BASE_PARAMS[a], P.AXDICT[a][2])
    return n


def shape_of(code):
    inv = {w: a for a, w in code.items()}
    assign = []

    def rec(pre):
        if pre in inv:
            assign.append(inv[pre])
            return None
        return (rec(pre + '1'), rec(pre + '0'))
    return rec(''), assign


def main():
    seed = int(sys.argv[1]); iters = int(sys.argv[2])
    rng = random.Random(seed)
    names = list(P.AXNAMES)
    multi = [a for a in names if len(BASE_PARAMS[a].split()) >= 2]
    T0 = 2.0
    if len(sys.argv) > 3:                       # restart from a config literal (low temperature)
        start = eval(open(sys.argv[3]).read())
        shape, names = shape_of(start['code'])
        cfg = (shape, names, dict(start.get('param_orders', {})), start.get('gen_style', 'inline'))
        T0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6
    else:
        rng.shuffle(names)
        shape = random_shape(len(names), rng)
        cfg = (shape, names, {}, 'inline')
    cur = evaluate(cfg)
    best, bestcfg = cur, cfg
    for it in range(iters):
        T = T0 * (1 - it / iters) + 0.05
        shape, assign, porders, gen = cfg
        r = rng.random()
        if r < 0.45:
            i, j = rng.sample(range(len(assign)), 2)
            assign = list(assign); assign[i], assign[j] = assign[j], assign[i]
        elif r < 0.75:
            shape = mutate_shape(shape, rng)
        elif r < 0.97:
            a = rng.choice(multi)
            ps = BASE_PARAMS[a].split()
            porders = dict(porders); porders[a] = ' '.join(rng.sample(ps, len(ps)))
        else:
            gen = 'param' if gen == 'inline' else 'inline'
        new = (shape, assign, porders, gen)
        n = evaluate(new)
        if n <= cur or rng.random() < math.exp((cur - n) / T):
            cfg, cur = new, n
            if n < best:
                best, bestcfg = n, new
                print(it, best, flush=True)
    shape, assign, porders, gen = bestcfg
    print('BEST', best)
    print(repr({'code': codes_of(shape, assign), 'param_orders': porders, 'gen_style': gen}))


if __name__ == '__main__':
    main()
