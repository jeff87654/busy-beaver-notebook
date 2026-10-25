def rng(s):
    out = []
    for part in s.split(','):
        if '-' in part[1:]:
            a, b = part.split('-', 1); st = 1
            if ':' in b: b, st = b.split(':')
            out += list(range(int(a), int(b) + 1, int(st)))
        else: out.append(int(part))
    return out
