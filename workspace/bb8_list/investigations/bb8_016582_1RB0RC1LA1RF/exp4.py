import threading,os
threading.Timer(30, lambda: os._exit(3)).start()
from exp2 import *
import sys
for w in sys.argv[1:]:
    s,t=PH[w]
    drive(w,s,None,matchers=(),maxev=100,verbose=True)
