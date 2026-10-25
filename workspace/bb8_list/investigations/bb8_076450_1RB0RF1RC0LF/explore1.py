import planner8 as P
P.set_tm("1RB0RF_1RC0LF_0RD0RB_1LE1LG_0LA0LC_0LD1RH_1RA1LC_1RF---")
run = lambda blk, v, c=0: P.mkrun(blk, {v: 1} if v else {}, c)
# T(j,m): X 1^(j+3) (01)^m 0 B>0  -> X 1^j (01)^(m+3) 0 B>0
L = [0] + run((1, 0), 'm') + [1, 1, 1] + run((1,), 'j') + [P.V('X')]
cfg = ('B', L, [P.BLANK], '>')
L2 = [0] + run((1, 0), 'm') + [1, 0, 1, 0, 1, 0] + run((1,), 'j') + [P.V('X')]
tgt = ('B', L2, [P.BLANK], '>')
script, end = P.drive('T', cfg, tgt)
print(script)
