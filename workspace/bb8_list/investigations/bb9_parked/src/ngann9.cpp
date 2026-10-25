// ngann9 (bb9_parked copy of bb8_m7_1RB0RA_1RG0LC/opus/ngann.cpp widened to <= 9 states: 4-bit state in the config key,
// 29-bit side ids, 9-bit g set).  ngann MACHINE kL kR ANN GON : n-gram closed position set over annotated cells, with learned predecessor lists.
// A cell is (bit, ann): ANN=0 no annotation; ANN=1 ann = direction of the write (0 blank, 1 L, 2 R);
// ANN=2 ann = state that wrote it (0 blank, 1+q); ANN=3 ann = (state, direction).
// A side state is the window of its first k annotated cells (+ for the right side, if GON, g = set of states whose
// right-moving run from the first cell halts). fold(s, c) pushes cell c; learned set S; unfold = learned predecessors.
// env: TC_CAP, TC_NOFAIL, TC_DUMP, TC_PATH, TC_PATHN
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64;
struct Tr { int w, d, q; bool ok; };
static int K[2], CW, ANN, GON;
static unsigned short GT[512][2]; static int NSG = 8;
static Tr TM[16][2];
static inline u64 wmask(int sd) { return K[sd] * CW >= 64 ? ~0ULL : ((1ULL << (K[sd] * CW)) - 1); }
static inline int gof(u64 s) { return (s >> 55) & 511; }
static inline u64 fold(int sd, u64 s, int c) {
  u64 w = (((s & wmask(sd)) << CW) | c) & wmask(sd);
  if (GON && sd == 1) w |= (u64)GT[gof(s)][c & 1] << 55;
  return w;
}
static inline int annof(int q, int d, int w) {
  int a = 0;
  if (ANN == 1) a = d == 1 ? 2 : 1;
  else if (ANN == 2) a = 1 + q;
  else if (ANN == 3) a = 1 + q * 2 + (d == 1);
  return w | (a << 1);
}
static string showS(int sd, u64 s) {
  string o; if (GON && sd == 1) { char b[16]; snprintf(b, 16, "g%02x ", gof(s)); o += b; }
  for (int i = 0; i < K[sd]; i++) { int c = (s >> (i * CW)) & ((1 << CW) - 1); o += char('0' + (c & 1)); if (ANN) { int a = c >> 1; o += a ? char('a' + a - 1) : '_'; } }
  return o;
}
struct HS { vector<u64> t; size_t n = 0, mask; HS() { t.assign(1 << 20, ~0ULL); mask = t.size() - 1; }
  static u64 h(u64 x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; x ^= x >> 33; return x; }
  bool ins(u64 k) { if ((n + 1) * 2 > t.size()) grow(); size_t i = h(k) & mask; while (t[i] != ~0ULL) { if (t[i] == k) return false; i = (i + 1) & mask; } t[i] = k; n++; return true; }
  void grow() { vector<u64> o; o.swap(t); t.assign(o.size() * 2, ~0ULL); mask = t.size() - 1; for (auto k : o) if (k != ~0ULL) { size_t i = h(k) & mask; while (t[i] != ~0ULL) i = (i + 1) & mask; t[i] = k; } } };
unordered_map<u64, uint32_t> sidx[2]; vector<u64> sval[2]; vector<char> inS[2]; vector<vector<uint32_t>> waitv[2]; vector<vector<pair<int, uint32_t>>> preds[2];
HS seen; vector<u64> all; vector<uint32_t> par; bool track;
static uint32_t aid(int sd, u64 s) { if (sval[sd].size() >= (1u << 29) - 1) { printf("SIDE OVERFLOW\n"); exit(3); } auto it = sidx[sd].find(s); if (it != sidx[sd].end()) return it->second; uint32_t i = sval[sd].size(); sidx[sd].emplace(s, i); sval[sd].push_back(s); inS[sd].push_back(0); waitv[sd].emplace_back(); preds[sd].emplace_back(); return i; }
static inline u64 key(int q, int m, uint32_t a, uint32_t b) { return ((u64)q << 59) | ((u64)m << 58) | ((u64)a << 29) | b; }
static void addc(u64 k, uint32_t from) { if (seen.ins(k)) { all.push_back(k); if (track) par.push_back(from); } }
vector<pair<int, uint32_t>> lq;
static void learn(int sd, uint32_t i) { if (inS[sd][i]) return; inS[sd][i] = 1; lq.push_back({sd, i}); }
static void expand(uint32_t idx, int onlyC, int onlyS) {
  u64 k = all[idx]; int q = k >> 59, m = (k >> 58) & 1; uint32_t a = (k >> 29) & ((1u << 29) - 1), b = k & ((1u << 29) - 1);
  Tr t = TM[q][m]; if (!t.ok) return;
  int ah = t.d == 1 ? 1 : 0;
  uint32_t ia = ah == 1 ? b : a, ib = ah == 1 ? a : b;
  learn(1 - ah, ib);
  uint32_t nb = aid(1 - ah, fold(1 - ah, sval[1 - ah][ib], annof(q, t.d, t.w)));
  vector<pair<int, uint32_t>> pl;
  if (onlyS >= 0) pl.push_back({onlyC, (uint32_t)onlyS}); else { waitv[ah][ia].push_back(idx); pl = preds[ah][ia]; }
  for (auto& pr : pl) { int x = pr.first & 1; addc(ah == 1 ? key(t.q, x, nb, pr.second) : key(t.q, x, pr.second, nb), idx); }
}
static void drain() {
  while (!lq.empty()) { auto [sd, i] = lq.back(); lq.pop_back();
    for (int c = 0; c < (1 << CW); c++) { if (!ANN && c > 1) break;
      u64 f = fold(sd, sval[sd][i], c); uint32_t fi = aid(sd, f); preds[sd][fi].push_back({c, i});
      for (size_t wi = 0; wi < waitv[sd][fi].size(); wi++) expand(waitv[sd][fi][wi], c, i); } }
}
int main(int argc, char** argv) {
  string ms = argv[1]; K[0] = atoi(argv[2]); K[1] = atoi(argv[3]); ANN = atoi(argv[4]); GON = atoi(argv[5]);
  CW = ANN == 0 ? 1 : ANN == 1 ? 3 : ANN == 2 ? 5 : 6;
  for (int s = 0; s < 2; s++) if (K[s] * CW > 54) { printf("window too wide\n"); return 9; }
  size_t cap = getenv("TC_CAP") ? atoll(getenv("TC_CAP")) : 200000000ULL;
  bool nofail = getenv("TC_NOFAIL") != nullptr; track = getenv("TC_PATH") != nullptr;
  int NS = 0;
  { stringstream ss(ms); string r; while (getline(ss, r, '_')) { for (int c = 0; c < 2; c++) { string t = r.substr(3 * c, 3); if (t[0] == '-') TM[NS][c] = {0, 0, 0, false}; else TM[NS][c] = {t[0] - '0', t[1] == 'R' ? 1 : -1, t[2] - 'A', true}; } NS++; } }
  if (NS > 9) { printf("too many states\n"); return 9; }
  for (int g = 0; g < 512; g++) for (int x = 0; x < 2; x++) { int r = 0; for (int X = 0; X < NS; X++) { Tr t = TM[X][x]; if (!t.ok || (t.d == 1 && ((g >> t.q) & 1))) r |= 1 << X; } GT[g][x] = r; }
  u64 zR = 0, zL = 0;
  if (GON) { int g = 0; for (int it = 0; it < 64; it++) g = GT[g][0]; zR |= (u64)g << 55; }
  uint32_t z0 = aid(0, zL), z1 = aid(1, zR);
  learn(0, z0); learn(1, z1); drain();
  addc(key(0, 0, z0, z1), ~0u);
  size_t nhalt = 0;
  for (size_t idx = 0; idx < all.size(); idx++) {
    if ((idx & ((1 << 23) - 1)) == 0 && idx) fprintf(stderr, "idx %zu / %zu S=%zu/%zu\n", idx, all.size(), sval[0].size(), sval[1].size());
    if (all.size() > cap) { printf("CAP kL=%d kR=%d ann=%d g=%d: more than %zu configs\n", K[0], K[1], ANN, GON, cap); return 2; }
    u64 k = all[idx]; int q = k >> 59, m = (k >> 58) & 1; uint32_t a = (k >> 29) & ((1u << 29) - 1), b = k & ((1u << 29) - 1);
    if (!TM[q][m].ok) {
      nhalt++;
      if (!nofail) {
        printf("FAIL kL=%d kR=%d ann=%d g=%d: halting config %c%d after %zu configs\n  L: %s\n  R: %s\n", K[0], K[1], ANN, GON, 'A' + q, m, all.size(), showS(0, sval[0][a]).c_str(), showS(1, sval[1][b]).c_str());
        if (track) { size_t j = idx; vector<size_t> pth; while (j != (size_t)~0u && pth.size() < 1000000) { pth.push_back(j); j = par[j]; } printf("path length %zu\n", pth.size());
          int lim = getenv("TC_PATHN") ? atoi(getenv("TC_PATHN")) : 60;
          for (int uu = 0; uu < (int)pth.size() && uu < lim; uu++) { u64 kk = all[pth[uu]]; int qq = kk >> 59, mm = (kk >> 58) & 1; uint32_t aa = (kk >> 29) & ((1u << 29) - 1), bb = kk & ((1u << 29) - 1);
            printf("  %c%d | L %s | R %s\n", 'A' + qq, mm, showS(0, sval[0][aa]).c_str(), showS(1, sval[1][bb]).c_str()); } }
        return 1;
      }
      continue;
    }
    expand(idx, -1, -1); drain();
  }
  size_t nl = 0, nr = 0; for (auto c : inS[0]) nl += c; for (auto c : inS[1]) nr += c;
  printf("%s kL=%d kR=%d ann=%d g=%d: %zu configs, |S_L|=%zu |S_R|=%zu, halting %zu\n", nhalt ? "SINK" : "NONHALT", K[0], K[1], ANN, GON, all.size(), nl, nr, nhalt);
  if (getenv("TC_DUMP")) {
    FILE* f = fopen(getenv("TC_DUMP"), "w");
    fprintf(f, "P %d %d %d %d\n", K[0], K[1], ANN, GON);
    for (int s = 0; s < 2; s++) for (size_t i = 0; i < inS[s].size(); i++) if (inS[s][i]) fprintf(f, "S %d %llu\n", s, sval[s][i]);
    if (!getenv("TC_NOC")) for (auto k : all) { int q = k >> 59, m = (k >> 58) & 1; uint32_t a = (k >> 29) & ((1u << 29) - 1), b = k & ((1u << 29) - 1); fprintf(f, "C %d %d %llu %llu\n", q, m, sval[0][a], sval[1][b]); }
    fclose(f);
  }
  return 0;
}
