// Literal simulation from blank tape: find the first time the configuration equals
// beta(1021,0,6,0) = [A0] 0 (100)^1021 1010 1010 (110)^6 10100 1101  (blank elsewhere)
const TMS="1RB1LD_1RC0RF_0LA0RA_0LA0LE_1LA0LG_0LA---_1RD1LG";
const T=TMS.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, "ABCDEFG".indexOf(e[2])];}));
function beta(x,j,k,t){return "0"+"0"+"100".repeat(x)+"1010"+"100".repeat(j)+"1010"+"110".repeat(k)+"10100"+"10".repeat(t)+"1101";}
const targets=[[1021,0,6,0]].map(p=>({p, s:beta(...p)}));
const N=1<<22; const tape=new Uint8Array(N); let pos=N>>1, st=0, steps=0, minp=pos, maxp=pos;
const maxSteps=+(process.argv[2]||2e7);
let found=null;
while(steps<maxSteps){
  const e=T[st][tape[pos]]; if(!e){console.log("HALT",steps); break;}
  tape[pos]=e[0]; pos+=e[1]; st=e[2]; steps++;
  if(pos<minp)minp=pos; if(pos>maxp)maxp=pos;
  if(st===0 && tape[pos]===0 && pos<=minp+3){
    // blank to the left?
    let blank=true; for(let i=minp;i<pos;i++) if(tape[i]){blank=false;break;}
    if(!blank) continue;
    let hi=maxp; while(hi>pos && tape[hi]===0) hi--;
    for(const tg of targets){
      if(hi-pos+1!==tg.s.length) continue;
      let ok=true; for(let i=0;i<tg.s.length;i++){ if(tape[pos+i]!==+tg.s[i]){ok=false;break;} }
      if(ok){ console.log("REACHED beta("+tg.p.join(",")+") at step",steps); found=steps; }
    }
    if(found) break;
  }
}
if(!found) console.log("not found within",steps);
