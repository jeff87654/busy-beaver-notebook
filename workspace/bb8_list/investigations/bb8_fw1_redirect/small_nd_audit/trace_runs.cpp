
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

struct Tr { int w, d, nx; bool def; };
static Tr t[16];
static std::string P, U_, S_, Ssep;
static long long al, be, alB, beB;
static bool mirror;

static bool kparse(const std::string &w, std::string &out) {
  if (!(w.size() >= P.size() + S_.size() && w.compare(0, P.size(), P) == 0 && w.compare(w.size()-S_.size(), S_.size(), S_) == 0)) return false;
  std::vector<long long> runs; size_t i = P.size(), e = w.size() - S_.size();
  const std::string &u = U_; const std::string &s = Ssep;
  while (true) {
    long long k = 0; size_t i0 = i;
    while (i + u.size() <= e && w.compare(i, u.size(), u) == 0) { i += u.size(); ++k; }
    if (i == e) { runs.push_back(k); break; }
    bool fs = false;
    for (long long kk = k; kk >= 0; --kk) {
      size_t j = i0 + kk*u.size();
      if (j + s.size() <= e && w.compare(j, s.size(), s) == 0) { runs.push_back(kk); i = j + s.size(); fs = true; break; }
    }
    if (!fs) return false;
  }
  if (runs.size() < 2) return false;
  out = "runs=[";
  for (size_t j = 0; j < runs.size(); ++j) {
    if (j) out += ",";
    out += std::to_string(runs[j]);
  }
  out += "] (a=" + std::to_string((runs[runs.size()-2]-be)/al) + ",r=" + std::to_string((runs[runs.size()-2]-be)%al)
      + ",b=" + std::to_string((runs.back()-beB)/alB) + ",rb=" + std::to_string((runs.back()-beB)%alB) + ")";
  return true;
}

int main(int argc, char **argv) {
  std::string m = argv[1];
  mirror = argv[2][0] == 'L'; int TQ = argv[3][0]-'A'; P = argv[4]; U_ = argv[5]; Ssep = argv[6];
  al = atoll(argv[7]); be = atoll(argv[8]); alB = atoll(argv[9]); beB = atoll(argv[10]); S_ = argv[11];
  if (P == "-") P = ""; if (S_ == "-") S_ = "";
  std::string w0 = argv[12];
  for (int q = 0; q < 8; ++q) for (int c = 0; c < 2; ++c) {
    size_t o = 7*q + 3*c;
    const char *x = m.c_str() + o;
    if (x[0] == '-') t[2*q+c].def = false;
    else t[2*q+c] = {x[0]-'0', (x[1] == 'R' ? 1 : -1) * (mirror ? -1 : 1), x[2]-'A', true};
  }
  long long size = 1 << 20; std::vector<unsigned char> tp(size, 0);
  long long off = size/2, lo = 0, hi = (long long)w0.size()-1, pos = (long long)w0.size();
  for (size_t i = 0; i < w0.size(); ++i) tp[off + i] = w0[i] - '0';
  int q = TQ;
  for (long long st = 0; st < 2000000; ++st) {
    unsigned char *T = tp.data() + off; int c = T[pos];
    if (st > 0 && c == 0 && q == TQ && pos > hi) {
      while (lo <= hi && !T[hi]) --hi;
      while (lo <= hi && !T[lo]) ++lo;
      std::string ww;
      for (long long i = lo; i < pos; ++i) ww += char('0'+T[i]);
      std::string out;
      if (kparse(ww, out)) {
        printf("@%lld: %s\n", st, out.c_str());
        if (out.find(",r=0,b=0,rb=0)") != std::string::npos) break;
      }
    }
    const Tr &tr = t[2*q+c];
    if (!tr.def) { printf("HALT @%lld\n", st); break; }
    T[pos] = tr.w;
    if (tr.w) { if (pos < lo) lo = pos; if (pos > hi) hi = pos; }
    pos += tr.d; q = tr.nx;
  }
  return 0;
}
