"""Measure logic-level template variants inside Wade's unchanged framework (import ext zf2.py read-only)."""
import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\ext\turing_machine_explorer')
import zf2 as Z
ORDER=[16, 17, 3, 18, 4, 7, 8, 9, 11, 5, 12, 13, 14, 2, 15, 0, 1, 6, 10, 19]
def count(cls, order=ORDER):
    m=cls(); m.debug=False; m.AXIOMORDER=order; m.build_machine()
    st=set(s[0] for s in m.tm.states); fw=len([s for s in st if s[0].isdigit()]); return fw, len(st)-fw, len(st)
def climb(cls, order):
    best=count(cls, order)[2]; changed=True
    while changed:
        changed=False
        n=len(order)
        for mid in range(1,n):
            for left in range(mid):
                for right in range(mid+1,n+1):
                    new=order[:left]+order[mid:right]+order[left:mid]+order[right:]
                    if new[-1] in (0,1): continue
                    c=count(cls,new)[2]
                    if c<best: best=c; order=new; changed=True
    return best, order
class Distinctor(Z.ZF2):
    def axioms(self):
        a=super().axioms()
        p1,p2,p3=self.par1(),self.par2(),self.par3()
        weq,wel,wim,wn,wal,wa,sel=self.weq(),self.wel(),self.wim(),self.wn(),self.wal(),self.wa(),self.select()
        D1=[p3,p3,p1,weq,wal,wn]; D2=[p3,p3,p2,weq,wal,wn]
        C1=[p1,p2,weq,p3,p1,p2,weq,wal,wim]; C2=[p1,p2,wel,p3,p1,p2,wel,wal,wim]
        a[8]=D1+D2+C1+C2+[wa,wim,wim,sel]
        return a
class PowUni(Z.ZF2):
    def axioms(self):
        a=super().axioms()
        v0,v1,v2,v3=self.v_0(),self.v_1(),self.v_2(),self.v_3()
        wel,wim,wn,wal,wa,wex,sel=self.wel(),self.wim(),self.wn(),self.wal(),self.wa(),self.wex(),self.select()
        # E. v1 A. v2 ( ( A. v3 ( v3 e. v2 -> v3 e. v0 ) \/ E. v3 ( v2 e. v3 /\ v3 e. v0 ) ) -> v2 e. v1 )
        # P \/ Q = ( -. P -> Q )
        sub=[v3,v3,v2,wel,v3,v0,wel,wim,wal]          # A. v3 (v3 e. v2 -> v3 e. v0)
        uni=[v3,v2,v3,wel,v3,v0,wel,wa,wex]           # E. v3 (v2 e. v3 /\ v3 e. v0)
        a[17]=[v1,v2]+sub+[wn]+uni+[wim,v2,v1,wel,wim,wal,wex,sel]
        a[18]=[v0,sel]  # stub (dropped axiom): v0 then select
        return a
class Inf2(Z.ZF2):
    def axioms(self):
        a=super().axioms()
        v0,v1,v2,v3=self.v_0(),self.v_1(),self.v_2(),self.v_3()
        wel,weq,wim,wn,wal,wa,wex,sel=self.wel(),self.weq(),self.wim(),self.wn(),self.wal(),self.wa(),self.wex(),self.select()
        # E. v1 ( v0 e. v1 /\ A. v0 ( v0 e. v1 -> E. v2 ( v2 e. v1 /\ ( v0 e. v2 /\ A. v1 ( v1 e. v2 -> v1 = v0 ) ) ) ) )
        inner=[v0,v2,wel, v1,v1,v2,wel,v1,v0,weq,wim,wal, wa]
        a[19]=[v1,v0,v1,wel, v0,v0,v1,wel, v2,v2,v1,wel]+inner+[wa,wex,wim,wal,wa,wex,sel]
        return a
if __name__=='__main__':
    print('base', count(Z.ZF2))
    for name,cls in [('B6a distinctor',Distinctor),('POW+UNI merged',PowUni),('INF subset form',Inf2)]:
        c=count(cls); print(name, 'fixed order', c)
        if len(sys.argv)>1: print(name,'climbed',climb(cls,ORDER))
