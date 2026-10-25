use std::env;
fn main(){
  let m=b"1RB1LH_1RC1LB_0RD1RE_1LB0LB_1RF0LA_1LG1LF_1RH0LD_---0LE";
  let mut w=[[-1i32;2];8];let mut d=[[0i64;2];8];let mut n=[[0usize;2];8];
  for i in 0..8{for s in 0..2{let c=&m[i*7+3*s..];if c[0]==b'-'{continue;}w[i][s]=(c[0]-b'0') as i32;d[i][s]=if c[1]==b'R'{1}else{-1};n[i][s]=(c[2]-b'A') as usize;}}
  let nn:u64=env::args().nth(1).unwrap().parse().unwrap();
  let l:usize=1<<30;let mut t=vec![0u8;l];
  let mut p=(l/2) as i64;let mut lo=p;let mut hi=p;let mut s=0usize;
  for i in 0..nn{
    let r=t[p as usize] as usize;
    if w[s][r]<0{println!("HALT step {}",i);return;}
    t[p as usize]=w[s][r] as u8;p+=d[s][r];s=n[s][r];
    if p<lo{lo=p;if s==1{
      let mut o=format!("{}:",i+1);let mut q=lo;
      while q<=hi{let mut e=q;while e<=hi&&t[e as usize]==t[q as usize]{e+=1;}o+=&format!(" {}^{}",t[q as usize],e-q);q=e;}
      println!("{}",&o[..o.len().min(160)]);}}
    if p>hi{hi=p;}
    if hi-lo>(l as i64)/2-10{println!("size");return;}
  }
  println!("done");
}
