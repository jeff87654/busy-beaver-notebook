// Literal simulation from the blank tape (no acceleration) of R1 or R2.  At every step where the head is in
// state A on the blank cell directly left of the leftmost 1, the word (leftmost 1 .. rightmost 1) is matched
// against the family configurations, and each detected family configuration is checked to be exactly the
// predicted successor of the previous one, reached after exactly the predicted number of steps.
//  R1 (tape right of the word is blank):
//    Z(n)    = 0^inf A>0 1^n 0^inf                     (n even)
//    C(a,k)  = 0^inf A>0 1^a (010)^k 0111 0000 1 0^inf  (a odd)
//    C(a,k), k>=2 -> C(4a+23,k-2)          in 8a^2+73a+165 steps
//    C(a,1)       -> Z(4a+38)              in 8a^2+121a+536 steps
//    Z(6q+2), q>=2 -> C(27,2q-3)           in 24q+259 steps;   Z(8)  -> Z(42) in 702 steps
//    Z(6q+4), q>=2 -> C(35,2q-3)           in 24q+473 steps;   Z(10) -> Z(50) in 1012 steps
//    Z(6q)         -> halt (G reads 0)     after 24q+5 steps
//  R2:
//    Z(n,j)   = 0^inf A>0 1^n 0000 1^j 0^inf            (n even)
//    C(a,k,j) = 0^inf A>0 1^a (010)^k 001 0000 1^j 0^inf (a odd)
//    C(a,k,j), k>=2 -> C(4a+23,k-2,j)       in 8a^2+73a+165 steps
//    C(a,0,j)       -> Z(a+9,j)             in 8a+26 steps
//    Z(6q+4,j), q>=1 -> C(27,2q-2,j+1)      in 24q+267 steps
//    Z(6q,j),   q>=2 -> C(29,2q-2,j+1)      in 24q+447 steps
//    Z(6q+2,j)       -> halt (G reads 0)    after 24q+13 steps
// Usage: node traj_R_fast.js R1|R2 maxSteps   (same as traj_R.js plus an exact cheap pre-filter)
const TMS = {R1: "1RB1LF_1RC0RE_1LD1LC_1LA0LD_1LB1RF_1RA1LG_---0LH_1RA0LF",
             R2: "1RB0LG_1RC0RE_1LD1LC_1LA0LD_1LB1RF_1RA1LG_---0LH_1RA0LF"};
const M = process.argv[2]; const TM = TMS[M];
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const Nn = 1<<23; const tape = new Uint8Array(Nn);
// flat transition table: index st*2+read -> write, move, next (next=-1: undefined = halt)
const TW = new Int8Array(16), TD = new Int8Array(16), TN = new Int8Array(16).fill(-1);
T.forEach((row,s)=>row.forEach((e,r)=>{ if(e){ TW[2*s+r]=e[0]; TD[2*s+r]=e[1]; TN[2*s+r]=e[2]; } }));
let pos = Nn>>1, st = 0, first1 = Nn, last1 = -1;
const maxSteps = +(process.argv[3]||1e7);
const reZ1 = /^(1+)$/, reC1 = /^(1+)((?:010)*)011100001$/;
const reZ2 = /^(1+)(?:0000(1+))?$/, reC2 = /^(1+)((?:010)*)001(?:0000(1+))?$/;
function detect(w){
  let m;
  if(M==='R1'){
    if((m=reZ1.exec(w)) && m[1].length%2===0) return ['Z', m[1].length];
    if((m=reC1.exec(w)) && m[1].length%2===1) return ['C', m[1].length, m[2].length/3];
  } else {
    if((m=reZ2.exec(w)) && m[1].length%2===0) return ['Z', m[1].length, m[2]?m[2].length:0];
    if((m=reC2.exec(w)) && m[1].length%2===1) return ['C', m[1].length, m[2].length/3, m[3]?m[3].length:0];
  }
  return null;
}
function succ(f){ // -> [config or 'HALT', steps]
  if(M==='R1'){
    if(f[0]==='C'){ const [,a,k]=f;
      if(k>=2) return [['C',4*a+23,k-2], 8*a*a+73*a+165];
      if(k===1) return [['Z',4*a+38], 8*a*a+121*a+536];
      return ['UNPREDICTED',0]; }
    const n=f[1], q=Math.floor(n/6);
    if(n%6===2) return q>=2 ? [['C',27,2*q-3], 24*q+259] : [['Z',42],702];
    if(n%6===4) return q>=2 ? [['C',35,2*q-3], 24*q+473] : [['Z',50],1012];
    return ['HALT', 24*q+5];
  } else {
    if(f[0]==='C'){ const [,a,k,j]=f;
      if(k>=2) return [['C',4*a+23,k-2,j], 8*a*a+73*a+165];
      if(k===0) return [['Z',a+9,j], 8*a+26];
      return ['UNPREDICTED',0]; }
    const n=f[1], j=f[2], q=Math.floor(n/6);
    if(n%6===4) return [['C',27,2*q-2,j+1], 24*q+267];
    if(n%6===0) return q>=2 ? [['C',29,2*q-2,j+1], 24*q+447] : ['UNPREDICTED',0];
    return ['HALT', 24*q+13];
  }
}
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
let prev=null, prevStep=0, found=0, bad=0, nZ=0;
for (let s=1; s<=maxSteps; s++){
  const r = tape[pos]; const ix = 2*st+r; const nx = TN[ix];
  if(nx<0){ console.log('HALT: state', String.fromCharCode(65+st), 'reads', r, 'after', s-1, 'steps');
    if(prev){ const p=succ(prev); console.log(' predicted', JSON.stringify(p[0]), 'after', p[1], 'steps; actual', s-1-prevStep, (p[0]==='HALT'&&p[1]===s-1-prevStep)?'OK':'MISMATCH'); if(!(p[0]==='HALT'&&p[1]===s-1-prevStep)) bad++; }
    let ones=0; for(let i=first1;i<=last1;i++) ones+=tape[i]; console.log(' ones on tape at halt:', ones);
    break; }
  const wr = TW[ix]; tape[pos]=wr;
  if(wr===1){ if(pos<first1) first1=pos; if(pos>last1) last1=pos; }
  else if(pos===first1){ while(first1<=last1 && tape[first1]===0) first1++; }
  else if(pos===last1){ while(last1>=first1 && tape[last1]===0) last1--; }
  pos+=TD[ix]; st=nx;
  if(pos<=0||pos>=Nn-1){ console.log('tape overflow'); break; }
  if(st===0 && pos===first1-1){
    // cheap pre-filter (exact: every family configuration passes it): a = length of the leading run of 1s;
    // the cells after it must be: end of word (Z, R1/R2), 0000 (Z, R2), 010 (C with k>=1), 0111 (C(a,0), R1), 001 (C(a,0), R2)
    let x=first1; while(x<=last1 && tape[x]===1) x++;
    if(x<=last1){
      const c0=tape[x], c1=tape[x+1], c2=tape[x+2], c3=tape[x+3];
      const ok = c0===0 && ((c1===1&&c2===0) || (M==='R1'&&c1===1&&c2===1&&c3===1) ||
                            (M==='R2'&&c1===0&&((c2===1)||(c2===0&&c3===0))));
      if(!ok) continue;
    }
    const w = Buffer.from(tape.subarray(first1, last1+1).map(c=>c+48)).toString();
    const f = detect(w);
    if(!f) continue;
    let tag='';
    if(prev){ const [p,ds]=succ(prev);
      if(!eq(p,f)||s-prevStep!==ds){ tag=' MISMATCH predicted '+JSON.stringify(p)+' after '+ds+' (actual '+(s-prevStep)+')'; bad++; } }
    found++; if(f[0]==='Z') nZ++;
    console.log(`step ${s}: ${f[0]}(${f.slice(1).join(',')})${tag}`);
    prev=f; prevStep=s;
  }
  if(s===maxSteps){ console.log('reached maxSteps', maxSteps); }
}
console.log(`found ${found} family configurations (${nZ} Z), ${bad} mismatches`);
