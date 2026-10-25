from rulecheck import check
import itertools
rules=[
 (1,"S D> 2^a S","S 2^a D> S","a"),
 (2,"S B> 1^a S","S 1^a B> S","a"),
 (3,"S A> 0^2 S","S <A 1^2 S","5"),
 (4,"S D> (11)^a S","S (21)^a D> S","2*a"),
 (4.5,"S A> (11)^a S","S (12)^a A> S","2*a"),
 (5,"S (21)^a <C S","S <C (11)^a S","2*a"),
 (5.5,"S (12)^a <A S","S <A (11)^a S","2*a"),
 (6,"S (12)^a A> 0^2 S","S <A (11)^{a+1} S","2*a+5"),
 (9,"S D> 0^2 S","S <B 2^2 S","3"),
 (10,"S 2 <D (11)^a 0^2 S","S <D (11)^{a+1} 2 S","4*a+7"),
 (11,"S 2 <D (11)^a 2 0^2 S","S <D (11)^{a+1} 2^2 S","4*a+7"),
 (12,"S 1^a <A (11)^b 0^2 S","S 1^{a-1} <A (11)^{b+1} 2 S","4*b+7"),
 (13,"S 1^a <A (11)^b 2 0^2 S","S 1^{a-1} <A (11)^{b+1} 2^2 S","4*b+7"),
 (14,"S (12)^a 1 <D (11)^b 0^2 S","S (12)^{a-1} 1 <D (11)^{b+2} S","4*b+8"),
 (15,"S (12)^a 1 <D (11)^b 0^inf","S 1 <D (11)^{b+2*a} 0^inf","4*a*a+4*b*a+4*a"),
 (16,"S (12)^a 2 1 <D (11)^b 0^inf","S (12)^{a-1} 2 (12)^{b+2} 1 <D (11)^1 0^inf","10*b+28"),
 (17,"S (12)^a 2 1 <D (11)^b 0^inf","S (12)^{a-1} 2 1 <D (11)^{2*b+5} 0^inf",None),
 (18,"S (12)^a 2 1 <D (11)^b 0^inf","S 2 1 <D (11)^{2**a*b+2**a*5-5} 0^inf",None),
 (19,"S (12)^a 2 1 <D (11)^b 2 0^inf","S (12)^a 2^2 1 <D (11)^{2*b-1} 0^inf",None),
 (20,"S (12)^a 1 <D (11)^b 2 0^inf","S (12)^a 2 1 <D (11)^{2*b-1} 0^inf",None),
 (21,"S (12)^a 2^2 1 <D (11)^b 0^inf","S (12)^{a-1} 2^2 1 <D (11)^{2**(b+4)*3-5} 0^inf",None),
 (22,"S 1 <D (11)^b 2^2 0^inf","S 2 (12)^{b-1} 2 1 <D (11)^1 0^inf",None),
 (23,"S (11)^a 2^2 1 <D (11)^b 0^inf","S (11)^{a-3} (12)^{2*b+11} 2^2 1 <D (11)^1 0^inf",None),
 (24,"0^inf 2^2 1 <D (11)^c 0^inf","0^inf (11)^{c+1} (12)^3 2^2 1 <D (11)^1 0^inf",None),
 (25,"0^inf (11)^2 2^2 1 <D (11)^c 0^inf","0^inf 1 (11)^{2*c+8} (12)^3 2^2 1 <D (11)^1 0^inf",None),
 (26,"0^inf 1 (11)^1 2^2 1 <D (11)^c 0^inf","0^inf 1 (11)^{2*c+7} (12)^3 2^2 1 <D (11)^1 0^inf",None),
 (27,"0^inf 1 2^2 1 <D (11)^c 0^inf","0^inf (11)^{2*c+5} (12)^3 2^2 1 <D (11)^1 0^inf",None),
 (29,"0^inf 1 (11)^2 2^2 1 <D (11)^c 0^inf","0^inf (11)^{2*c+10} (12)^2 2^2 1 <D (11)^1 0^inf",None),
]
for num,l,r,st in rules:
    res=[]
    for a in range(0,5):
      for b in range(0,4):
        for c in range(0,4):
          env=dict(a=a,b=b,c=c)
          try:
            sv = eval(st,{},env) if st else None
            out=check(l,r,env,steps=sv,maxsteps=200000)
          except AssertionError as e:
            out=('neg',)
          res.append(((a,b,c),out[0]))
    oks=[x for x,o in res if o=='OK']; bad=[(x,o) for x,o in res if o not in ('OK','neg')]
    print(num, 'OK on',len(oks), 'fail',len(bad), bad[:4])
