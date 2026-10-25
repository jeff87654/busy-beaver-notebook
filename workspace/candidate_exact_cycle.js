// Exact whole-tape translation recurrence detector for C01. No hashes.
const fs=require('node:fs');
const machine=fs.readFileSync('discovery_holdouts.txt','utf8').trim().split(/\r?\n/)[0];
const table=machine.split('_').flatMap(c=>[0,3].map(i=>[
  Number(c[i]),c[i+1]==='R'?1:-1,c[i+2]==='Z'?-1:c.charCodeAt(i+2)-65]));
function step(c){
  const [w,d,n]=table[2*c.state+Number(c.tape.has(c.head))];
  if(w)c.tape.add(c.head);else c.tape.delete(c.head);
  c.head+=d;c.state=n;c.steps++;
}
function blank(){return {tape:new Set(),head:0,state:0,steps:0};}
function normalized(c){return [...c.tape].map(x=>x-c.head).sort((a,b)=>a-b);}
const start=Date.now(),c=blank(),seen=new Map(),snapshots=[];
let certificate=null,peakOnes=0;
while(c.state>=0&&c.steps<25_000_000){
  if(c.state===0&&c.tape.size<=100){
    const key=normalized(c).join(',');
    if(seen.has(key)){
      const firstStep=seen.get(key),first=blank();
      while(first.steps<firstStep)step(first);
      const a=normalized(first),b=normalized(c);
      if(first.state!==c.state||JSON.stringify(a)!==JSON.stringify(b))throw Error('Invalid recurrence');
      certificate={firstStep,repeatStep:c.steps,period:c.steps-firstStep,
        firstHead:first.head,repeatHead:c.head,translation:c.head-first.head,
        state:'A',onesRelativeToHead:b,
        proof:'Exact full-tape configuration recurs up to translation on a blank infinite background. Determinism repeats this period indefinitely.'};
      break;
    }
    seen.set(key,c.steps);
    if(seen.size>300000)seen.delete(seen.keys().next().value);
  }
  step(c);
  peakOnes=Math.max(peakOnes,c.tape.size);
  if(c.steps%100000===0){
    if(snapshots.length<100)snapshots.push({steps:c.steps,state:c.state,head:c.head,
      ones:c.tape.size,relativeOnes:c.tape.size<=30?normalized(c):null});
    if(Date.now()-start>30000)break;
  }
}
const result={candidate:'C01',machine,status:certificate?'infinite':c.state<0?'halt':'cutoff',
  reason:certificate?'exact_translation_recurrence':'literal_simulation_limit',
  steps:c.steps,ones:c.tape.size,peakOnes,elapsedSeconds:(Date.now()-start)/1000,
  snapshots,certificate};
fs.writeFileSync('candidate_exact_cycle.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({...result,snapshots:undefined}));
