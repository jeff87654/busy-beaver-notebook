// ngpar MACHINE kL E1L M1L E2L M2L kR E1R M1R E2R M2R : closed position set with window + run-length counters.
// Side state (u64): bits 0..k-1 = window (bit 0 = nearest cell); bits 40..47 = run1 (length of the near-end run of
// equal cells, lasso counter exact <= E1 then cycling mod M1; 255 = infinite (blank side only)); bits 48..55 = run2
// (length of the near-end alternating suffix, lasso exact <= E2 then mod M2).
// fold(s, c): window <<= 1 | c; run1 = c == last ? succ1(run1) : 1; run2 = c != last ? succ2(run2) : 1.
// env: TC_CAP, TC_DUMP, TC_PATH, TC_PATHN
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64;
struct Tr { int w, d, q; bool ok; };
static int K[2], E1[2], M1[2], E2[2], M2[2];
static Tr TM[16][2];
static inline int succ(int x, int E, int M) { if (x == 255) return 255; return x < E + M ? x + 1 : E + 1; }
static inline u64 fold(int sd, u64 s, int c) {
  u64 wm = (1ULL << K[sd]) - 1; int last = s & 1;
  int r1 = (s >> 40) & 255, r2 = (s >> 48) & 255;
  int n1 = c == last ? succ(r1, E1[sd], M1[sd]) : 1;
  int n2 = c != last ? succ(r2, E2[sd], M2[sd]) : 1;
  u64 w = ((s << 1) | c) & wm;
  return w | ((u64)n1 << 40) | ((u64)n2 << 48);
}
static string showS(int sd, u64 s) {
  string o; for (int i = 0; i < K[sd]; i++) o += char('0' + ((s >> i) & 1));
  char b[32]; snprintf(b, 32, " r1=%d r2=%d", (int)((s >> 40) & 255), (int)((s >> 48) & 255)); return o + b;
}
struct HS { vector<u64> t; size_t n = 0, mask; HS() { t.assign(1 << 20, ~0ULL); mask = t.size() - 1; }
  static u64 h(u64 x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; x ^= x >> 33; return x; }
  bool ins(u64 k) { if ((n + 1) * 2 > t.size()) grow(); size_t i = h(k) & mask; while (t[i] != ~0ULL) { if (t[i] == k) return false; i = (i + 1) & mask; } t[i] = k; n++; return true; }
  void grow() { vector<u64> o; o.swap(t); t.assign(o.size() * 2, ~0ULL); mask = t.size() - 1; for (auto k : o) if (k != ~0ULL) { size_t i = h(k) & mask; while (t[i] != ~0ULL) i = (i + 1) & mask; t[i] = k; } } };
unordered_map<u64, uint32_t> sidx[2]; vector<u64> sval[2]; vector<char> inS[2]; vector<vector<uint32_t>> waitv[2]; vector<vector<pair<int, uint32_t>>> preds[2];
HS seen; vector<u64> all; vector<uint32_t> par; bool track;
static uint32_t aid(int sd, u64 s) { auto it = sidx[sd].find(s); if (it != sidx[sd].end()) return it->second; uint32_t i = sval[sd].size(); sidx[sd].emplace(s, i); sval[sd].push_back(s); inS[sd].push_back(0); waitv[sd].emplace_back(); preds[sd].emplace_back(); return i; }
static inline u64 key(int q, int m, uint32_t a, uint32_t b) { return ((u64)q << 61) | ((u64)m << 60) | ((u64)a << 30) | b; }
static void addc(u64 k, uint32_t from) { if (seen.ins(k)) { all.push_back(k); if (track) par.push_back(from); } }
vector<pair<int, uint32_t>> lq;
static void learn(int sd, uint32_t i) { if (inS[sd][i]) return; inS[sd][i] = 1; lq.push_back({sd, i}); }
static void expand(uint32_t idx, int onlyC, int onlyS) {
  u64 k = all[idx]; int q = k >> 61, m = (k >> 60) & 1; uint32_t a = (k >> 30) & ((1u << 30) - 1), b = k & ((1u << 30) - 1);
  Tr t = TM[q][m]; if (!t.ok) return;
  int ah = t.d == 1 ? 1 : 0;
  uint32_t ia = ah == 1 ? b : a, ib = ah == 1 ? a : b;
  learn(1 - ah, ib);
  uint32_t nb = aid(1 - ah, fold(1 - ah, sval[1 - ah][ib], t.w));
  vector<pair<int, uint32_t>> pl;
  if (onlyS >= 0) pl.push_back({onlyC, (uint32_t)onlyS}); else { waitv[ah][ia].push_back(idx); pl = preds[ah][ia]; }
  for (auto& pr : pl) { int x = pr.first & 1; addc(ah == 1 ? key(t.q, x, nb, pr.second) : key(t.q, x, pr.second, nb), idx); }
}
static void drain() {
  while (!lq.empty()) { auto [sd, i] = lq.back(); lq.pop_back();
    for (int c = 0; c < 2; c++) {
      u64 f = fold(sd, sval[sd][i], c); uint32_t fi = aid(sd, f); preds[sd][fi].push_back({c, i});
      for (size_t wi = 0; wi < waitv[sd][fi].size(); wi++) expand(waitv[sd][fi][wi], c, i); } }
}
int main(int argc, char** argv) {
  if (argc < 12) { printf("usage\n"); return 9; }
  string ms = argv[1];
  for (int s = 0; s < 2; s++) { K[s] = atoi(argv[2 + 5 * s]); E1[s] = atoi(argv[3 + 5 * s]); M1[s] = atoi(argv[4 + 5 * s]); E2[s] = atoi(argv[5 + 5 * s]); M2[s] = atoi(argv[6 + 5 * s]);
    if (K[s] < 1 || K[s] > 39 || E1[s] + M1[s] > 250 || E2[s] + M2[s] > 250 || M1[s] < 1 || M2[s] < 1) { printf("bad params\n"); return 9; } }
  size_t cap = getenv("TC_CAP") ? atoll(getenv("TC_CAP")) : 100000000ULL;
  track = getenv("TC_PATH") != nullptr;
  int NS = 0;
  { stringstream ss(ms); string r; while (getline(ss, r, '_')) { for (int c = 0; c < 2; c++) { string t = r.substr(3 * c, 3); if (t[0] == '-') TM[NS][c] = {0, 0, 0, false}; else TM[NS][c] = {t[0] - '0', t[1] == 'R' ? 1 : -1, t[2] - 'A', true}; } NS++; } }
  u64 z = ((u64)255 << 40) | ((u64)1 << 48);
  uint32_t z0 = aid(0, z), z1 = aid(1, z);
  learn(0, z0); learn(1, z1); drain();
  addc(key(0, 0, z0, z1), ~0u);
  for (size_t idx = 0; idx < all.size(); idx++) {
    if (all.size() > cap) { printf("CAP: more than %zu configs\n", cap); return 2; }
    u64 k = all[idx]; int q = k >> 61, m = (k >> 60) & 1; uint32_t a = (k >> 30) & ((1u << 30) - 1), b = k & ((1u << 30) - 1);
    if (!TM[q][m].ok) {
      printf("FAIL: halting config %c%d after %zu configs\n  L: %s\n  R: %s\n", 'A' + q, m, all.size(), showS(0, sval[0][a]).c_str(), showS(1, sval[1][b]).c_str());
      if (track) { size_t j = idx; vector<size_t> pth; while (j != (size_t)~0u && pth.size() < 1000000) { pth.push_back(j); j = par[j]; } printf("path length %zu\n", pth.size());
        int lim = getenv("TC_PATHN") ? atoi(getenv("TC_PATHN")) : 60;
        for (int uu = 0; uu < (int)pth.size() && uu < lim; uu++) { u64 kk = all[pth[uu]]; int qq = kk >> 61, mm = (kk >> 60) & 1; uint32_t aa = (kk >> 30) & ((1u << 30) - 1), bb = kk & ((1u << 30) - 1);
          string ls = showS(0, sval[0][aa]); string lw = ls.substr(0, K[0]); reverse(lw.begin(), lw.end());
          printf("  %s%s [%c%d] %s\n", lw.c_str(), ls.substr(K[0]).c_str(), 'A' + qq, mm, showS(1, sval[1][bb]).c_str()); } }
      return 1;
    }
    expand(idx, -1, -1); drain();
  }
  size_t nl = 0, nr = 0; for (auto c : inS[0]) nl += c; for (auto c : inS[1]) nr += c;
  printf("NONHALT: %zu configs, |S_L|=%zu |S_R|=%zu\n", all.size(), nl, nr);
  if (getenv("TC_DUMP")) {
    FILE* f = fopen(getenv("TC_DUMP"), "w");
    fprintf(f, "P"); for (int s = 0; s < 2; s++) fprintf(f, " %d %d %d %d %d", K[s], E1[s], M1[s], E2[s], M2[s]); fprintf(f, "\n");
    for (int s = 0; s < 2; s++) for (size_t i = 0; i < inS[s].size(); i++) if (inS[s][i]) fprintf(f, "S %d %llu\n", s, sval[s][i]);
    if (!getenv("TC_NOC")) for (auto k : all) { int q = k >> 61, m = (k >> 60) & 1; uint32_t a = (k >> 30) & ((1u << 30) - 1), b = k & ((1u << 30) - 1); fprintf(f, "C %d %d %llu %llu\n", q, m, sval[0][a], sval[1][b]); }
    fclose(f);
  }
  return 0;
}
