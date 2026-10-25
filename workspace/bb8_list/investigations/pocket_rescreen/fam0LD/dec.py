import re
def dec(s):
    # s read outward from head: u^b s u^a s D1..Dn S, u='10', s='1', D=u^d s, S='1'
    m=re.fullmatch(r'((?:10)*)1((?:10)*)1((?:(?:10)*1)*)1',s)
    if not m: return None
    b=len(m.group(1))//2; a=len(m.group(2))//2
    ds=[len(x)//2 for x in re.findall(r'((?:10)*)1',m.group(3))]
    return ds,a,b
