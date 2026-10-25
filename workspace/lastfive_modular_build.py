from pathlib import Path
import hashlib,json,subprocess,os
base=Path('candidate_deciders_deep_verified.cpp');source=base.read_text()
struct=r'''
// Search abstraction only; CTL_Fixedlen_verify is unchanged.
struct Modular{
 inline static thread_local int64_t modulus=3,suffix_bits=4,length_mod=1;
 int64_t residue=0,suffix=0,length_residue=0;
 bool started=false;
 static void init(){modulus=3;suffix_bits=4;length_mod=1;}
 bool operator<(const Modular &x)const{
  return std::make_tuple(residue,suffix,length_residue,started)<std::make_tuple(x.residue,x.suffix,x.length_residue,x.started);
 }
 void push(Word w){
  assert(log2_N_CHAR==1 && ChrTransform::len_h==0);
  assert(modulus>=1 && modulus<=1000000 && suffix_bits>=0 && suffix_bits<=24 && length_mod>=1);
  int64_t mask=(int64_t(1)<<suffix_bits)-1;
  // Word's lowest bit is nearest the head: consume far-to-near.
  for(int64_t i=w.len;i-->0;){
   int64_t bit=w.get_chr(i);assert(bit==0 || bit==1);
   if(!started && !bit)continue;
   started=true;
   residue=(2*residue+bit)%modulus;
   suffix=((suffix<<1)|bit)&mask;
   length_residue=(length_residue+1)%length_mod;
  }
 }
 friend std::ostream &operator<<(std::ostream &os,const Modular &x){return os<<x.residue<<":"<<x.suffix<<":"<<x.length_residue<<":"<<x.started;}
};
'''
needle='struct LRUpair{';assert source.count(needle)==1;source=source.replace(needle,struct+needle)
dispatch='''
            add_cmd("Modular",[this]{
                Modular::init();
                def_var(m,Modular::modulus);
                def_var(k,Modular::suffix_bits);
                def_var(lmod,Modular::length_mod);
                add_cmd("run",[this]{
                    MitM_CTL::Decider<Modular> f;
                    f.len=n;
                    throw f.decide(tm,maxT,tape);
                });
            });
'''
needle='\t\t\tadd_cmd("LRUpair",[this]{';assert source.count(needle)==1;source=source.replace(needle,dispatch+needle)
dest=Path('lastfive_modular_native.cpp');dest.write_text(source)
env=os.environ.copy();env['PATH']=r'C:\msys64\ucrt64\bin'+os.pathsep+env['PATH']
cmd=[r'C:\msys64\ucrt64\bin\g++.exe','-O2','-std=c++17',str(dest),'-o','lastfive_modular_native.exe']
p=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=180)
Path('lastfive_modular_build.log').write_text(p.stdout+p.stderr)
out={'base_source':str(base),'base_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'source':str(dest),'source_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'command':cmd,'returncode':p.returncode,'changes':'Added Modular push summary and CLI dispatch only; verifier unchanged.'}
if p.returncode==0:out['binary_sha256']=hashlib.sha256(Path('lastfive_modular_native.exe').read_bytes()).hexdigest()
Path('lastfive_modular_build.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));raise SystemExit(p.returncode)
