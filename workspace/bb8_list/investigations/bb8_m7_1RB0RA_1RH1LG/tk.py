# token string -> bit string; tokens: aN (10)^N, c=110, 0, 1
import sys,re
def bits(ts):
    out=''
    for t in ts.split():
        if t[0]=='a': out+='10'*int(t[1:])
        elif t=='c': out+='110'
        elif t in('0','1'): out+=t
        else: raise ValueError(t)
    return out
if __name__=='__main__': print(bits(' '.join(sys.argv[1:])))
