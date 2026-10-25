from rulecheck import check
rules=[
 ("Bounce11","0^inf 1 1 <D (11)^b 0^inf","0^inf (11)^{b+1} 1 <A (11) 0^inf"),
 ("Bounce1","0^inf 1 <D (11)^b 0^inf","0^inf (11)^{b+1} 1 <A (11) 0^inf"),
 ("Bounce2","0^inf 2 1 <D (11)^b 0^inf","0^inf (11)^{b+1} 1 <A (11) 0^inf"),
 ("Bounce21","0^inf 1 2 1 <D (11)^b 0^inf","0^inf (11)^{b+1} 1 <A (11) 0^inf"),
]
for name,l,r in rules:
    res=[]
    for b in range(0,6):
        try: out=check(l,r,dict(b=b),maxsteps=300000)
        except AssertionError: out=('neg',)
        res.append((b,out))
    print(name,res)
