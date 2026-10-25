use std::env;
fn main(){
  let args:Vec<String>=env::args().collect();
  let n:i64=args[1].parse().unwrap();
  let m="1RB---_0RC1LG_1LB1RD_0RE1RA_1RF0LC_1LE1RG_0LH1RE_0RB1LG";
  let mut w=[[-1i32;2];8];let mut d=[[0i64;2];8];let mut nx=[[0usize;2];8];
  let b=m.as_bytes();
  for q in 0..8{for s in 0..2{let o=q*7+s*3; if b[o]==b'-'{w[q][s]=-1;}else{w[q][s]=(b[o]-b'0') as i32;d[q][s]=if b[o+1]==b'R'{1}else{-1};nx[q][s]=(b[o+2]-b'A') as usize;}}}
  let sz:usize=1<<26; let mut tape=vec![0u8;sz]; let mut pos:i64=(sz/2) as i64; let mut q=0usize;
  let (mut mn,mut mx)=(pos,pos); let mut nxt:i64=1;
  let base=(sz/2) as i64;
  for i in 0..n{
    let s=tape[pos as usize] as usize;
    if w[q][s]<0{println!("HALT at {}",i);return;}
    tape[pos as usize]=w[q][s] as u8; pos+=d[q][s]; q=nx[q][s];
    if pos<mn{mn=pos;} if pos>mx{mx=pos;}
    if i+1==nxt{let ones:u64=(mn..=mx).map(|k|tape[k as usize] as u64).sum();
      println!("step {} pos {} range [{},{}] ones {} state {}",i+1,pos-base,mn-base,mx-base,ones,(b'A'+q as u8) as char);nxt*=4;}
  }
  println!("final step {} pos {} range [{},{}]",n,pos-base,mn-base,mx-base);
  let s:String=(mn..=mx).map(|k|if tape[k as usize]==1{'1'}else{'0'}).collect();
  println!("{}",s);
}
