// Literal simulation from the blank tape (no acceleration). Reports every configuration
//   Y(k,n) = 0^inf 10 (1110)^k 11 (10)^n E> 0^inf
// and checks that each one is the predicted successor of the previous one, at the predicted step:
//   Y(k+1,n) -> Y(k,9n+13)                 in D(n) steps
//   Y(0,n) -> 0^inf (10)^m E>, m = 3n+7    then m odd: Y((m-1)/2, 2); m even: halt
// Usage: node trajectory.js maxSteps
const TM = process.env.TM || "1RB1RH_0LC0LF_0RH1LD_0RE1LF_1RA1RD_0LG0LE_1LB1LF_1RF---";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const Nn = 1<<22; const tape = new Uint8Array(Nn);
let pos = Nn>>1, st = 0, first1 = Nn, last1 = -1;
const [RO_A, RO_B, RE_A, RE_B] = [10, 23, 10, 25]; // from check_rules.out
const maxSteps = +(process.argv[2]||1e7);
const re = /^10((?:1110)*)11((?:10)*)$/;
const Tc = b => 8*b+22, Rc = b => 4*b+51, L1c = b => 8*b+22, ROc = j => RO_A*j+RO_B, REc = j => RE_A*j+RE_B;
function Tsum(cnt){ let s=0; for(let i=0;i<cnt;i++) s+=Tc(4+3*i); return s; }
function succ(f){
  const [k,n]=f;
  if(k>=1) return [[k-1,9*n+13], Rc(n-1)+Tsum(n-1)+Tc(3*n+1)+Rc(3*n+3)+Tsum(3*n+3)];
  const pre = Rc(n-1)+Tsum(n-1)+Tc(3*n+1)+L1c(3*n+4);
  const m = 3*n+7;
  if(m%2===1){ const j=(m-1)/2; return [[j,2], pre+ROc(j)]; }
  const j=(m-2)/2; return ['HALT', pre+REc(j)];
}
let prev=null, prevStep=0, found=0, bad=0;
for (let s=1; s<=maxSteps; s++){
  const r = tape[pos]; const e = T[st][r];
  if(!e){ console.log('HALT at step', s-1); break; }
  tape[pos]=e[0];
  if(e[0]===1){ if(pos<first1) first1=pos; if(pos>last1) last1=pos; }
  else if(pos===first1){ while(first1<=last1 && tape[first1]===0) first1++; }
  else if(pos===last1){ while(last1>=first1 && tape[last1]===0) last1--; }
  pos+=e[1]; st=e[2];
  if(pos<=0||pos>=Nn-1){ console.log('tape overflow'); break; }
  if(st===4 && pos===last1+2 && tape[pos-1]===0){
    const w = Buffer.from(tape.subarray(first1, last1+2).map(c=>c+48)).toString();
    const m = re.exec(w);
    if(!m) continue;
    const f=[m[1].length/4, m[2].length/2];
    let tag='';
    if(prev){ const [p,ds]=succ(prev);
      if(p==='HALT'||p[0]!==f[0]||p[1]!==f[1]||s-prevStep!==ds){ tag=' MISMATCH predicted '+JSON.stringify(p)+' after '+ds+' actual '+(s-prevStep); bad++; } }
    found++;
    console.log(`step ${s}: Y(${f[0]},${f[1]})${tag}`);
    prev=f; prevStep=s;
  }
}
console.log(`found ${found} Y-configurations, ${bad} mismatches`);
