import re
for i,ln in enumerate(open('ae.txt')):
    p=ln.split(' ',3)
    if len(p)<4: continue
    s=p[3].strip()
    s=re.sub(r'(?:0\^2 1 ){3,}0\^2 1', lambda m:'(0^2 1)^%d'%((m.group(0).count('0^2 1'))), s)
    if int(p[0])<70000 or int(p[0])>62974384 :
        if len(s)>0 and (int(p[0]) in (6,15,48,113,122,155,215,1160,1412,21461,22609,22657,23224,23428) or int(p[0])>62974384 and i%400==0): print(p[0],p[1],s[-100:] if len(s)>150 else s)
