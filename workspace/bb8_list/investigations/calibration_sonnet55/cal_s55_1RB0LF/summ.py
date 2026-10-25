import re,sys
for ln in open('ae.txt'):
    p=ln.split(' ',3)
    if len(p)<4: continue
    s=p[3].strip()
    s=re.sub(r'(?:0\^2 1 ){3,}0\^2 1', lambda m:'(0^2 1)^%d'%((m.group(0).count('0^2 1'))), s)
    p3=s
    print(p[0],p[1],p[2],p3[:150])
