import sys
from comp import compress
def D(m): return '10'*m+'1'
def bits(toks,r,P=True,tail='0111001'):
    return ('11' if P else '')+''.join(D(m) for m in toks)+'10'*r+tail
if __name__=='__main__':
    toks=eval(sys.argv[1]); r=int(sys.argv[2])
    b=bits(toks,r)
    print(b); print(compress(b,2,8))
