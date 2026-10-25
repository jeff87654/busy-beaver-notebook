// Literal simulator reporting events. usage: node ev.js maxSteps [word state headIdx]
// Event M: state H reading 0, cells to right = 1 0 0 then blank (right edge).
// Event L: state F reading 1, right = 1 0 1 then blank.
const TM = process.env.TM || "1RB0RF_1RC1RH_0RD0RG_1LE0RB_0LA0LC_0LD0RA_1RD0LB_0RF---";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const maxSteps=+process.argv[2];
const N=1<<27; const tape=new Uint8Array(N); let base=N>>2; let pos=base, st=0;
if(process.argv[3]){ const w=process.argv[3]; for(let i=0;i<w.length;i++) tape[base+i]=+w[i]; st="ABCDEFGH".indexOf(process.argv[4]); pos=base+(+process.argv[5]); }
let lo=Math.min(pos,base), hi=Math.max(pos, base+(process.argv[3]||"").length);
function rl(s){ let out=[]; let i=0;
  while(i<s.length){ let best=null;
    for(const u of ["0110","0101","1010","0011","01","10"]){ let k=0; while(s.substr(i+k*u.length,u.length)===u) k++;
      if(k>=2 && (!best || k*u.length>best.k*best.u.length)) best={u,k}; }
    if(best){ out.push("("+best.u+")^"+best.k); i+=best.k*best.u.length; } else { out.push(s[i]); i++; } }
  return out.join(" "); }
function leftstr(){ let a=lo; while(a<pos&&tape[a]===0)a++; let s=""; for(let i=a;i<pos;i++) s+=tape[i]; return s; }
let steps=0;
const EV=process.env.EV||"ML";
while(steps<maxSteps){
  const r=tape[pos]; const e=T[st][r]; if(!e){console.log("HALT",steps,"state","ABCDEFGH"[st], rl(leftstr())); process.exit(0);}
  tape[pos]=e[0]; pos+=e[1]; st=e[2]; steps++; if(pos<lo)lo=pos; if(pos>hi)hi=pos;
  if(pos+4>=hi){
    if(EV.includes("M") && st===7 && tape[pos]===0 && tape[pos+1]===1 && tape[pos+2]===0 && tape[pos+3]===0 && pos+3>=hi-0) {
      let ok=true; for(let i=pos+4;i<=hi;i++) if(tape[i]) ok=false; if(ok) console.log("M",steps,rl(leftstr()));
    }
    if(EV.includes("L") && st===5 && tape[pos]===1 && tape[pos+1]===1 && tape[pos+2]===0 && tape[pos+3]===1) {
      let ok=true; for(let i=pos+4;i<=hi;i++) if(tape[i]) ok=false; if(ok) console.log("L",steps,rl(leftstr()));
    }
  }
  if(pos<2||pos>N-3){console.log("OVERFLOW");process.exit(0);}
}
console.log("LIMIT",steps);
