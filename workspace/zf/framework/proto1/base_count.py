import sys, os, time
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); os.chdir(HERE)
import zf2
ORDER = [16, 17, 3, 18, 4, 7, 8, 9, 11, 5, 12, 13, 14, 2, 15, 0, 1, 6, 10, 19]
t=time.time()
z=zf2.ZF2(); z.AXIOMORDER=ORDER; z.build_machine()
st=set(s[0] for s in z.tm.states)
print(len([s for s in st if s[0].isdigit()]), len([s for s in st if not s[0].isdigit()]), len(st), time.time()-t)
z.tm.save('base_rebuilt.tm')
