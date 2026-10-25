s=open('kl2.cpp',newline='').read()
bad='%s'+chr(10)+'",st'
print(s.count(bad), s.count('%s'+chr(13)+chr(10)+'",st'))
s=s.replace('%s'+chr(13)+chr(10)+'",st','%s'+chr(92)+'n",st').replace(bad,'%s'+chr(92)+'n",st')
open('kl2.cpp','w',newline='').write(s)
