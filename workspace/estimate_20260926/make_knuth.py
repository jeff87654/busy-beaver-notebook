# Build knuth_tnf.cpp: mxdys's TNF enumerator (unchanged deciders) plus a
# Knuth random-probe tree-size estimator. Estimates, for the full TNF tree
# rooted at A0=1RB: node count, holdouts (o_fail), terminal halters, and
# single-thread CPU seconds (per-node own time, excluding children).
import re, sys
src = open(r"C:/Users/jeffr/Downloads/bb8/mxdys_main.cpp", encoding="utf-8").read().replace("\r\n", "\n")

def sub1(old, new, s):
    assert s.count(old) == 1, (old, s.count(old))
    return s.replace(old, new)

# State count selectable at compile time.
src = sub1("#define BB7\n", "", src)
src = sub1("#ifdef BB7\nconstexpr int64_t N_STATE=7;\nconstexpr int64_t N_CHAR=2;\nconstexpr int64_t log2_N_STATE=3;",
           "#ifdef BBN\nconstexpr int64_t N_STATE=BBN;\nconstexpr int64_t N_CHAR=2;\nconstexpr int64_t log2_N_STATE=(BBN<=2?1:BBN<=4?2:BBN<=8?3:4);", src)
src = src.replace("#ifdef BB6\n", "#ifdef BB6_UNUSED\n")

# Globals for the estimator, placed before struct TNF.
src = sub1("struct TNF{\n", r'''
bool knuth_mode=false;
double kw_cur=1;               // weight of the node being processed
double k_nodes=0,k_unknown=0,k_halters=0,k_time=0; // per-probe accumulators
std::mt19937_64 krng;
inline double know(){return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();}
struct TNF{
''', src)

# expand(): in knuth mode follow one uniformly random child, scaling weight.
src = sub1("""		if(rest_trans==1)return;
		//if(rest_trans==5&&mt()%293!=2)return;
		auto &tr=tm.trans[s][in];
		auto tr0=tr;
""", """		if(rest_trans==1){ if(knuth_mode) k_halters+=kw_cur; return; }
		//if(rest_trans==5&&mt()%293!=2)return;
		auto &tr=tm.trans[s][in];
		auto tr0=tr;
		if(knuth_mode){
			int64_t ns=std::min<int64_t>(min_unused_state,N_STATE-1)+1;
			int64_t no=std::min<int64_t>(min_unused_char,N_CHAR-1)+1;
			int64_t k=ns*no*2;
			int64_t pick=(int64_t)(krng()%(uint64_t)k);
			int64_t s0=pick/(no*2), out=(pick/2)%no, dir=(pick%2)?1:-1;
			tr.nxt=s0;tr.dir=dir;tr.out=out;
			double w=kw_cur; kw_cur=w*k;
			dfs0(tm,min_unused_state+(s0==min_unused_state),min_unused_char+(out==min_unused_char),rest_trans-1);
			kw_cur=w; tr=tr0; return;
		}
""", src)

# dfs(): charge own time before recursing into expand, and at the end.
src = sub1("""	void dfs(TM &tm,int64_t min_unused_state,int64_t min_unused_char,int64_t rest_trans){
		if(app_stopped)return;
""", """	void dfs(TM &tm,int64_t min_unused_state,int64_t min_unused_char,int64_t rest_trans){
		if(app_stopped)return;
		const double kw=kw_cur; const double kt0=knuth_mode?know():0; bool kcharged=false;
		if(knuth_mode) k_nodes+=kw;
#define KCHARGE() do{ if(knuth_mode&&!kcharged){ k_time+=kw*(know()-kt0); kcharged=true; } }while(0)
""", src)
n = src.count("\t\t\t\texpand(tm,min_unused_state,min_unused_char,rest_trans,s,m);")
assert n == 5, n
src = src.replace("\t\t\t\texpand(tm,min_unused_state,min_unused_char,rest_trans,s,m);",
                  "\t\t\t\tKCHARGE(); expand(tm,min_unused_state,min_unused_char,rest_trans,s,m);")
src = sub1("""			++n_unknown;
			merr<<tm<<'\\n';
""", """			++n_unknown;
			if(knuth_mode) k_unknown+=kw; else merr<<tm<<'\\n';
""", src)
src = sub1("""		++n_decided;
		o:;
""", """		++n_decided;
		o:;
		KCHARGE();
""", src)

# New entry points: "knuth SECONDS SEED" and "exact" (full DFS from root, for validation).
src = sub1("int main(int argc,char **argv){\n", r'''
int main_knuth(int argc,char **argv){
	double secs=atof(argv[1]); uint64_t seed=strtoull(argv[2],0,10);
	krng.seed(seed); knuth_mode=true;
	TNF tnf;
	double S[4]={0,0,0,0},Q[4]={0,0,0,0},M[4]={0,0,0,0}; int64_t P=0;
	double t_start=know();
	while(know()-t_start<secs){
		TM tm; tm.trans[0][0].nxt=1; tm.trans[0][0].dir=1; tm.trans[0][0].out=1;
		k_nodes=k_unknown=k_halters=k_time=0; kw_cur=1;
		tnf.dfs(tm,2,2,N_STATE*N_CHAR-1);
		double v[4]={k_nodes,k_unknown,k_halters,k_time};
		for(int i=0;i<4;++i){S[i]+=v[i];Q[i]+=v[i]*v[i];M[i]=std::max(M[i],v[i]);}
		++P;
	}
	std::cout.precision(17);
	std::cout<<"{\"states\":"<<N_STATE<<",\"seed\":"<<seed<<",\"probes\":"<<P;
	const char *nm[4]={"nodes","holdouts","halters","cpu_seconds"};
	for(int i=0;i<4;++i) std::cout<<",\""<<nm[i]<<"\":{\"sum\":"<<S[i]<<",\"sumsq\":"<<Q[i]<<",\"max\":"<<M[i]<<"}";
	std::cout<<"}"<<std::endl;
	return 0;
}
int main_knuthfrom(int argc,char **argv){
	// knuthfrom TM a b c SECONDS SEED
	TM root; { std::stringstream ss(argv[1]); assert(ss>>root); }
	int64_t a=atoi(argv[2]),b=atoi(argv[3]),c=atoi(argv[4]);
	double secs=atof(argv[5]); uint64_t seed=strtoull(argv[6],0,10);
	krng.seed(seed); knuth_mode=true; TNF tnf;
	double S[4]={0,0,0,0},Q[4]={0,0,0,0},M[4]={0,0,0,0}; int64_t P=0; double t_start=know();
	while(know()-t_start<secs){
		TM tm=root; k_nodes=k_unknown=k_halters=k_time=0; kw_cur=1;
		tnf.dfs(tm,a,b,c);
		double v[4]={k_nodes,k_unknown,k_halters,k_time};
		for(int i=0;i<4;++i){S[i]+=v[i];Q[i]+=v[i]*v[i];M[i]=std::max(M[i],v[i]);}
		++P;
	}
	std::cout.precision(17);
	std::cout<<"{\"root\":\""<<argv[1]<<"\",\"states\":"<<N_STATE<<",\"seed\":"<<seed<<",\"probes\":"<<P;
	const char *nm[4]={"nodes","holdouts","halters","cpu_seconds"};
	for(int i=0;i<4;++i) std::cout<<",\""<<nm[i]<<"\":{\"sum\":"<<S[i]<<",\"sumsq\":"<<Q[i]<<",\"max\":"<<M[i]<<"}";
	std::cout<<"}"<<std::endl;
	return 0;
}
int main_exactfrom(int argc,char **argv){
	// exactfrom TM a b c HOLDOUT_FILE
	TM root; { std::stringstream ss(argv[1]); assert(ss>>root); }
	int64_t a=atoi(argv[2]),b=atoi(argv[3]),c=atoi(argv[4]);
	log_stream=std::ofstream(argv[5]);
	TNF tnf; double t0=know();
	tnf.dfs(root,a,b,c);
	log_stream.flush();
	std::cout<<"{\"root\":\""<<argv[1]<<"\",\"nodes\":"<<tnf.n_tot<<",\"holdouts\":"<<tnf.n_unknown<<",\"cpu_seconds\":"<<(know()-t0)<<"}"<<std::endl;
	return 0;
}
int main_batch(int argc,char **argv){
	// batch IN OUT_HOLDOUTS: run the enumerator's decider battery on each listed machine as a leaf
	// (rest_trans=1, so reaching an undefined transition within the deciders' limits counts as a quick halt).
	std::ifstream in(argv[1]); assert(in.is_open());
	log_stream=std::ofstream(argv[2]);
	TNF tnf; int64_t n=0; double t0=know();
	for(std::string line; std::getline(in,line); ){
		if(line.size()<10) continue;
		TM tm; { std::stringstream ss(line); if(!(ss>>tm)) continue; }
		tnf.dfs(tm,N_STATE,N_CHAR,1); ++n;
		if(n%5000==0){ log_stream.flush(); std::cerr<<n<<" machines, "<<tnf.n_unknown<<" holdouts, "<<(know()-t0)<<"s"<<std::endl; }
	}
	log_stream.flush();
	std::cout<<"{\"machines\":"<<n<<",\"holdouts\":"<<tnf.n_unknown<<",\"cpu_seconds\":"<<(know()-t0)<<"}"<<std::endl;
	return 0;
}
int main_exact(){
	TNF tnf; double t0=know();
	TM tm; tm.trans[0][0].nxt=1; tm.trans[0][0].dir=1; tm.trans[0][0].out=1;
	tnf.dfs(tm,2,2,N_STATE*N_CHAR-1);
	std::cout<<"{\"states\":"<<N_STATE<<",\"nodes\":"<<tnf.n_tot<<",\"holdouts\":"<<tnf.n_unknown<<",\"cpu_seconds\":"<<(know()-t0)<<"}"<<std::endl;
	return 0;
}
int main(int argc,char **argv){
	if(argc>=2&&!strcmp(argv[1],"knuth")) return main_knuth(argc-1,argv+1);
	if(argc>=2&&!strcmp(argv[1],"exact")) return main_exact();
	if(argc>=2&&!strcmp(argv[1],"knuthfrom")) return main_knuthfrom(argc-1,argv+1);
	if(argc>=2&&!strcmp(argv[1],"batch")) return main_batch(argc-1,argv+1);
	if(argc>=2&&!strcmp(argv[1],"exactfrom")) return main_exactfrom(argc-1,argv+1);
''', src)
open(sys.argv[1], "w", encoding="utf-8").write(src)
print("ok")
