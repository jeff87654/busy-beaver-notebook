# bnc.py: translated-cycle validator. cfg = Q| pre X^n suf (head at left end). For each n in range, run events (Q,side)
# until a config pre X^m suf appears again (exact pre/suf); report m-n, steps.
import sys,re
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s2')
from val import probe, expand
def cycle(m,Q,side,pre,X,suf,n,maxev=400):
    pat=re.compile('^'+pre+'((?:'+X+')*)'+suf+'0*$')
    R=pre+X*n+suf; L=''; tot=0
    for ev in range(maxev):
        r=probe(m,Q,side,[f'{Q} {L}|{R}'])[0]
        if r[0]!='S': return (r[0],ev)
        tot+=r[1]; L=r[2].lstrip('0'); R=r[4]
        if side=='L' and L: return ('L?',ev)
        g=pat.match(R)
        if g: return (len(g.group(1))//len(X)-n, ev+1, tot)
    return ('noret',)
if __name__=='__main__':
    m,Q,pre,X,suf,a,b=sys.argv[1:8]
    from collections import Counter
    c=Counter(); ex=[]
    for n in range(int(a),int(b)):
        r=cycle(m,Q,'L',expand(pre),expand(X),expand(suf),n)
        c[r[:2]]+=1
        if len(ex)<3: ex.append((n,r))
    print(m,dict(c),ex)
