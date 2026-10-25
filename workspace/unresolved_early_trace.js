const fs=require('node:fs');
const machines=fs.readFileSync('discovery_holdouts.txt','utf8').trim().split(/\r?\n/);
const results=[];
for(const index of [3,5,6]){
 const tm=machines[index-1],table=tm.split('_').flatMap(c=>[0,3].map(i=>[+c[i],c[i+1]==='R'?1:-1,c[i+2]==='Z'?-1:c.charCodeAt(i+2)-65]));
 const ones=new Set();let head=0,state=0,steps=0,lo=Infinity,hi=-Infinity;
 const snapshots=[];const start=Date.now();let lastKey='';
 function snap(){
  let rle=[];
  for(let p=lo;p<=hi;p++){
   const symbol=ones.has(p)?1:0;
   if(rle.length&&rle.at(-1)[0]===symbol)rle.at(-1)[1]++;else rle.push([symbol,1]);
  }
  const key=state+':'+(head-lo)+':'+JSON.stringify(rle);
  if(key!==lastKey){snapshots.push({steps,state:String.fromCharCode(65+state),head,lo,hi,ones:ones.size,headRelative:head-lo,rle});lastKey=key;}
 }
 while(state>=0&&steps<2_000_000&&snapshots.length<1500){
  if(ones.size>=4&&((head>hi&&(state===6||state===7||state===4))||(head<lo&&(state===0||state===4||state===5))))snap();
  const [w,d,n]=table[2*state+Number(ones.has(head))];
  if(w){ones.add(head);lo=Math.min(lo,head);hi=Math.max(hi,head);}
  else if(ones.delete(head)&&(head===lo||head===hi)){
   lo=Infinity;hi=-Infinity;for(const p of ones){lo=Math.min(lo,p);hi=Math.max(hi,p);}
  }
  head+=d;state=n;steps++;
  if(steps%100000===0&&Date.now()-start>12000)break;
 }
 const result={candidate:'C'+String(index).padStart(2,'0'),machine:tm,steps,state,ones:ones.size,elapsedSeconds:(Date.now()-start)/1000,snapshots};
 results.push(result);
 console.log(JSON.stringify({...result,snapshots:snapshots.slice(0,24)}));
}
fs.writeFileSync('unresolved_early_trace.json',JSON.stringify(results,null,2)+'\n');
