import sys,random
from vsr import run
random.seed(5)
def rule(y,z): return (3*y+6,z-2) if z>=3 else (3,3*y+6)
cases=[(2*random.randint(1,150)+1,2*random.randint(1,60)+1) for i in range(90)]+[(2*random.randint(1,150)+1,1) for i in range(30)]
for M in sys.argv[1:]: run(M,'E','00110','1','0','1','-',cases,rule)
