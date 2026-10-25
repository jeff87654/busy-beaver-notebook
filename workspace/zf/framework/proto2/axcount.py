# Count postfix tokens per axiom body (primitives: atom=3 tok, im/neg=+1, forall=+2).
# ph/ps/ch are parameter COPIES (not literal tokens); count them separately.
# connectives: imp, neg, all(var,body), eq(a,b), el(a,b), and(a,b), iff(a,b), ex(var,body)
def imp(a,b): return ('imp',a,b)
def neg(a): return ('neg',a)
def alL(v,b): return ('all',v,b)
def exL(v,b): return ('ex',v,b)      # E.x p = -. A.x -.p
def eq(a,b): return ('eq',a,b)
def el(a,b): return ('el',a,b)
def andL(a,b): return ('and',a,b)    # a/\b = -.(a-> -.b)
def iff(a,b): return ('iff',a,b)     # -.((a->b)-> -.(b->a))
PH,PS,CH='ph','ps','ch'
V=lambda i:('v',i)
def lit_and_copies(t):
    """return (literal_tokens, copies)."""
    if t in (PH,PS,CH): return (0,1)
    if isinstance(t,tuple) and t[0]=='v': return (1,0)   # var push
    k=t[0]
    if k in('eq','el'):
        la,ca=lit_and_copies(t[1]); lb,cb=lit_and_copies(t[2])
        return (la+lb+1, ca+cb)            # rel token
    if k=='neg':
        l,c=lit_and_copies(t[1]); return (l+1,c)
    if k=='imp':
        la,ca=lit_and_copies(t[1]); lb,cb=lit_and_copies(t[2]); return(la+lb+1,ca+cb)
    if k=='all':
        lv,cv=lit_and_copies(t[1]); lb,cb=lit_and_copies(t[2]); return(lv+lb+1,cv+cb) # al token; var pushed
    if k=='ex':   # -. A.x -. p
        return lit_and_copies(neg(alL(t[1],neg(t[2]))))
    if k=='and':
        return lit_and_copies(neg(imp(t[1],neg(t[2]))))
    if k=='iff':
        return lit_and_copies(neg(imp(imp(t[1],t[2]),neg(imp(t[2],t[1])))))
    raise ValueError(k)
x,y,z=V(0),V(1),V(2); v0,v1,v2,v3=V(0),V(1),V(2),V(3)
AX={
 'B1': imp(imp(PH,PS),imp(imp(PS,CH),imp(PH,CH))),
 'B2': imp(imp(neg(PH),PH),PH),
 'B3': imp(PH,imp(neg(PH),PS)),
 'B4': imp(alL(x,imp(PH,PS)),imp(alL(x,PH),alL(x,PS))),
 'B6a': imp(eq(x,y), andL(alL(z,eq(x,y)), imp(el(x,y),alL(z,el(x,y))))),
 'B6b': imp(alL(x,alL(y,PH)),alL(y,alL(x,PH))),
 'B6c': imp(exL(x,alL(x,PH)),PH),
 'B7': exL(x,eq(x,y)),
 'B8a': imp(eq(x,y),imp(eq(x,z),eq(y,z))),
 'B8b': imp(eq(x,y),imp(el(x,z),el(y,z))),
 'B8c': imp(eq(x,y),imp(el(z,x),el(z,y))),
 'EXT': imp(alL(v2,iff(el(v2,v0),el(v2,v1))),eq(v0,v1)),
 'REP': imp(alL(v3,exL(v1,alL(v2,imp(alL(v1,PH),eq(v2,v1))))),
            exL(v1,alL(v2,iff(el(v2,v1),exL(v3,andL(el(v3,v0),alL(v1,PH))))))),
 'POW': exL(v1,alL(v2,imp(alL(v3,imp(el(v3,v2),el(v3,v0))),el(v2,v1)))),
 'UNI': exL(v1,alL(v2,imp(exL(v3,andL(el(v2,v3),el(v3,v0))),el(v2,v1)))),
 'INF': exL(v1,andL(el(v0,v1),alL(v0,imp(el(v0,v1),
         exL(v2,andL(el(v2,v1),alL(v1,iff(el(v1,v2),eq(v1,v0))))))))),
}
TL=TC=0
for n,t in AX.items():
    l,c=lit_and_copies(t); TL+=l; TC+=c
    print(f"{n:4s} lit={l:3d} copies={c}")
print("TOTAL literal tokens",TL,"copies",TC,"axioms",len(AX))
open("axcount.out","w").write(f"{TL} {TC} {len(AX)}")
