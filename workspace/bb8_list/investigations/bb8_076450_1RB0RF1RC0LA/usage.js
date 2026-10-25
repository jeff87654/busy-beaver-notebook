// Count transition usage in the first N literal steps from the blank tape.
const TM = "1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF";
const T = TM.split("_").map(ch=>[0,3].map(i=>{const e=ch.substr(i,3); if(e==="---") return null; return [+e[0], e[1]==="R"?1:-1, e.charCodeAt(2)-65];}));
const N=+(process.argv[2]||1e8); const SZ=1<<26; const tape=new Uint8Array(SZ); let pos=SZ>>1, st=0; const cnt={};
for(let s=0;s<N;s++){ const r=tape[pos]; const e=T[st][r]; const k="ABCDEFGH"[st]+r; cnt[k]=(cnt[k]||0)+1; if(!e){console.log("HALT",s);break;} tape[pos]=e[0]; pos+=e[1]; st=e[2]; }
console.log(JSON.stringify(cnt));
console.log("transitions used:", Object.keys(cnt).length);
