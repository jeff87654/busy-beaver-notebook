// Exact literal checks of the level rules (blank tape outside the word, head on the word's first cell).
// A run passes if it reaches exactly the predicted configuration (full tape, state, head) with no halt.
// usage: node check_rules.js [scale]
const TM = "1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const rep=(u,k)=>u.repeat(k);
const Lv=N=>({w:"1"+rep("10",N)+"1", s:4});             // E reading 1, right (10)^N 1
const al=(A,n)=>({w:"1"+rep("01",A)+"1010110101"+rep("01",n), s:0});
const be=(A,n)=>({w:"1"+rep("01",A)+"1010110111"+rep("10",n)+"1", s:0});
const SZ=1<<24; const tape=new Uint8Array(SZ);
function run(src,dst,maxSteps){
  tape.fill(0); const base=SZ>>1;
  for(let i=0;i<src.w.length;i++) tape[base+i]=+src.w[i];
  let pos=base, st=src.s, steps=0, lo=base, hi=base+src.w.length;
  const dw=dst.w, dl=dw.length;
  while(steps<maxSteps){
    // check target: head at left edge, state match, full tape equality
    if(st===dst.s && tape[pos]===1 && tape[pos-1]===0 && tape[pos-2]===0 && tape[pos-3]===0){
      let ok=true;
      for(let i=lo;i<pos;i++) if(tape[i]){ok=false;break;}
      if(ok){ for(let i=0;i<dl;i++) if(tape[pos+i]!==+dw[i]){ok=false;break;} }
      if(ok){ for(let i=pos+dl;i<=hi;i++) if(tape[i]){ok=false;break;} }
      if(ok) return {ok:true, steps};
    }
    const e=T[st][tape[pos]];
    if(!e) return {ok:false, why:"halt", steps};
    tape[pos]=e[0]; pos+=e[1]; st=e[2]; steps++;
    if(pos<lo) lo=pos; if(pos>hi) hi=pos;
    if(pos<1||pos>SZ-2) return {ok:false, why:"overflow"};
  }
  return {ok:false, why:"limit", steps};
}
const sc=+(process.argv[2]||1);
let total=0, fails=0; const stepsOut={};
function chk(name, src, dst, key, lim){
  const r=run(src,dst,lim||2e8); total++;
  if(!r.ok){ fails++; console.log("FAIL",name,key,r.why,r.steps); }
  (stepsOut[name]=stepsOut[name]||[]).push([key,r.steps]);
}
for(let N=1;N<=Math.round(301*sc);N+=2) chk("LvOdd",Lv(N),Lv(4*N+6),N);
for(let N=4;N<=Math.round(400*sc);N+=2) chk("LvEven",Lv(N),be(N-3,10),N);
for(let A=3;A<=Math.round(21*sc);A+=2) for(let n=4;n<=Math.round(60*sc);n+=2) chk("be",be(A,n),al(A-2,4*n+15),[A,n]);
for(let A=3;A<=Math.round(21*sc);A+=2) for(let n=1;n<=Math.round(61*sc);n+=2) chk("al",al(A,n),be(A-2,4*n+20),[A,n]);
for(let n=1;n<=Math.round(101*sc);n+=2) chk("al1",al(1,n),Lv(16*n+95),n);
console.log("total",total,"fails",fails);
require("fs").writeFileSync("check_rules_steps.json", JSON.stringify(stepsOut));
