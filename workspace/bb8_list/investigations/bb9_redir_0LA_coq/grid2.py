from trace0 import start
import sys
def run(p,m,b):
    s=start([9]*p+[8,0]+[1]*m+[1,3*b+1,2])
    while s.steps<10**7:
        if not s.step():
            st,l,r=s.word(); ones=st.count('1')
            return s.q,s.t[s.pos],s.steps,ones
    return None
if __name__ == "__main__":
 for m in (25,60,95):
  for p in range(0,7):
    for b in range(0,6):
      res=run(p,m,b)
      print(m,p,b,res, (res[3]-2*(3*b+1)) if res else None)
