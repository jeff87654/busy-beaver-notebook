// Literal simulation from the blank tape (no acceleration). Reports every configuration
//   S(n,k,j) = 0^inf A>0 1^n (001)^k 0 0 0 1^j 0^inf   (n even)
// and checks that each one is the predicted successor of the previous one, at the predicted step:
//   S(n,k+1,j) -> S(4n+2,k,j)                     in 12n^2-21n+15 steps
//   S(n,0,j), n%6==4 -> S(10,(n-4)/3,j+1)          in (20n-5)/3 + 42 steps (R4, then two O rules)
//   S(n,0,j), n%6==2 -> S(8,(n-5)/3,j+1)           in (20n+44)/3 steps (R2)
//   S(n,0,j), n%6==0 -> halt (H reads 0)           after (20n-6)/3 steps (R0)
// Usage: node trajectory.js maxSteps     (machine from env TM, default = main machine)
const TM = process.env.TM || "1RB0LF_1RC0RE_1LD1LC_1LA0LD_1LB1RA_1RG1LG_0LH0RD_---1RF";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const Nn = 1<<22; const tape = new Uint8Array(Nn);
let pos = Nn>>1, st = 0, first1 = Nn, last1 = -1;
const maxSteps = +(process.argv[2]||1e7);
const re = /^(1+)((?:001)*)(?:000(1+))?$/;
function succ(f){ // [n,k,j] -> [[n',k',j'] or 'HALT', steps]
  const [n,k,j]=f;
  if(k>=1) return [[4*n+2,k-1,j], 12*n*n-21*n+15];
  if(n%6===4) return [[10,(n-4)/3,j+1], (20*n-5)/3+42];
  if(n%6===2) return [[8,(n-5)/3,j+1], (20*n+44)/3];
  return ['HALT', (20*n-6)/3];
}
let prev=null, prevStep=0, found=0, bad=0;
for (let s=1; s<=maxSteps; s++){
  const r = tape[pos]; const e = T[st][r];
  if(!e){ console.log('HALT at step', s-1, 'state', String.fromCharCode(65+st)); if(prev){const p=succ(prev); console.log(' predicted', p[0], 'after', p[1], 'steps; actual', s-1-prevStep);} break; }
  tape[pos]=e[0];
  if(e[0]===1){ if(pos<first1) first1=pos; if(pos>last1) last1=pos; }
  else if(pos===first1){ while(first1<=last1 && tape[first1]===0) first1++; }
  else if(pos===last1){ while(last1>=first1 && tape[last1]===0) last1--; }
  pos+=e[1]; st=e[2];
  if(pos<=0||pos>=Nn-1){ console.log('tape overflow'); break; }
  if(st===0 && pos===first1-1){
    const w = Buffer.from(tape.subarray(first1, last1+1).map(c=>c+48)).toString();
    const m = re.exec(w);
    if(!m) continue;
    const n = m[1].length; if(n%2) continue;
    const f=[n, m[2].length/3, m[3]?m[3].length:0];
    let tag='';
    if(prev){ const [p,ds]=succ(prev);
      if(p==='HALT'||p[0]!==f[0]||p[1]!==f[1]||p[2]!==f[2]||s-prevStep!==ds){ tag=' MISMATCH predicted '+JSON.stringify(p)+' after '+ds; bad++; } }
    found++;
    console.log(`step ${s}: S(${f[0]},${f[1]},${f[2]})${tag}`);
    prev=f; prevStep=s;
  }
}
console.log(`found ${found} S-configurations, ${bad} mismatches`);
