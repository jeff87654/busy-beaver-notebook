// xs: exact macro (K-block, run-length, self-loop accelerated) simulator over a template family.
// usage: xs MACHINE K MAXMACRO "TEMPLATE" PNAME LO HI [LOGLEFT]
//   TEMPLATE in ms 'i' format: "Q side | b^n ... [cur] b^n ..." with {x} placeholders; PNAME = name of the swept
//   placeholder (other placeholders must be given as env vars, e.g. a=2).  For each value v in LO..HI: run; print
//   "v H macro steps ones" or "v END steps maxlen lastLeftEndConfig" (head-at-left-end config, compressed).
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64; typedef long double LD;
int NS; int W[16][2], Dd[16][2], NX[16][2]; int K;
struct Run { u64 b; u64 n; };
struct MT { u64 nb; int ns; int dir; u64 steps; int halt; int ok; };
map<u64, MT> cache;
MT macro(int q, int side, u64 b) {
  u64 key = ((u64)q << 40) | ((u64)side << 39) | b; auto it = cache.find(key); if (it != cache.end()) return it->second;
  MT r; r.ok = 1; r.halt = 0; r.steps = 0; int pos = side ? K - 1 : 0; u64 bl = b; long lim = 100000;
  while (true) { int c = (bl >> (K - 1 - pos)) & 1; if (NX[q][c] < 0) { r.halt = 1; break; }
    if (W[q][c]) bl |= (1ULL << (K - 1 - pos)); else bl &= ~(1ULL << (K - 1 - pos));
    pos += Dd[q][c]; q = NX[q][c]; r.steps++; if (pos < 0) { r.dir = -1; break; } if (pos >= K) { r.dir = 1; break; } if (--lim == 0) { r.ok = 0; break; } }
  r.nb = bl; r.ns = q; if (r.halt) r.dir = pos; cache[key] = r; return r; }
void push(vector<Run>& S, u64 b, u64 n) { if (S.empty() && b == 0) return; if (!S.empty() && S.back().b == b) S.back().n += n; else S.push_back({b, n}); }
u64 pop(vector<Run>& S) { if (S.empty()) return 0; u64 b = S.back().b; if (--S.back().n == 0) S.pop_back(); return b; }
string bs(u64 b) { string s; for (int i = K - 1; i >= 0; --i) s += ((b >> i) & 1) ? '1' : '0'; return s; }
string subst(string t, map<string,string>& v) { string o; for (size_t i = 0; i < t.size(); i++) { if (t[i] == '{') { size_t j = t.find('}', i); o += v[t.substr(i + 1, j - i - 1)]; i = j; } else o += t[i]; } return o; }
int main(int argc, char** argv) {
  const char* m = argv[1]; K = atoi(argv[2]); u64 MAXM = strtoull(argv[3], 0, 10); string tmpl = argv[4]; string pn = argv[5];
  int RSIDE = getenv("RSIDE") != 0;
  long long lo = atoll(argv[6]), hi = atoll(argv[7]); int LOGL = argc > 8 ? atoi(argv[8]) : 0;
  NS = 0; const char* p = m;
  while (*p) { for (int c = 0; c < 2; ++c) { if (p[0] == '-') { NX[NS][c] = -1; W[NS][c] = 1; Dd[NS][c] = 1; } else { W[NS][c] = p[0] - '0'; Dd[NS][c] = p[1] == 'R' ? 1 : -1; NX[NS][c] = p[2] - 'A'; } p += 3; } NS++; if (*p == '_') ++p; }
  map<string,string> vars; for (char** e = environ; *e; e++) { string s = *e; size_t k = s.find('='); if (k != string::npos && k <= 2) vars[s.substr(0, k)] = s.substr(k + 1); }
  for (long long v = lo; v <= hi; v++) {
    vars[pn] = to_string(v); string line = subst(tmpl, vars);
    vector<Run> L, R; int q, side; u64 cur = 0; LD steps = 0;
    { stringstream ss(line); string qs; ss >> qs >> side; q = qs[0] - 'A'; string tok; bool right = false; vector<Run> rr;
      auto pb = [](const string& t) { u64 b = 0; for (char c : t) { if (c == '0' || c == '1') b = b * 2 + (c - '0'); else break; } return b; };
      while (ss >> tok) { if (tok == "|") continue; if (tok[0] == '[') { cur = pb(tok.substr(1)); right = true; continue; }
        size_t c = tok.find('^'); u64 n = c != string::npos ? strtoull(tok.c_str() + c + 1, 0, 10) : 1; u64 b = pb(tok);
        if (n == 0) continue; if (!right) push(L, b, n); else rr.push_back({b, n}); }
      for (size_t i = rr.size(); i-- > 0;) push(R, rr[i].b, rr[i].n); }
    string last; u64 it; bool halted = false; size_t maxlen = 0; int nl = 0;
    for (it = 0; it < MAXM; ++it) {
      if (!RSIDE ? (L.empty() && side == 1 && cur == 0) : (R.empty() && side == 0 && cur == 0)) { // head at the tape end
        vector<Run>& O = RSIDE ? L : R;
        string s = string(1, 'A' + q) + " |"; for (size_t i = O.size(); i-- > 0;) { s += " " + bs(O[i].b); if (O[i].n > 1) s += "^" + to_string(O[i].n); }
        last = to_string(it) + " " + s; maxlen = max(maxlen, O.size());
        static size_t pz = 0; if (LOGL && nl < LOGL && O.size() != pz) { pz = O.size(); printf("  %s\n", last.c_str()); nl++; } }
      MT t = macro(q, side, cur);
      if (!t.ok) { printf("%lld INBLOCK-LOOP\n", v); break; }
      if (t.halt) { steps += t.steps + 1; LD o = __builtin_popcountll(t.nb) + 1 - ((t.nb >> (K - 1 - t.dir)) & 1);
        for (auto& r : L) o += (LD)__builtin_popcountll(r.b) * r.n; for (auto& r : R) o += (LD)__builtin_popcountll(r.b) * r.n;
        printf("%lld H macro=%llu steps=%.6Le ones=%.6Le\n", v, it, steps, o); halted = true; break; }
      vector<Run>& Ah = t.dir > 0 ? R : L; vector<Run>& Be = t.dir > 0 ? L : R; int nside = t.dir > 0 ? 0 : 1;
      if (t.ns == q && nside == side && !Ah.empty() && Ah.back().b == cur) { u64 n = Ah.back().n; Ah.pop_back(); push(Be, t.nb, n + 1); steps += (LD)t.steps * (n + 1); cur = pop(Ah); q = t.ns; side = nside; continue; }
      steps += t.steps; push(Be, t.nb, 1); cur = pop(Ah); q = t.ns; side = nside;
    }
    if (!halted) printf("%lld END steps=%.4Le runs=%zu last: %s\n", v, steps, maxlen, last.substr(0, 240).c_str());
    fflush(stdout);
  }
}
