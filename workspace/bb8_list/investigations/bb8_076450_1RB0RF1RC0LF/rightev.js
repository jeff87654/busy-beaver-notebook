// Literal simulation; print compressed tape at right-edge B0 events, skipping the repetitive transfer shape.
const TM = process.env.TM || "1RB0RF_1RC0LF_0RD0RB_1LE1LG_0LA0LC_0LD1RH_1RA1LC_1RF---";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const N = 1<<25; const tape = new Uint8Array(N);
let pos = N>>1, state=0, steps=0, minp=pos, maxp=pos;
function rl(s){ // run-length encode with blocks 010, 10, 01, 1, 0111 greedy
  let out=[]; let i=0;
  while(i<s.length){
    let best=null;
    for(const u of ["010","10","01","0111","1","100","110","001"]){
      let k=0; while(s.substr(i+k*u.length,u.length)===u) k++;
      if(k>=2 && (!best || k*u.length>best.k*best.u.length)) best={u,k};
    }
    if(best){ out.push("("+best.u+")^"+best.k); i+=best.k*best.u.length; }
    else { out.push(s[i]); i++; }
  }
  return out.join(" ");
}
function show(){
  let lo=minp, hi=maxp;
  while(lo<pos && tape[lo]===0) lo++;
  while(hi>pos && tape[hi]===0) hi--;
  const left = Array.from(tape.subarray(lo,pos)).join("");
  return rl(left)+" ["+"ABCDEFGH"[state]+tape[pos]+"]";
}
const maxSteps = +(process.argv[2]||1e6);
const re = /\(1\)\^\d+ \(01\)\^\d+ 0 \[B0\]$/;
while(steps<maxSteps){
  const r = tape[pos]; const e = T[state][r];
  if(!e){ console.log("HALT at step",steps,"state","ABCDEFGH"[state],"read",r); console.log(show()); break; }
  tape[pos]=e[0]; pos+=e[1]; state=e[2]; steps++;
  if(pos>maxp){ maxp=pos; if(state===1){ const s=show(); if(!re.test(s)) console.log(steps, s);} }
  if(pos<minp) minp=pos;
}
let c=0; for(let i=minp;i<=maxp;i++) c+=tape[i];
console.log("steps",steps,"ones",c,"width",maxp-minp+1);
