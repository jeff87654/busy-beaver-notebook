const tm="1RB0RH_1RC1LE_0LD0RF_---1RE_1LB0LB_1RA0RG_0LC1RF_0LG1LA";
const W=new Int8Array(16),D=new Int8Array(16),NQ=new Int8Array(16);
for(let q=0;q<8;q++)for(let s=0;s<2;s++){const e=tm.substr(q*7+s*3,3);const k=q*2+s; if(e[0]=='-'){W[k]=-1;continue;} W[k]=+e[0]; D[k]=e[1]=='R'?1:-1; NQ[k]=e.charCodeAt(2)-65;}
const N=+process.argv[2]; const SZ=1<<27; const t=new Uint8Array(SZ); let pos=SZ>>1,lo=pos,hi=pos,q=0; let next=1000;
for(let i=0;i<N;i++){
  const k=q*2+t[pos]; const w=W[k]; if(w<0){console.log('HALT',i,String.fromCharCode(65+q),t[pos]);process.exit();}
  t[pos]=w; pos+=D[k]; q=NQ[k];
  if(pos<lo)lo=pos; else if(pos>hi)hi=pos;
  if(i==next){console.log(i,'width',hi-lo,'lo',pos-lo,'hi',hi-pos);next*=4;}
}
let ones=0;for(let p=lo;p<=hi;p++)ones+=t[p];console.log('end',N,'ones',ones,'width',hi-lo);
