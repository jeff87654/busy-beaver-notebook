// Literal simulator from a given configuration; prints compressed tape at left-edge and/or right-edge visits.
// usage: node trace.js "leftword" "State" "rightword(starting with head cell)" maxSteps mode(L|R|B) gap
// words: strings of 0/1 with optional (u)^k repetitions, e.g. "(10)^20 1"
const TM = process.env.TM || "1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
function expand(w){ return w.replace(/\(([01]+)\)\^(\d+)/g,(m,u,k)=>u.repeat(+k)).replace(/\s+/g,""); }
const N = 1<<27; const tape = new Uint8Array(N);
const lw=expand(process.argv[2]), st=process.argv[3], rw=expand(process.argv[4]);
let pos = N>>1;
for(let i=0;i<lw.length;i++) tape[pos-lw.length+i]=+lw[i];
for(let i=0;i<rw.length;i++) tape[pos+i]=+rw[i];
let state="ABCDEFGH".indexOf(st), steps=0, minp=pos-lw.length, maxp=pos+rw.length;
const Z=30;
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
const maxSteps = +(process.argv[5]||1e6);
const mode = process.argv[6]||"B";
const gap = +(process.argv[7]||100);
let lastL=-1e18, lastR=-1e18;
console.log(0, show());
while(steps<maxSteps){
  const r = tape[pos]; const e = T[state][r];
  if(!e){ console.log("HALT at step",steps,"state","ABCDEFGH"[state],"read",r); console.log(show()); break; }
  tape[pos]=e[0]; pos+=e[1]; state=e[2]; steps++;
  if(pos<minp) minp=pos; if(pos>maxp) maxp=pos;
  if((mode==="L"||mode==="B") && e[1]<0 && steps-lastL>gap && tape[pos-1]===0){
    let any=false; for(let i=pos-Z;i<pos;i++) if(tape[i]){any=true;break;}
    if(!any){ console.log("L",steps, show()); lastL=steps; }
  }
  if((mode==="R"||mode==="B") && e[1]>0 && steps-lastR>gap && tape[pos+1]===0){
    let any=false; for(let i=pos+1;i<=pos+Z;i++) if(tape[i]){any=true;break;}
    if(!any){ console.log("R",steps, show()); lastR=steps; }
  }
}
console.log("END",steps, show().slice(0,300));
