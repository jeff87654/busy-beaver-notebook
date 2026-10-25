import sys,random
src=open('grid.py').read()
head=src.split('cases=[]')[0]
tail=src.split("print(len(cases),file=sys.stderr)")[1]
exec(head)
random.seed(int(sys.argv[2]) if len(sys.argv)>2 else 1)
cases=[]
def add(ds,a,b): cases.append((tuple(ds),a,b))
for _ in range(1500):
    L=random.randint(0,6)
    ds=[random.choice([0,0,0,1,2,3,4,5]) for _ in range(L)]
    a=random.choice([0,0,0,1,2,5]); b=random.randint(0,14)
    add(ds,a,b)
for b in range(0,15):
    for n in (0,1,2,17,40,63): add([0]*n,0,b)
for k in (1,2,5,13,20,30):
    for b in (0,1,3,7,12,16):
        add([2,0,3]+[0]*k,0,b); add([1]+[0]*k,0,b)
exec(tail.replace('print(len(cases),file=sys.stderr)',''))
