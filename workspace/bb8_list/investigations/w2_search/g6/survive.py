"""survive.py: does any far-left bit pattern survive G6's left event with the standard repack?
For every pattern F (starting with 1, length <= L) and gap g, run one literal stage of G6 from F + 0^g + [1^30|1|19]
and classify: STD (tokens = G6's repack 6^16 8 1^98 | 1 | 2, record far bits), OTHER tokens, HALT/T/W."""
import sys, itertools, collections
sys.path.insert(0, '.')
import g6lib
G6 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_1RJ1LA_1LI---'
L = int(sys.argv[1]) if len(sys.argv) > 1 else 8
ref, _ = g6lib.stage(G6, '1^30 1 19')
refk = g6lib.key(ref)
print('ref', refk)
cnt = collections.Counter(); keep = []
for n in range(1, L + 1):
    for bits in itertools.product('01', repeat=n - 1):
        F = '1' + ''.join(bits)
        for g in range(1, 7):
            out, _ = g6lib.stage(G6, '1^30 1 19', far=F + '0' * g, maxs=3_000_000)
            f = out.split()
            if f[0] != 'J':
                cnt[f[0]] += 1; continue
            parts = out.split('|'); toks = [int(x) for x in parts[1].split()]; far = parts[2].strip()
            if toks == [int(x) for x in ref.split('|')[1].split()]:
                cnt['STD far' if far else 'STD clean'] += 1
                if far: keep.append((F, g, far))
            else:
                cnt['OTHER'] += 1
print(cnt)
for k in keep[:30]: print(k)
