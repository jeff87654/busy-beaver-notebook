// Independent universal locality proof: an unread suffix is symbolic, not sampled.
const fs=require('fs'),assert=require('assert');
const manifest=JSON.parse(fs.readFileSync('candidate_manifest.json','utf8'));
function parse(text){return text.split('_').map(r=>[r.slice(0,3),r.slice(3)].map(e=>[+e[0],e[1]==='R'?1:-1,e[2]==='Z'?-1:e.charCodeAt(2)-65]));}
function run(table,ones,p,state,steps,unknownFrom=Infinity){
 let minRead=Infinity,maxRead=-Infinity;
 for(let n=0;n<steps;n++){
  assert(p<unknownFrom,'Attempt to read arbitrary suffix');
  minRead=Math.min(minRead,p);maxRead=Math.max(maxRead,p);
  const [w,d,s]=table[state][ones.has(p)?1:0];
  if(w)ones.add(p);else ones.delete(p);
  p+=d;state=s;assert(state>=0,'Unexpected halt');
 }
 return {ones,p,state,minRead,maxRead};
}
function positions(word,shift=0){return new Set([...word].flatMap((c,i)=>c==='1'?[i+shift]:[]));}
function sorted(s){return [...s].sort((a,b)=>a-b);}
const results=[];
for(const [id,n,len,seed,period,d,wake]of[['C05',3,8,30517,30494,324,6],['C06',2,9,12631,12611,205,7]]){
 const machine=manifest.find(r=>r.id===id).machine,T=parse(machine),W='1'.repeat(n)+'0'.repeat(len-n);
 const start=run(T,new Set(),0,0,seed);
 assert.equal(start.state,0);assert.deepEqual(sorted(new Set([...start.ones].map(q=>q-start.p-1).filter(q=>q<W.length))),sorted(positions(W)));
 const cycle=run(T,positions(W),-1,0,period,W.length);
 assert.equal(cycle.state,0);assert.equal(cycle.p,-d-1);
 const expected=positions('1'.repeat(n),-d);expected.add(wake);
 assert.deepEqual(sorted(cycle.ones),sorted(expected));
 assert.deepEqual(sorted(new Set([...cycle.ones].filter(q=>q<-d+W.length))),sorted(positions(W,-d)));
 // The new prefix is identical, everything left remains blank, and the new suffix may be arbitrary.
 results.push({id,machine,status:'nonhalting_by_universal_locality',known_prefix:W,seed_steps:seed,seed_head:start.p,period,head_shift:-d,min_cell_read:cycle.minRead,max_cell_read:cycle.maxRead,arbitrary_suffix_starts:W.length,arbitrary_suffix_never_read:true,new_prefix_identical:true,all_cells_left_of_new_prefix_blank:true,wake_one_position:wake,initial_ones:start.ones.size,ones_added_per_period:1});
}
const out={method:'A literal finite trace rejects every read of an arbitrary suffix. It reproduces the known prefix farther left, proving the same transition for all suffixes. Induction proves nonhalting.',source:'unresolved_early_locality.js',results};
fs.writeFileSync('unresolved_early_locality_js.json',JSON.stringify(out,null,2));console.log(JSON.stringify(out,null,2));
