import sys
from lit import *
from tok import *
TM="1RB1RD_1LC0LB_1RA0LB_0RE0RG_1RA1LF_1LG0LH_1RD0LF_1LF---"
t=parse(TM)
# print each visit to state A (rare?)
cnt={}
def cb(k,tape,pos,st):
    cnt[st]=cnt.get(st,0)+1
r=run(TM,200000,cb)
print(cnt)
