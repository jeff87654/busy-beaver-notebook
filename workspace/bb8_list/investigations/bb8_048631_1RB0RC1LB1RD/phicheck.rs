// Literal simulation of the machine; at every return of H to cell -2 parse the tape as a std head (a; ts) and check
// that the std head is the Phi image of the previous std head.  Reports halts / mismatches.
use std::env;
fn push(a:u64)->(u64,Vec<u64>){ match a%5 { 3|4=>(3,vec![2*a-6]), 0|2=>(2,vec![2*a-4]), _=>(2,vec![1,2*a-5]) } }
fn phi(a:u64,ts:&Vec<u64>)->(u64,Vec<u64>){
  if a>=4 { let (a2,mut l)=push(a); l.extend(ts.iter()); return (a2,l); }
  let mut m=0; while m<ts.len() && ts[m]<=2 {m+=1;}
  let p=&ts[..m]; let s:u64=p.iter().sum(); let aa=a+m as u64+1;
  let mut tail:Vec<u64>=Vec::new();
  if m<ts.len(){ let t=ts[m]; assert!(t>=3); if t-2>=1 {tail.push(t-2);} tail.extend(ts[m+1..].iter()); }
  let u=2*(m as u64)-s; let e=2*a+s+2;
  if u%10==0 { return (e/2,tail); }
  let (a2,mut l)= match aa%5 { 3|4=>(3,vec![e-6]), 0|2=>(2,vec![e-4]), _=>(2,vec![1,e-5]) };
  l.extend(tail.iter()); (a2,l)
}
fn parse(tape:&[u8],base:usize,hi:usize)->Option<(u64,Vec<u64>)>{
  // cells base.. (cell 0) to hi ; require cells left of base blank (checked by caller via min pos)
  let mut i=base; let mut a=0u64;
  while i+1<=hi && tape[i]==1 && tape[i+1]==0 { a+=1; i+=2; }
  if a<2 {return None;}
  if !(i+1<=hi && tape[i]==1 && tape[i+1]==1) {return None;}
  i+=2;
  let g=(2*a+3) as usize;
  for k in 0..g { if i+k>hi || tape[i+k]!=0 {return None;} }
  i+=g; if i>hi || tape[i]!=1 {return None;} i+=1;
  let mut ts=Vec::new();
  while i<=hi {
    let mut z=0usize; while i<=hi && tape[i]==0 {z+=1;i+=1;}
    if i>hi {return None;}
    if z%2==0 {return None;}
    ts.push(((z+1)/2) as u64); i+=1;
  }
  Some((a,ts))
}
fn main(){
  let args:Vec<String>=env::args().collect();
  let n:u64=args[1].parse().unwrap();
  let m="1RB---_0RC1LG_1LB1RD_0RE1RA_1RF0LC_1LE1RG_0LH1RE_0RB1LG";
  let b=m.as_bytes();
  let mut w=[[-1i32;2];8];let mut d=[[0i64;2];8];let mut nx=[[0usize;2];8];
  for q in 0..8{for s in 0..2{let o=q*7+s*3; if b[o]!=b'-'{w[q][s]=(b[o]-b'0') as i32;d[q][s]=if b[o+1]==b'R'{1}else{-1};nx[q][s]=(b[o+2]-b'A') as usize;}}}
  let sz:usize=1<<16; let base=1000usize; let mut tape=vec![0u8;sz]; let mut pos:i64=base as i64; let mut q=0usize;
  let mut hi=base; let mut minpos=base as i64;
  let mut prev:Option<(u64,Vec<u64>)>=None; let (mut ok,mut bad,mut nstd)=(0u64,0u64,0u64);
  let mut step:u64=0; let mut last_report=1u64;
  while step<n {
    let s=tape[pos as usize] as usize;
    if q==7 && pos==base as i64-2 {
      if let Some(cur)=parse(&tape,base,hi) {
        nstd+=1;
        if let Some((pa,pt))=&prev { let e=phi(*pa,pt); if e==cur {ok+=1;} else {bad+=1; if bad<5 {println!("MISMATCH at step {}: prev ({};{:?}) phi {:?} actual {:?}",step,pa,pt,e,cur);} } }
        prev=Some(cur);
      }
    }
    if w[q][s]<0 { println!("HALT at step {}",step); return; }
    tape[pos as usize]=w[q][s] as u8; pos+=d[q][s]; q=nx[q][s];
    if pos<minpos {minpos=pos;}
    if (pos as usize)>hi { hi=pos as usize; }
    step+=1;
    if step==last_report { println!("step {} std heads {} phi ok {} bad {} width {} minpos {}",step,nstd,ok,bad,hi-base+1,minpos-base as i64); last_report*=4; }
  }
  if let Some((a,t))=&prev {println!("last std head ({}; {:?})",a,t);}
  println!("DONE steps {} std heads {} phi ok {} bad {} width {} minpos {}",step,nstd,ok,bad,hi-base+1,minpos-base as i64);
}
