// Independent literal simulation and direct string comparison with wiki B.
const fs = require('node:fs');
const machine='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF';
const table=machine.split('_').map(s=>[0,3].map(i=>[
  Number(s[i]),s[i+1]==='R'?1:-1,s[i+2]==='Z'?-1:s.charCodeAt(i+2)-65]));
// B is constructed right to left: terminal suffix, then a block,
// a separator, then vector blocks in the order b,c,..., then prefix.
function B(a,vec){
  let word='1'+'01'.repeat(3*a+1)+'0011100';
  for(const value of vec) word='01'.repeat(3*value+1)+'1'+word;
  return '111'+word;
}
function initial(word='') {
  return {tape:new Set([...word].flatMap((c,i)=>c==='1'?[i-word.length]:[])),head:0,state:0,steps:0};
}
function step(c){
  const [w,d,n]=table[c.state][Number(c.tape.has(c.head))];
  if(w)c.tape.add(c.head);else c.tape.delete(c.head);
  c.head+=d;c.state=n;c.steps++;
}
function word(c){
  const lo=Math.min(...c.tape);
  let s='';for(let p=lo;p<c.head;p++)s+=c.tape.has(p)?'1':'0';
  return s;
}
const blank=initial(), snapshots=[];
for(let n=0;n<=8574;n++){
  if([8178,8574].includes(n))snapshots.push({steps:n,state:blank.state,head:blank.head,
    ones:blank.tape.size,wordBeforeHead:word(blank),
    matchesB2:word(blank)===B(2,Array(12).fill(1)),
    matchesB4:word(blank)===B(4,Array(12).fill(1)),
    anyOnesAtOrRightOfHead:[...blank.tape].some(x=>x>=blank.head)});
  if(n<8574)step(blank);
}
const halts=[];
for(let a=0;a<3;a++)for(let k=0;k<3;k++){
  const c=initial(B(a,Array(k).fill(0)));
  while(c.state!==-1&&c.steps<100000)step(c);
  halts.push({a,k,state:c.state,steps:c.steps,ones:c.tape.size,
    sourceFormula:3*a+2*k+9,observedFormula:3*a+2*k+10});
}
const result={machine,snapshots,halts};
console.log(JSON.stringify(result,null,2));
fs.writeFileSync('audit_bb7_conventions.json',JSON.stringify(result,null,2)+'\n');
