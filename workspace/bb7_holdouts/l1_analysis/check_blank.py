from pathlib import Path
from rewrite import Rope,advance
root=Path(__file__).parent
a=4;tail=Rope([('110100100',1)]);t=189;count=0
with (root/'blank_expectations.txt').open('w') as f:
    while t<1_000_000_000:
        print(t,('0000'+'100'*a+tail.string()).rstrip('0'),file=f)
        count+=1
        a,tail,dt,r=advance(a,tail);t+=dt
        assert a is not None
print(count,'checkpoints; next step',t)
