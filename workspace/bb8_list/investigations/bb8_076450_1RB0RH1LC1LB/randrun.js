// Random general run-list configs: 0^inf A>0 0^3 1^a (0^{s} 1^{l})* 0 1^2 0^inf ; run fixed steps, report halts.
const TM = process.env.TM || "1RB0RH_1LC1LB_---1LD_0RE0LE_0LG1LF_1RE0LD_1RG0LA_1RA1RH";
function parse(tm){ return tm.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];})); }
const T = parse(TM);
let seed=+(process.argv[2]||1); function rnd(){ seed=(seed*1103515245+12345)%2147483648; return seed/2147483648; }
const trials=+(process.argv[3]||1000), maxSteps=+(process.argv[4]||200000), maxSep=+(process.argv[5]||2), lead=+(process.argv[6]||3);
const N=1<<20; let halts=0;
for(let t=0;t<trials;t++){
  let w="0".repeat(lead)+"1".repeat(1+Math.floor(rnd()*30)); const nr=1+Math.floor(rnd()*8);
  for(let i=0;i<nr;i++){ const s=1+Math.floor(rnd()*maxSep); const l=1+Math.floor(rnd()*(rnd()<0.5?2:20)); w+="0".repeat(s)+"1".repeat(l); }
  w+= "01"+"1";
  const tape=new Uint8Array(N); let pos=N>>1; for(let i=0;i<w.length;i++) tape[pos+1+i]=+w[i];
  let st=0, steps=0;
  while(steps<maxSteps){ const e=T[st][tape[pos]]; if(!e){ halts++; console.log("HALT",steps,w); break;} tape[pos]=e[0]; pos+=e[1]; st=e[2]; steps++; if(pos<2||pos>N-3) break; }
}
console.log("trials",trials,"halts",halts);
