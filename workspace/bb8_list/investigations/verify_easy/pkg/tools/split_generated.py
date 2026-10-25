"""Split the large generated machine-lemma files into parts that compile in parallel.

    python3 -I tools/split_generated.py SRC DST [--target 6e6] [--min 8e6]

SRC is a package tree (lib/ dev/ k31/ ...), DST a new directory (must not exist).  DST receives a copy of SRC in which
every generated file (header + Lemma ... Qed. blocks only) whose cost is above --min is replaced by

    X.v            the aggregator:  From <Dir> Require Export X_p00 X_p01 ... .
    X_p00.v ...    the parts: X's header, the Requires of the parts holding the lemmas they use, and then X's lemmas,
                   verbatim and in X's order.

so that every other file (which says `From Dev Require Import X`) is unchanged and sees the same lemma names.
Parts are built in waves: wave w holds the lemmas whose longest chain of same-file dependencies has length w, split
into parts of about --target cost units by longest-processing-time packing.  Cost of a lemma = (number of symbolic
steps + 1) x (length of its statement); on the shared 16-core machine at Idle priority one unit is about 5.5e-5 s
(fit over all 26 generated files, +-15%).  The split changes no statement and no proof script.
"""
import argparse, math, os, re, shutil, sys

LEM = re.compile(r'^(Lemma|Theorem)\s+([A-Za-z0-9_\']+)', re.M)
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_']*")
LOGICAL = {'lib': 'BB8', 'dev': 'Dev', 'k31': 'K31', 'score': 'Score', 'fgh': 'Fgh', 'm8': 'M8', 'main': 'Main'}


def parse(src):
    ms = list(LEM.finditer(src))
    if not ms:
        return None
    header = src[:ms[0].start()]
    if re.search(r'^\s*(Definition|Fixpoint|Ltac|Notation|Section|Module|Hint|Local|Global|#\[)', header, re.M):
        return None
    blocks = []
    for i, m in enumerate(ms):
        blk = src[m.start():(ms[i + 1].start() if i + 1 < len(ms) else len(src))]
        if re.search(r'^(?!Lemma|Theorem|Proof|Qed|\s|$)', blk, re.M):
            return None                       # something other than Lemma/Proof/Qed blocks: leave the file alone
        blocks.append((m.group(2), blk))
    return header, blocks


def cost(blk):
    stmt = blk[:blk.find('Proof.')] if 'Proof.' in blk else blk
    steps = sum(int(x) for x in re.findall(r'do (\d+) step', blk)) + 3 * len(re.findall(r'\bexecute\b', blk)) + 1
    return steps * len(stmt)


def split_file(path, logical, target, header, blocks):
    names = [n for n, _ in blocks]
    S = set(names)
    deps, lvl, c = {}, {}, {}
    for n, blk in blocks:
        proof = blk[blk.find('Proof.'):] if 'Proof.' in blk else ''
        deps[n] = (set(IDENT.findall(proof)) & S) - {n}
        lvl[n] = 1 + max((lvl[d] for d in deps[n]), default=-1)   # file order is a topological order
        c[n] = cost(blk)
    base = os.path.splitext(os.path.basename(path))[0]
    parts = []                                                     # (wave, [names])
    for w in range(max(lvl.values()) + 1):
        xs = sorted((n for n in names if lvl[n] == w), key=lambda n: -c[n])
        k = max(1, round(sum(c[n] for n in xs) / target))
        bins = [[0, []] for _ in range(k)]
        for n in xs:                                               # LPT packing
            b = min(bins, key=lambda b: b[0]); b[0] += c[n]; b[1].append(n)
        for _, ns in bins:
            if ns:
                parts.append((w, ns))
    where = {}
    pname = []
    for i, (w, ns) in enumerate(parts):
        pname.append('%s_p%02d' % (base, i))
        for n in ns:
            where[n] = i
    order = {n: i for i, n in enumerate(names)}
    blk_of = dict(blocks)
    out = {}
    for i, (w, ns) in enumerate(parts):
        need = sorted({where[d] for n in ns for d in deps[n]} - {i})
        assert all(j < i for j in need)
        req = ''.join('From %s Require Import %s.\n' % (logical, pname[j]) for j in need)
        body = ''.join(blk_of[n] for n in sorted(ns, key=order.get))
        out[pname[i] + '.v'] = ('(** Part %d of %s.v (wave %d), split by tools/split_generated.py: the lemmas are %s.v\'s, '
                                'verbatim. *)\n' % (i, base, w, base)) + header + req + '\n' + body
    agg = ('(** %s.v, split by tools/split_generated.py into %d parts (%s_p00 .. %s_p%02d) that compile in parallel;\n'
           '    the lemmas, their statements and proofs are those of the original file, verbatim. *)\n'
           'From %s Require Export %s.\n') % (base, len(parts), base, base, len(parts) - 1, logical, ' '.join(pname))
    # estimated critical path (cost units) through the parts
    pc = [sum(c[n] for n in ns) for _, ns in parts]
    crit = []
    for i, (w, ns) in enumerate(parts):
        need = {where[d] for n in ns for d in deps[n]} - {i}
        crit.append(pc[i] + max((crit[j] for j in need), default=0))
    return out, agg, len(parts), sum(pc), max(crit), max(pc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('dst')
    ap.add_argument('--target', type=float, default=6e6)
    ap.add_argument('--min', type=float, default=8e6)
    a = ap.parse_args()
    if os.path.exists(a.dst):
        sys.exit('%s exists' % a.dst)
    shutil.copytree(a.src, a.dst, ignore=shutil.ignore_patterns('*.vo', '*.vok', '*.vos', '*.glob', '.*.aux',
                                                                '_verify', '_busycoq', 'Makefile.coq*', '_CoqProject',
                                                                '.lia.cache', '.nia.cache'))
    U = 5.5e-5
    print('%-18s %6s %10s %10s %10s' % ('file', 'parts', 'total s', 'crit s', 'max part s'))
    for d in sorted(LOGICAL):
        dd = os.path.join(a.dst, d)
        if not os.path.isdir(dd):
            continue
        for f in sorted(os.listdir(dd)):
            if not f.endswith('.v'):
                continue
            p = os.path.join(dd, f)
            src = open(p, encoding='utf-8').read()
            r = parse(src)
            if r is None:
                continue
            header, blocks = r
            if sum(cost(b) for _, b in blocks) < a.min:
                continue
            out, agg, k, tot, crit, mx = split_file(p, LOGICAL[d], a.target, header, blocks)
            for name, text in out.items():
                with open(os.path.join(dd, name), 'w', encoding='utf-8', newline='\n') as fh:
                    fh.write(text)
            with open(p, 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(agg)
            print('%-18s %6d %10.0f %10.0f %10.0f' % (d + '/' + f, k, tot * U, crit * U, mx * U))


if __name__ == '__main__':
    main()
