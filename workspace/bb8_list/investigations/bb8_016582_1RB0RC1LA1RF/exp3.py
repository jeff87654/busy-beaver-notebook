from exp2 import *
k={'k':1}
s=('A',[1,1,1,1,BLANK],mkrun((0,),k,2)+R,'>')
t=('A',[BLANK],[0,1,1,0,1,0,1]+mkrun((0,),k,1)+R,'>')
drive('Z6',s,t,matchers=(),maxev=100,verbose=True)
