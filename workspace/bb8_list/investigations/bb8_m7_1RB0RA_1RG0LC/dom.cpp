// ngpath MACHINE nL nR : like ngcps2 but BFS with parent pointers; on FAIL prints the abstract path to the halting config.
// Windows: LS/RS = sets of windows that may occur (any offset). Tracks for each LS/RS window the config that first created it.
#include <bits/stdc++.h>
using namespace std;
struct Tr { int w, d, q; bool ok; };
int main(int argc, char** argv) {
  string ms = argv[1]; int nL = atoi(argv[2]), nR = atoi(argv[3]);
  Tr tm[16][2]; int S = 0;
  { stringstream ss(ms); string r; while (getline(ss, r, '_')) { for (int c = 0; c < 2; c++) { string t = r.substr(3 * c, 3); if (t[0] == '-') tm[S][c] = {0, 0, 0, false}; else tm[S][c] = {t[0] - '0', t[1] == 'R' ? 1 : -1, t[2] - 'A', true}; } S++; } }
  uint64_t mL = (1ULL << nL) - 1, mR = (1ULL << nR) - 1;
  vector<char> LS(1ULL << nL, 0), RS(1ULL << nR, 0); LS[0] = RS[0] = 1;
  vector<int> LSsrc(1ULL << nL, -1), RSsrc(1ULL << nR, -1);
  auto key = [&](int q, int m, uint64_t l, uint64_t r) { return ((uint64_t)q << 61) | ((uint64_t)m << 60) | (l << 30) | r; };
  unordered_map<uint64_t,int> seen; vector<uint64_t> all; vector<int> par;
  auto addc = [&](uint64_t k, int p) { if (seen.emplace(k, all.size()).second) { all.push_back(k); par.push_back(p); return true; } return false; };
  {
    long long N0 = getenv("NG_START") ? atoll(getenv("NG_START")) : 0;
    if (getenv("NG_TAPE")) {
      string w = getenv("NG_TAPE"); int q = getenv("NG_Q") ? getenv("NG_Q")[0] - 'A' : 1;
      long long SZ = 1LL << 20; vector<uint8_t> tape(SZ, 0); long long p = SZ / 2;
      for (size_t i = 0; i < w.size(); i++) tape[p - w.size() + i] = w[i] - '0';
      auto winL = [&](long long off) { uint64_t x = 0; for (int j = 0; j < nL; j++) x |= (uint64_t)tape[p - 1 - off - j] << j; return x; };
      auto winR = [&](long long off) { uint64_t x = 0; for (int j = 0; j < nR; j++) x |= (uint64_t)tape[p + 1 + off + j] << j; return x; };
      for (long long off = 0; off < (long long)w.size() + 64; off++) { LS[winL(off)] = 1; RS[winR(off)] = 1; }
      addc(key(q, tape[p], winL(0), winR(0)), -1);
    } else
    if (N0 == 0) addc(key(0, 0, 0, 0), -1);
    else {
      long long SZ = 1LL << 24; vector<uint8_t> tape(SZ, 0); long long p = SZ / 2; int q = 0;
      for (long long st = 0; st < N0; st++) { Tr t = tm[q][tape[p]]; tape[p] = t.w; p += t.d; q = t.q; }
      auto winL = [&](long long off) { uint64_t w = 0; for (int j = 0; j < nL; j++) w |= (uint64_t)tape[p - 1 - off - j] << j; return w; };
      auto winR = [&](long long off) { uint64_t w = 0; for (int j = 0; j < nR; j++) w |= (uint64_t)tape[p + 1 + off + j] << j; return w; };
      for (long long off = 0; off < 2000; off++) { LS[winL(off)] = 1; RS[winR(off)] = 1; }
      addc(key(q, tape[p], winL(0), winR(0)), -1);
    }
  }
  bool changed = true; long haltidx = -1;
  auto show = [&](uint64_t k) {
    uint64_t r = k & ((1ULL << 30) - 1), l = (k >> 30) & ((1ULL << 30) - 1); int m = (k >> 60) & 1; int q = k >> 61;
    string s; for (int i = nL - 1; i >= 0; i--) s += char('0' + ((l >> i) & 1));
    s += string(" [") + char('A' + q) + char('0' + m) + "] ";
    for (int i = 0; i < nR; i++) s += char('0' + ((r >> i) & 1));
    return s;
  };
  auto showw = [&](uint64_t w, int n, bool left) { string s; if (left) { for (int i = n - 1; i >= 0; i--) s += char('0' + ((w >> i) & 1)); } else for (int i = 0; i < n; i++) s += char('0' + ((w >> i) & 1)); return s; };
  auto fail = [&](size_t idx, int q, int m) {
    printf("FAIL halting local config %c%d; path:\n", 'A' + q, m);
    vector<int> path; for (int i = idx; i >= 0; i = par[i]) path.push_back(i);
    reverse(path.begin(), path.end());
    for (size_t i = 0; i < path.size(); i++) printf("%3zu %s\n", i, show(all[path[i]]).c_str());
    // provenance of the windows in the last config
    uint64_t k = all[idx]; uint64_t r = k & ((1ULL << 30) - 1), l = (k >> 30) & ((1ULL << 30) - 1);
    int ls = LSsrc[l], rs = RSsrc[r];
    printf("left window %s created by config idx %d: %s\n", showw(l, nL, true).c_str(), ls, ls >= 0 ? show(all[ls]).c_str() : "(blank)");
    printf("right window %s created by config idx %d: %s\n", showw(r, nR, false).c_str(), rs, rs >= 0 ? show(all[rs]).c_str() : "(blank)");
  };
  while (changed) {
    changed = false;
    for (size_t idx = 0; idx < all.size(); idx++) {
      uint64_t k = all[idx]; uint64_t r = k & ((1ULL << 30) - 1), l = (k >> 30) & ((1ULL << 30) - 1); int m = (k >> 60) & 1; int q = k >> 61;
      Tr t = tm[q][m];
      if (!t.ok) { if (haltidx < 0) haltidx = idx; continue; }
      if (t.d == 1) {
        uint64_t nl = ((l << 1) | t.w) & mL; if (!LS[nl]) { LS[nl] = 1; LSsrc[nl] = idx; changed = true; }
        int nm = r & 1; uint64_t rb = r >> 1;
        for (int x = 0; x < 2; x++) { uint64_t nr = rb | ((uint64_t)x << (nR - 1)); if (RS[nr] && addc(key(t.q, nm, nl, nr), idx)) changed = true; }
      } else {
        uint64_t nr = ((r << 1) | t.w) & mR; if (!RS[nr]) { RS[nr] = 1; RSsrc[nr] = idx; changed = true; }
        int nm = l & 1; uint64_t lb = l >> 1;
        for (int x = 0; x < 2; x++) { uint64_t nl = lb | ((uint64_t)x << (nL - 1)); if (LS[nl] && addc(key(t.q, nm, nl, nr), idx)) changed = true; }
      }
    }
  }
  if (haltidx < 0) { printf("NONHALT: %zu configs\n", all.size()); return 0; }
  printf("closure %zu configs; first halting config idx %ld\n", all.size(), haltidx);
  vector<int> path; for (int i = haltidx; i >= 0; i = par[i]) path.push_back(i);
  reverse(path.begin(), path.end());
  printf("shortest path length %zu\n", path.size());
  auto succs = [&](int idx, vector<int>& out) {
    out.clear();
    uint64_t k = all[idx]; uint64_t r = k & ((1ULL << 30) - 1), l = (k >> 30) & ((1ULL << 30) - 1); int m = (k >> 60) & 1; int q = k >> 61;
    Tr t = tm[q][m]; if (!t.ok) return;
    if (t.d == 1) {
      uint64_t nl = ((l << 1) | t.w) & mL; int nm = r & 1; uint64_t rb = r >> 1;
      for (int x = 0; x < 2; x++) { uint64_t nr = rb | ((uint64_t)x << (nR - 1)); if (RS[nr]) { auto it = seen.find(key(t.q, nm, nl, nr)); if (it != seen.end()) out.push_back(it->second); } }
    } else {
      uint64_t nr = ((r << 1) | t.w) & mR; int nm = l & 1; uint64_t lb = l >> 1;
      for (int x = 0; x < 2; x++) { uint64_t nl = lb | ((uint64_t)x << (nL - 1)); if (LS[nl]) { auto it = seen.find(key(t.q, nm, nl, nr)); if (it != seen.end()) out.push_back(it->second); } }
    }
  };
  vector<int> sc; vector<char> vis(all.size());
  int ndom = 0;
  int stride = getenv("DOM_STRIDE") ? atoi(getenv("DOM_STRIDE")) : 1;
  for (size_t pi = 1; pi + 1 < path.size(); pi += stride) {
    int x = path[pi];
    fill(vis.begin(), vis.end(), 0); vector<int> st; st.push_back(0); vis[0] = 1; vis[x] = 1; bool reach = false;
    while (!st.empty() && !reach) { int u = st.back(); st.pop_back(); succs(u, sc); for (int v : sc) { if (v == (int)haltidx) { reach = true; break; } if (!vis[v]) { vis[v] = 1; st.push_back(v); } } }
    if (!reach) { ndom++; printf("DOMINATOR at path pos %zu: %s\n", pi, show(all[x]).c_str()); fflush(stdout); }
  }
  printf("dominators: %d\n", ndom);
  return 0;
}
