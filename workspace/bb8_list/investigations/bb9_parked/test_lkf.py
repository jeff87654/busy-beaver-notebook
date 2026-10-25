"""test_lkf.py: round-trip tests of the cell-atom <-> Ligocki block conversion used by lkf.py"""
import sys, random, importlib.util, argparse
spec = importlib.util.spec_from_file_location('lkf', 'lkf.py'); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
def cells(at): return ''.join(p * c for p, c in at)
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
for bs in (2, 6):
    bad = 0
    for trial in range(3000):
        at = [(random.choice(['10', '1', '0', '101', '11111100', '1001', '01', '011', '100']), random.choice([1, 2, 3, 5, 40, 77, 300])) for _ in range(random.randint(1, 7))]
        at = L.norm(at)
        Lc = L.alen(at); pad = (-Lc) % bs
        at2 = L.norm([('0', pad)] + at)
        try:
            blocks = L.to_blocks(at2, bs)
        except RuntimeError as e:
            continue
        back = ''.join(b * n for b, n in blocks)
        if back != cells(at2):
            bad += 1
            if bad < 4: print('MISMATCH bs', bs, at, blocks[:6])
    print('bs', bs, 'mismatches', bad)
