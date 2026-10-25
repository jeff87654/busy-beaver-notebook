// Literal simulator: print compressed tape whenever head bounces at the left or right end of the written region.
// usage: node bounce.js maxSteps side(L|R|B) gap
const TM = process.env.TM || "1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const N = 1<<27; const tape = new Uint8Array(N);
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
  const left = Array.from(tape.subarray(lo,pos)).join("");
  const right = Array.from(tape.subarray(pos+1,hi+1)).join("");
  return compress(left)+" ["+"ABCDEFGH"[state]+tape[pos]+"] "+compress(right);
}
const maxSteps = +(process.argv[2]||1e6);
const side = process.argv[3]||"B";
const gap = +(process.argv[4]||100);
let lastL=-1e9, lastR=-1e9;
let lo1=pos, hi1=pos; // extent of ones approx: track min/max position of any written 1
while(steps<maxSteps){
  const r = tape[pos]; const e = T[state][r];
  if(!e){ console.log("HALT at step",steps,"state","ABCDEFGH"[state],"read",r); console.log(show()); break; }
  tape[pos]=e[0]; pos+=e[1]; state=e[2]; steps++;
  if(pos<minp) minp=pos; if(pos>maxp) maxp=pos;
  if((side==="L"||side==="B") && pos<=minp+1 && steps-lastL>gap){ // at left end
    // recompute: is there any 1 left of pos?
    let any=false; for(let i=minp;i<pos;i++) if(tape[i]){any=true;break;}
    if(!any){ console.log("L",steps, show()); lastL=steps; }
  }
  if((side==="R"||side==="B") && pos>=maxp-1 && steps-lastR>gap){
    let any=false; for(let i=pos+1;i<=maxp;i++) if(tape[i]){any=true;break;}
    if(!any){ console.log("R",steps, show()); lastR=steps; }
  }
}
