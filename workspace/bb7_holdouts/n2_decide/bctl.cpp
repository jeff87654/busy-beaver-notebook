// bctl: MitM closed-tape-language search with a 2-BLOCK run-length side abstraction (single-cell head).
// Blocks are aligned to absolute even positions. A side is the cell sequence pushed from the far end towards the head;
// summary = partial cell (if the nearest pushed cell starts a block) + runs (block, count) of complete blocks; count exact
// <= BK else big mod BM; first TA runs kept as anchors, then at most H nearest runs (older non-anchor runs dropped).
// Leading 00 blocks ignored. Sound: side languages are closures of observed pushes (DFA = push function).
//   bctl MACHINE TA H BK BM MAXCFG [certfile|-] [tracelen]
#include <bits/stdc++.h>
using namespace std;
struct Tr { int w, d, q; bool ok; };
static Tr tm_[8][2]; static int NS = 0;
static int TA, H;
// entry: a:8 bits | b:6 bits | cnt:8 bits ; partial stored as last element with a flag bit 31
typedef vector<uint32_t> Sum;  // s[0] = partial (0 none, 1 cell0, 2 cell1); then runs: blk<<16 | code
static int BK, BM;  // block count abstraction: exact <= BK, then big mod BM
static unordered_map<string, int> idOf; static vector<Sum> sums;
static int intern(const Sum& s) {
  string k((const char*)s.data(), s.size() * 4); auto it = idOf.find(k); if (it != idOf.end()) return it->second;
  int id = sums.size(); sums.push_back(s); idOf.emplace(k, id); return id;
}
static uint32_t incv(uint32_t v, int K, int M) { if ((int)v < K) return v + 1; if ((int)v == K) return K + 1 + ((K + 1) % M); return K + 1 + ((v - K - 1 + 1) % M); }
static Sum pushS(const Sum& s0, int bit) {
  Sum s = s0;
  if (s[0] == 0) { s[0] = 1 + bit; return s; }
  uint32_t blk = ((s[0] - 1) << 1) | bit; s[0] = 0;
  if (s.size() == 1 && blk == 0) return s;  // leading 00 ignored
  if (s.size() > 1 && (s.back() >> 16) == blk) { s.back() = (blk << 16) | incv(s.back() & 0xffff, BK, BM); return s; }
  s.push_back((blk << 16) | 1);
  if ((int)s.size() - 1 > TA + H) s.erase(s.begin() + 1 + TA);
  return s;
}
static string vstr(uint32_t v, int K) { return (int)v <= K ? to_string(v) : ("~" + to_string(v - K - 1)); }
static const char* BN[4] = {"00", "01", "10", "11"};
static const char* BNR[4] = {"00", "10", "01", "11"};
static string showS(const Sum& s, bool right = false) {
  string o;
  for (size_t i = 1; i < s.size(); i++) { int b = s[i] >> 16; o += string(right ? BNR[b] : BN[b]) + "^" + vstr(s[i] & 0xffff, BK) + ((int)i == TA ? " |" : "") + " "; }
  if (s[0]) o += "<" + to_string(s[0] - 1) + ">";
  return o.empty() ? "_" : o;
}
static unordered_map<uint64_t, int> pushT; static vector<vector<pair<int, int>>> pops; static vector<vector<uint64_t>> waitL, waitR;
static int pushId(int id, int b) {
  uint64_t k = ((uint64_t)id << 1) | b; auto it = pushT.find(k); if (it != pushT.end()) return it->second;
  int nid = intern(pushS(sums[id], b));
  if (pops.size() < sums.size()) { pops.resize(sums.size()); waitL.resize(sums.size()); waitR.resize(sums.size()); }
  pushT.emplace(k, nid); pops[nid].push_back({id, b});
  return nid;
}
static inline uint64_t ck(uint64_t l, int q, int s, uint64_t r) { return (l << 34) | (r << 4) | (q << 1) | s; }
static void decode(uint64_t c, int& l, int& q, int& s, int& r) { l = c >> 34; r = (c >> 4) & ((1u << 30) - 1); q = (c >> 1) & 7; s = c & 1; }
static unordered_map<uint64_t, uint64_t> parent; static deque<uint64_t> work;
static void add(uint64_t c, uint64_t par) { if (parent.emplace(c, par).second) work.push_back(c); }
static string showC(uint64_t c) { int l, q, s, r; decode(c, l, q, s, r); string rr = showS(sums[r], true); return "L: " + showS(sums[l]) + "  [" + char('A' + q) + to_string(s) + "]  R(far->near): " + rr; }
int main(int argc, char** argv) {
  string ms = argv[1]; TA = atoi(argv[2]); H = atoi(argv[3]); BK = atoi(argv[4]); BM = atoi(argv[5]);
  long long MAXC = atoll(argv[6]); string certf = argc > 7 ? argv[7] : ""; int TL = argc > 8 ? atoi(argv[8]) : 300;
  if (certf == "-") certf = "";
  { stringstream ss(ms); string row; while (getline(ss, row, '_')) { for (int c = 0; c < 2; c++) { string t = row.substr(3 * c, 3); if (t[0] == '-') tm_[NS][c] = {0, 0, 0, false}; else tm_[NS][c] = {t[0] - '0', t[1] == 'R' ? 1 : -1, t[2] - 'A', true}; } NS++; } }
  int E = intern(Sum{0}); int E1 = intern(Sum{1}); pops.resize(2); waitL.resize(2); waitR.resize(2);
  pushT.emplace(((uint64_t)E << 1) | 0, E1); pops[E1].push_back({E, 0}); pushT.emplace(((uint64_t)E1 << 1) | 0, E); pops[E].push_back({E1, 0});
  if (getenv("SEED")) {  // SEED="word headpos state": seed config instead of the blank tape
    string sw; long long hp; char sq; { stringstream ss(getenv("SEED")); ss >> sw >> hp >> sq; }
    int l = E; for (long long i = 0; i < hp; i++) l = pushId(l, sw[i] - '0');
    int r = E; for (long long i = (long long)sw.size() - 1; i > hp; i--) r = pushId(r, sw[i] - '0');
    int s = hp < (long long)sw.size() ? sw[hp] - '0' : 0;
    add(ck(l, sq - 'A', s, r), ~0ULL);
  } else add(ck(E, 0, 0, E1), ~0ULL);
  vector<size_t> propL, propR; long long iter = 0;
  while (true) {
    while (!work.empty()) {
      uint64_t c = work.front(); work.pop_front();
      int l, q, s, r; decode(c, l, q, s, r); Tr t = tm_[q][s];
      if (!t.ok) {
        printf("FAIL: halting abstract config reachable (%zu configs, %zu sides)\n", parent.size(), sums.size());
        vector<uint64_t> path; uint64_t x = c; while (x != ~0ULL) { path.push_back(x); x = parent[x]; }
        reverse(path.begin(), path.end());
        for (int i = max(0, (int)path.size() - TL); i < (int)path.size(); i++) printf("%5d %s\n", i, showC(path[i]).c_str());
        return 1;
      }
      if (t.d == 1) { int nl = pushId(l, t.w); waitR[r].push_back(c); for (auto [pr, b] : pops[r]) add(ck(nl, t.q, b, pr), c); }
      else { int nr = pushId(r, t.w); waitL[l].push_back(c); for (auto [pl, b] : pops[l]) add(ck(pl, t.q, b, nr), c); }
      if ((long long)parent.size() > MAXC) { printf("GIVEUP: %zu configs, %zu side states\n", parent.size(), sums.size());
        mt19937 rng(1); for (int i = 0; i < 40; i++) { size_t k = rng() % sums.size(); printf("  side %zu: %s\n", k, showS(sums[k]).c_str()); }
        int cnt = 0; for (auto& [cc, pp] : parent) { if (rng() % 100000 == 0 && cnt < 30) { printf("  cfg %s\n", showC(cc).c_str()); cnt++; } }
        return 2; }
      if (++iter % 2000000 == 0) fprintf(stderr, "iter %lld cfgs %zu sides %zu\n", iter, parent.size(), sums.size());
    }
    bool any = false;
    propL.resize(sums.size(), 0); propR.resize(sums.size(), 0);
    for (size_t st = 0; st < pops.size(); st++) {
      size_t ne = pops[st].size();
      if (propL[st] < ne) {
        for (size_t wi = 0; wi < waitL[st].size(); wi++) { uint64_t c = waitL[st][wi]; int l, q, s, r; decode(c, l, q, s, r); Tr t = tm_[q][s];
          int nr = pushId(r, t.w); for (size_t ei = propL[st]; ei < ne; ei++) { auto [pl, b] = pops[st][ei]; add(ck(pl, t.q, b, nr), c); } }
        propL[st] = ne; any = true;
      }
      if (propR[st] < ne) {
        for (size_t wi = 0; wi < waitR[st].size(); wi++) { uint64_t c = waitR[st][wi]; int l, q, s, r; decode(c, l, q, s, r); Tr t = tm_[q][s];
          int nl = pushId(l, t.w); for (size_t ei = propR[st]; ei < ne; ei++) { auto [pr, b] = pops[st][ei]; add(ck(nl, t.q, b, pr), c); } }
        propR[st] = ne; any = true;
      }
    }
    if (work.empty()) {
      bool done = true; propL.resize(sums.size(), 0); propR.resize(sums.size(), 0);
      for (size_t st = 0; st < pops.size(); st++) if (propL[st] < pops[st].size() || propR[st] < pops[st].size()) { done = false; break; }
      if (done) break;
    }
    (void)any;
  }
  printf("CLOSED: %zu abstract configs, %zu side states, %zu push edges\n", parent.size(), sums.size(), pushT.size());
  if (!certf.empty()) {
    FILE* f = fopen(certf.c_str(), "w");
    fprintf(f, "sides %zu\n", sums.size());
    for (auto& [k, v] : pushT) fprintf(f, "e %llu %d %d\n", (unsigned long long)(k >> 1), (int)(k & 1), v);
    for (auto& [c, p] : parent) { int l, q, s, r; decode(c, l, q, s, r); fprintf(f, "c %d %d %d %d\n", l, q, s, r); }
    fclose(f);
  }
  return 0;
}
