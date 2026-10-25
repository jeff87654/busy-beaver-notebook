/* Exact symbolic terminal-tail maps for C14; the fold theorem is documented
 * in lastfive_family_theory_symbolic.md. Unknown tail reads are never zero-filled.
 * makeMapper also supports C16 when supplied its table and tailConstant=16. */
"use strict";
const fs = require("fs");
const path = require("path");
const MACHINE = "1RB1LA_0LA0RC_1RA1LD_0LE1RZ_0LC1LF_1RH1LG_1LA0LE_0RE0RH";
function makeMapper(machine=MACHINE, deadline=Infinity, tailConstant=18) {
 const T=machine.split("_").map(r=>[r.slice(0,3),r.slice(3)]);
 return (function map(runs,limit=100000,expand=false,resume=null) {
 let input=runs.map(n=>"1".repeat(n)).join("0"),t=new Set([...input].flatMap((c,i)=>c==="1"?[i]:[])),B=input.length,p=-1,s=0,a=0,b=0,folds=0,offs=0,minK=0;
 let startMicro=0;
 if(resume){t=new Set(resume.known_ones);B=resume.tail_position;p=resume.head;s=resume.state;a=resume.a;b=resume.b;folds=resume.folds;offs=resume.tail_offset;minK=resume.minK;startMicro=resume.micro;}
 const snapshot=(micro)=>({known_ones:[...t].sort((x,y)=>x-y),tail_position:B,head:p,state:s,a,b,folds,tail_offset:offs,minK,micro});
 for(let micro=startMicro;micro<startMicro+limit;micro++){ if((micro&4095)===0 && Date.now()>deadline) return {input:runs,status:'time_cap',a,b,folds,minK,micro,checkpoint:snapshot(micro)};
  if(micro&&s===0&&!t.has(p)&&p<Math.min(...t)){
   let out=Array.from({length:B-p-1},(_,i)=>t.has(p+1+i)?"1":"0").join(""),trim=0;
   while(out.endsWith("011")){out=out.slice(0,-3);trim++;}
   return {input:runs,input_word:input,output_word:out,output:out.split("0").map(v=>v.length),a,b,shift:p+1,folds,offset:offs+trim,minK,micro};
  }
  if(s===7&&p===B&&!t.has(B-1)){
   t.add(B-1);t.add(B);t.add(B+1);p=B-2;B+=2;s=0;a+=tailConstant+12*offs;b+=12;folds++;continue;
  }
  if(p>=B){
   if(!expand)return{input:runs,status:"variable_read",state:String.fromCharCode(s+65),offset:p-B,a,b,folds,micro};
   minK=Math.max(minK,1-offs);t.add(B+1);t.add(B+2);B+=3;offs--;continue;
  }
  let tr=T[s][t.has(p)?1:0];if(tr[0]==1)t.add(p);else t.delete(p);p+=tr[1]==="R"?1:-1;s=tr.charCodeAt(2)-65;a++;
  if(s===25)return{input:runs,status:"halt",a,b,folds,minK,micro};
 }
 return{input:runs,status:"cutoff",a,b,folds,minK,checkpoint:snapshot(startMicro+limit)};
});
}
module.exports={makeMapper,MACHINE};
if(require.main===module){
 const args=process.argv.slice(2);
 const arg=(name,fallback)=>{let i=args.indexOf(name);return i<0?fallback:Number(args[i+1]);};
 const seconds=arg("--seconds",50), maxBoundaries=arg("--boundaries",1000), perMap=arg("--map-limit",10000000);
 const deadline=Date.now()+seconds*1000, mapper=makeMapper(MACHINE,deadline,18);
 let prefix=[3],K=0n,steps=17n,head=-3n,chain=[],seen=new Map(),outcome="boundary_cap";
 const destination=path.join(__dirname,"lastfive_family_theory_symbolic.json");
 const save=()=>fs.writeFileSync(destination,JSON.stringify({machine:MACHINE,
   proof_basis:"literal known-prefix steps plus universal tail fold; all minimum-k conditions must hold",
   seed:{prefix:[3],tail_count:"0",steps:"17",head:"-3"},
   wall_limit_seconds:seconds,per_map_micro_limit:perMap,outcome,
   completed_maps:chain.filter(r=>!r.status&&r.repeat_from===undefined).length,
   last_complete_boundary:{prefix,tail_count:K.toString(),steps:steps.toString(),head:head.toString()},chain},null,2)+"\n");
 for(let i=0;i<maxBoundaries;i++){
  if(Date.now()>deadline){outcome="time_cap";break;}
  const key=JSON.stringify(prefix);
  if(seen.has(key)){outcome="prefix_repeat_candidate";chain.push({repeat_from:seen.get(key),K:K.toString(),steps:steps.toString(),prefix});break;}
  seen.set(key,i);
  const r=mapper(prefix,perMap,true);
  if(r.status){outcome=r.status;chain.push({i,prefix,tail_count:K.toString(),steps:steps.toString(),...r});break;}
  if(![r.a,r.b,r.offset,r.minK,r.shift].every(Number.isSafeInteger)){outcome="unsafe_integer";chain.push({i,...r,status:outcome});break;}
  if(K<BigInt(r.minK)){outcome="domain_not_met";chain.push({i,prefix,tail_count:K.toString(),steps:steps.toString(),...r,status:outcome});break;}
  const beforeK=K;
  steps+=BigInt(r.a)+BigInt(r.b)*K; K+=BigInt(r.offset); head+=BigInt(r.shift);
  chain.push({...r,i,tail_before:beforeK.toString(),tail_after:K.toString(),steps_after:steps.toString(),head_after:head.toString()});
  prefix=r.output; save();
 }
 save();
 console.log(JSON.stringify({outcome,completed_maps:chain.filter(r=>!r.status&&r.repeat_from===undefined).length,
   tail_count:K.toString(),steps:steps.toString(),head:head.toString()},null,2));
}
