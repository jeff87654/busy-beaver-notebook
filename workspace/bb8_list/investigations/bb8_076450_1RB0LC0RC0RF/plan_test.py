import planner8 as pl
from planner8 import drive, mkrun, V, BLANK, is_run, norm_side
pl.set_tm("1RB0LC_0RC0RF_0RD0RH_1LE---_0LF1LG_1RD1LA_1RC1LA_0LF0LA")
def D(L): return ('D', L, [BLANK], '>')
S3=(1,1,1); S6=(1,)*6
def swF(cfg):
    q, L, R, mode = cfg
    if q == 'F' and mode == '>' and L[0] == 0 and is_run(R[0]) and all(x == 1 for x in R[0][1]):
        blk = R[0][1]
        return ((q, norm_side([0, ('run', blk, R[0][2])] + L[1:]), R[1:], '>'), 'follow swF%d.' % len(blk), 'swF')
    return None
PH = {
 'R1': (D([0,0]+mkrun(S3,{'m':1})+[1,0,V('l')]), D([0,0]+mkrun(S3,{'m':1})+[1]*6+[V('l')])),
 'R0o': (D([0,0]+mkrun(S6,{'i':1})+[1,1,1,0,V('l')]), D([0,0,1]+mkrun((0,1,0,1,0,1),{'i':1})+[0,1,0,1,1,V('l')])),
 'R2': (D([0,0]+mkrun(S6,{'j':1})+[1,1,BLANK]), D([0,0,1,1,1]+mkrun((0,1,0,1,0,1),{'j':1})+[0,1,0,1,1,BLANK])),
}
if __name__ == '__main__':
    for k,(s,t) in PH.items():
        drive(k, s, t, matchers=(swF,), maxev=200)
