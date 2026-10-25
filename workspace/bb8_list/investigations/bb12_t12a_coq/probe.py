"""probe.py: run a symbolic start config (VAR far side -> marker word) literally to the next B-form (bsim.run_lit).
next_b(S, vals) -> (steps, view of the word, with the marker shown as 'L|')"""
import sys
sys.path.insert(0, 'ana')
import validate
from view import view
from bsim import run_lit
MK = ''.join(map(str, reversed(validate.MARK))).lstrip('0')

def next_b(S, vals, maxsteps=10**8):
    q, l, h, r = validate.concretize(S, vals)
    assert q == 'H' and h == 0 and not any(r)
    word = ''.join(map(str, reversed(l)))
    word = word[word.find('1'):]
    res = run_lit(word, len(word), 'H', maxsteps=maxsteps)
    if res[0] != 'B':
        return res[:3] + (res[3].replace(MK, 'L|') if len(res) > 3 else '',)
    w = res[1]
    i = w.find(MK)
    pre = ''
    if i >= 0:
        pre = ('<%d>' % i if i else '') + 'L|'; w = w[i + len(MK):]
    return res[2], pre + view(w.lstrip('0'))

def word_of(cfg, vals):
    q, l, h, r = validate.concretize(cfg, vals)
    word = ''.join(map(str, reversed(l)))
    return word[word.find('1'):]

def fast_check(S, T, vals, maxsteps=10**8):
    """True iff the first B-form reached from S equals T (word compare); returns (ok, steps, actual view)"""
    word = word_of(S, vals)
    res = run_lit(word, len(word), 'H', maxsteps=maxsteps)
    if res[0] != 'B':
        return False, res[:3], ''
    want = word_of(T, vals)
    got = res[1]
    ok = got.lstrip('0') == want.lstrip('0')
    return ok, res[2], ('' if ok else next_b(S, vals))
