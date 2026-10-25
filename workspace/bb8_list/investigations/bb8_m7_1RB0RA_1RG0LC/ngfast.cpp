// ngfast MACHINE nL nR [dumpfile] : ngcps2 with an open-addressing hash set, progress on stderr, cap NG_CAP configs (default 600M).
#include <bits/stdc++.h>
using namespace std;
struct Tr { int w, d, q; bool ok; };
struct HS { vector<uint64_t> t; size_t n=0, mask; HS(){ t.assign(1<<20, ~0ULL); mask=t.size()-1; }
  static uint64_t h(uint64_t x){ x^=x>>33; x*=0xff51afd7ed558ccdULL; x^=x>>33; x*=0xc4ceb9fe1a85ec53ULL; x^=x>>33; return x; }
  bool ins(uint64_t k){ if((n+1)*2>t.size()) grow(); size_t i=h(k)&mask; while(t[i]!=~0ULL){ if(t[i]==k) return false; i=(i+1)&mask; } t[i]=k; n++; return true; }
  void grow(){ vector<uint64_t> o; o.swap(t); t.assign(o.size()*2, ~0ULL); mask=t.size()-1; for(auto k:o) if(k!=~0ULL){ size_t i=h(k)&mask; while(t[i]!=~0ULL) i=(i+1)&mask; t[i]=k; } } };
int main(int argc, char** argv) {
  string ms = argv[1]; int nL = atoi(argv[2]), nR = atoi(argv[3]); string dump = argc > 4 ? argv[4] : "";
  size_t cap = getenv("NG_CAP") ? atoll(getenv("NG_CAP")) : 600000000ULL;
  Tr tm[16][2]; int S = 0;
  { stringstream ss(ms); string r; while (getline(ss, r, '_')) { for (int c = 0; c < 2; c++) { string t = r.substr(3 * c, 3); if (t[0] == '-') tm[S][c] = {0, 0, 0, false}; else tm[S][c] = {t[0] - '0', t[1] == 'R' ? 1 : -1, t[2] - 'A', true}; } S++; } }
  uint64_t mL = (1ULL << nL) - 1, mR = (1ULL << nR) - 1;
  vector<char> LS(1ULL << nL, 0), RS(1ULL << nR, 0); LS[0] = RS[0] = 1;
  auto key = [&](int q, int m, uint64_t l, uint64_t r) { return ((uint64_t)q << 61) | ((uint64_t)m << 60) | (l << 30) | r; };
  HS seen; vector<uint64_t> all;
  auto addc = [&](uint64_t k) { if (seen.ins(k)) { all.push_back(k); return true; } return false; };
  {
    long long N0 = getenv("NG_START") ? atoll(getenv("NG_START")) : 0;
    if (getenv("NG_TAPE")) {
      string w = getenv("NG_TAPE"); int q = getenv("NG_Q") ? getenv("NG_Q")[0] - 'A' : 1;
      long long SZ = 1LL << 20; vector<uint8_t> tape(SZ, 0); long long p = SZ / 2;
      for (size_t i = 0; i < w.size(); i++) tape[p - w.size() + i] = w[i] - '0';
      auto winL = [&](long long off) { uint64_t x = 0; for (int j = 0; j < nL; j++) x |= (uint64_t)tape[p - 1 - off - j] << j; return x; };
      auto winR = [&](long long off) { uint64_t x = 0; for (int j = 0; j < nR; j++) x |= (uint64_t)tape[p + 1 + off + j] << j; return x; };
      for (long long off = 0; off < (long long)w.size() + 64; off++) { LS[winL(off)] = 1; RS[winR(off)] = 1; }
      addc(key(q, tape[p], winL(0), winR(0)));
    } else
    if (N0 == 0) addc(key(0, 0, 0, 0));
    else {
      long long SZ = 1LL << 24; vector<uint8_t> tape(SZ, 0); long long p = SZ / 2; int q = 0;
      for (long long st = 0; st < N0; st++) { Tr t = tm[q][tape[p]]; if (!t.ok) { printf("real halt at %lld\n", st); return 3; } tape[p] = t.w; p += t.d; q = t.q; }
      // windows at all offsets
      auto winL = [&](long long off) { uint64_t w = 0; for (int j = 0; j < nL; j++) w |= (uint64_t)tape[p - 1 - off - j] << j; return w; };
      auto winR = [&](long long off) { uint64_t w = 0; for (int j = 0; j < nR; j++) w |= (uint64_t)tape[p + 1 + off + j] << j; return w; };
      for (long long off = 0; off < 2000; off++) { LS[winL(off)] = 1; RS[winR(off)] = 1; }
      addc(key(q, tape[p], winL(0), winR(0)));
      fprintf(stderr, "start at step %lld state %c\n", N0, 'A' + q);
    }
  }
  bool changed = true; int pass = 0; size_t nhalt = 0;
  while (changed) {
    changed = false; pass++;
    for (size_t idx = 0; idx < all.size(); idx++) {
      if ((idx & ((1<<24)-1)) == 0) fprintf(stderr, "pass %d idx %zu / %zu\n", pass, idx, all.size());
      if (all.size() > cap) { printf("CAP nL=%d nR=%d: more than %zu configs\n", nL, nR, cap); return 2; }
      uint64_t k = all[idx]; uint64_t r = k & ((1ULL << 30) - 1), l = (k >> 30) & ((1ULL << 30) - 1); int m = (k >> 60) & 1; int q = k >> 61;
      Tr t = tm[q][m];
      if (!t.ok) { if (getenv("NG_NOFAIL")) { nhalt++; if (getenv("NG_HALTDUMP") && pass == (int)atoi(getenv("NG_HALTDUMP"))) { string a, b; for (int i = nL - 1; i >= 0; i--) a += char(48 + ((l >> i) & 1)); for (int i = 0; i < nR; i++) b += char(48 + ((r >> i) & 1)); fprintf(stderr, "HALTCFG %s [%c%d] %s idx=%zu\n", a.c_str(), 65 + q, m, b.c_str(), idx); } continue; } printf("FAIL nL=%d nR=%d: halting local config %c%d\n", nL, nR, 'A' + q, m); return 1; }
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
  printf("[halt configs %zu] ", nhalt); printf("NONHALT nL=%d nR=%d: %zu configs, %lld left windows, %lld right windows, %d passes\n", nL, nR, all.size(), cl, cr, pass);
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
