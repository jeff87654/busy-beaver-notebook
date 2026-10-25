// Checks the local invariant I(state, tape) at every step: (1) along the blank-tape run, (2) from random tapes that satisfy I.
const TM = "1RB0RH_1LC1LB_---1LD_0RE0LE_0LG1LF_1RE0LD_1RG0LA_1RA1RH";
function parse(tm){ return tm.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];})); }
const T = parse(TM);
function P(t,p){ // leftwards from p-1: 1^k 0 1
  let i=p-1; while(i>=0 && t[i]===1) i--; if(i<1) return false; return t[i]===0 && t[i-1]===1; }
function R(t,p){ // rightwards from p: 1^k 0 x y with x=1 or y=0
  let i=p; while(i<t.length && t[i]===1) i++; if(i+2>=t.length) return false; return t[i+1]===1 || t[i+2]===0; }
function inv(t,p,q){ const s=t[p], l0=t[p-1], l1=t[p-2], r0=t[p+1], r1=t[p+2];
  switch(q){
    case 0: return (s===0 && (r0===0 || P(t,p))) || (s===1 && (l0===1 || R(t,p+1)));
    case 1: return (s===0 && l0===1) || (s===1 && P(t,p));
    case 2: return s===1;
    case 3: return true;
    case 4: return s===1 || l0===0 || r0===0;
    case 5: return r0===1;
    case 6: return (l0===1&&l1===1) || (s===1&&r1===0) || (s===0&&r0===0) || (s===0&&l0===1);
    case 7: return P(t,p) || R(t,p);
  } }
const mode=process.argv[2];
if(mode==="blank"){
  const maxSteps=+process.argv[3]; const N=1<<22; const t=new Uint8Array(N); let p=N>>1, q=0, steps=0, bad=0;
  // P and R scan runs; to keep cost down we check invariant every step but the scans are bounded by run lengths
  while(steps<maxSteps){ if(!inv(t,p,q)){ bad++; if(bad<5) console.log("VIOLATION at",steps,"state","ABCDEFGH"[q]); }
    const e=T[q][t[p]]; if(!e){ console.log("HALT",steps); break; } t[p]=e[0]; p+=e[1]; q=e[2]; steps++; }
  console.log("blank run steps",steps,"violations",bad);
} else {
  let seed=+(process.argv[3]||7); function rnd(){ seed=(seed*1103515245+12345)%2147483648; return seed/2147483648; }
  const trials=+process.argv[4], maxSteps=+process.argv[5]; const N=1<<16; let tried=0, halts=0, bad=0, accepted=0;
  while(accepted<trials){ tried++; const t=new Uint8Array(N); const p0=N>>1; const len=4+Math.floor(rnd()*40); const d=rnd();
    for(let i=0;i<len;i++) t[p0-(len>>1)+i]= rnd()<d?1:0; let q=Math.floor(rnd()*8); let p=p0;
    if(!inv(t,p,q)) continue; accepted++;
    for(let s=0;s<maxSteps;s++){ if(!inv(t,p,q)){ bad++; console.log("VIOLATION after",s); break; } const e=T[q][t[p]]; if(!e){ halts++; console.log("HALT"); break;} t[p]=e[0]; p+=e[1]; q=e[2]; if(p<3||p>N-4) break; } }
  console.log("random: tried",tried,"accepted",accepted,"halts",halts,"violations",bad);
}
