// Literal simulator from blank tape or given word; print full tape (raw) for steps in [from,to].
// usage: node trace.js from to [word state headIndex]
const TM = process.env.TM || "1RB0RF_1RC1RH_0RD0RG_1LE0RB_0LA0LC_0LD0RA_1RD0LB_0RF---";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const from=+process.argv[2], to=+process.argv[3];
const N=1<<24; const tape=new Uint8Array(N); let base=N>>1; let pos=base, st=0;
if(process.argv[4]){ const w=process.argv[4]; for(let i=0;i<w.length;i++) tape[base+i]=+w[i]; st="ABCDEFGH".indexOf(process.argv[5]); pos=base+(+process.argv[6]); }
let lo=Math.min(pos,base), hi=Math.max(pos, base+(process.argv[4]||"").length);
let steps=0;
function show(){ let a=lo,b=hi; while(a<pos&&tape[a]===0)a++; while(b>pos&&tape[b]===0)b--; let s=""; for(let i=a;i<=b;i++){ if(i===pos) s+="["+"ABCDEFGH"[st]+tape[i]+"]"; else s+=tape[i]; } return s; }
while(steps<to){
  if(steps>=from) console.log(steps, show());
  const e=T[st][tape[pos]]; if(!e){console.log("HALT",steps,show()); break;}
  tape[pos]=e[0]; pos+=e[1]; st=e[2]; steps++; if(pos<lo)lo=pos; if(pos>hi)hi=pos;
}
