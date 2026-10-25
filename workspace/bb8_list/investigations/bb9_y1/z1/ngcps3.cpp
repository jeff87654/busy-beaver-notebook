// ngcps3 MACHINE nL nR SEEDFILE [dumpfile]: ngcps2 seeded from a real configuration (SEEDFILE: "STATE HEAD TAPE",
//   TAPE a 0/1 string, HEAD index into it, blank beyond): all windows of its left/right sides are added to LS/RS.
// ngcps2 MACHINE nL nR [dumpfile]: n-gram closed position set with separate left/right window lengths.
// Left windows: nL cells left of the head, bit 0 = nearest.  Right windows: nR cells right of the head, bit 0 = nearest.
// LS/RS: sets of windows that may occur at any offset of the left/right side (all-zero window always present).
// Config: (q, m, l, r).  Closure as in NGramCPS.  Prints NONHALT/FAIL and statistics; optionally dumps the certificate.
#include <bits/stdc++.h>
using namespace std;
struct Tr { int w, d, q; bool ok; };
int main(int argc, char** argv) {
  string ms = argv[1]; int nL = atoi(argv[2]), nR = atoi(argv[3]); string dump = argc > 5 ? argv[5] : "";
  Tr tm[16][2]; int S = 0;
  { stringstream ss(ms); string r; while (getline(ss, r, '_')) { for (int c = 0; c < 2; c++) { string t = r.substr(3 * c, 3); if (t[0] == '-') tm[S][c] = {0, 0, 0, false}; else tm[S][c] = {t[0] - '0', t[1] == 'R' ? 1 : -1, t[2] - 'A', true}; } S++; } }
  uint64_t mL = (1ULL << nL) - 1, mR = (1ULL << nR) - 1;
  vector<char> LS(1ULL << nL, 0), RS(1ULL << nR, 0); LS[0] = RS[0] = 1;
  auto key = [&](int q, int m, uint64_t l, uint64_t r) { return ((uint64_t)q << 61) | ((uint64_t)m << 60) | (l << 30) | r; };
  unordered_set<uint64_t> seen; vector<uint64_t> all;
  auto addc = [&](uint64_t k) { if (seen.insert(k).second) { all.push_back(k); return true; } return false; };
  { FILE* sf = fopen(argv[4], "r"); char st[8]; long hp; static char tp[1 << 24]; if (fscanf(sf, "%7s %ld %16777215s", st, &hp, tp) != 3) { printf("bad seed\n"); return 2; } fclose(sf);
    long n = strlen(tp); auto cell = [&](long i) -> uint64_t { return (i >= 0 && i < n && tp[i] == '1') ? 1 : 0; };
    // left side: cells hp-1, hp-2, ... ; window at offset o: bits j = cell(hp-1-o-j)
    for (long o = 0; o <= hp + nL; o++) { uint64_t w = 0; for (int j = 0; j < nL; j++) w |= cell(hp - 1 - o - j) << j; LS[w] = 1; }
    for (long o = 0; o <= n - hp + nR; o++) { uint64_t w = 0; for (int j = 0; j < nR; j++) w |= cell(hp + 1 + o + j) << j; RS[w] = 1; }
    uint64_t l0 = 0, r0 = 0; for (int j = 0; j < nL; j++) l0 |= cell(hp - 1 - j) << j; for (int j = 0; j < nR; j++) r0 |= cell(hp + 1 + j) << j;
    addc(key(st[0] - 'A', (int)cell(hp), l0, r0)); }
  bool changed = true; int pass = 0;
  while (changed) {
    changed = false; pass++;
    for (size_t idx = 0; idx < all.size(); idx++) {
      uint64_t k = all[idx]; uint64_t r = k & ((1ULL << 30) - 1), l = (k >> 30) & ((1ULL << 30) - 1); int m = (k >> 60) & 1; int q = k >> 61;
      Tr t = tm[q][m];
      if (!t.ok) { printf("FAIL nL=%d nR=%d: halting local config %c%d\n", nL, nR, 'A' + q, m); return 1; }
      if (t.d == 1) {
        uint64_t nl = ((l << 1) | t.w) & mL; if (!LS[nl]) { LS[nl] = 1; changed = true; }
        int nm = r & 1; uint64_t rb = r >> 1;
        for (int x = 0; x < 2; x++) { uint64_t nr = rb | ((uint64_t)x << (nR - 1)); if (RS[nr] && addc(key(t.q, nm, nl, nr))) changed = true; }
      } else {
        uint64_t nr = ((r << 1) | t.w) & mR; if (!RS[nr]) { RS[nr] = 1; changed = true; }
        int nm = l & 1; uint64_t lb = l >> 1;
        for (int x = 0; x < 2; x++) { uint64_t nl = lb | ((uint64_t)x << (nL - 1)); if (LS[nl] && addc(key(t.q, nm, nl, nr))) changed = true; }
      }
    }
  }
  long long cl = 0, cr = 0; for (auto c : LS) cl += c; for (auto c : RS) cr += c;
  printf("NONHALT nL=%d nR=%d: %zu configs, %lld left windows, %lld right windows, %d passes\n", nL, nR, all.size(), cl, cr, pass);
  if (!dump.empty()) {
    FILE* f = fopen(dump.c_str(), "w");
    fprintf(f, "%d %d\n", nL, nR);
    for (uint64_t i = 0; i < LS.size(); i++) if (LS[i]) fprintf(f, "L %llu\n", (unsigned long long)i);
    for (uint64_t i = 0; i < RS.size(); i++) if (RS[i]) fprintf(f, "R %llu\n", (unsigned long long)i);
    if (!getenv("NOC")) for (auto k : all) { uint64_t r = k & ((1ULL << 30) - 1), l = (k >> 30) & ((1ULL << 30) - 1); int m = (k >> 60) & 1; int q = k >> 61; fprintf(f, "C %d %d %llu %llu\n", q, m, (unsigned long long)l, (unsigned long long)r); }
    fclose(f);
  }
  return 0;
}
