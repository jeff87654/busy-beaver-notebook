from common import *
def CA(rest_far, R='R', u='u', extra_near=(), extra_far=(), d9=False):
    return ('F', [0, 1] * 4 + list(extra_near) + [run(Z, **{R: 1})] + [1] + list(Z) * 4 + [run(Z * 5, **{u: 1})]
            + list(extra_far) + tok(12) + (tok(9) if d9 else []) + rest_far, [BLANK], '>')
LA_START = CA([V('l')], extra_far=list(Z) * 5)
LA_TARGET = CA([V('l')], extra_near=list(Z) * 2, d9=True)
