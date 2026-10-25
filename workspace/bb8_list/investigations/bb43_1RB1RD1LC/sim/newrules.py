from rulecheck import check
rules=[
 ("R21a","S 2 2 1 <D (11)^b 0^inf","S 2 <D (11)^{b+2} 0^inf"),
 ("R20","S 1 <D (11)^{b+1} 2 0^inf","S 2 1 <D (11)^{2*b+1} 0^inf"),
 ("Y","S 1 1 1 <D (11)^b 0^inf","S 1 <A (11)^{b+2} 0^inf"),
 ("R23z","S A> 1 (11)^b 2 2 0^inf","S (12)^b 2 2 1 <D (11) 0^inf"),
 ("R22","S 1 <D (11)^{b+1} 2 2 0^inf","S 2 (12)^b 2 1 <D (11) 0^inf"),
 ("R23","S (11)^3 2 2 1 <D (11)^b 0^inf","S (12)^{2*b+11} 2 2 1 <D (11) 0^inf"),
 ("R21","S (12) 2 2 1 <D (11)^b 0^inf","S 2 2 1 <D (11)^{3*2**(b+4)-5} 0^inf"),
 ("R25","0^inf (11)^2 2 2 1 <D (11)^b 0^inf","0^inf 1 (11)^{2*b+8} (12)^3 2 2 1 <D (11) 0^inf"),
 ("R26","0^inf 1 (11) 2 2 1 <D (11)^b 0^inf","0^inf 1 (11)^{2*b+7} (12)^3 2 2 1 <D (11) 0^inf"),
 ("R27","0^inf 1 2 2 1 <D (11)^b 0^inf","0^inf (11)^{2*b+5} (12)^3 2 2 1 <D (11) 0^inf"),
]
for name,l,r in rules:
    res=[]
    for b in range(0,6):
        try: out=check(l,r,dict(b=b),maxsteps=3000000)
        except AssertionError: out=('neg',)
        res.append((b,out))
    print(name,res)
