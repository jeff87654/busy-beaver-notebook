// Independent one-transition-at-a-time checker. No macro or rewrite rules.
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <windows.h>
int main(int argc,char**argv){
 SetPriorityClass(GetCurrentProcess(),IDLE_PRIORITY_CLASS);
 const std::string m="1RB---_1RC1RD_0LD1LC_1RF0LE_0LG1LC_0RB0RG_0RA1LD";
 int w[7][2],d[7][2],n[7][2];
 for(int q=0;q<7;q++)for(int s=0;s<2;s++){
  int p=7*q+3*s;
  if(m[p]=='-'){n[q][s]=-1;continue;}
  w[q][s]=m[p]-'0';d[q][s]=m[p+1]=='R'?1:-1;n[q][s]=m[p+2]-'A';
 }
 std::vector<unsigned char> tape(4000000);int h=2000000,lo=h,hi=h,q=0;
 unsigned long long t=0,target;std::string expected;int checks=0;
 std::ifstream f(argv[1]);
 while(f>>target>>expected){
  while(t<target){
   int b=tape[h];if(n[q][b]<0){std::cerr<<"EARLY HALT "<<t<<"\n";return 2;}
   tape[h]=w[q][b];h+=d[q][b];q=n[q][b];++t;
   if(h<1||h+1>=(int)tape.size()){std::cerr<<"TAPE LIMIT\n";return 3;}
   if(h<lo)lo=h;if(h>hi)hi=h;
  }
  int last=hi;while(last>=lo&&!tape[last])--last;
  bool ok=q==6 && last-h+1==(int)expected.size();
  for(int i=lo;i<h&&ok;i++)if(tape[i])ok=false;
  for(int i=h;i<=last&&ok;i++)if(tape[i]!=expected[i-h]-'0')ok=false;
  if(!ok){std::cerr<<"MISMATCH "<<t<<" state "<<q<<" length "<<last-h+1<<" expected "<<expected.size()<<"\n";return 4;}
  ++checks;
 }
 std::cout<<"PASS "<<checks<<" complete tapes and head/state checks; "<<t<<" literal transitions\n";
}
