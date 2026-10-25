import planner8 as P
P.set_tm("1RB0RF_1RC0LF_0RD0RB_1LE1LG_0LA0LC_0LD1RH_1RA1LC_1RF---")
def run(blk, v, c=0): return P.mkrun(blk, {v: 1} if isinstance(v, str) else v, c)
L = [0, 1, 0, 1, 0, 1, 1] + run((1, 1, 1), 'k') + [1, 1] + [1, 1, 1, 0, 1, 1, 1, 0] + [0, 1, 0] * 5 + [P.V('l')]
cfg = ('B', L, [P.BLANK], '>')
script, end = P.drive('P1', cfg, None, maxev=60)
