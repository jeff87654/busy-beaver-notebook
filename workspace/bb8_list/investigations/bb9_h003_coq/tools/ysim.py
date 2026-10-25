import idle, sys
from x3sim import *
from trace1 import comp
def Yw(n, m, t):
    return [1] + [1] + [1,0]*n + [0] + [1,0,1]*m + [1,0,0,1,1,1,0,0]*(t+1) + [1,0,0,1,0,1]
def ysim(n, m, t):
    s = Sim(X3, [])
    s.t = bytearray(1000) + bytearray(Yw(n,m,t)) + bytearray(200000); s.pos = 1001; s.q = 'A'
    return s
