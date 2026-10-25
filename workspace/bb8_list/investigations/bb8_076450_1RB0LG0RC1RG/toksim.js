// Literal simulator printing tapes tokenized into gap-words: "1"->x "10"->a "100"->b "1000"->c
// Usage: node toksim.js maxSteps mode [every]
const TM = process.env.TM || "1RB0LG_0RC1RG_1LD1RF_1RE---_0LH1LC_1RA1LA_1RH0RE_0LF0RH";
function parse(tm){
  return tm.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---"||e[2]==="Z") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
}
const T = parse(TM);
const N = 1<<27;
const tape = new Uint8Array(N);
let pos = N>>1, state = 0, steps = 0;
let minp = pos, maxp = pos;
function compress(s){
  let out=[]; let i=0;
  while(i<s.length){
    let best=null;
    for(let L=1;L<=10;L++){
      const u=s.substr(i,L); if(u.length<L) break;
      if(u.indexOf('[')>=0||u.indexOf(']')>=0) break;
      let k=1; while(s.substr(i+k*L,L)===u) k++;
      if(k>=2 && k*L>=Math.max(3,2*L) && (!best || k*L>best.k*best.L)) best={u,k,L};
    }
    if(best){ out.push("("+best.u+")"+best.k); i+=best.k*best.L; }
    else { out.push(s[i]); i++; }
  }
  return out.join(" ");
}
const L="xabcdefghij";
function tok(str){ // str of 0/1 beginning with 1 (or empty)
  let out=""; let i=0;
  // leading zeros
  let lz=0; while(i<str.length && str[i]==='0'){lz++;i++;}
  if(lz) out+="0".repeat(lz);
  while(i<str.length){ // str[i]=='1'
    i++; let z=0; while(i<str.length && str[i]==='0'){z++;i++;}
    out+= z<L.length? L[z] : "<"+z+">";
  }
  return out;
}
function show(){
  let lo=minp, hi=maxp;
  while(lo<pos && tape[lo]===0) lo++;
  while(hi>pos && tape[hi]===0) hi--;
  const left = Array.from(tape.subarray(lo,pos)).join("");
  const right = Array.from(tape.subarray(pos,hi+1)).join("");
  // tokenise left part fully; right starts at head cell
  return compress(tok(left))+" |"+"ABCDEFGH"[state]+"| "+right.substr(0,1)+" "+compress(tok(right.substr(1)));
}
const maxSteps = +(process.argv[2]||1e6);
const mode = process.argv[3]||"left";
while(steps<maxSteps){
  const r = tape[pos];
  const e = T[state][r];
  if(!e){ console.log("HALT at step",steps,"state","ABCDEFGH"[state],"read",r); console.log(show()); break; }
  tape[pos]=e[0]; pos+=e[1]; state=e[2]; steps++;
  let nl=false, nr=false;
  if(pos<minp){minp=pos; nl=true;} if(pos>maxp){maxp=pos; nr=true;}
  if(mode==="left" && nl){ console.log(steps, show()); }
  if(mode==="right" && nr){ console.log(steps, show()); }
}
let c=0; for(let i=minp;i<=maxp;i++) c+=tape[i];
console.log("steps",steps,"ones",c,"width",maxp-minp+1);
