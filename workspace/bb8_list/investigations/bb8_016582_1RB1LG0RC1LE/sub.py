import sys
s=open(sys.argv[1]).read()
s=s.replace(sys.argv[2].encode().decode('unicode_escape'),sys.argv[3].encode().decode('unicode_escape'))
open(sys.argv[1],'w').write(s)
