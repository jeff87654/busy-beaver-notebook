# decode lit.exe 'ends' RLE lines into cell strings and a u=10 token view
import sys,re
def cells(rle):
    out=[];head=None
    for tok in rle.split():
        m=re.match(r'\[([A-Z])([01])\]',tok)
        if m: head=(len(out),m.group(1)); out.append(m.group(2)); continue
        if '^' in tok: c,n=tok.split('^'); out.append(c*int(n))
        else: out.append(tok)
    s=''.join(out)
    return s,head
def u10(s):
    # tokens: maximal (10)^n blocks -> n ; leftover single chars shown
    res=[];i=0
    while i<len(s):
        n=0
        while s.startswith('10',i): n+=1; i+=2
        if n: res.append(str(n)); continue
        res.append('.' if s[i]=='0' else '#'); i+=1
    return ' '.join(res)
if __name__=='__main__':
    for line in sys.stdin:
        p=line.split(None,3)
        if len(p)<4: print(line.strip()); continue
        s,h=cells(p[3]); print(p[0],p[1],p[2],len(s),u10(s.strip('0')) if '1' in s else '')
