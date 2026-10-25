"""Transcription checks for universal C14 A/E/H word identities.

Each test uses a finite known interval and rejects any read outside it. Thus
successful concrete traces leave every unspecified tape cell untouched.
The parameter-universal proofs are in the companion markdown.
"""
from pathlib import Path
from itertools import product
import json

MACHINE = '1RB1LA_0LA0RC_1RA1LD_0LE1RZ_0LC1LF_1RH1LG_1LA0LE_0RE0RH'
T = [[(int(row[j]), 1 if row[j+1]=='R' else -1,
       -1 if row[j+2]=='Z' else ord(row[j+2])-65)
      for j in (0,3)] for row in MACHINE.split('_')]

def check(word, origin, state, head, steps, wanted, wanted_origin, final_state, final_head):
    tape={origin+i for i,c in enumerate(word) if c=='1'}
    lo,hi=origin,origin+len(word)-1
    trace=[]
    for _ in range(steps):
        assert lo<=head<=hi, ('unknown read',head,lo,hi)
        r=int(head in tape)
        trace.append(chr(65+state)+str(r))
        w,d,state=T[state][r]
        if w:tape.add(head)
        else:tape.discard(head)
        head+=d
        if state<0:break
    assert len(trace)==steps and state==final_state and head==final_head
    assert tape=={wanted_origin+i for i,c in enumerate(wanted) if c=='1'}, (word,trace,tape,wanted)
    return trace

counts={}
def add(name):counts[name]=counts.get(name,0)+1
for r in range(1,65):
    check('0'+'1'*r,0,7,0,r+3,'1'+'0'*r,0,7,r+1);add('H_run')
    check('010'+'1'*r,0,0,0,5,'101'+'1'*r,0,0,1);add('A_leading_one')

check('000',0,7,0,7,'110',0,0,-1);add('H_tail_reset')
check('000',-1,4,0,6,'110',-1,0,-2);add('E_zero_reset')
check('01',-1,4,0,3,'10',-1,7,1);add('E_one_boundary')
check('011',-2,4,0,3,'111',-2,0,-3);add('E_two_boundary')
check('111',-2,4,0,3,'011',-2,4,-3);add('E_triple')
check('010',-2,4,0,3,'010',-2,4,-3);add('E_zero_left_one')
check('110',-2,4,0,3,'110',-2,-1,-1);add('E_local_halt')

for n in range(2,65):
    check('00'+'1'*n,-1,0,0,n+9,'101'+'0'*(n-1),-1,7,n+1);add('A_left_zero')
    check('010'+'1'*n,-2,0,0,7,'1110'+'1'*(n-1),-2,0,-3);add('A_left_01')
    check('110'+'1'*n,-2,0,0,7,'0110'+'1'*(n-1),-2,4,-3);add('A_left_11')

for n in range(2,7):
    for k in range(3):
        for rs in product(range(1,5),repeat=k):
            right='1'*n+''.join('0'+'1'*r for r in rs)+'01'
            word='00'+right+'000'
            expected='101'+'0'*(n-1)+'1'+''.join('0'*r+'1' for r in rs)+'011'
            dt=n+20+sum(rs)+3*k
            check(word,-1,0,0,dt,expected,-1,0,len(right));add('whole_right_pass')

# An artificial input demonstrating why observed run bounds do not prove safety.
word='11110110111101'
tape={i for i,c in enumerate(word) if c=='1'};head=-1;state=0;events=[];last=[]
for step in range(2000):
    r=int(head in tape)
    if state==4 and r==0:
        events.append({'step':step,'left':int(head-1 in tape),'right':int(head+1 in tape)})
    last.append({'step':step,'state':chr(65+state),'read':r,'head':head})
    last=last[-6:]
    w,d,state=T[state][r]
    if w:tape.add(head)
    else:tape.discard(head)
    head+=d
    if state<0:break
assert step+1==1086 and len(tape)==30 and len(events)==15
assert all(not e['left'] and not e['right'] for e in events[:-1])
assert events[-1]=={'step':1083,'left':1,'right':0}
families=[]
for n in (2,3,4):
    for k in range(33):
        source=[n]+[2]*k+[1]
        if n==2:
            target=[3,3]+[2]*k+[1];dt=37+12*k;shift=-3
        elif n==3:
            target=[4]+[2]*(k+1)+[1];dt=38+12*k;shift=-2
        else:
            target=[3,4]+[2]*(k+1)+[1];dt=77+24*k;shift=-3
        before='0'*9+'0'.join('1'*r for r in source)+'0'*8
        after='0'.join('1'*r for r in target)
        check(before,-8,0,0,dt,after,shift+1,0,shift)
        add('all_two_tail_family')
        if k in (0,1,32):families.append({'input_runs':source,'output_runs':target,'steps':dt,'head_shift':shift})
out={'machine':MACHINE,'counts':counts,'total_checks':sum(counts.values()),
     'meaning':'Finite transcription checks; universal identities follow from the explicit transition derivations.',
     'artificial_halting_input':{'word':word,'head':-1,'state':'A','left_background':0,
        'right_background':0,'steps':step+1,'ones':len(tape),'E0_events':events,'last_steps':last},
     'all_two_tail_family_examples':families,
     'blank_classification':'unresolved; the artificial input is not asserted reachable from blank'}
Path('lastfive_family_theory_macros.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'counts':counts,'total_checks':sum(counts.values()),'halting_counterexample_steps':step+1},indent=2))
