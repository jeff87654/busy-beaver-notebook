import sys
exec(open('ev.py').read().split("N=int")[0])
N=int(sys.argv[1]); SZ=1<<24
tape=bytearray(SZ); p=SZ//2; q=0
left=p; right=p
# track leftmost 1 index and count of ones? detect: head at cell with all nonzero to its right contiguous. Use A-state at p with tape[p-1..] left all zero
ones=0
for t in range(N):
    if q==0 and p<=left and tape[p]==0:
        # measure the run to right
        j=p+1
        while tape[j]: j+=1
        n=j-p-1
        if tape[p+1] and all(tape[k]==0 for k in range(j,j+50)):
            print(t,"Y(%d)"%n)
    r=tb[q*2+tape[p]]
    if r is None: print("HALT",t); break
    tape[p]=r[0]; p+=r[1]; q=r[2]
    if p<left:left=p
