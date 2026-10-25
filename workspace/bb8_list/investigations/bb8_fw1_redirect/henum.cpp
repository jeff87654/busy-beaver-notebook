// henum: halt-redirect enumerator for 7-state bases.
//  henum BASE SIDE Q P u s al be alB beB S STARTS BUD_BLANK BUD_E [ONLY_T=-1]
// For every defined base slot T (or only ONLY_T = 2*state+read) and every (w,d), T := w d H (H = 8th state); then
// TNF-branches the undefined slots {U, H0, H1} on first reach (blank start first, then the STARTS with branch flag 1),
// leaving at least one undefined. Each node is also a leaf. Output per leaf (except quick blank halters, counted):
//   T=<slot><wd> <machine> | blank outcome | per start outcome
// blank: H:steps:ones:slot  or  R:steps:ones:hUses:hLast:span (running at budget)  or  W (tape overflow)
// start: H:steps:slot | K:ds;a;b:steps | U:slot (undefined, non-branch start) | T (budget) | W
// Starts file lines: label word head(index) state(letter) branchflag ; coordinates in the template frame (mirrored if SIDE=L).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
struct Tr { int w, d, nx; bool def; };
static const int NS = 8; static int H = 7;
static std::vector<Tr> t(16);
static int TQ; static std::string P, U_, S_; static long long al, be, alB, beB; static bool mirror;
static long long BB, BE, B0 = -1;
struct St { std::string lab, w; long long head; int q; int br; };
static std::vector<St> sts;
static long long nodes = 0, quiet = 0, printed = 0;
static std::string fmt() { std::string s;
  for (int q = 0; q < NS; ++q) { if (q) s += '_'; for (int c = 0; c < 2; ++c) { const Tr &x = t[2*q+c];
    if (!x.def) s += "---"; else { s += char('0'+x.w); int d = mirror ? -x.d : x.d; s += d > 0 ? 'R' : 'L'; s += char('A'+x.nx); } } }
  return s; }
static std::vector<unsigned char> tp;
// parse tape word w (lo..pos-1) as P u^(al d+be) s ... u^(alB b+beB) S ; returns false if not parseable
static bool kparse(const std::string &w, std::string &out) {
  if (!(w.size() >= P.size() + S_.size() && w.compare(0, P.size(), P) == 0 && w.compare(w.size()-S_.size(), S_.size(), S_) == 0)) return false;
  std::vector<long long> runs; size_t i = P.size(), e = w.size() - S_.size();
  const std::string &u = U_; extern std::string Ssep; const std::string &s = Ssep;
  while (true) { long long k = 0; size_t i0 = i; while (i + u.size() <= e && w.compare(i, u.size(), u) == 0) { i += u.size(); ++k; }
    if (i == e) { runs.push_back(k); break; }
    bool fs = false;
    for (long long kk = k; kk >= 0; --kk) { size_t j = i0 + kk*u.size(); if (j + s.size() <= e && w.compare(j, s.size(), s) == 0) { runs.push_back(kk); i = j + s.size(); fs = true; break; } }
    if (!fs) return false; }
  if (runs.size() < 2) return false;
  long long bl = runs.back(); if (bl < beB || (bl-beB) % alB) return false; if (B0 >= 0 && (bl-beB)/alB != B0) return false;
  for (size_t j = 0; j + 1 < runs.size(); ++j) if (runs[j] < be || (runs[j]-be) % al) return false;
  out.clear();
  for (size_t j = 0; j + 2 < runs.size();) { long long v = (runs[j]-be)/al; size_t r = j; while (r + 2 < runs.size() && (runs[r]-be)/al == v) ++r;
    out += std::to_string(v); if (r - j > 1) out += "^" + std::to_string(r-j); if (r + 2 < runs.size()) out += ","; j = r; }
  out += ";" + std::to_string((runs[runs.size()-2]-be)/al) + ";" + std::to_string((bl-beB)/alB);
  return true; }
std::string Ssep;
struct Res { char kind; long long steps, ones; int slot; std::string k; long long huses, hlast, span; };
// mode 0 = blank (run to budget), mode 1 = stop at first parseable K-moment after step>=1
static Res sim(const St *s, long long bud) {
  long long size = 1 << 16; std::string w = s ? s->w : ""; while (size < 4*(long long)w.size() + 1024) size *= 2;
  tp.assign(size, 0); long long off = size/2; long long lo = 1, hi = 0;
  for (size_t z = 0; z < w.size(); ++z) if (w[z] == '1') { tp[off+z] = 1; if (lo > hi) lo = hi = z; else hi = z; }
  long long pos = s ? s->head : 0; int q = s ? s->q : 0; long long huses = 0, hlast = -1, mn = 0, mx = 0, ckp = 1024, lastsp = -1;
  for (long long st = 0; st < bud; ++st) {
    if (pos + off < 2 || pos + off + 2 >= size) { if (size >= (1LL << 26)) return {'W', st, 0, -1, "", huses, hlast, mx-mn};
      std::vector<unsigned char> nt(size*2, 0); memcpy(nt.data()+size/2, tp.data(), size); off += size/2; size *= 2; tp.swap(nt); }
    unsigned char *T = tp.data() + off; int c = T[pos];
    if (s && st > 0 && c == 0 && q == TQ && lo <= hi) {
      while (lo <= hi && !T[hi]) --hi; while (lo <= hi && !T[lo]) ++lo;
      if (pos > hi && lo <= hi) { std::string ww; ww.reserve(pos-lo); for (long long i = lo; i < pos; ++i) ww += char('0'+T[i]); std::string o;
        if (kparse(ww, o)) return {'K', st, 0, -1, o, huses, hlast, 0}; } }
    const Tr &tr = t[2*q+c];
    if (!tr.def) { long long ones = 0; for (auto v : tp) ones += v; return {'H', st, ones, 2*q+c, "", huses, hlast, mx-mn}; }
    if (q == H) { ++huses; hlast = st; }
    T[pos] = tr.w; if (tr.w) { if (lo > hi) lo = hi = pos; else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; } }
    pos += tr.d; q = tr.nx; if (pos < mn) mn = pos; if (pos > mx) mx = pos;
    if (!s && st == ckp) { long long sp = mx - mn; double lim = 8.0 * __builtin_sqrt((double)st) + 200;
      if (st >= 32768 && sp > lim) return {'X', st, 0, -1, "", huses, hlast, sp};
      if (st >= 131072 && sp == lastsp) return {'C', st, 0, -1, "", huses, hlast, sp};
      lastsp = sp; ckp *= 2; }
  }
  return {'T', bud, 0, -1, "", huses, hlast, mx-mn}; }
static std::string sl(int x) { std::string r; r += char('A'+x/2); r += char('0'+x%2); return r; }
static std::string tag;
static void dfs() {
  ++nodes; int undef = 0; for (int i = 0; i < 16; ++i) if (!t[i].def) ++undef;
  Res b = sim(nullptr, BB); int bs = -1;
  std::vector<Res> rs;
  if (b.kind == 'H') bs = b.slot;
  else if (b.kind == 'T') for (auto &s : sts) { Res r = sim(&s, BE); if (r.kind == 'H' && !s.br) { r.kind = 'U'; } rs.push_back(r); if (r.kind == 'H' && bs < 0) bs = r.slot; }
  if (b.kind == 'H' && b.steps < 100000) ++quiet;
  else { ++printed; printf("%s\t%s\t", tag.c_str(), fmt().c_str());
    if (b.kind == 'H') printf("H:%lld:%lld:%s", b.steps, b.ones, sl(b.slot).c_str());
    else printf("%c:%lld:%lld:%lld:%lld", b.kind, b.steps, b.huses, b.hlast, b.span);
    for (size_t i = 0; i < rs.size(); ++i) { auto &r = rs[i]; printf("\t");
      if (r.kind == 'H') printf("H:%lld:%s", r.steps, sl(r.slot).c_str()); else if (r.kind == 'U') printf("U:%s", sl(r.slot).c_str());
      else if (r.kind == 'K') printf("K:%s:%lld", r.k.c_str(), r.steps); else printf("%c", r.kind); }
    printf("\n"); }
  if (bs < 0 || undef <= 1) return;
  for (int nx = 0; nx < NS; ++nx) for (int w = 0; w < 2; ++w) for (int d = -1; d <= 1; d += 2) {
    t[bs] = {w, d, nx, true}; dfs(); t[bs].def = false; } }
int main(int argc, char **argv) {
  std::string base = argv[1]; mirror = argv[2][0] == 'L'; TQ = argv[3][0]-'A'; P = argv[4]; U_ = argv[5]; Ssep = argv[6];
  al = atoll(argv[7]); be = atoll(argv[8]); alB = atoll(argv[9]); beB = atoll(argv[10]); S_ = argv[11];
  if (P == "-") P = ""; if (S_ == "-") S_ = "";
  BB = atoll(argv[13]); BE = atoll(argv[14]); B0 = atoll(argv[15]); int only = argc > 16 ? atoi(argv[16]) : -1;
  for (int q = 0; q < 7; ++q) for (int c = 0; c < 2; ++c) { const char *x = base.c_str() + 7*q + 3*c;
    if (x[0] == '-') t[2*q+c].def = false; else t[2*q+c] = {x[0]-'0', (x[1] == 'R' ? 1 : -1) * (mirror ? -1 : 1), x[2]-'A', true}; }
  t[14].def = t[15].def = false;
  { std::ifstream f(argv[12]); std::string l; while (std::getline(f, l)) { std::stringstream ss(l); St s; std::string qs; if (ss >> s.lab >> s.w >> s.head >> qs >> s.br) { if (s.w == "-") s.w = ""; s.q = qs[0]-'A'; sts.push_back(s); } } }
  printf("#starts"); for (auto &s : sts) printf("\t%s", s.lab.c_str()); printf("\n");
  for (int T = 0; T < 14; ++T) { if (!t[T].def) continue; if (only >= 0 && T != only) continue; Tr save = t[T];
    for (int w = 0; w < 2; ++w) for (int d = -1; d <= 1; d += 2) { t[T] = {w, d, H, true};
      tag = sl(T) + char('0'+w) + ((mirror ? -d : d) > 0 ? "R" : "L"); dfs(); }
    t[T] = save; }
  printf("#summary nodes=%lld printed=%lld quiet=%lld\n", nodes, printed, quiet); }
