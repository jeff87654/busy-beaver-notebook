// Parity exploration: which parameter classes satisfy the rules (literal)
const src=require("fs").readFileSync("check_rules.js","utf8");
const TM = "1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const rep=(u,k)=>u.repeat(k);
const Lv=N=>({w:"1"+rep("10",N)+"1", s:4});
const al=(A,n)=>({w:"1"+rep("01",A)+"1010110101"+rep("01",n), s:0});
const be=(A,n)=>({w:"1"+rep("01",A)+"1010110111"+rep("10",n)+"1", s:0});
const X=(m)=>({w:"1010110111"+rep("10",m)+"1", s:0});
const SZ=1<<22; const tape=new Uint8Array(SZ);
function run(src,dst,maxSteps){
  tape.fill(0); const base=SZ>>1;
  for(let i=0;i<src.w.length;i++) tape[base+i]=+src.w[i];
  let pos=base, st=src.s, steps=0, lo=base, hi=base+src.w.length;
  const dw=dst.w, dl=dw.length;
  while(steps<maxSteps){
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
function row(name, f, xs){ console.log(name, xs.map(x=>{const r=f(x); return x+":"+(r.ok?"ok":r.why);}).join(" ")); }
const L=2e6;
row("LvEven N", N=>run(Lv(N),be(N-3,10),L), [4,5,6,7,8,9,10,11,12,13,14,16,18]);
row("be A=3 n", n=>run(be(3,n),al(1,4*n+15),L), [3,4,5,6,7,8,9,10,11]);
row("be A=4 n", n=>run(be(4,n),al(2,4*n+15),L), [3,4,5,6,7,8,9,10,11]);
row("be A=2 n", n=>run(be(2,n),al(0,4*n+15),L), [3,4,5,6,7,8,9,10,11]);
row("be n=10 A", A=>run(be(A,10),al(A-2,55),L), [2,3,4,5,6,7,8]);
row("al A=3 n", n=>run(al(3,n),be(1,4*n+20),L), [0,1,2,3,4,5,6,7,8]);
row("al A=4 n", n=>run(al(4,n),be(2,4*n+20),L), [0,1,2,3,4,5,6,7,8]);
row("al n=11 A", A=>run(al(A,11),be(A-2,64),L), [2,3,4,5,6,7,8]);
row("al1->X n", n=>run(al(1,n),X(4*n+20),L), [0,1,2,3,4,5,6,7,8,9]);
row("X m", m=>run(X(m),Lv(4*m+15),L), [0,1,2,3,4,5,6,7,8,9,10,11,12]);
row("LvOdd N", N=>run(Lv(N),Lv(4*N+6),L), [1,2,3,5,7,9]);
