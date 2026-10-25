// Exact literal simulator (no acceleration) for 1RB1LD_1RC0RF_0LA0RA_0LA0LE_1LA0LG_0LA---_1RD1LG
// Usage: node litsim.js [maxSteps] [mode]
// mode "left": print compressed tape each time the head reaches the leftmost visited cell.
const TM = process.env.TM || "1RB1LD_1RC0RF_0LA0RA_0LA0LE_1LA0LG_0LA---_1RD1LG";
function parse(tm){
  return tm.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---"||e[2]==="Z") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
}
const T = parse(TM);
const N = 1<<26;
const tape = new Uint8Array(N);
let pos = N>>1, state = 0, steps = 0;
let minp = pos, maxp = pos;
function compress(s){
  // greedy period compression
  let out=[]; let i=0;
  while(i<s.length){
    let best=null;
    for(let L=1;L<=6;L++){
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
  const left = Array.from(tape.subarray(lo,pos)).join("");
  const right = Array.from(tape.subarray(pos+1,hi+1)).join("");
  return compress(left)+" ["+"ABCDEFG"[state]+tape[pos]+"] "+compress(right);
}
const maxSteps = +(process.argv[2]||1e6);
const mode = process.argv[3]||"left";
let ones=0;
while(steps<maxSteps){
  const r = tape[pos];
  const e = T[state][r];
  if(!e){ console.log("HALT at step",steps,"state",state,"read",r); console.log(show()); break; }
  tape[pos]=e[0]; pos+=e[1]; state=e[2]; steps++;
  if(pos<minp) minp=pos; if(pos>maxp) maxp=pos;
  if(mode==="left" && pos===minp+0 ){ console.log(steps, show()); }
}
let c=0; for(let i=minp;i<=maxp;i++) c+=tape[i];
console.log("steps",steps,"ones",c,"width",maxp-minp+1);
