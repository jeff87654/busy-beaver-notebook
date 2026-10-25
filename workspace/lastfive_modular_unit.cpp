#define main upstream_main
#include "lastfive_modular_native.cpp"
#undef main
int main(){
 ChrTransform::init();
 using M=MitM_CTL::Modular;
 M::init(); M::suffix_bits=4; M::length_mod=5;
 M x;x.push(Word(0,7));assert(!x.started && x.residue==0 && x.suffix==0 && x.length_residue==0);
 x.push(Word(11,4));assert(x.residue==2 && x.suffix==11 && x.length_residue==4);
 x.push(Word(6,4));assert(x.residue==2 && x.suffix==6 && x.length_residue==3);
 M y;y.push(Word(182,8));assert(!(x<y)&&!(y<x));
 for(int n=1;n<=3;++n){
  MitM_CTL::Decider<M>::DFA d;d.init(n);
  auto id=d.push_all(std::vector<chr_t>{1,0,1,1,0,1,1,0},1,n);
  auto z=*d.idr.at(id);assert(!(z<x)&&!(x<z));
 }
 std::cout<<"PASS: Word bit order, block lengths1/2/3, leading padding, residue, suffix, length modulus\n";
}
