use std::collections::HashSet;
fn main(){
  let m="1RB---_0RC1LG_1LB1RD_0RE1RA_1RF0LC_1LE1RG_0LH1RE_0RB1LG";
  let b=m.as_bytes();
  let mut w=[[-1i32;2];8];let mut d=[[0i64;2];8];let mut nx=[[0usize;2];8];
  for q in 0..8{for s in 0..2{let o=q*7+s*3; if b[o]!=b'-'{w[q][s]=(b[o]-b'0') as i32;d[q][s]=if b[o+1]==b'R'{1}else{-1};nx[q][s]=(b[o+2]-b'A') as usize;}}}
  let sz:usize=1<<22; let mut tape=vec![0u8;sz]; let mut pos:i64=(sz/2) as i64; let mut q=0usize;
  let n:i64=200_000_000;
  let ks=[2usize,3,4,5,6,7,8,9,10];
  let mut sets:Vec<HashSet<(usize,u32,u32)>>=ks.iter().map(|_|HashSet::new()).collect();
  for i in 0..n{
    let s=tape[pos as usize] as usize;
    if i%7!=0 || true {
    for (j,&k) in ks.iter().enumerate(){
      if sets[j].len()>3_000_000 {continue;}
      let mut l=0u32; for t in 1..=k{ l=(l<<1)|tape[(pos-t as i64) as usize] as u32; }
      let mut r=0u32; for t in 0..k{ r=(r<<1)|tape[(pos+t as i64) as usize] as u32; }
      sets[j].insert((q,l,r));
    }}
    if w[q][s]<0{println!("HALT {}",i);return;}
    tape[pos as usize]=w[q][s] as u8; pos+=d[q][s]; q=nx[q][s];
  }
  for (j,&k) in ks.iter().enumerate(){println!("k={} windows={}",k,sets[j].len());}
}
