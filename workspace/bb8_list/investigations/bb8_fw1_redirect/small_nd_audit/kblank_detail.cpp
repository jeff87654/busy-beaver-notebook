// kblank_detail.cpp: trace blank tape up to N steps for each machine in MACHINES_FILE.
// Records first 8 list-changing K-moments (with b == B0), all E_r -> K_after_E_r full configs, and last K-moment.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>

struct Tr { int w, d, nx; bool def; };
static const int NS = 8;
static std::vector<Tr> t(16);
static int TQ;
static std::string P, U_, S_, Ssep;
static long long al, be, alB, beB, B0 = -1;
static bool mirror;
static std::vector<unsigned char> tp;

static bool kparse(const std::string &w, std::string &out, std::string &ds_out, long long &len_out, long long &a_out, long long &b_out) {
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
  long long bl = runs.back();
  if (bl < beB || (bl-beB) % alB) return false;
  b_out = (bl-beB)/alB;
  if (B0 >= 0 && b_out != B0) return false;
  for (size_t j = 0; j + 1 < runs.size(); ++j) if (runs[j] < be || (runs[j]-be) % al) return false;
  ds_out.clear();
  len_out = (long long)runs.size() - 2;
  for (size_t j = 0; j + 2 < runs.size();) {
    long long v = (runs[j]-be)/al; size_t r = j;
    while (r + 2 < runs.size() && (runs[r]-be)/al == v) ++r;
    ds_out += std::to_string(v);
    if (r - j > 1) ds_out += "^" + std::to_string(r-j);
    if (r + 2 < runs.size()) ds_out += ",";
    j = r;
  }
  a_out = (runs[runs.size()-2]-be)/al;
  out = "[" + ds_out + "];" + std::to_string(a_out) + ";" + std::to_string(b_out);
  return true;
}

static void load(const std::string &m) {
  for (int q = 0; q < NS; ++q) for (int c = 0; c < 2; ++c) {
    size_t o = 7*q + 3*c;
    if (o >= m.size()) { t[2*q+c].def = false; continue; }
    const char *x = m.c_str() + o;
    if (x[0] == '-') t[2*q+c].def = false;
    else t[2*q+c] = {x[0]-'0', (x[1] == 'R' ? 1 : -1) * (mirror ? -1 : 1), x[2]-'A', true};
  }
}

int main(int argc, char **argv) {
  mirror = argv[2][0] == 'L'; TQ = argv[3][0]-'A'; P = argv[4]; U_ = argv[5]; Ssep = argv[6];
  al = atoll(argv[7]); be = atoll(argv[8]); alB = atoll(argv[9]); beB = atoll(argv[10]); S_ = argv[11];
  if (P == "-") P = ""; if (S_ == "-") S_ = "";
  long long N = atoll(argv[12]); B0 = atoll(argv[13]);
  std::ifstream mf(argv[1]); std::string l;
  while (std::getline(mf, l)) {
    if (l.size() < 20) continue;
    std::string m = l.substr(0, l.find('\t'));
    load(m);
    long long size = 1 << 16; tp.assign(size, 0);
    long long off = size/2, lo = 1, hi = 0, pos = 0; int q = 0;
    long long nK = 0, nE = 0, maxlen = 0;
    std::string first_ks, e_rebuilds, last_k, prev_ds = "___NONE___";
    int n_first_logged = 0;
    bool afterE = false;
    char stc = 'T'; long long hst = 0;
    for (long long st = 0; st < N; ++st) {
      if (pos + off < 2 || pos + off + 2 >= size) {
        if (size >= (1LL << 24)) { stc = 'W'; hst = st; break; }
        std::vector<unsigned char> nt(size*2, 0);
        memcpy(nt.data()+size/2, tp.data(), size);
        off += size/2; size *= 2; tp.swap(nt);
      }
      unsigned char *T = tp.data() + off; int c = T[pos];
      if (c == 0 && q == TQ && lo <= hi) {
        while (lo <= hi && !T[hi]) --hi;
        while (lo <= hi && !T[lo]) ++lo;
        if (pos > hi && lo <= hi && pos - lo < 100000) {
          std::string ww; ww.reserve(pos - lo);
          for (long long i = lo; i < pos; ++i) ww += char('0'+T[i]);
          std::string o, ds; long long len = 0, a_val = 0, b_val = 0;
          if (kparse(ww, o, ds, len, a_val, b_val)) {
            ++nK;
            if (len > maxlen) maxlen = len;
            last_k = "@" + std::to_string(st) + ":" + o;
            if (ds != prev_ds || len == 0) {
              if (n_first_logged < 8) {
                if (!first_ks.empty()) first_ks += " -> ";
                first_ks += "@" + std::to_string(st) + ":" + o;
                ++n_first_logged;
              }
              prev_ds = ds;
            }
            if (len == 0) {
              ++nE;
              if (e_rebuilds.size() < 600) {
                if (!e_rebuilds.empty()) e_rebuilds += " | ";
                e_rebuilds += "E" + std::to_string(nE) + "(" + std::to_string(a_val) + ")@" + std::to_string(st);
              }
              afterE = true;
            } else if (afterE) {
              if (e_rebuilds.size() < 600) {
                e_rebuilds += "->" + o + "(L=" + std::to_string(len) + ")";
              }
              afterE = false;
            }
          }
        }
      }
      const Tr &tr = t[2*q+c];
      if (!tr.def) { stc = 'H'; hst = st; break; }
      T[pos] = tr.w;
      if (tr.w) { if (lo > hi) lo = hi = pos; else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; } }
      pos += tr.d; q = tr.nx;
      if (st == 100000 && nK == 0) { stc = 'N'; hst = st; break; }
    }
    printf("%s\t%c:%lld\t%lld\t%lld\t%lld\t%s\t%s\t%s\n",
           m.c_str(), stc, hst, nK, nE, maxlen,
           first_ks.c_str(), e_rebuilds.c_str(), last_k.c_str());
    fflush(stdout);
  }
  return 0;
}
