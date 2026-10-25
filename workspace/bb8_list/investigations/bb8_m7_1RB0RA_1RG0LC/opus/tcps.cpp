// tcps MACHINE kL kR ML MR : closed position set with exact tail memory.
// A side (left or right half-tape, nearest cell first) is abstracted by a state:
//   Exact(w)  : the whole side is w ++ 0^inf (w empty or ending in 1), |w| <= M;
//   Far(t, h) : the side is longer than M (up to its last 1); t = its last M cells, h = its first k cells.
// fold(s, x) pushes cell x onto the near end (deterministic); a learned set S of states closes the abstraction:
// a side r has state s iff there is a run f with f 0 = s, f(i+1) in S and fold(f(i+1), r_i) = f(i).
// Abstract configuration (q, m, sL, sR). Search learns S_L, S_R and the config set C to a fixpoint.
// env: TC_CAP (config cap), TC_NOFAIL (treat halts as sinks), TC_DUMP=file (certificate), TC_PATH (store parents, print a path to a halt)
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64;
struct Tr { int w, d, q; bool ok; };
static int K[2], M[2];
static const u64 FAR = 1ULL << 63;
static inline u64 kmask(int s) { return (1ULL << K[s]) - 1; }
static inline u64 mkExact(int len, u64 w) { return ((u64)len << 56) | w; }
static inline u64 fold(int sd, u64 s, int x) {
  if (s & FAR) { u64 t = (s >> K[sd]) & ((1ULL << M[sd]) - 1); u64 h = s & kmask(sd); h = ((h << 1) | x) & kmask(sd); return FAR | (t << K[sd]) | h; }
  int len = (s >> 56) & 127; u64 w = s & ((1ULL << 56) - 1);
  if (len == 0 && x == 0) return s;
  u64 w2 = (w << 1) | x; int l2 = len + 1;
  if (l2 <= M[sd]) return mkExact(l2, w2);
  return FAR | (w << K[sd]) | (w2 & kmask(sd));
}
// candidates (x, s') with fold(s', x) == s (before filtering by membership in S)
static inline int cands(int sd, u64 s, int* xs, u64* ss) {
  if (s & FAR) {
    u64 t = (s >> K[sd]) & ((1ULL << M[sd]) - 1); u64 h = s & kmask(sd); int x = h & 1; u64 h2 = h >> 1; int n = 0;
    for (int y = 0; y < 2; y++) { xs[n] = x; ss[n] = FAR | (t << K[sd]) | h2 | ((u64)y << (K[sd] - 1)); n++; }
    if ((t & ((1ULL << (K[sd] - 1)) - 1)) == h2) { xs[n] = x; ss[n] = mkExact(M[sd], t); n++; }
    return n;
  }
  int len = (s >> 56) & 127; u64 w = s & ((1ULL << 56) - 1);
  if (len == 0) { xs[0] = 0; ss[0] = s; return 1; }
  xs[0] = w & 1; u64 w2 = w >> 1; int l2 = len - 1;
  if (l2 > 0 && !((w2 >> (l2 - 1)) & 1)) return 0;  // cannot happen for normalized states
  ss[0] = mkExact(l2, w2); return 1;
}
static string show(int sd, u64 s) {
  string o;
  if (s & FAR) { u64 t = (s >> K[sd]) & ((1ULL << M[sd]) - 1); u64 h = s & kmask(sd);
    for (int i = 0; i < K[sd]; i++) o += char('0' + ((h >> i) & 1)); o += " ..? "; for (int i = 0; i < M[sd]; i++) o += char('0' + ((t >> i) & 1)); o += " 0^inf"; return o; }
  int len = (s >> 56) & 127; for (int i = 0; i < len; i++) o += char('0' + ((s >> i) & 1)); o += " 0^inf"; return o;
}
struct IdMap { unordered_map<u64, uint32_t> m; vector<u64> v; uint32_t id(u64 s) { auto it = m.find(s); if (it != m.end()) return it->second; uint32_t i = v.size(); m.emplace(s, i); v.push_back(s); return i; } };
struct HS { vector<u64> t; size_t n = 0, mask; HS() { t.assign(1 << 20, ~0ULL); mask = t.size() - 1; }
  static u64 h(u64 x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; x ^= x >> 33; return x; }
  bool ins(u64 k) { if ((n + 1) * 2 > t.size()) grow(); size_t i = h(k) & mask; while (t[i] != ~0ULL) { if (t[i] == k) return false; i = (i + 1) & mask; } t[i] = k; n++; return true; }
  void grow() { vector<u64> o; o.swap(t); t.assign(o.size() * 2, ~0ULL); mask = t.size() - 1; for (auto k : o) if (k != ~0ULL) { size_t i = h(k) & mask; while (t[i] != ~0ULL) i = (i + 1) & mask; t[i] = k; } } };
int main(int argc, char** argv) {
  string ms = argv[1]; K[0] = atoi(argv[2]); K[1] = atoi(argv[3]); M[0] = atoi(argv[4]); M[1] = atoi(argv[5]);
  for (int s = 0; s < 2; s++) if (M[s] < K[s] || M[s] + K[s] > 62 || M[s] > 55 || K[s] < 1) { printf("bad params\n"); return 9; }
  size_t cap = getenv("TC_CAP") ? atoll(getenv("TC_CAP")) : 200000000ULL;
  bool nofail = getenv("TC_NOFAIL") != nullptr, track = getenv("TC_PATH") != nullptr;
  Tr tm[16][2]; int NS = 0;
  { stringstream ss(ms); string r; while (getline(ss, r, '_')) { for (int c = 0; c < 2; c++) { string t = r.substr(3 * c, 3); if (t[0] == '-') tm[NS][c] = {0, 0, 0, false}; else tm[NS][c] = {t[0] - '0', t[1] == 'R' ? 1 : -1, t[2] - 'A', true}; } NS++; } }
  IdMap ids[2]; vector<char> inS[2]; vector<vector<uint32_t>> wait[2];  // wait[sd][id] = indices of configs that unfold state id
  auto ensure = [&](int sd, uint32_t i) { if (inS[sd].size() <= i) { inS[sd].resize(i + 1 + i / 2, 0); wait[sd].resize(i + 1 + i / 2); } };
  HS seen; vector<u64> all; vector<u64> par; size_t nhalt = 0;
  auto key = [](int q, int m, uint32_t a, uint32_t b) { return ((u64)q << 61) | ((u64)m << 60) | ((u64)a << 30) | b; };
  long long firsthalt = -1;
  auto addc = [&](u64 k, u64 from) { if (seen.ins(k)) { all.push_back(k); if (track) par.push_back(from); return true; } return false; };
  // learn: add state s to S_sd; notify waiters of fold(s, x)
  function<void(int, u64)> learn;
  learn = [&](int sd, u64 s) {
    uint32_t i = ids[sd].id(s); ensure(sd, i); if (inS[sd][i]) return; inS[sd][i] = 1;
    for (int x = 0; x < 2; x++) {
      u64 f = fold(sd, s, x); uint32_t fi = ids[sd].id(f); ensure(sd, fi);
      for (size_t wi = 0; wi < wait[sd][fi].size(); wi++) { uint32_t widx = wait[sd][fi][wi]; u64 kk = all[widx];
        int q = kk >> 61, m = (kk >> 60) & 1; uint32_t a = (kk >> 30) & ((1u << 30) - 1), b = kk & ((1u << 30) - 1);
        Tr t = tm[q][m]; uint32_t oth = sd == 1 ? a : b; u64 nf = fold(1 - sd, ids[1 - sd].v[oth], t.w); uint32_t nfi = ids[1 - sd].m.at(nf);
        addc(sd == 1 ? key(t.q, x, nfi, i) : key(t.q, x, i, nfi), widx); }
    }
  };
  uint32_t z0 = ids[0].id(mkExact(0, 0)), z1 = ids[1].id(mkExact(0, 0)); ensure(0, z0); ensure(1, z1);
  learn(0, mkExact(0, 0)); learn(1, mkExact(0, 0));
  addc(key(0, 0, z0, z1), ~0ULL);
  for (size_t idx = 0; idx < all.size(); idx++) {
    if ((idx & ((1 << 23) - 1)) == 0 && idx) fprintf(stderr, "idx %zu / %zu  S=%zu/%zu\n", idx, all.size(), ids[0].v.size(), ids[1].v.size());
    if (all.size() > cap) { printf("CAP kL=%d kR=%d ML=%d MR=%d: more than %zu configs\n", K[0], K[1], M[0], M[1], cap); return 2; }
    u64 k = all[idx]; int q = k >> 61, m = (k >> 60) & 1; uint32_t a = (k >> 30) & ((1u << 30) - 1), b = k & ((1u << 30) - 1);
    Tr t = tm[q][m];
    if (!t.ok) {
      nhalt++;
      if (firsthalt < 0) firsthalt = idx;
      if (!nofail) {
        printf("FAIL kL=%d kR=%d ML=%d MR=%d: halting config %c%d after %zu configs\n  L: %s\n  R: %s\n", K[0], K[1], M[0], M[1], 'A' + q, m, all.size(), show(0, ids[0].v[a]).c_str(), show(1, ids[1].v[b]).c_str());
        if (track) { size_t j = idx; vector<size_t> pth; while (j != (size_t)~0ULL && pth.size() < 100000) { pth.push_back(j); j = par[j]; } printf("path length %zu (from start=%d)\n", pth.size(), j == (size_t)~0ULL);
          int lim = getenv("TC_PATHN") ? atoi(getenv("TC_PATHN")) : 60;
          for (int u = 0; u < (int)pth.size() && u < lim; u++) { u64 kk = all[pth[u]]; int qq = kk >> 61, mm = (kk >> 60) & 1; uint32_t aa = (kk >> 30) & ((1u << 30) - 1), bb = kk & ((1u << 30) - 1);
            printf("  %c%d | L %s | R %s\n", 'A' + qq, mm, show(0, ids[0].v[aa]).c_str(), show(1, ids[1].v[bb]).c_str()); } }
        return 1;
      }
      continue;
    }
    int sd = t.d == 1 ? 1 : 0;  // side we unfold from (move direction)
    uint32_t mine = sd == 1 ? b : a, oth = sd == 1 ? a : b;  // unfold side, fold side
    u64 so = ids[1 - sd].v[oth];
    learn(1 - sd, so);
    u64 nf = fold(1 - sd, so, t.w); uint32_t nfi = ids[1 - sd].id(nf); ensure(1 - sd, nfi);
    u64 su = ids[sd].v[mine];
    // register waiter, then enumerate known predecessors
    wait[sd][mine].push_back((uint32_t)idx);
    int xs[3]; u64 ss[3]; int n = cands(sd, su, xs, ss);
    for (int c = 0; c < n; c++) { auto it = ids[sd].m.find(ss[c]); if (it == ids[sd].m.end()) continue; uint32_t ci = it->second; if (ci >= inS[sd].size() || !inS[sd][ci]) continue;
      addc(sd == 1 ? key(t.q, xs[c], nfi, ci) : key(t.q, xs[c], ci, nfi), idx); }
  }
  size_t nl = 0, nr = 0; for (auto c : inS[0]) nl += c; for (auto c : inS[1]) nr += c;
  printf("%s kL=%d kR=%d ML=%d MR=%d: %zu configs, |S_L|=%zu |S_R|=%zu, halting configs %zu (first at %lld)\n", nhalt ? "SINK" : "NONHALT", K[0], K[1], M[0], M[1], all.size(), nl, nr, nhalt, firsthalt);
  if (getenv("TC_DUMP")) {
    FILE* f = fopen(getenv("TC_DUMP"), "w");
    fprintf(f, "P %d %d %d %d\n", K[0], K[1], M[0], M[1]);
    for (int s = 0; s < 2; s++) for (size_t i = 0; i < inS[s].size(); i++) if (inS[s][i]) fprintf(f, "S %d %llu\n", s, ids[s].v[i]);
    if (!getenv("TC_NOC")) for (auto k : all) { int q = k >> 61, m = (k >> 60) & 1; uint32_t a = (k >> 30) & ((1u << 30) - 1), b = k & ((1u << 30) - 1); fprintf(f, "C %d %d %llu %llu\n", q, m, ids[0].v[a], ids[1].v[b]); }
    fclose(f);
  }
  return 0;
}
