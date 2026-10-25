import sys, os, csv, glob
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
OUT_DIR = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_7state_fw1_redirects'
t_str = "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0"
T = kl.tmpl("1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC", t_str)

print("=== 1. ALL E2_HALT MACHINES IN enum_rebE2_9.tsv ===")
with open(os.path.join(OUT_DIR, 'enum_rebE2_9.tsv'), 'r') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        if r['type'] == 'E2_HALT':
            tm = r['machine']
            print(f"  {tm} | {r['redir']} | {r['blank']} | {r['E1_7']} | {r['E1_9']} | {r['E2_7']}")
            for k_zeros in [4, 5]:
                e1_ds = [1] + [0]*k_zeros
                outs = []
                for a in [5, 7, 9, 11]:
                    evs = kl.run(tm, e1_ds, a, 1, steps=50000, nchg=0, maxl=50, T=T, pall=1)
                    nxt = next((e for e in evs[1:] if e[0] == 'H' or (e[0] == 'K' and e[4] == 1 and e[2] != e1_ds)), ('END',))
                    if nxt[0] == 'K':
                        outs.append(f"a={a}:K({short(nxt[2])};{nxt[3]};{nxt[4]})@{nxt[1]}")
                    elif nxt[0] == 'H':
                        outs.append(f"a={a}:H({nxt[2]}{nxt[3]})@{nxt[1]}")
                print(f"    E1(1,0^{k_zeros}; a): {' | '.join(outs)}")

print("\n=== 2. AUDITING c209_plus_dl3.tsv GEMS ===")
dl2_files = sorted(glob.glob(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl2_out\c*.tsv'))
print(f"Latest dl2_out file: {os.path.basename(dl2_files[-1]) if dl2_files else 'none'} (total {len(dl2_files)} files)")

with open(os.path.join(OUT_DIR, 'c209_plus_dl3.tsv'), 'r') as f:
    rows = list(csv.DictReader(f, delimiter='\t'))

interesting = [r for r in rows if r['grade'] in ('CHAMPION', 'MULTI?', 'W1-LOOPER', 'REBUILD', 'HALT-SOME')]
print(f"Auditing {len(interesting)} machines in c209_plus_dl3.tsv:")
for r in interesting:
    tm = r['machine']
    verdict = r['grade']
    t = r['template']
    print(f"  [{verdict:9s}] {tm} | tmpl={t} | w1={r['w1'][:80]} | params={r['params']}")
    if not t or t == '-':
        continue
    T_cur = kl.tmpl(tm, t)
    b_res = kl.blank(tm, steps=200000, maxl=40, T=T_cur)
    max_len = max((len(l[2]) for l in b_res if l[0] == 'K'), default=0)
    first_deep = next((l for l in b_res if l[0] == 'K' and len(l[2]) >= 4), b_res[0] if b_res else None)
    last_l = b_res[-1] if b_res else None
    fd_str = f"K({short(first_deep[2])};{first_deep[3]};{first_deep[4]})@{first_deep[1]}" if (first_deep and first_deep[0] == 'K') else str(first_deep)
    ll_str = f"K({short(last_l[2])};{last_l[3]};{last_l[4]})@{last_l[1]}" if (last_l and last_l[0] == 'K') else str(last_l)
    print(f"              blank: max_len={max_len} | first4+={fd_str} | last={ll_str}")
