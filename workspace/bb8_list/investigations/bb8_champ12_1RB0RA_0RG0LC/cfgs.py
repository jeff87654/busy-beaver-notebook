import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
TM1='1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0LH0RF_---1RE'
TM2='1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0RH0RF_---1LE'
SUF=[1,0,0,1,1,1]
T3=(0,1,0,1,0,1)
U2=[0,1]
def units(n_const, var=None, coef=1):
    """(01)^(3*var*coef + n_const) as nearest-first tokens"""
    toks=[0,1]*n_const
    if var: toks+=mkrun(T3,{var:coef})
    return toks
def Kcfg(rest, a, b, a_var, b_var, acoef=1, bcoef=1, mode='<'):
    pass
def K(L):  # L nearest-first
    return ('B',L,[BLANK],'>')
def mk(b_const,b_var,b_coef,a_const,a_var,a_coef,rest,state='B'):
    # b units: 3*b+2 -> const given as number of (01) pairs beyond 3*var
    L=SUF+units(b_const,b_var,b_coef)+[1]+units(a_const,a_var,a_coef)+[1]+rest
    return (state,L,[BLANK],'>')
