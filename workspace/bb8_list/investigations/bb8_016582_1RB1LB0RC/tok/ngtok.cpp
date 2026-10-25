// ngtok MACHINE HL KAL KBL KCL HR KAR KBR KCR : closed position set over run-length TOKEN side automata.
// A side (nearest cell first) is folded from its far end: cells form tokens 1^a 0^b (push order: ones then zeros);
// equal consecutive tokens merge into (a,b)^cnt.  a, b, cnt are exact up to KA/KB/KC, else "big" (= K+1).
// The state keeps the nearest H closed tokens (farther ones are dropped) and the open partial token.
// Encoding (u64): bits 0..2 ntok, 3..5 pa, 6..10 pb, 11 hasP, then token i (i=0 nearest) at 12+13i: a(3) b(5) c(5).
// Learned predecessor lists as in ngann (generic soundness lemma nonhalt_of_check).
// env: TC_CAP, TC_DUMP, TC_PATH, TC_PATHN
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64;
struct Tr { int w, d, q; bool ok; };
static int H[2], KA[2], KB[2], KC[2];
static Tr TM[16][2];
static int MB = 1;
static inline u64 inc(u64 v, int K) { if (v <= (u64)K) return v + 1; return K + 1 + ((v - K) % MB); }  // big mod MB
static inline u64 tok(u64 s, int i) { return (s >> (12 + 13 * i)) & 0x1fff; }
static u64 fold(int sd, u64 s, int c) {
  int n = s & 7; u64 pa = (s >> 3) & 7, pb = (s >> 6) & 31, hp = (s >> 11) & 1;
  u64 toks[8]; for (int i = 0; i < n; i++) toks[i] = tok(s, i);
  if (!hp) { if (c == 0) return s; hp = 1; pa = 1; pb = 0; }
  else if (c == 0) { pb = pb == 0 ? 1 : inc(pb, KB[sd]); }
  else if (pb == 0) { pa = inc(pa, KA[sd]); }
  else {
    // close (pa,pb)
    if (n > 0 && (toks[0] & 0xff) == (pa | (pb << 3))) { u64 cnt = toks[0] >> 8; cnt = inc(cnt, KC[sd]); toks[0] = (toks[0] & 0xff) | (cnt << 8); }
    else { for (int i = min(n, H[sd] - 1); i > 0; i--) toks[i] = toks[i - 1]; toks[0] = pa | (pb << 3) | (1ULL << 8); n = min(n + 1, H[sd]); }
    pa = 1; pb = 0;
  }
  u64 r = (u64)n | (pa << 3) | (pb << 6) | (hp << 11);
  for (int i = 0; i < n; i++) r |= toks[i] << (12 + 13 * i);
  return r;
}
static string vs(u64 v, int K) { return v <= (u64)K ? to_string(v) : string("*"); }
static string showS(int sd, u64 s) {
  int n = s & 7; u64 pa = (s >> 3) & 7, pb = (s >> 6) & 31, hp = (s >> 11) & 1; string o;
  if (hp) o += "<" + vs(pa, KA[sd]) + "," + vs(pb, KB[sd]) + "> ";
  for (int i = 0; i < n; i++) { u64 t = tok(s, i); o += "(" + vs(t & 7, KA[sd]) + "," + vs((t >> 3) & 31, KB[sd]) + ")^" + vs(t >> 8, KC[sd]) + " "; }
  return o.empty() ? "_" : o;
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
  string ms = argv[1];
  for (int s = 0; s < 2; s++) { H[s] = atoi(argv[2 + 4 * s]); KA[s] = atoi(argv[3 + 4 * s]); KB[s] = atoi(argv[4 + 4 * s]); KC[s] = atoi(argv[5 + 4 * s]);
    if (H[s] > 4 || KA[s] > 6 || KB[s] > 30 || KC[s] > 30) { printf("params too large\n"); return 9; } }
  if (getenv("TC_MB")) MB = atoi(getenv("TC_MB"));
  size_t cap = getenv("TC_CAP") ? atoll(getenv("TC_CAP")) : 100000000ULL;
  track = getenv("TC_PATH") != nullptr;
  int NS = 0;
  { stringstream ss(ms); string r; while (getline(ss, r, '_')) { for (int c = 0; c < 2; c++) { string t = r.substr(3 * c, 3); if (t[0] == '-') TM[NS][c] = {0, 0, 0, false}; else TM[NS][c] = {t[0] - '0', t[1] == 'R' ? 1 : -1, t[2] - 'A', true}; } NS++; } }
  uint32_t z0 = aid(0, 0), z1 = aid(1, 0);
  learn(0, z0); learn(1, z1); drain();
  if (getenv("TC_START")) {  // "Q LEFT M RIGHT": LEFT written left-to-right (far..near), RIGHT left-to-right (near..far)
    char qc; char lw[4096], rw[4096]; int mb; sscanf(getenv("TC_START"), " %c %4095s %d %4095s", &qc, lw, &mb, rw);
    string L = lw, R = rw; if (L == "-") L = ""; if (R == "-") R = "";
    uint32_t a = z0; for (char ch : L) { learn(0, a); drain(); a = aid(0, fold(0, sval[0][a], ch - '0')); }
    uint32_t b = z1; for (int i = (int)R.size() - 1; i >= 0; i--) { learn(1, b); drain(); b = aid(1, fold(1, sval[1][b], R[i] - '0')); }
    addc(key(qc - 'A', mb, a, b), ~0u);
    printf("start %c L=%s m=%d R=%s\n", qc, showS(0, sval[0][a]).c_str(), mb, showS(1, sval[1][b]).c_str());
  } else addc(key(0, 0, z0, z1), ~0u);
  for (size_t idx = 0; idx < all.size(); idx++) {
    if (all.size() > cap) { printf("CAP: more than %zu configs\n", cap); return 2; }
    u64 k = all[idx]; int q = k >> 61, m = (k >> 60) & 1; uint32_t a = (k >> 30) & ((1u << 30) - 1), b = k & ((1u << 30) - 1);
    if (!TM[q][m].ok) {
      printf("FAIL: halting config %c%d after %zu configs\n  L: %s\n  R: %s\n", 'A' + q, m, all.size(), showS(0, sval[0][a]).c_str(), showS(1, sval[1][b]).c_str());
      if (track) { size_t j = idx; vector<size_t> pth; while (j != (size_t)~0u && pth.size() < 1000000) { pth.push_back(j); j = par[j]; } printf("path length %zu\n", pth.size());
        int lim = getenv("TC_PATHN") ? atoi(getenv("TC_PATHN")) : 60;
        for (int uu = 0; uu < (int)pth.size() && uu < lim; uu++) { u64 kk = all[pth[uu]]; int qq = kk >> 61, mm = (kk >> 60) & 1; uint32_t aa = (kk >> 30) & ((1u << 30) - 1), bb = kk & ((1u << 30) - 1);
          printf("  %c%d | L %s | R %s\n", 'A' + qq, mm, showS(0, sval[0][aa]).c_str(), showS(1, sval[1][bb]).c_str()); } }
      return 1;
    }
    expand(idx, -1, -1); drain();
  }
  size_t nl = 0, nr = 0; for (auto c : inS[0]) nl += c; for (auto c : inS[1]) nr += c;
  printf("NONHALT: %zu configs, |S_L|=%zu |S_R|=%zu\n", all.size(), nl, nr);
  if (getenv("TC_DUMP")) {
    FILE* f = fopen(getenv("TC_DUMP"), "w");
    fprintf(f, "P"); for (int s = 0; s < 2; s++) fprintf(f, " %d %d %d %d", H[s], KA[s], KB[s], KC[s]); fprintf(f, "\n");
    for (int s = 0; s < 2; s++) for (size_t i = 0; i < inS[s].size(); i++) if (inS[s][i]) fprintf(f, "S %d %llu\n", s, sval[s][i]);
    fprintf(f, "N %zu\n", all.size());
    fclose(f);
  }
  return 0;
}
