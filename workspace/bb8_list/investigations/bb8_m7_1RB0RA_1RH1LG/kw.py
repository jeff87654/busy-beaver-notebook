import sys
P='11';U='10';S='111001'
def word(ds,a,b):
    w=P
    for d in ds: w+=U*(3*d+1)+'1'
    w+=U*(3*a+1)+'1'
    w+=U*(3*b+2)+S
    return w
if __name__=='__main__':
    ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3])
    print(word(ds,a,b))
