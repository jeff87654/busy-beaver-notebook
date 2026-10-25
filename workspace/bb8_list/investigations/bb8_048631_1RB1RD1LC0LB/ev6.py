from fam_b import *
def normA(cfg):
    q,L,R,mode=cfg
    # [1, run(0,1) k, BL] -> [run (1,0) k+1, BL]
    if len(L)==3 and L[0]==1 and P.is_run(L[1]) and L[1][1]==(0,1) and L[2]==BL:
        return (q,[('run',(1,0),P.cadd(L[1][2],P.cconst(1))),BL],R,mode)
    return cfg
def next_event(cfg,verbose=False,maxev=60):
    L0=cfg[1]
    def tgt(c): return c[0]=='A' and c[1]!=L0 
    script,end=P.drive('ev',cfg,tgt,matchers=[m_loop],maxev=maxev,verbose=verbose,maxlit=100000)
    return script,normA(end)
def run_events(cfg,k,verbose=False):
    print('   ',P.show(cfg))
    for i in range(k):
        try:
            sc,cfg=next_event(cfg,verbose)
        except Exception as e:
            print('ERR',type(e).__name__,e); return
        if sc[-1]==('stuck',): print('STUCK'); print('   ',P.show(cfg)); return
        print(i,P.show(cfg))
if __name__=='__main__':
    L=toks([('01',C(3,n=1))],left=True)
    R=toks([('10',C(2,p=1)),('11',1),('01',C(2,q=1)),('00',1),('10',1),('01',1),('00',1),('10',1)])
    run_events(('A',L,R,'>'),6)
