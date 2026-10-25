import planner9 as P
BL = P.BLANK
R0 = [1, 0, 0, 1, 1, BL]
start = ('E', [('run', (0,0,1), P.C(0, c=1)), ('run', (1,1,1), P.C(1, b=1)), P.V('l')], R0, '>')
tgt = ('E', [('run', (0,0,1), P.C(3, c=1)), ('run', (1,1,1), P.C(0, b=1)), P.V('l')], R0, '>')
script, end = P.drive('TL1', start, tgt, maxev=200)
print(script)
print(P.lemma_text('TL1', start, tgt, script, '-->+'))
