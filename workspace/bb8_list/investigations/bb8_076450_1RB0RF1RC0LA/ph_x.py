import sys
from phases import *
s = XCX([1,0]*4 + run((1,0,1,0),'j'))
t = Lv([1,0]*31 + run((1,0)*8,'j'))
trydrive('XC', s, t, maxev=3000)
