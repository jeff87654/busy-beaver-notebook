// Literal simulator for 1RB1RD1LC_2LB1RB1LC_1RZ1LA1LD_0RB2RA2RD.
// usage: sim <maxsteps> <mode> [K]
//   mode "left": print config when head enters the leftmost K cells of the used tape
//   mode "halt": just run and report
use std::env;
fn rle(v:&[u8])->String{let mut s=String::new();let mut i=0;while i<v.len(){let mut j=i;while j<v.len()&&v[j]==v[i]{j+=1;}
 if !s.is_empty(){s.push(' ');} if j-i>1{s+=&format!("{}^{}",v[i],j-i);}else{s+=&format!("{}",v[i]);} i=j;} s}
fn main(){
 let a:Vec<String>=env::args().collect();
 let maxs:u64=a[1].parse().unwrap(); let mode=a[2].clone(); let k:usize=if a.len()>3{a[3].parse().unwrap()}else{8};
 let m="1RB1RD1LC_2LB1RB1LC_1RZ1LA1LD_0RB2RA2RD";
 let mut tw=[[0u8;3];4];let mut td=[[0i8;3];4];let mut tq=[[0u8;3];4];
 for (qi,g) in m.split('_').enumerate(){let b=g.as_bytes();for s in 0..3{tw[qi][s]=b[3*s]-b'0';td[qi][s]=if b[3*s+1]==b'R'{1}else{-1};tq[qi][s]=b[3*s+2]-b'A';}}
 let n=1usize<<27; let mut t=vec![0u8;n]; let mut p=n/2; let mut lo=p; let mut hi=p; let mut q=0usize; let mut steps:u64=0;
 let mut inside=true;
 loop{
  if steps>=maxs{println!("nohalt {} width {}",steps,hi-lo+1);return;}
  let s=t[p] as usize;
  if mode=="left"{let ins=p<=lo+k; if ins&&!inside{println!("{} {} [{}{}] {}",steps,rle(&t[lo..p]),(b'A'+q as u8) as char,s,rle(&t[p+1..hi+1]));} inside=ins;}
  if mode=="dcfg" && q==3 && s==1 && p>=lo+2 && t[p-1]==2 && t[p-2]==2 {
    let mut j=p+1; while j<=hi && t[j]==1 {j+=1;} let rc=j-(p+1);
    let mut okr=true; while j<=hi { if t[j]!=0 {okr=false;break;} j+=1;}
    if okr && rc%2==0 {
      let mut i=lo; while i<p-2 && t[i]==0 {i+=1;}
      let st=i; while i<p-2 && t[i]==1 {i+=1;} let n1=i-st;
      let rest=&t[i..p-2]; let mut okl=true;
      for (k,&x) in rest.iter().enumerate(){ if x != (if k%2==0 {2} else {1}) {okl=false;} }
      if okl && (rest.len()==0 || rest.len()%2==1) {
        let (n,b)= if rest.len()==0 {(n1,0)} else {(n1-1,(rest.len()+1)/2)};
        println!("{} {}({},{},{})",steps, if n%2==0 {"D"} else {"D1"}, n/2, b, rc/2);
      } else { println!("{} Dweird {} [D1] c={}",steps,rle(&t[lo..p]),rc/2); }
    }
  }
  let nq=tq[q][s]; t[p]=tw[q][s]; steps+=1;
  if nq==25{let ones=t[lo..hi+1].iter().filter(|&&x|x!=0).count();println!("HALT steps {} nonzero {}",steps,ones);return;}
  if td[q][s]>0{p+=1;}else{p-=1;} if p<lo{lo=p;} if p>hi{hi=p;} q=nq as usize;
  if p==0||p==n-1{println!("tape overflow at {}",steps);return;}
 }
}
