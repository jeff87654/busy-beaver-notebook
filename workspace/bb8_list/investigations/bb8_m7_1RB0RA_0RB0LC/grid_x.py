import subprocess,sys
M=sys.argv[1]; N=sys.argv[2]
SIM=r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_from_bb8\sim9.exe'
halts=[]; cnt=0
for x in range(0,13):
    for z in range(0,13):
        w='11011'+'01'*x+'11'+'01'*z+'0011111111001001'
        out=subprocess.run([SIM,M,w,str(len(w)),'B',N,'10'],capture_output=True,text=True).stdout
        cnt+=1
        if 'no halt' not in out: halts.append((x,z,out.strip().splitlines()[-2:]))
print('runs',cnt,'halts',len(halts)); print(halts[:5])
