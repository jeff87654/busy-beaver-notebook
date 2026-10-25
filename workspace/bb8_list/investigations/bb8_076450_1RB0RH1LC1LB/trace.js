// step-by-step trace from 0^inf A>0 <word>; prints every step
const TM = process.env.TM || "1RB0RH_1LC1LB_---1LD_0RE0LE_0LG1LF_1RE0LD_1RG0LA_1RA1RH";
function parse(tm){ return tm.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];})); }
const T = parse(TM);
function expand(spec){ let s=""; for(const tok of spec.trim().split(/\s+/).filter(x=>x)){ let m=tok.match(/^\(?([01]+)\)?(?:\^(\d+))?$/); if(!m) throw "bad "+tok; s+=m[1].repeat(m[2]?+m[2]:1);} return s; }
const word = expand(process.argv[2]); const maxS=+process.argv[3]; const pad=+(process.argv[4]||12);
let tape=new Array(pad).fill(0).concat(word.split("").map(Number)).concat(new Array(pad+10).fill(0));
let pos=pad-1, st=0;
for(let s=0;s<=maxS;s++){
  let line=""; for(let i=0;i<tape.length;i++) line+= i===pos? "["+"ABCDEFGH"[st]+"]"+tape[i] : " "+tape[i];
  console.log(String(s).padStart(4), line.replace(/ /g,""));
  const e=T[st][tape[pos]]; if(!e){console.log("HALT");break;}
  tape[pos]=e[0]; pos+=e[1]; st=e[2]; if(pos<0){tape.unshift(0);pos=0;} if(pos>=tape.length) tape.push(0);
}
