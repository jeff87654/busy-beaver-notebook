// Random finite tapes in random start state: count halts
const TM = process.env.TM || "1RB0RH_1LC1LB_---1LD_0RE0LE_0LG1LF_1RE0LD_1RG0LA_1RA1RH";
function parse(tm){ return tm.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];})); }
const T = parse(TM);
let seed=+(process.argv[2]||1); function rnd(){ seed=(seed*1103515245+12345)%2147483648; return seed/2147483648; }
const trials=+(process.argv[3]||1000), maxSteps=+(process.argv[4]||100000), len=+(process.argv[5]||30), dens=+(process.argv[6]||0.5);
const N=1<<20; let halts=0; const byState={};
for(let t=0;t<trials;t++){
  const tape=new Uint8Array(N); let pos=N>>1; let w=""; for(let i=0;i<len;i++){ const b=rnd()<dens?1:0; tape[pos-(len>>1)+i]=b; w+=b; }
  let st=Math.floor(rnd()*8); const st0=st; let steps=0;
  while(steps<maxSteps){ const e=T[st][tape[pos]]; if(!e){ halts++; byState[st0]=(byState[st0]||0)+1; if(halts<=5) console.log("HALT",steps,"ABCDEFGH"[st0],w); break;} tape[pos]=e[0]; pos+=e[1]; st=e[2]; steps++; if(pos<2||pos>N-3) break; }
}
console.log("trials",trials,"halts",halts, JSON.stringify(byState));
