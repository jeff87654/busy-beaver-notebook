from common import *
S3E = KF(tok(1), tok(0, 'r'), [run(Z, M=1)] + tok(0) + tok(3, 'T') + tok(8) + tok(9) + [V('l')])
T3E = ('I', [0, 1] + tok(0, 'T') + tok(8) + tok(9) + [V('l')],
       list(Z) + [1] + [1, 0] * 5 + [run((1, 0, 1, 0), r=1)] + [0] + list(Z) * 2 + [run(Z, M=1), BLANK], '>')
