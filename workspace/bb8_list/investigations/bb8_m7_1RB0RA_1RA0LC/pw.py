import sys
def D(m): return '10'*m+'1'
def word(toks,r,P=False):
    return ('11' if P else '')+''.join(D(m) for m in toks)+'10'*r+'111001'
if __name__=='__main__':
    toks=eval(sys.argv[1]); r=int(sys.argv[2])
    print(word(toks,r,len(sys.argv)>3))
