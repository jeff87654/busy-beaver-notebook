// ngram MACHINE MAXSTEPS NG : literal run from blank; counts of transition n-grams (state,read) ending at each step,
// fast integer coding. Prints n-grams that contain a given substring (argv[4]) or all.
#include <bits/stdc++.h>
using namespace std;
int main(int argc,char**argv){
  string m=argv[1]; long long MX=atoll(argv[2]); int NG=atoi(argv[3]); string flt=argc>4?argv[4]:"";
  int w[16][2],d[16][2],nx[16][2],S=0; {stringstream ss(m);string r;while(getline(ss,r,'_')){for(int c=0;c<2;c++){string t=r.substr(3*c,3);if(t[0]=='-'){w[S][c]=0;d[S][c]=0;nx[S][c]=-1;}else{w[S][c]=t[0]-'0';d[S][c]=t[1]=='R'?1:-1;nx[S][c]=t[2]-'A';}}S++;}}
  const long long N=1<<27; vector<unsigned char> T(N,0); long long p=N/2; int q=0;
  unsigned long long code=0, msk=(1ULL<<(4*NG))-1; unordered_map<unsigned long long,long long> h;
  long long s;
  for(s=0;s<MX;s++){
    int c=T[p]; code=((code<<4)|(q*2+c))&msk; if(s>=NG-1) h[code]++;
    if(nx[q][c]<0){printf("HALT at %lld\n",s);break;}
    T[p]=w[q][c]; p+=d[q][c]; q=nx[q][c]; if(p<2||p>N-3){printf("overflow\n");break;}
  }
  vector<pair<string,long long>> v;
  for(auto&e:h){string k; for(int i=NG-1;i>=0;i--){int x=(e.first>>(4*i))&15; k+=char('A'+x/2); k+=char('0'+x%2);} if(flt.empty()||k.find(flt)!=string::npos) v.push_back({k,e.second});}
  sort(v.begin(),v.end()); for(auto&e:v) printf("%s %lld\n",e.first.c_str(),e.second);
  printf("steps %lld\n",s);
}
