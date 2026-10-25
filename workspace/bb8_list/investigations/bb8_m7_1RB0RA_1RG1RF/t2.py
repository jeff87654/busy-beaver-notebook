from evsum import *
import sys
Tp=int(sys.argv[1]); lim=int(sys.argv[2])
st=('C', U(3+Tp)+[1,0,1,1,1,BLANK], [0,1,0,1,1,0,1,R('J',Z),0,BLANK], '<')
go(st,lim)
