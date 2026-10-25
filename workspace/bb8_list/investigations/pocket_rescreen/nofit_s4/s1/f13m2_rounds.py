# F1.3 member 2 round map (validated rules): N even -> k=N/2, v=(4^(k+1)-1)/3, N'=floor((52v+2)/3); N odd -> W-branch (unanalysed)
import sys
def nxt_exact(N):
    k=N//2; v=(4**(k+1)-1)//3; return (52*v+2)//3
def nxt_mod(N, i):
    # N known exactly or mod 2*3^(i+1); returns N' mod 2*3^i
    k=N//2; m3=3**(i+2)
    v=(pow(4,k+1,3*m3)-1)//3 % m3          # v mod 3^(i+2)... v odd
    # v mod 2*3^(i+2) via CRT with v odd
    V = v if v%2==1 else v+m3
    t=(52*V+2)                               # mod 2*3^(i+2)
    Nn=(t - t%3)//3                          # floor/3 ; residue t%3 exact since mod 3^(i+2)
    return Nn % (2*3**i)
N=[18]; N.append(nxt_exact(18)); print('N1',N[1])
N2=nxt_exact(N[1]) if N[1]%2==0 else None
print('N2 parity', N2%2, 'bits', N2.bit_length())
cur=N2; i=300; r=2
while cur%2==0 and i>2:
    cur=nxt_mod(cur,i); i-=1; r+=1
    print('round',r,'N mod 6',cur%6)
print('first odd N at round', r if cur%2 else None)
