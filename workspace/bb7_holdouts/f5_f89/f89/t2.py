from msim import *
T=parse(M)
for w in ['101','011','110','01','10','101101','011011','110110']:
    for frm in 'LR':
        out=[]
        for q in 'ABCDEFG':
            r=copy_sim(T,w,q,frm)
            if r and r[0]!=frm and r[1]==q: out.append('%s:%s'%(q,r[2]))
        print(w,frm,out)
