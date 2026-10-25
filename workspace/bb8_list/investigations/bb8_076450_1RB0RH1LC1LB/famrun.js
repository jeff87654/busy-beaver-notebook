// Main-run family printer that suppresses plain R1 transitions ([n;k+1]... -> [n+9;k]... with the rest unchanged).
const TM = process.env.TM || "1RB0RH_1LC1LB_---1LD_0RE0LE_0LG1LF_1RE0LD_1RG0LA_1RA1RH";
function parse(tm){ return tm.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];})); }
const T = parse(TM);
const N = 1<<29; const tape = new Uint8Array(N);
let pos = N>>1, state=0, steps=0, minp=pos, maxp=pos;
function famParseTape(lo,hi){ // returns {lead,segs} or null; fast scan
  let segs=[]; let i=lo; let z=0; let first=true; let lead=0;
  while(i<=hi){ if(tape[i]===0){z++; i++; continue;} let j=i; while(j<=hi&&tape[j]===1) j++; const l=j-i;
    if(first){ lead=z; segs.push([l,0]); first=false; } else if(z===1){ segs.push([l,0]); } else if(z===2&&l===1){ segs[segs.length-1][1]++; } else return null;
    z=0; i=j; }
  if(first) return null; return {lead,segs}; }
function fmt(f){ return "z"+f.lead+" "+f.segs.map(s=>"["+s[0]+";"+s[1]+"]").join(""); }
const maxSteps=+(process.argv[2]||1e8); let prev=null; let ev=0, supp=0;
function isR1(p,f){ if(!p||p.lead!==3||f.lead!==3||p.segs.length!==f.segs.length) return false;
  if(p.segs[0][1]<1) return false; if(f.segs[0][0]!==p.segs[0][0]+9||f.segs[0][1]!==p.segs[0][1]-1) return false;
  for(let i=1;i<p.segs.length;i++) if(p.segs[i][0]!==f.segs[i][0]||p.segs[i][1]!==f.segs[i][1]) return false; return true; }
while(steps<maxSteps){ const r=tape[pos]; const e=T[state][r];
  if(!e){ let c=0; for(let i=minp;i<=maxp;i++) c+=tape[i]; console.log("HALT",steps,"ones",c); break; }
  tape[pos]=e[0]; pos+=e[1]; state=e[2]; steps++;
  if(pos<minp){ minp=pos; if(state===0){ let hi=maxp; while(hi>pos&&tape[hi]===0) hi--; const f=famParseTape(pos+1,hi);
      if(f){ ev++; if(isR1(prev,f)){ supp++; } else { if(supp>0) console.log("   ... R1 x"+supp); supp=0; console.log(ev, steps, fmt(f)); } prev=f; } } }
  if(pos>maxp) maxp=pos; }
if(supp>0) console.log("   ... R1 x"+supp);
console.log("end",steps,"width",maxp-minp+1);
