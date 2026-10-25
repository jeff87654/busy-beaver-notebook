import sys
def mirror(m): return '_'.join(''.join(t if t=='---' else t[0]+{'L':'R','R':'L'}[t[1]]+t[2] for t in [s[i:i+3] for i in (0,3)]) for s in m.split('_'))
if __name__=='__main__': print(mirror(sys.argv[1]))
