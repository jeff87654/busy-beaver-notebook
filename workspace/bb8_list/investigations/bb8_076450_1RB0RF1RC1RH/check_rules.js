// Exact literal checks of the rules (no acceleration).
// A configuration is written as  <left word> <state> <head+right word>, blank elsewhere.
// Families (tape order):
//   P      = p 10101000                        (p = left context, never visited)
//   L(p,X) = P (0110)^X            F> 1101     (F reads the first 1)
//   M(p,x,y)= P (0110)^x 1010 (0101)^(y+1) H> 0100
// Rules:
//   Mstep : M(p,x+3,y) -> M(p,x,36y+452)
//   Start : L(p,x+5)   -> M(p,x,272)
//   End1  : M(1,0,y)   -> L(11010010,y+8)      (p = "1", blank to its left)
//   Halt2 : M(p,2,y)   -> halts (H reading 1), ones = ones(p)+72y+898+... (reported)
// usage: node check_rules.js [nctx] [ymax] [xmax]
const TM = "1RB0RF_1RC1RH_0RD0RG_1LE0RB_0LA0LC_0LD0RA_1RD0LB_0RF---";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const SN="ABCDEFGH";
const N=1<<24; const tape=new Uint8Array(N);
function rep(s,n){ return s.repeat(n); }
function P(p){ return p+"10101000"; }
function L(p,X){ return [P(p)+rep("0110",X), "F", "1101"]; }
function M(p,x,y){ return [P(p)+rep("0110",x)+"1010"+rep("0101",y+1), "H", "0100"]; }
function run(start, target, maxSteps){
  // place start with left word ending at base
  const [lw, st0, rw] = start; const base=N>>1;
  tape.fill(0);
  for(let i=0;i<lw.length;i++) tape[base-lw.length+i]=+lw[i];
  for(let i=0;i<rw.length;i++) tape[base+i]=+rw[i];
  let pos=base, st=SN.indexOf(st0), lo=base-lw.length, hi=base+rw.length-1, steps=0;
  const leftEdge = base-lw.length; // start of left word (context p starts here)
  let tpos=-1, tst=-1, tw=null;
  if(target){ const [tl, ts, tr]=target; tpos=leftEdge+tl.length; tst=SN.indexOf(ts); tw={s:leftEdge, str:tl+tr}; }
  while(steps<maxSteps){
    const e=T[st][tape[pos]];
    if(!e){ let c=0; for(let i=lo;i<=hi;i++) c+=tape[i]; return {halt:true, steps, ones:c, state:SN[st], sym:tape[pos], lo:lo-leftEdge}; }
    tape[pos]=e[0]; pos+=e[1]; st=e[2]; steps++;
    if(pos<lo) lo=pos; if(pos>hi) hi=pos;
    if(pos<16||pos>N-16) return {overflow:true, steps};
    if(target && target.free && st===tst && pos+target[2].length-1>=hi){
      // translation-free comparison: nonblank content and head offset from its leftmost 1
      let a=lo; while(tape[a]===0) a++; let b=hi; while(tape[b]===0) b--;
      const want=target[0]+target[2]; const w1=want.indexOf("1"), w2=want.lastIndexOf("1");
      if(b-a===w2-w1 && pos-a===target[0].length-w1){ let ok=true; for(let i=a;i<=b;i++) if(tape[i]!==+want[w1+i-a]){ok=false;break;} if(ok) return {hit:true, steps, lo:0, shift:(a-(leftEdge))-w1}; }
    }
    if(target && !target.free && pos===tpos && st===tst){
      let ok=true; const a=Math.min(lo,tw.s), b=Math.max(hi, tw.s+tw.str.length-1);
      for(let i=a;i<=b;i++){ const want=(i>=tw.s && i<tw.s+tw.str.length)?+tw.str[i-tw.s]:0; if(tape[i]!==want){ok=false;break;} }
      if(ok) return {hit:true, steps, lo:lo-leftEdge};
    }
  }
  return {limit:true, steps};
}
function randctx(n){ let s="1"; for(let i=1;i<n;i++) s+=(Math.random()<0.5?"0":"1"); return s; }
const nctx=+(process.argv[2]||3), ymax=+(process.argv[3]||40), xmax=+(process.argv[4]||4), hmax=+(process.argv[5]||40), MODE=process.argv[6]||"MSHE";
const ctxs=["1","11010010"]; for(let i=0;i<nctx;i++) ctxs.push(randctx(6+i));
let tot=0, fail=0; const res={};
function rec(name, ok, info){ tot++; if(!ok){ fail++; console.log("FAIL", name, JSON.stringify(info)); } res[name]=(res[name]||0)+(ok?1:0); }
const stepsOut={Mstep:[],Start:[],End1:[],Halt2:[]};
for(const p of ctxs){
  if(MODE.includes("M")) for(let x=0;x<=xmax;x++) for(let y=0;y<=ymax;y++){
    const r=run(M(p,x+3,y), M(p,x,36*y+452), 1e9);
    const ok = r.hit && r.lo>=0; rec("Mstep", ok, {p,x,y,r}); if(p==="1"&&x===0) stepsOut.Mstep.push([y,r.steps]);
  }
  if(MODE.includes("S")) for(let x=0;x<=xmax+3;x++){
    const r=run(L(p,x+5), M(p,x,272), 1e9);
    const ok = r.hit && r.lo>=0; rec("Start", ok, {p,x,r}); if(p==="1") stepsOut.Start.push([x,r.steps]);
  }
  if(MODE.includes("H")) for(let y=0;y<=hmax;y++){
    const r=run(M(p,2,y), null, 1e10);
    const pones=[...P(p)].filter(c=>c==="1").length;
    const ok = r.halt && r.lo>=0 && r.state==="H" && r.sym===1 && r.ones===pones+72*y+891; rec("Halt2", ok, {p,y,r,pones});
    if(p==="1") stepsOut.Halt2.push([y,r.steps,r.ones]);
  }
}
if(MODE.includes("E")) for(let y=0;y<=hmax;y++){
  const start=M("1",0,y); const tgt=L("11010010",y+8);
  // End1: p = "1" is the leftmost nonblank; target prefix 11010010 extends 7 cells further left.
  tgt.free=true;
  const r=run(start, tgt, 1e9);
  rec("End1", r.hit, {y,r}); stepsOut.End1.push([y,r.steps,r.shift]);
}
console.log(JSON.stringify(res), "total", tot, "fail", fail);
require("fs").writeFileSync("check_rules_steps_"+MODE+".json", JSON.stringify(stepsOut));
