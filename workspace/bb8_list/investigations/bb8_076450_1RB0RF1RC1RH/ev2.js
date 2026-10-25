// Literal simulator reporting canonical events. usage: node ev2.js maxSteps [word state headIdx]
// M(p,x,y): left of head = p 10101000 (0110)^x 1010 (0101)^(y+1), state H reading 0, right = 1 0 0 blank.
// L(p,X): left = p 10101000 (0110)^X, state F reading 1, right = 1 1 0 1 blank (head on first 1).
const TM = process.env.TM || "1RB0RF_1RC1RH_0RD0RG_1LE0RB_0LA0LC_0LD0RA_1RD0LB_0RF---";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const maxSteps=+process.argv[2];
const N=1<<27; const tape=new Uint8Array(N); let base=N>>2; let pos=base, st=0;
if(process.argv[3]){ const w=process.argv[3]; for(let i=0;i<w.length;i++) tape[base+i]=+w[i]; st="ABCDEFGH".indexOf(process.argv[4]); pos=base+(+process.argv[5]); }
let lo=Math.min(pos,base), hi=Math.max(pos, base+(process.argv[3]||"").length);
function leftstr(){ let a=lo; while(a<pos&&tape[a]===0)a++; let s=""; for(let i=a;i<pos;i++) s+=tape[i]; return s; }
const reM=/^(.*?)10101000((?:0110)*)1010((?:0101)+)$/, reL=/^(.*?)10101000((?:0110)*)$/;
let steps=0; const quiet=+(process.env.QUIET||0); let lastM=null, nM=0;
const STOPL=+(process.env.STOPL||0);
while(steps<maxSteps){
  const r=tape[pos]; const e=T[st][r]; if(!e){ if(lastM&&quiet) console.log(lastM); console.log("HALT",steps,"state","ABCDEFGH"[st], "left", leftstr().slice(-60)); process.exit(0);}
  tape[pos]=e[0]; pos+=e[1]; st=e[2]; steps++; if(pos<lo)lo=pos; if(pos>hi)hi=pos;
  if(pos+4>=hi){
    let okr=true; for(let i=pos+4;i<=hi;i++) if(tape[i]) {okr=false;break;}
    if(okr && st===7 && tape[pos]===0 && tape[pos+1]===1 && tape[pos+2]===0 && tape[pos+3]===0) {
      const s=leftstr(); const m=reM.exec(s); if(m){ const line="M "+steps+" p="+m[1]+" x="+m[2].length/4+" y="+(m[3].length/4-1); nM++; if(quiet){ if(!lastM) console.log(line); lastM=line;} else console.log(line);} }
    if(okr && st===5 && tape[pos]===1 && tape[pos+1]===1 && tape[pos+2]===0 && tape[pos+3]===1) {
      const s=leftstr(); const m=reL.exec(s); if(m){ if(lastM&&quiet) console.log(lastM); lastM=null; console.log("L",steps,"p="+m[1],"X="+m[2].length/4); if(STOPL && steps>1) {console.log("STOP"); process.exit(0);} } }
  }
  if(pos<2||pos>N-3){console.log("OVERFLOW");process.exit(0);}
}
if(lastM&&quiet) console.log(lastM);
console.log("LIMIT",steps);
