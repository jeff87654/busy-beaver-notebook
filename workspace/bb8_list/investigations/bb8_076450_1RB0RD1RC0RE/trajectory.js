// Literal simulation from the blank tape (no acceleration). Reports every configuration
//   M(a,b,T) = 0^inf A>0 1^6 0^a 1 0^b T 0^inf,   T = T1 = 1111001 or T = T2 = 111,
// and checks that each one is the predicted successor of the previous one, at the predicted step:
//   M(a,b+3,T)  -> M(6a+6,b,T)     in 6a^2+49a+43 steps   (variant H0=1LC: 6a^2+45a+43)
//   M(a,0,T1)   -> M(4,6a+7,T2)    in 6a^2+37a+77 steps   (variant: 6a^2+33a+77)
//   M(a,1,T2)   -> M(4,6a+3,T1)    in 6a^2+37a+89 steps   (variant: 6a^2+33a+89)
// (any other M is reported as UNEXPECTED).  The first M must be M(4,1,T2) at step 82.
// Usage: node trajectory.js maxSteps     (machine from env TM, default = main machine)
const MAIN = "1RB0RD_1RC0RE_1LD1LC_1LA0LD_1LB1RF_---1LG_0RB1RH_0LB1RG";
const TM = process.env.TM || MAIN;
const c = (TM === MAIN) ? 25 : 21;   // a rules O with n = 6,12,...,6a cost 6a^2 + c*a steps (O = 2n+19 main, 2n+15 variant)
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const Nn = 1<<24; const tape = new Uint8Array(Nn);
let pos = Nn>>1, st = 0, first1 = Nn, last1 = -1;
const maxSteps = +(process.argv[2]||1e7);
const re = /^111111(0*)1(0*)(1111001|111)$/;
function succ(f){ // [a,b,T] -> [[a',b',T'], steps]
  const [a,b,t]=f; const Osum = 6*a*a + c*a;   // cost of a O-rules with n = 6,12,...,6a
  if(b>=3) return [[6*a+6,b-3,t], Osum + 4*(6*a+7)+15];
  if(b===0 && t==='T1') return [[4,6*a+7,'T2'], Osum + (2*(6*a+11)+11) + 9 + 35];
  if(b===1 && t==='T2') return [[4,6*a+3,'T1'], Osum + (2*(6*a+7)+31) + 9 + 35];
  return ['UNEXPECTED', 0];
}
let prev=null, prevStep=0, found=0, bad=0;
for (let s=1; s<=maxSteps; s++){
  const r = tape[pos]; const e = T[st][r];
  if(!e){ console.log('HALT at step', s-1, 'state', String.fromCharCode(65+st)); bad++; break; }
  tape[pos]=e[0];
  if(e[0]===1){ if(pos<first1) first1=pos; if(pos>last1) last1=pos; }
  else if(pos===first1){ while(first1<=last1 && tape[first1]===0) first1++; }
  else if(pos===last1){ while(last1>=first1 && tape[last1]===0) last1--; }
  pos+=e[1]; st=e[2];
  if(pos<=0||pos>=Nn-1){ console.log('tape overflow'); break; }
  if(st===0 && tape[pos]===0 && pos<first1 && tape[pos+1]===1 && tape[pos+6]===1 && tape[pos+7]===0){
    const w = Buffer.from(tape.subarray(pos+1, last1+1).map(c=>c+48)).toString();
    const m = re.exec(w);
    if(!m) continue;
    const f=[m[1].length, m[2].length, m[3]==='111'?'T2':'T1'];
    let tag='';
    if(prev){ const [p,ds]=succ(prev);
      if(p==='UNEXPECTED'||p[0]!==f[0]||p[1]!==f[1]||p[2]!==f[2]||s-prevStep!==ds){ tag=' MISMATCH predicted '+JSON.stringify(p)+' after '+ds; bad++; } }
    else if(!(f[0]===4&&f[1]===1&&f[2]==='T2'&&s===82)){ tag=' MISMATCH (first M should be M(4,1,T2) at step 82)'; bad++; }
    found++;
    console.log(`step ${s}: M(${f[0]},${f[1]},${f[2]})${tag}`);
    prev=f; prevStep=s;
  }
}
console.log(`found ${found} M-configurations, ${bad} mismatches`);
