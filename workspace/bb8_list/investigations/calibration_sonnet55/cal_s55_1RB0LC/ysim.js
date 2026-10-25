// usage: node ysim.js n maxsteps  -> runs Y(n)=A>0 1^n until next Y(m) (A on 0 at left edge, blank left, single run right)
const M="1RB0LC_0RC0RF_0RD0RH_1LE---_0LF1LG_1RD1LA_1RC1LA_0LF0LA";
const W=new Int8Array(16),D=new Int8Array(16),S=new Int8Array(16);
M.split("_").forEach((ch,i)=>{for(let s=0;s<2;s++){const e=ch.substr(3*s,3);const k=i*2+s;if(e==="---"){S[k]=-1;}else{W[k]=+e[0];D[k]=e[1]==="R"?1:-1;S[k]=e.charCodeAt(2)-65;}}});
function runY(n,maxSteps,size){
  const tape=new Uint8Array(size);let p=size>>1;const origin=p;let q=0;
  for(let i=0;i<n;i++)tape[p+1+i]=1;
  let left=p,right=p+n;
  for(let t=0;t<maxSteps;t++){
    if(q===0&&p<=left&&tape[p]===0&&t>0&&tape[p+1]===1){
      // count run and check blank after
      let j=p+1;while(tape[j]===1)j++;
      if(j>right){return {t,m:j-p-1};}
    }
    const k=q*2+tape[p];const s=S[k];
    if(s<0)return {t,halt:"ABCDEFGH"[q]+tape[p]};
    tape[p]=W[k];p+=D[k];q=s;
    if(p<left)left=p;if(p>right)right=p;
    if(p<5||p>size-5)return {t,overflow:1};
  }
  return {t:maxSteps,none:1};
}
const n0=+process.argv[2],n1=+process.argv[3]||n0,maxS=+process.argv[4]||1e9;
for(let n=n0;n<=n1;n++){console.log(n,JSON.stringify(runY(n,maxS,1<<24)));}
