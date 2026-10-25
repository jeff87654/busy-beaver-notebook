from msim import *
T=parse(M)
for w in ['1','0','111','110','011','101','01','10']:
    for frm in 'LR':
        out=[]
        for q in 'ABCDEFG':
            r=copy_sim(T,w,q,frm)
            if r and r[0]!=frm: out.append('%s->%s:%s'%(q,r[1],r[2]))
        print(w,frm,out)
