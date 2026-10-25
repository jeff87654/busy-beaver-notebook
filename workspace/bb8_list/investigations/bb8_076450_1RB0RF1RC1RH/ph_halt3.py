import planner8 as P, pext, loops
loops.STOP_SYMBOLIC=True
BL=P.BLANK
def run(blk,v,c=1): return [('run',tuple(blk),((v,c),))]
P2=[0,0,0,1,0,1,0,1,0,1,0,0,1,0,1,1]
M=[loops.m_TA, loops.m_TB, pext.m_concrete, pext.m_sweep]
seg=('H', run((1,0,1,0),'m') + [0,1,1,0]*2 + P2 + [BL], [0,1,0,0,BL], '>')
for it in range(6):
    sc,e=P.drive('seg%d'%it, seg, 'HALT', matchers=M, maxev=3000, verbose=False)
    print('seg%d'%it, 'start', P.show(seg)[:300])
    print('   ops', len(sc), 'last', sc[-1][:2], sc[-1][2][:3] if sc[-1][0]=='stop' else '')
    if sc[-1][0]!='stop': print('   END', P.show(e)[:300]); break
    kind,kstr,mstr,m0,mr,k0,kr,i,j = sc[-1][2]
    q,L,R,mode=e
    print('   at', P.show(e)[:300])
    # build next start: output run with concrete part and fresh var
    blk = (0,1,0,1) if kind=='TA' else (1,0,1,0)
    conc = m0 + 6*k0
    fresh = 'n%d'%it
    rest = ([0,0,1,0] + L[j:]) if kind=='TA' else L[j:]
    seg = (q, [x for _ in range(conc) for x in blk] + run(blk, fresh) + rest, R, mode)
