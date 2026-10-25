// Literal simulator: print compressed tape at geometric step checkpoints.
// usage: node snap.js maxSteps ratio
const TM = process.env.TM || "1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF";
function parse(tm){ return tm.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];})); }
const T = parse(TM);
const N = 1<<28; const tape = new Uint8Array(N);
let pos = N>>1, state = 0, steps = 0, minp = pos, maxp = pos;
function compress(s){
  let out=[]; let i=0;
  while(i<s.length){
    let best=null;
    for(let L=1;L<=8;L++){
      const u=s.substr(i,L); if(u.length<L) break;
      let k=1; while(s.substr(i+k*L,L)===u) k++;
      if(k*L>=Math.max(6,2*L) && (!best || k*L>best.k*best.L)) best={u,k,L};
    }
    if(best){ out.push("("+best.u+")^"+best.k); i+=best.k*best.L; }
    else { out.push(s[i]); i++; }
  }
  return out.join(" ");
}
function show(){
  let lo=minp, hi=maxp;
  while(lo<pos && tape[lo]===0) lo++;
  while(hi>pos && tape[hi]===0) hi--;
  if (pos-lo > 3e6 || hi-pos > 3e6) return "(too wide)";
  const left = Array.from(tape.subarray(lo,pos)).join("");
  const right = Array.from(tape.subarray(pos+1,hi+1)).join("");
  return compress(left)+" ["+"ABCDEFGH"[state]+tape[pos]+"] "+compress(right);
}
const maxSteps = +(process.argv[2]||1e6);
const ratio = +(process.argv[3]||1.5);
let next = 1000;
while(steps<maxSteps){
  const r = tape[pos]; const e = T[state][r];
  if(!e){ console.log("HALT at step",steps); console.log(show()); break; }
  tape[pos]=e[0]; pos+=e[1]; state=e[2]; steps++;
  if(pos<minp) minp=pos; if(pos>maxp) maxp=pos;
  if(steps>=next){ console.log(steps, show()); next=Math.ceil(next*ratio); }
}
