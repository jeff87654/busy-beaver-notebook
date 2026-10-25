import sys, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen'); import idle
from val import V
m=sys.argv[1]; J=int(sys.argv[2])
def Y(j): return '0'+'1'*(54+16*j)+'0'*(18+8*j)+'1'+''.join('0'*(8*i-2)+'1' for i in range(j,0,-1))+'001'
inp=''.join(f"E - {Y(j)} C1:{54+16*(j+1)}\n" for j in range(J))
out=subprocess.run([V,m,'E','L','4000000000'],input=inp,capture_output=True,text=True).stdout.split('\n')
bad=[(j,out[j][:60]) for j in range(J) if not (out[j].startswith('M') and out[j].split()[3]==Y(j+1))]
print('Y',J,'bad',len(bad),bad[:3])
