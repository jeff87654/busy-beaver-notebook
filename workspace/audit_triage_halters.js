// Scalar independent confirmation of all new discovery-pilot halters.
const fs=require('node:fs');
const rows=JSON.parse(fs.readFileSync('discovery_triage.json','utf8')).results.filter(r=>r.status==='halt');
const results=[];
for(const row of rows){
  const table=row.machine.split('_').flatMap(c=>[0,3].map(i=>({w:Number(c[i]),d:c[i+1]==='R'?1:-1,n:c[i+2]==='Z'?-1:c.charCodeAt(i+2)-65})));
  const expectedSteps=Number(row.steps.decimal), expectedOnes=Number(row.ones.decimal);
  const tape=new Uint8Array(4_000_001);let head=2_000_000,state=0,steps=0,ones=0;
  const start=Date.now();
  while(state>=0&&steps<=expectedSteps){
    const old=tape[head],t=table[2*state+old];
    tape[head]=t.w;ones+=t.w-old;head+=t.d;state=t.n;steps++;
    if(head<0||head>=tape.length)throw Error('Tape bounds exceeded');
  }
  const result={machine:row.machine,steps,ones,halted:state===-1,
    verified:state===-1&&steps===expectedSteps&&ones===expectedOnes,
    elapsedSeconds:(Date.now()-start)/1000};
  if(!result.verified)throw Error(JSON.stringify(result));
  results.push(result);
}
fs.writeFileSync('audit_triage_halters.json',JSON.stringify(results,null,2)+'\n');
console.log(JSON.stringify(results,null,2));
