// Literal simulator; prints RLE tape each time the head reaches a new leftmost cell in state A.
// Usage: node lefta.js maxSteps [everyLeft]
const TM = process.env.TM || "1RB0RH_1LC1LB_---1LD_0RE0LE_0LG1LF_1RE0LD_1RG0LA_1RA1RH";
function parse(tm){ return tm.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];})); }
const T = parse(TM);
const N = 1<<28;
const tape = new Uint8Array(N);
let pos = N>>1, state = 0, steps = 0, minp = pos, maxp = pos;
function rle(lo,hi){ // runs from lo..hi
  let out=[]; let i=lo;
  while(i<=hi){ let j=i; while(j<=hi && tape[j]===tape[i]) j++; const n=j-i; out.push((tape[i]?"1":"0")+(n>1?"^"+n:"")); i=j; }
  return out.join(" ");
}
const maxSteps = +(process.argv[2]||1e6);
const all = process.argv[3]==="all";
while(steps<maxSteps){
  const r = tape[pos]; const e = T[state][r];
  if(!e){ console.log("HALT at step",steps,"state","ABCDEFGH"[state],"read",r, "pos-minp",pos-minp); let c=0; for(let i=minp;i<=maxp;i++) c+=tape[i]; console.log("ones",c); break; }
  tape[pos]=e[0]; pos+=e[1]; state=e[2]; steps++;
  if(pos<minp){ minp=pos; if(all || state===0){ let hi=maxp; while(hi>pos && tape[hi]===0) hi--; console.log(steps, "ABCDEFGH"[state], rle(pos+1,hi)); } }
  if(pos>maxp){ maxp=pos; }
}
