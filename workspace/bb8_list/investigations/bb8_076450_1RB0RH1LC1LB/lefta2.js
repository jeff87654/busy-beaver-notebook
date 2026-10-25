// Literal simulator; prints compressed RLE tape at new-leftmost state-A events (collapses repeated token groups).
const TM = process.env.TM || "1RB0RH_1LC1LB_---1LD_0RE0LE_0LG1LF_1RE0LD_1RG0LA_1RA1RH";
function parse(tm){ return tm.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];})); }
const T = parse(TM);
const N = 1<<28;
const tape = new Uint8Array(N);
let pos = N>>1, state = 0, steps = 0, minp = pos, maxp = pos;
function toks(lo,hi){ let out=[]; let i=lo;
  while(i<=hi){ let j=i; while(j<=hi && tape[j]===tape[i]) j++; const n=j-i; out.push((tape[i]?"1":"0")+(n>1?"^"+n:"")); i=j; } return out; }
function comp(t){ // collapse repeated groups of length 1..4 tokens
  let out=[]; let i=0;
  while(i<t.length){ let best=null;
    for(let L=1;L<=6;L++){ if(i+L>t.length) break; let k=1;
      while(i+(k+1)*L<=t.length){ let ok=true; for(let q=0;q<L;q++) if(t[i+k*L+q]!==t[i+q]){ok=false;break;} if(!ok) break; k++; }
      if(k>=3 && (!best || k*L>best.k*best.L)) best={L,k}; }
    if(best){ out.push("("+t.slice(i,i+best.L).join(" ")+")x"+best.k); i+=best.L*best.k; } else { out.push(t[i]); i++; } }
  return out.join(" "); }
const maxSteps = +(process.argv[2]||1e6);
const filt = process.argv[3]||"";
let cnt=0;
while(steps<maxSteps){
  const r = tape[pos]; const e = T[state][r];
  if(!e){ console.log("HALT at step",steps,"state","ABCDEFGH"[state],"read",r); let c=0; for(let i=minp;i<=maxp;i++) c+=tape[i]; console.log("ones",c); let hi=maxp; while(hi>pos && tape[hi]===0) hi--; console.log(comp(toks(pos+1,hi))); break; }
  tape[pos]=e[0]; pos+=e[1]; state=e[2]; steps++;
  if(pos<minp){ minp=pos; if(state===0){ let hi=maxp; while(hi>pos && tape[hi]===0) hi--; const s=comp(toks(pos+1,hi)); cnt++; if(!filt || !new RegExp(filt).test(s)) console.log(cnt, steps, s); } }
  if(pos>maxp){ maxp=pos; }
}
console.log("end steps",steps, "width", maxp-minp+1);
