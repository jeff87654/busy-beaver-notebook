fn main(){
  let m="1RB---_0RC1LG_1LB1RD_0RE1RA_1RF0LC_1LE1RG_0LH1RE_0RB1LG";
  let b=m.as_bytes();
  let mut w=[[-1i32;2];8];let mut d=[[0i64;2];8];let mut nx=[[0usize;2];8];
  for q in 0..8{for s in 0..2{let o=q*7+s*3; if b[o]!=b'-'{w[q][s]=(b[o]-b'0') as i32;d[q][s]=if b[o+1]==b'R'{1}else{-1};nx[q][s]=(b[o+2]-b'A') as usize;}}}
  let sz:usize=1<<20; let mut tape=vec![0u8;sz]; let mut pos:i64=(sz/2) as i64; let mut q=0usize;
  let mut cnt=[[0u64;2];8];
  let n:i64=1_000_000_000;
  for _ in 0..n{
    let s=tape[pos as usize] as usize;
    cnt[q][s]+=1;
    tape[pos as usize]=w[q][s] as u8; pos+=d[q][s]; q=nx[q][s];
  }
  for q in 0..8{println!("state {}: reads0={} reads1={}",(b'A'+q as u8) as char,cnt[q][0],cnt[q][1]);}
}
