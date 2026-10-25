"""Like c7mom.py but parses B-at-right moments as  FAR (10)^y 011 (100)^P 1^L 11 (11111100)^t 1001  (D0-like) or
FAR (10)^r 11 (11111100)^t 1001 (Kt-like).  python c7mom2.py 'frame|toks|m|r|t' from to [H0]"""
import idle, sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f3_coq\gen')
from tm import Sim, rle
from c7sim import C7, ktword, parse_toks, view
D0 = re.compile(r'(.*?)((?:10)*)011((?:100)*)(1*)11((?:11111100)*)1001')
KT = re.compile(r'(.*?1)((?:10)*)11((?:11111100)*)1001')
def toks(w):
    # far-first token view of a word made of D-tokens and 0-gaps
    out = []; i = 0; n = len(w)
    while i < n:
        if w[i] == '0':
            j = i
            while j < n and w[j] == '0': j += 1
            out.append('z%d' % (j - i)); i = j; continue
        j = i; x = 0
        while j + 2 < n and w[j + 1] == '0' and w[j + 2] == '1': j += 2; x += 1
        out.append(str(x)); i = j + 1
    comp = []
    for t in out:
        if comp and comp[-1][0] == t: comp[-1][1] += 1
        else: comp.append([t, 1])
    return ' '.join(t if k == 1 else '%s*%d' % (t, k) for t, k in comp)
def desc(w):
    m = D0.fullmatch(w)
    if m:
        return 'D0[far=%s | y=%d P=%d L=%d t=%d]' % (toks(m.group(1)), len(m.group(2)) // 2, len(m.group(3)) // 3, len(m.group(4)), len(m.group(5)) // 8)
    m = KT.fullmatch(w)
    if m:
        return 'KT[%s | r=%d t=%d]' % (toks(m.group(1)), len(m.group(2)) // 2, len(m.group(3)) // 8)
    return 'RAW ' + rle(w)
if __name__ == '__main__':
    frame, tk, m, r, t = sys.argv[1].split('|')
    s = Sim(C7, ktword(frame, parse_toks(tk), int(m), int(r), int(t)), state='B')
    a, b = int(sys.argv[2]), int(sys.argv[3]); h0 = len(sys.argv) > 4
    while s.steps < b:
        if h0 and s.q == 'H' and s.t[s.pos] == 0 and s.steps >= a:
            print('H0 step=%d left=%d' % (s.steps, s.t[s.pos - 1]))
        if not s.step():
            print('HALT', s.steps, view(s)); break
        if s.steps >= a and s.q == 'B' and s.t[s.pos] == 0 and s.t.rfind(1) == s.pos - 1:
            w, lo, rr = s.word()
            print('B> %d %s' % (s.steps, desc(w[lo:rr + 1])))
