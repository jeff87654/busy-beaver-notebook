// tcps2 MACHINE kL kR ML MR UL UR [policy] : closed position set with exact tail memory and exact near stacks.
// A side (half-tape, nearest cell first) is abstracted by (u, s):
//   u : exact list of the nearest |u| cells (|u| <= U);
//   s : automaton state for the rest:  Exact(w) (rest = w 0^inf, |w| <= M, w empty or ending in 1)
//                                       Far(t, h) (rest longer than M; t = its last M cells, h = its first k cells).
// fold(s, x) pushes x onto the near end of the rest (deterministic). Learned set S per side:
//   rest has state s iff there is a run f, f 0 = s, f(i+1) in S, fold(f(i+1), rest_i) = f(i).
// Moves: the side ahead of the head pops u, or unfolds s when u is empty (all learned candidates);
//        the side behind receives the written cell: pushed onto u when (policy) else folded into s.
// policy bit 1: push onto u when the other side's s is Exact (near mode) or u is non-empty (keep);
// policy bit 2: when not pushing and u is non-empty, flush u into s first (else keep pushing).
// env: TC_CAP, TC_NOFAIL, TC_DUMP=file, TC_PATH (parents + path print), TC_PATHN
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64;
struct Tr { int w, d, q; bool ok; };
static int K[2], M[2], U[2], POL;
static const u64 FAR = 1ULL << 63;
static inline u64 kmask(int s) { return (1ULL << K[s]) - 1; }
static inline u64 mkExact(int len, u64 w) { return ((u64)len << 56) | w; }
static inline bool isExact(u64 s) { return !(s & FAR); }
static inline u64 fold(int sd, u64 s, int x) {
  if (s & FAR) { u64 t = (s >> K[sd]) & ((1ULL << M[sd]) - 1); u64 h = s & kmask(sd); h = ((h << 1) | x) & kmask(sd); return FAR | (t << K[sd]) | h; }
  int len = (s >> 56) & 127; u64 w = s & ((1ULL << 56) - 1);
  if (len == 0 && x == 0) return s;
  u64 w2 = (w << 1) | x; int l2 = len + 1;
  if (l2 <= M[sd]) return mkExact(l2, w2);
  return FAR | (w << K[sd]) | (w2 & kmask(sd));
}
static inline int cands(int sd, u64 s, int* xs, u64* ss) {
  if (s & FAR) {
    u64 t = (s >> K[sd]) & ((1ULL << M[sd]) - 1); u64 h = s & kmask(sd); int x = h & 1; u64 h2 = h >> 1; int n = 0;
    for (int y = 0; y < 2; y++) { xs[n] = x; ss[n] = FAR | (t << K[sd]) | h2 | ((u64)y << (K[sd] - 1)); n++; }
    if ((t & ((1ULL << (K[sd] - 1)) - 1)) == h2) { xs[n] = x; ss[n] = mkExact(M[sd], t); n++; }
    return n;
  }
  int len = (s >> 56) & 127; u64 w = s & ((1ULL << 56) - 1);
  if (len == 0) { xs[0] = 0; ss[0] = s; return 1; }
  xs[0] = w & 1; ss[0] = mkExact(len - 1, w >> 1); return 1;
}
static inline int ulen(u64 u) { return (u >> 56) & 127; }
static inline u64 ubits(u64 u) { return u & ((1ULL << 56) - 1); }
static string showS(int sd, u64 s) {
  string o;
  if (s & FAR) { u64 t = (s >> K[sd]) & ((1ULL << M[sd]) - 1); u64 h = s & kmask(sd);
    for (int i = 0; i < K[sd]; i++) o += char('0' + ((h >> i) & 1)); o += " ..? "; for (int i = 0; i < M[sd]; i++) o += char('0' + ((t >> i) & 1)); o += " 0^inf"; return o; }
  int len = (s >> 56) & 127; for (int i = 0; i < len; i++) o += char('0' + ((s >> i) & 1)); o += " 0^inf"; return o;
}
static string showSide(int sd, pair<u64, u64> p) { string o = "["; for (int i = 0; i < ulen(p.first); i++) o += char('0' + ((p.first >> i) & 1)); o += "] "; return o + showS(sd, p.second); }
struct PH { size_t operator()(const pair<u64, u64>& p) const { return p.first * 0x9E3779B97F4A7C15ULL ^ (p.second + 0x632BE59BD9B4E019ULL + (p.first << 6)); } };
struct SideMap { unordered_map<pair<u64, u64>, uint32_t, PH> m; vector<pair<u64, u64>> v;
  uint32_t id(pair<u64, u64> s) { auto it = m.find(s); if (it != m.end()) return it->second; uint32_t i = v.size(); m.emplace(s, i); v.push_back(s); return i; } };
struct HS { vector<u64> t; size_t n = 0, mask; HS() { t.assign(1 << 20, ~0ULL); mask = t.size() - 1; }
  static u64 h(u64 x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; x ^= x >> 33; return x; }
  bool ins(u64 k) { if ((n + 1) * 2 > t.size()) grow(); size_t i = h(k) & mask; while (t[i] != ~0ULL) { if (t[i] == k) return false; i = (i + 1) & mask; } t[i] = k; n++; return true; }
  void grow() { vector<u64> o; o.swap(t); t.assign(o.size() * 2, ~0ULL); mask = t.size() - 1; for (auto k : o) if (k != ~0ULL) { size_t i = h(k) & mask; while (t[i] != ~0ULL) i = (i + 1) & mask; t[i] = k; } } };

Tr TM[16][2];
SideMap sides[2];
unordered_map<u64, uint32_t> sidx[2];  // automaton state -> index for S membership and waiters
vector<u64> sval[2]; vector<char> inS[2]; vector<vector<uint32_t>> waitv[2];
HS seen; vector<u64> all; vector<uint32_t> par; bool track;
static uint32_t aid(int sd, u64 s) { auto it = sidx[sd].find(s); if (it != sidx[sd].end()) return it->second; uint32_t i = sval[sd].size(); sidx[sd].emplace(s, i); sval[sd].push_back(s); inS[sd].push_back(0); waitv[sd].emplace_back(); return i; }
static inline u64 key(int q, int m, uint32_t a, uint32_t b) { return ((u64)q << 61) | ((u64)m << 60) | ((u64)a << 30) | b; }
static void addc(u64 k, uint32_t from) { if (seen.ins(k)) { all.push_back(k); if (track) par.push_back(from); } }
static void learn(int sd, u64 s);
// the side behind the head receives cell x; 'near' = the other side's s is Exact after the move
static pair<u64, u64> give(int sd, pair<u64, u64> p, int x, bool nearOther) {
  u64 u = p.first, s = p.second; int ul = ulen(u);
  bool push = U[sd] > 0 && (POL & 1) && (nearOther || ul > 0);
  if (!push && ul > 0 && !(POL & 2)) push = U[sd] > 0;  // keep pushing while u is non-empty
  if (push) {
    u64 b = (ubits(u) << 1) | x; int l = ul + 1;
    if (l > U[sd]) { int y = (b >> (l - 1)) & 1; learn(sd, s); s = fold(sd, s, y); b &= (1ULL << (l - 1)) - 1; l--; }
    return {((u64)l << 56) | b, s};
  }
  // flush u (far end first), then fold x
  for (int i = ul - 1; i >= 0; i--) { learn(sd, s); s = fold(sd, s, (ubits(u) >> i) & 1); }
  learn(sd, s); s = fold(sd, s, x);
  return {0, s};
}
// successors of config idx; if onlyS != ~0 restrict to the unfold candidate with automaton state onlyS (side 'osd')
static void expand(uint32_t idx, int osd, u64 onlyS) {
  u64 k = all[idx]; int q = k >> 61, m = (k >> 60) & 1; uint32_t a = (k >> 30) & ((1u << 30) - 1), b = k & ((1u << 30) - 1);
  Tr t = TM[q][m]; if (!t.ok) return;
  int ah = t.d == 1 ? 1 : 0;  // side ahead
  pair<u64, u64> pa = sides[ah].v[ah == 1 ? b : a], pb = sides[1 - ah].v[ah == 1 ? a : b];
  vector<pair<int, pair<u64, u64>>> outs;  // (scanned symbol, new ahead side)
  if (ulen(pa.first) > 0) {
    if (onlyS != ~0ULL) return;
    int x = pa.first & 1; u64 u2 = (((u64)(ulen(pa.first) - 1)) << 56) | (ubits(pa.first) >> 1);
    outs.push_back({x, {u2, pa.second}});
  } else {
    uint32_t si = aid(ah, pa.second);
    if (onlyS == ~0ULL) waitv[ah][si].push_back(idx);
    int xs[3]; u64 ss[3]; int n = cands(ah, pa.second, xs, ss);
    for (int c = 0; c < n; c++) {
      if (onlyS != ~0ULL && (osd != ah || ss[c] != onlyS)) continue;
      auto it = sidx[ah].find(ss[c]); if (it == sidx[ah].end() || !inS[ah][it->second]) continue;
      outs.push_back({xs[c], {0, ss[c]}});
    }
  }
  for (auto& o : outs) {
    bool nearOther = isExact(o.second.second);
    pair<u64, u64> nb = give(1 - ah, pb, t.w, nearOther);
    uint32_t ia = sides[ah].id(o.second), ib = sides[1 - ah].id(nb);
    addc(ah == 1 ? key(t.q, o.first, ib, ia) : key(t.q, o.first, ia, ib), idx);
  }
}
vector<pair<int, u64>> lq;  // learned states whose waiters are not yet notified
static void learn(int sd, u64 s) { uint32_t i = aid(sd, s); if (inS[sd][i]) return; inS[sd][i] = 1; lq.push_back({sd, s}); }
static void drain() {
  while (!lq.empty()) { auto [sd, s] = lq.back(); lq.pop_back();
    for (int x = 0; x < 2; x++) { u64 f = fold(sd, s, x); uint32_t fi = aid(sd, f);
      for (size_t wi = 0; wi < waitv[sd][fi].size(); wi++) expand(waitv[sd][fi][wi], sd, s); } }
}
int main(int argc, char** argv) {
  string ms = argv[1]; K[0] = atoi(argv[2]); K[1] = atoi(argv[3]); M[0] = atoi(argv[4]); M[1] = atoi(argv[5]); U[0] = atoi(argv[6]); U[1] = atoi(argv[7]);
  POL = argc > 8 ? atoi(argv[8]) : 1;
  for (int s = 0; s < 2; s++) if (M[s] < K[s] || M[s] + K[s] > 62 || M[s] > 55 || K[s] < 1 || U[s] > 55) { printf("bad params\n"); return 9; }
  size_t cap = getenv("TC_CAP") ? atoll(getenv("TC_CAP")) : 200000000ULL;
  bool nofail = getenv("TC_NOFAIL") != nullptr; track = getenv("TC_PATH") != nullptr;
  int NS = 0;
  { stringstream ss(ms); string r; while (getline(ss, r, '_')) { for (int c = 0; c < 2; c++) { string t = r.substr(3 * c, 3); if (t[0] == '-') TM[NS][c] = {0, 0, 0, false}; else TM[NS][c] = {t[0] - '0', t[1] == 'R' ? 1 : -1, t[2] - 'A', true}; } NS++; } }
  learn(0, mkExact(0, 0)); learn(1, mkExact(0, 0)); lq.clear();
  uint32_t z0 = sides[0].id({0, mkExact(0, 0)}), z1 = sides[1].id({0, mkExact(0, 0)});
  addc(key(0, 0, z0, z1), ~0u);
  size_t nhalt = 0; long long firsthalt = -1;
  for (size_t idx = 0; idx < all.size(); idx++) {
    if ((idx & ((1 << 23) - 1)) == 0 && idx) fprintf(stderr, "idx %zu / %zu  sides=%zu/%zu S=%zu/%zu\n", idx, all.size(), sides[0].v.size(), sides[1].v.size(), sval[0].size(), sval[1].size());
    if (all.size() > cap) { printf("CAP kL=%d kR=%d ML=%d MR=%d UL=%d UR=%d pol=%d: more than %zu configs\n", K[0], K[1], M[0], M[1], U[0], U[1], POL, cap); return 2; }
    u64 k = all[idx]; int q = k >> 61, m = (k >> 60) & 1; uint32_t a = (k >> 30) & ((1u << 30) - 1), b = k & ((1u << 30) - 1);
    if (!TM[q][m].ok) {
      nhalt++; if (firsthalt < 0) firsthalt = idx;
      if (!nofail) {
        printf("FAIL kL=%d kR=%d ML=%d MR=%d UL=%d UR=%d pol=%d: halting config %c%d after %zu configs\n  L: %s\n  R: %s\n", K[0], K[1], M[0], M[1], U[0], U[1], POL, 'A' + q, m, all.size(), showSide(0, sides[0].v[a]).c_str(), showSide(1, sides[1].v[b]).c_str());
        if (track) { size_t j = idx; vector<size_t> pth; while (j != (size_t)~0u && pth.size() < 1000000) { pth.push_back(j); j = par[j]; } printf("path length %zu\n", pth.size());
          int lim = getenv("TC_PATHN") ? atoi(getenv("TC_PATHN")) : 60;
          for (int uu = 0; uu < (int)pth.size() && uu < lim; uu++) { u64 kk = all[pth[uu]]; int qq = kk >> 61, mm = (kk >> 60) & 1; uint32_t aa = (kk >> 30) & ((1u << 30) - 1), bb = kk & ((1u << 30) - 1);
            printf("  %c%d | L %s | R %s\n", 'A' + qq, mm, showSide(0, sides[0].v[aa]).c_str(), showSide(1, sides[1].v[bb]).c_str()); } }
        return 1;
      }
      continue;
    }
    expand(idx, -1, ~0ULL); drain();
  }
  size_t nl = 0, nr = 0; for (auto c : inS[0]) nl += c; for (auto c : inS[1]) nr += c;
  printf("%s kL=%d kR=%d ML=%d MR=%d UL=%d UR=%d pol=%d: %zu configs, sides %zu/%zu, |S_L|=%zu |S_R|=%zu, halting configs %zu (first at %lld)\n", nhalt ? "SINK" : "NONHALT", K[0], K[1], M[0], M[1], U[0], U[1], POL, all.size(), sides[0].v.size(), sides[1].v.size(), nl, nr, nhalt, firsthalt);
  if (getenv("TC_DUMP")) {
    FILE* f = fopen(getenv("TC_DUMP"), "w");
    fprintf(f, "P %d %d %d %d %d %d %d\n", K[0], K[1], M[0], M[1], U[0], U[1], POL);
    for (int s = 0; s < 2; s++) for (size_t i = 0; i < inS[s].size(); i++) if (inS[s][i]) fprintf(f, "S %d %llu\n", s, sval[s][i]);
    if (!getenv("TC_NOC")) for (auto k : all) { int q = k >> 61, m = (k >> 60) & 1; uint32_t a = (k >> 30) & ((1u << 30) - 1), b = k & ((1u << 30) - 1);
      fprintf(f, "C %d %d %llu %llu %llu %llu\n", q, m, sides[0].v[a].first, sides[0].v[a].second, sides[1].v[b].first, sides[1].v[b].second); }
    fclose(f);
  }
  return 0;
}
