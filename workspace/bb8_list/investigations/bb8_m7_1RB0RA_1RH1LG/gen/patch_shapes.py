s=open('shapes.py').read()
s=s.replace("return [1, 0, 0, 1, run(TB, t=1), 1, 1]","return [1, 0, 0, 1, 1, 1]")
open('shapes.py','w').write(s)
