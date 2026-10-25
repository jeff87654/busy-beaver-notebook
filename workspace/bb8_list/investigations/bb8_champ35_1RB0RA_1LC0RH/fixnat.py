import re,sys
s=open('glue35.v').read()
# add %nat to arithmetic expressions with literal 0/1 : handle known patterns
s=s.replace("[1;0]^^2 *>","[1;0]^^(2) *>")
s=s.replace("[1;0]^^(3 * d + 1) *>","[1;0]^^((3 * d + 1)%nat) *>")
s=s.replace("[1;0]^^(3 * b + 1) *>","[1;0]^^((3 * b + 1)%nat) *>").replace("[1;0]^^(3 * a + 1) *>","[1;0]^^((3 * a + 1)%nat) *>")
s=s.replace("(3 * 0 + 1)","((3 * 0 + 1)%nat)")
s=re.sub(r"\(3 \* ([A-Za-z() *+0-9]+?) \+ 1\)(?! *%nat)",lambda m:"((3 * %s + 1)%%nat)"%m.group(1),s) if False else s
open('glue35.v','w').write(s)
