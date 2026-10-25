// ngprod MACHINE nL nR : n-gram CPS where the local-config set is a PRODUCT over (q,m):
// CL(q,m) = set of left windows, CR(q,m) = set of right windows; a config (q,m,l,r) is abstractly present iff
// l in CL(q,m) and r in CR(q,m).  Window sets LS/RS as in NGramCPS.  Tests whether this coarser invariant closes.
#include <bits/stdc++.h>
using namespace std;
struct Tr { int w, d, q; bool ok; };
int main(int argc, char** argv) {
  string ms = argv[1]; int nL = atoi(argv[2]), nR = atoi(argv[3]);
  Tr tm[16][2]; int S = 0;
  { stringstream ss(ms); string r; while (getline(ss, r, '_')) { for (int c = 0; c < 2; c++) { string t = r.substr(3 * c, 3); if (t[0] == '-') tm[S][c] = {0, 0, 0, false}; else tm[S][c] = {t[0] - '0', t[1] == 'R' ? 1 : -1, t[2] - 'A', true}; } S++; } }
  uint64_t mL = (1ULL << nL) - 1, mR = (1ULL << nR) - 1;
  vector<char> LS(1ULL << nL, 0), RS(1ULL << nR, 0); LS[0] = RS[0] = 1;
  vector<vector<char>> CL(16, vector<char>(1ULL << nL, 0)), CR(16, vector<char>(1ULL << nR, 0));
  CL[0][0] = 1; CR[0][0] = 1;  // (A,0): l=0, r=0
  bool changed = true; int pass = 0;
  while (changed) {
    changed = false; pass++;
    for (int q = 0; q < S; q++) for (int m = 0; m < 2; m++) {
      int qm = q * 2 + m;
      bool anyL = false, anyR = false;
      for (auto c : CL[qm]) if (c) { anyL = true; break; }
      for (auto c : CR[qm]) if (c) { anyR = true; break; }
      if (!anyL || !anyR) continue;
      Tr t = tm[q][m];
      if (!t.ok) { printf("FAIL nL=%d nR=%d: halting %c%d reachable\n", nL, nR, 'A' + q, m); return 1; }
      if (t.d == 1) {
        // new head symbol from right windows; new right windows from shifting
        bool nmPossible[2] = {false, false};
        for (uint64_t r = 0; r <= mR; r++) if (CR[qm][r]) {
          int nm = r & 1; uint64_t rb = r >> 1;
          for (int x = 0; x < 2; x++) { uint64_t nr = rb | ((uint64_t)x << (nR - 1)); if (RS[nr]) { nmPossible[nm] = true; int qm2 = t.q * 2 + nm; if (!CR[qm2][nr]) { CR[qm2][nr] = 1; changed = true; } } }
        }
        for (uint64_t l = 0; l <= mL; l++) if (CL[qm][l]) {
          uint64_t nl = ((l << 1) | t.w) & mL; if (!LS[nl]) { LS[nl] = 1; changed = true; }
          for (int nm = 0; nm < 2; nm++) if (nmPossible[nm]) { int qm2 = t.q * 2 + nm; if (!CL[qm2][nl]) { CL[qm2][nl] = 1; changed = true; } }
        }
      } else {
        bool nmPossible[2] = {false, false};
        for (uint64_t l = 0; l <= mL; l++) if (CL[qm][l]) {
          int nm = l & 1; uint64_t lb = l >> 1;
          for (int x = 0; x < 2; x++) { uint64_t nl = lb | ((uint64_t)x << (nL - 1)); if (LS[nl]) { nmPossible[nm] = true; int qm2 = t.q * 2 + nm; if (!CL[qm2][nl]) { CL[qm2][nl] = 1; changed = true; } } }
        }
        for (uint64_t r = 0; r <= mR; r++) if (CR[qm][r]) {
          uint64_t nr = ((r << 1) | t.w) & mR; if (!RS[nr]) { RS[nr] = 1; changed = true; }
          for (int nm = 0; nm < 2; nm++) if (nmPossible[nm]) { int qm2 = t.q * 2 + nm; if (!CR[qm2][nr]) { CR[qm2][nr] = 1; changed = true; } }
        }
      }
    }
  }
  long long a = 0, b = 0; for (auto& v : CL) for (auto c : v) a += c; for (auto& v : CR) for (auto c : v) b += c;
  printf("NONHALT nL=%d nR=%d product: CL %lld CR %lld passes %d\n", nL, nR, a, b, pass);
}
