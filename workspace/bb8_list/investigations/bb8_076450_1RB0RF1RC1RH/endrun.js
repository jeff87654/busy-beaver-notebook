// Run M(p,r,y) literally until HALT or first L event or first M event with x>r+3 (next level) ; print summary.
// usage: node endrun.js p r y [maxSteps]
const TM = process.env.TM || "1RB0RF_1RC1RH_0RD0RG_1LE0RB_0LA0LC_0LD0RA_1RD0LB_0RF---";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const [p, r, y] = [process.argv[2], +process.argv[3], +process.argv[4]];
const maxSteps = +(process.argv[5]||4e10);
const w = p + "10101000" + "0110".repeat(r) + "1010" + "0101".repeat(y+1) + "0100";
const N = Math.max(1<<22, 16*w.length*64); const tape=new Uint8Array(N); const base=N>>2;
for(let i=0;i<w.length;i++) tape[base+i]=+w[i];
let pos=base+w.length-4, st=7, lo=base, hi=base+w.length-1, steps=0;
function leftstr(){ let a=lo; while(a<pos&&tape[a]===0)a++; let s=""; for(let i=a;i<pos;i++) s+=tape[i]; return s; }
const reM=/^(.*?)10101000((?:0110)*)1010((?:0101)+)$/, reL=/^(.*?)10101000((?:0110)*)$/;
let out=null;
while(steps<maxSteps){
  const e=T[st][tape[pos]];
  if(!e){ let c=0; for(let i=lo;i<=hi;i++) c+=tape[i]; out={res:"HALT",steps,ones:c,state:"ABCDEFGH"[st],pos:pos-lo,width:hi-lo+1}; break; }
  tape[pos]=e[0]; pos+=e[1]; st=e[2]; steps++; if(pos<lo)lo=pos; if(pos>hi)hi=pos;
  if(pos+4>=hi && ((st===7&&tape[pos]===0)||(st===5&&tape[pos]===1))){
    let okr=true; for(let i=pos+4;i<=hi;i++) if(tape[i]) {okr=false;break;}
    if(okr && st===7 && tape[pos+1]===1 && tape[pos+2]===0 && tape[pos+3]===0){ const m=reM.exec(leftstr()); if(m && m[2].length/4 > r+3){ out={res:"M",steps,p:m[1],x:m[2].length/4,y:m[3].length/4-1}; break; } }
    if(okr && st===5 && tape[pos+1]===1 && tape[pos+2]===0 && tape[pos+3]===1){ const m=reL.exec(leftstr()); if(m){ out={res:"L",steps,p:m[1],X:m[2].length/4}; break; } }
  }
  if(pos<2||pos>N-3){ out={res:"OVERFLOW",steps}; break; }
}
if(!out) out={res:"LIMIT",steps};
out.start={p,r,y};
console.log(JSON.stringify(out));
