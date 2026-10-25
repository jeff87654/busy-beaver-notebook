import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
from bcfg import BASES, T
import fit7

def make_tnew(tag):
    t = T(tag)
    B0 = BASES[tag][2]
    S_new = t['s'] + t['u'] * (t['alB'] * B0 + t['beB']) + t['S']
    P_str = t['P'] if t['P'] else '-'
    S_str = S_new if S_new else '-'
    return f"{t['o']},{t['q']},P={P_str},u={t['u']},s={t['s']},d={t['al']}d+{t['be']},b={t['al']}b+{t['be']},S={S_str}"

for tag in sorted(BASES):
    tn = make_tnew(tag)
    R, err = fit7.fit(BASES[tag][0], tn)
    print(f"Base {tag}: {tn} -> {'OK' if R else err}")
