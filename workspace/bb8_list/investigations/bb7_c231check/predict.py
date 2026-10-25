def predict(a,ds,w):
    if ds and ds[0]>0:
        st=12*a*a+66*a+(56 if w==1 else 58)
        return ('K',st,(3*a+3,[ds[0]-1]+ds[1:]))
    k=0
    while k<len(ds) and ds[k]==0: k+=1
    if k>3*a: return ('BAD',)
    if k==len(ds):
        st=48*a*a+(192 if w==1 else 198)*a+(137-28*k if w==1 else 143-30*k)
        return ('HALT',st,6*a+7)
    st=12*a*a+(24*k+66)*a+74+10*(k-1)-4*(k-1)*(k-2)+(0 if w==1 else 2*(k+1))
    return ('K',st,(1,[1]*(k-1)+[3*a+3-k,ds[k]-1]+ds[k+1:]))
