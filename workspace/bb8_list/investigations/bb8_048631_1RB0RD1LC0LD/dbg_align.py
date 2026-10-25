import pickle
import planner9 as P
import fam9 as F
SC = pickle.load(open('rounds.pkl', 'rb'))
P.LEMMAS.update(pickle.load(open('lemmas.pkl', 'rb')))
tpl, start, script, got, tnext = SC['A']
# replay with verbose to see configs around the align
import io, contextlib
orig_align = P.align
def align(cfg):
    r = orig_align(cfg)
    if r:
        print('ALIGN at', P.show(cfg)[-300:])
        print('   L tail', cfg[1][-12:])
    return r
P.align = align
from planner9 import C
tgt = F.PB(C(0, z=1), C(5, y=1), C(4083, x=27))
P.drive_until_string2('RA', start, tgt, matchers=[F.m_TL])
