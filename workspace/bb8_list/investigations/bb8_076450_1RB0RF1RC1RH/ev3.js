// literal sim from word; print compressed tape whenever head reaches a new rightmost or leftmost cell (dedup by shape), and on halt.
const TM = process.env.TM || "1RB0RF_1RC1RH_0RD0RG_1LE0RB_0LA0LC_0LD0RA_1RD0LB_0RF---";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const maxSteps=+process.argv[2];
const N=1<<26; const tape=new Uint8Array(N); let base=N>>2; let pos=base, st=0;
const w=process.argv[3]; for(let i=0;i<w.length;i++) tape[base+i]=+w[i]; st="ABCDEFGH".indexOf(process.argv[4]); pos=base+(+process.argv[5]);
let lo=Math.min(pos,base), hi=Math.max(pos, base+w.length-1);
function rl(s){ let out=[]; let i=0;
  while(i<s.length){ let best=null;
    for(const u of ["0110","0101","1010","0011","1100","1001","01","10"]){ let k=0; while(s.substr(i+k*u.length,u.length)===u) k++;
      if(k>=2 && (!best || k*u.length>best.k*best.u.length)) best={u,k}; }
    if(best){ out.push("("+best.u+")^"+best.k); i+=best.k*best.u.length; } else { out.push(s[i]); i++; } }
  return out.join(" "); }
function show(){ let a=lo,b=hi; while(a<pos&&tape[a]===0)a++; while(b>pos&&tape[b]===0)b--; let L="",R=""; for(let i=a;i<pos;i++) L+=tape[i]; for(let i=pos+1;i<=b;i++) R+=tape[i]; return rl(L)+" ["+"ABCDEFGH"[st]+tape[pos]+"] "+rl(R); }
let steps=0, prev="";
while(steps<maxSteps){
  const e=T[st][tape[pos]]; if(!e){ console.log("HALT",steps, show()); let c=0; for(let i=lo;i<=hi;i++) c+=tape[i]; console.log("ones",c); process.exit(0);}
  tape[pos]=e[0]; pos+=e[1]; st=e[2]; steps++;
  let ev=false; if(pos<lo){lo=pos;ev=true;} if(pos>hi){hi=pos;ev=true;}
  if(ev || process.env.ALL){ const s=show(); const sh=s.replace(/\^\d+/g,"^N"); if(sh!==prev || process.env.ALL) console.log(steps,s); prev=sh; }
}
console.log("LIMIT");
