// Literal simulator printing family configs at new-leftmost-A events.
// Family: A>0 0^z [n;k][m1;j1]...[mr;jr] where [m;j] = (0 1^m)(001)^j ; first segment has leading 0^z (z>=3) instead of single 0.
// Usage: node fam.js "<word spec>" maxSteps maxEvents [all]
const TM = process.env.TM || "1RB0RH_1LC1LB_---1LD_0RE0LE_0LG1LF_1RE0LD_1RG0LA_1RA1RH";
function parse(tm){ return tm.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];})); }
const T = parse(TM);
function expand(spec){ let s=""; for(const tok of spec.trim().split(/\s+/).filter(x=>x)){ let m=tok.match(/^\(?([01]+)\)?(?:\^(\d+))?$/); if(!m) throw "bad "+tok; s+=m[1].repeat(m[2]?+m[2]:1);} return s; }
const word = expand(process.argv[2]);
const N = 1<<27;
const tape = new Uint8Array(N);
let pos = N>>2; for(let i=0;i<word.length;i++) tape[pos+1+i]=+word[i];
let state=0, steps=0, minp=pos, maxp=pos+word.length;
function runs(lo,hi){ // list of [sep,len]
  let out=[]; let i=lo; let z=0;
  while(i<=hi){ if(tape[i]===0){z++; i++; continue;} let j=i; while(j<=hi&&tape[j]===1) j++; out.push([z,j-i]); z=0; i=j; }
  return out; }
function famParse(rs){
  if(rs.length===0) return null;
  let segs=[]; let lead=rs[0][0];
  for(let i=0;i<rs.length;i++){
    const [s,l]=rs[i];
    if(i===0 || s===1){ segs.push([l,0]); }
    else if(s===2 && l===1){ segs[segs.length-1][1]++; }
    else return null;
  }
  return {lead,segs};
}
function fmt(f){ return "z"+f.lead+" "+f.segs.map(s=>"["+s[0]+";"+s[1]+"]").join(""); }
const maxSteps = +(process.argv[3]||1e7), maxEv = +(process.argv[4]||20), all=process.argv[5]==="all";
let ev=0;
while(steps<maxSteps && ev<maxEv){
  const r = tape[pos]; const e = T[state][r];
  if(!e){ let c=0; for(let i=minp;i<=maxp;i++) c+=tape[i]; console.log("HALT", steps, "ones", c); break; }
  tape[pos]=e[0]; pos+=e[1]; state=e[2]; steps++;
  if(pos<minp){ minp=pos; if(state===0){ let hi=maxp; while(hi>pos && tape[hi]===0) hi--; const rs=runs(pos+1,hi); const f=famParse(rs);
      if(f){ ev++; console.log(ev, steps, fmt(f)); } else if(all){ console.log("  -", steps, rs.map(x=>x[0]+":"+x[1]).join(" ")); } } }
  if(pos>maxp){ maxp=pos; }
}
