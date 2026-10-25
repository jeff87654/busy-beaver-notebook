// Literal simulator reporting canonical events (head at the left edge of the content).
// Lv(N):   E reading 1, right = (10)^N 1, left blank
// al(A,n): A reading 1, right = (01)^A (10101)^2 (01)^n , left blank
// be(A,n): A reading 1, right = (01)^A 1 0 (101)^2 1 1 (10)^n 1, left blank
// usage: node ev.js maxSteps [word state headIdx]   (default: blank tape)
const TM = process.env.TM || "1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
function expand(w){ return w.replace(/\(([01]+)\)\^(\d+)/g,(m,u,k)=>u.repeat(+k)).replace(/\s+/g,""); }
const maxSteps=+process.argv[2];
const N=1<<28; const tape=new Uint8Array(N); let base=N>>1; let pos=base, st=0;
if(process.argv[3]!==undefined){ const w=expand(process.argv[3]); for(let i=0;i<w.length;i++) tape[base+i]=+w[i]; st="ABCDEFGH".indexOf(process.argv[4]); pos=base+(+process.argv[5]); }
let lo=Math.min(pos,base)-2, hi=Math.max(pos, base+(process.argv[3]?expand(process.argv[3]).length:0))+2;
const reLv=/^((?:10)*)1$/, reAl=/^((?:01)*)1010110101((?:01)*)$/, reBe=/^((?:01)*)1010110111((?:10)*)1$/;
function rightstr(){ let b=hi; while(b>pos&&tape[b]===0)b--; let s=""; for(let i=pos+1;i<=b;i++) s+=tape[i]; return s; }
let steps=0; const quiet=+(process.env.QUIET||0);
const Z=30;
while(steps<maxSteps){
  const r=tape[pos]; const e=T[st][r];
  if(!e){ console.log("HALT",steps,"state","ABCDEFGH"[st],"read",r, "right", rightstr().slice(0,80), "len", rightstr().length); process.exit(0);}
  tape[pos]=e[0]; pos+=e[1]; st=e[2]; steps++; if(pos<lo)lo=pos; if(pos>hi)hi=pos;
  if(e[1]<0 && tape[pos]===1 && (st===4||st===0)){
    let any=false; for(let i=pos-1;i>=pos-Z && i>=lo;i--) if(tape[i]){any=true;break;}
    if(!any){
      const s=rightstr(); let m;
      if(st===4 && (m=reLv.exec(s))) console.log("Lv",steps,"N="+m[1].length/2);
      else if(st===0 && (m=reAl.exec(s))) console.log("al",steps,"A="+m[1].length/2,"n="+m[2].length/2);
      else if(st===0 && (m=reBe.exec(s))) console.log("be",steps,"A="+m[1].length/2,"n="+m[2].length/2);
    }
  }
  if(pos<2||pos>N-3){console.log("OVERFLOW");process.exit(0);}
}
console.log("LIMIT",steps);
