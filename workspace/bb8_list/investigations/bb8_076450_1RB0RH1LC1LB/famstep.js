// famstep: given family config(s), run literal until next family event (or halt), print result.
// config syntax: "z3 [n;k][m;j]..."  ; stdin lines or argv. Options via env: EVENTS (default 1), MAXSTEPS
const TM = process.env.TM || "1RB0RH_1LC1LB_---1LD_0RE0LE_0LG1LF_1RE0LD_1RG0LA_1RA1RH";
function parse(tm){ return tm.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];})); }
const T = parse(TM);
function build(cfg){ const m=cfg.match(/z(\d+)\s*(.*)/); const z=+m[1]; let segs=[...m[2].matchAll(/\[(\d+);(\d+)\]/g)].map(x=>[+x[1],+x[2]]);
  let s="0".repeat(z); segs.forEach((sg,i)=>{ if(i>0) s+="0"; s+="1".repeat(sg[0]); s+="001".repeat(sg[1]); }); return s; }
function runs(tape,lo,hi){ let out=[]; let i=lo; let z=0;
  while(i<=hi){ if(tape[i]===0){z++; i++; continue;} let j=i; while(j<=hi&&tape[j]===1) j++; out.push([z,j-i]); z=0; i=j; } return out; }
function famParse(rs){ if(rs.length===0) return null; let segs=[]; let lead=rs[0][0];
  for(let i=0;i<rs.length;i++){ const [s,l]=rs[i]; if(i===0 || s===1){ segs.push([l,0]); } else if(s===2 && l===1){ segs[segs.length-1][1]++; } else return null; }
  return {lead,segs}; }
function fmt(f){ return "z"+f.lead+" "+f.segs.map(s=>"["+s[0]+";"+s[1]+"]").join(""); }
function step(cfg, events, maxSteps){
  const word=build(cfg); const N=Math.max(1<<16, word.length*8+(1<<16)); const tape=new Uint8Array(N);
  let pos=N>>1; for(let i=0;i<word.length;i++) tape[pos+1+i]=+word[i];
  let state=0, steps=0, minp=pos, maxp=pos+word.length, ev=0; let res=[];
  while(steps<maxSteps){ const r=tape[pos]; const e=T[state][r];
    if(!e){ let c=0; for(let i=minp;i<=maxp;i++) c+=tape[i]; let lo=minp,hi=maxp; while(tape[lo]===0&&lo<pos) lo++; while(tape[hi]===0&&hi>pos) hi--;
      const L=runs(tape,lo,pos-1).map(x=>x[0]+":"+x[1]).join(" "); const R=runs(tape,pos+1,hi).map(x=>x[0]+":"+x[1]).join(" ");
      res.push("HALT@"+steps+" ones="+c+" L{"+L+"} R{"+R+"} relpos="+(pos-minp)); return res; }
    tape[pos]=e[0]; pos+=e[1]; state=e[2]; steps++;
    if(pos<=0||pos>=N-1) { res.push("OOB"); return res; }
    if(pos<minp){ minp=pos; if(state===0){ let hi=maxp; while(hi>pos&&tape[hi]===0) hi--; const f=famParse(runs(tape,pos+1,hi)); if(f){ ev++; res.push(fmt(f)+" @"+steps); if(ev>=events) return res; } } }
    if(pos>maxp) maxp=pos; }
  res.push("LIMIT"); return res; }
const events=+(process.env.EVENTS||1), maxSteps=+(process.env.MAXSTEPS||5e7);
let cfgs=process.argv.slice(2); if(cfgs.length===0){ cfgs=require('fs').readFileSync(0,'utf8').split(/\r?\n/).map(x=>x.trim()).filter(x=>x); }
for(const c of cfgs){ console.log(c+"  ->  "+step(c,events,maxSteps).join("  ->  ")); }
