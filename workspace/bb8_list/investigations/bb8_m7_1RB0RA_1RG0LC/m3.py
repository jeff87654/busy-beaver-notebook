import sys
def m3(K,n,pre=''):
    # 1^2 3| (1|)^K (3n+7)| 1| 1.   as a literal tape; head B on the blank right
    s='10'*2+'1'*3+'00'+'100'*K+'1'*(3*n+7)+'00'+'1'+'00'+'1'
    return s
if __name__=='__main__':
    print(m3(int(sys.argv[1]),int(sys.argv[2])))
