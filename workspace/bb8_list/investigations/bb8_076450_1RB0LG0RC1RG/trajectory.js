// Literal simulation from the blank tape; report every configuration of the form
//   0^inf A>0 (abb)^N (bab)^M 1 0^inf        = P(N,M)
//   0^inf A>0 (abb)^N 100 (bab)^M 1 0^inf    = Q(N,M)
// and check each is the predicted successor of the previous one.
// Usage: node trajectory.js maxSteps   (TM from env TM)
const TM = process.env.TM || "1RB0LG_0RC1RG_1LD1RF_1RE---_0LH1LC_1RA1LA_1RH0RE_0LF0RH";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const Nn = 1<<26; const tape = new Uint8Array(Nn);
let pos = Nn>>1, st = 0, first1 = Nn, last1 = -1;
const maxSteps = +(process.argv[2]||1e7);
const reP = /^((?:10100100)*)((?:10010100)*)1$/, reQ = /^((?:10100100)*)100((?:10010100)*)1$/;
function succ(f){ const [k,N,M]=f; if(k==='P') return M>=1?['Q',2*N+1,M-1]:['Q',2,N]; return M>=1?['P',2*N+2,M-1]:['Q',2,2*N+1]; }
let prev=null, found=0, bad=0;
for (let s=1; s<=maxSteps; s++){
  const r = tape[pos]; const e = T[st][r];
  if(!e){ console.log('HALT at', s-1); break; }
  tape[pos]=e[0];
  if(e[0]===1){ if(pos<first1) first1=pos; if(pos>last1) last1=pos; }
  else if(pos===first1){ while(first1<=last1 && tape[first1]===0) first1++; }
  else if(pos===last1){ while(last1>=first1 && tape[last1]===0) last1--; }
  pos+=e[1]; st=e[2];
  if(st===0 && pos===first1-1){
    // quick filter
    let ok = true;
    const head = [1,0,1,0,0,1,0,0];
    for(let i=0;i<8 && first1+i<=last1;i++){ if(tape[first1+i]!==head[i]){ ok=false; break; } }
    if(!ok) continue;
    const w = Buffer.from(tape.subarray(first1, last1+1).map(c=>c+48)).toString();
    let m = reP.exec(w), f=null;
    if(m) f=['P', m[1].length/8, m[2].length/8];
    else { m = reQ.exec(w); if(m) f=['Q', m[1].length/8, m[2].length/8]; }
    if(!f) continue;
    let tag = '';
    if(prev){ const p = succ(prev); if(p[0]!==f[0]||p[1]!==f[1]||p[2]!==f[2]){ tag=' MISMATCH predicted '+p.join(','); bad++; } }
    found++;
    let ones=0; for(let i=first1;i<=last1;i++) ones+=tape[i];
    console.log(`step ${s}: ${f[0]}(${f[1]},${f[2]}) ones=${ones}${tag}`);
    prev=f;
  }
}
console.log(`found ${found} family configs, ${bad} mismatches`);
