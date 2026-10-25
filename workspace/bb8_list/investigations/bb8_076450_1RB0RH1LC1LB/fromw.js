// Literal simulator from a constructed tape: 0^inf A>0 <word> 0^inf. Prints compressed tape at new-leftmost A events.
// Usage: node fromw.js "<python-like word expr using W(...)>" maxSteps maxEvents
const TM = process.env.TM || "1RB0RH_1LC1LB_---1LD_0RE0LE_0LG1LF_1RE0LD_1RG0LA_1RA1RH";
function parse(tm){ return tm.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];})); }
const T = parse(TM);
// word spec: tokens like 1^5 0 (001)^3 separated by spaces
function expand(spec){ let s=""; for(const tok of spec.trim().split(/\s+/).filter(x=>x)){ let m=tok.match(/^\(?([01]+)\)?(?:\^(\d+))?$/); if(!m) throw "bad "+tok; s+=m[1].repeat(m[2]?+m[2]:1);} return s; }
const word = expand(process.argv[2]);
const N = 1<<26;
const tape = new Uint8Array(N);
let pos = N>>2; for(let i=0;i<word.length;i++) tape[pos+1+i]=+word[i];
let state=0, steps=0, minp=pos, maxp=pos+word.length;
function toks(lo,hi){ let out=[]; let i=lo;
  while(i<=hi){ let j=i; while(j<=hi && tape[j]===tape[i]) j++; const n=j-i; out.push((tape[i]?"1":"0")+(n>1?"^"+n:"")); i=j; } return out; }
function comp(t){ let out=[]; let i=0;
  while(i<t.length){ let best=null;
    for(let L=1;L<=6;L++){ if(i+L>t.length) break; let k=1;
      while(i+(k+1)*L<=t.length){ let ok=true; for(let q=0;q<L;q++) if(t[i+k*L+q]!==t[i+q]){ok=false;break;} if(!ok) break; k++; }
      if(k>=3 && (!best || k*L>best.k*best.L)) best={L,k}; }
    if(best){ out.push("("+t.slice(i,i+best.L).join(" ")+")x"+best.k); i+=best.L*best.k; } else { out.push(t[i]); i++; } }
  return out.join(" "); }
function show(){ let lo=minp, hi=maxp; while(lo<pos && tape[lo]===0) lo++; while(hi>pos && tape[hi]===0) hi--;
  return comp(toks(lo,pos-1))+" ["+"ABCDEFGH"[state]+tape[pos]+"] "+comp(toks(pos+1,hi)); }
const maxSteps = +(process.argv[3]||1e7), maxEv = +(process.argv[4]||20);
let ev=0;
while(steps<maxSteps && ev<maxEv){
  const r = tape[pos]; const e = T[state][r];
  if(!e){ console.log("HALT at step",steps); console.log(show()); let c=0; for(let i=minp;i<=maxp;i++) c+=tape[i]; console.log("ones",c); break; }
  tape[pos]=e[0]; pos+=e[1]; state=e[2]; steps++;
  if(pos<minp){ minp=pos; if(state===0){ let hi=maxp; while(hi>pos && tape[hi]===0) hi--; ev++; console.log(ev, steps, comp(toks(pos+1,hi))); } }
  if(pos>maxp){ maxp=pos; }
}
if(process.argv[5]) console.log(show());
