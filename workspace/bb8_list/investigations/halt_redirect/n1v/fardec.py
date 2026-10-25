from st import *
def dec(far):
    """greedy decode from the left: D-tokens (10)^m 1, else raw"""
    out=[]; i=0; raw=''
    while i < len(far):
        j=i; m=0
        while far.startswith('10', j): m+=1; j+=2
        if j < len(far) and far[j]=='1':
            if raw: out.append('<'+raw+'>'); raw=''
            out.append(f'D{m}'); i=j+1
        else:
            raw += far[i]; i+=1
    if raw: out.append('<'+raw+'>')
    # rle
    s=[]; 
    for t in out:
        if s and s[-1][0]==t: s[-1][1]+=1
        else: s.append([t,1])
    return ' '.join(f'{t}^{c}' if c>1 else t for t,c in s)
if __name__ == '__main__':
    for k,m in ((3,71),(3,5),(5,71),(1,71),(7,15),(2,20)):
        r = stage('', expand(f"2^{k} 5 1^{m} 0^3 1 40 0 1^32") + [1, 19])
        print(f"k={k} m={m}: {fmt(r)[:30]} far[{len(r['far'])}] = {dec(r['far'])}")
        print("   raw:", r['far'])
