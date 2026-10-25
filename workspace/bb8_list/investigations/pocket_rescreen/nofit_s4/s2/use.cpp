// use MACHINE STEPS : print first-use step of each transition (or - if unused)
#include <bits/stdc++.h>
#include <windows.h>
using namespace std;
int ns,W[16][2],M[16][2],N_[16][2];
void parse(const string&s){ns=0;size_t i=0;int q=0;
 while(i<s.size()){for(int b=0;b<2;b++){ if(s[i]=='-'){W[q][b]=-1;i+=3;} else {W[q][b]=s[i]-'0';M[q][b]=s[i+1]=='R'?1:-1;N_[q][b]=s[i+2]-'A';i+=3;}} q++; if(i<s.size()&&s[i]=='_')i++;} ns=q;}
int main(int c,char**v){SetPriorityClass(GetCurrentProcess(),IDLE_PRIORITY_CLASS);parse(v[1]);long long n=atoll(v[2]);
 const long long SZ=1<<26; vector<unsigned char>t(SZ,0); long long p=SZ/2; int q=0; long long fu[16][2]; for(auto&a:fu)a[0]=a[1]=-1;
 for(long long s=0;s<n;s++){int b=t[p]; if(fu[q][b]<0)fu[q][b]=s; if(W[q][b]<0){printf("HALT %lld ",s);break;} t[p]=W[q][b]; p+=M[q][b]; q=N_[q][b]; if(p<1||p>=SZ-1){printf("TAPE ");break;}}
 for(int i=0;i<ns;i++)for(int b=0;b<2;b++) printf("%c%d:%s ",'A'+i,b,fu[i][b]<0?"-":to_string(fu[i][b]).c_str()); puts("");}
