import subprocess,sys,re
TV=r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s0\tv.exe'
def first(M,side,state,init_state,hidx,spec,steps=10**9,skip=0):
    out=subprocess.run([TV,M,str(steps),side+':'+state,'1','1',str(skip+1),init_state,str(hidx),spec],capture_output=True,text=True).stdout.split('\n')
    n=0
    for l in out:
        if l.startswith('HALT'): return l
        if '|' in l and ('[%s]'%state) in l:
            n+=1
            if n>skip: return l.split('|',1)[1].strip()
    return None
import re as _re
def expand(cfg):
    """compressed tape text -> (explicit string with state letter inserted before head cell)"""
    out=[]
    for tok in cfg.split():
        m=_re.fullmatch(r'\((\d+)\)\^(\d+)',tok)
        if m: out.append(m.group(1)*int(m.group(2)))
        else:
            m=_re.fullmatch(r'\[([A-H])\](\d)',tok)
            if m: out.append(m.group(1)+m.group(2))
            else: out.append(tok)
    return ''.join(out).strip('0') if False else ''.join(out)
def run_seq(M,steps,sidestate,init_state,hidx,spec,maxrec=10**8):
    p=subprocess.Popen([TV,M,str(steps),sidestate,'1','1',str(maxrec),init_state,str(hidx),spec],stdout=subprocess.PIPE,text=True)
    return p
