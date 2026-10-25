// rend MACHINE WORD N W [mode]: simulate from WORD (head right of it, state B; WORD "" = blank tape, state A)
// and collect distinct right-end windows: (state, head offset from last 1, last W cells) whenever the head is within W cells of the last 1.
// Prints the number of distinct windows over time and finally all of them (mode 1) or a summary.
#include <bits/stdc++.h>
using namespace std;
struct Tr { int w, d, q; bool ok; };
int main(int argc, char** argv) {
  string ms = argv[1]; string w = argv[2]; long long N = atoll(argv[3]); int W = atoi(argv[4]); int mode = argc > 5 ? atoi(argv[5]) : 0;
  Tr tm[8][2]; int ns = 0; { stringstream ss(ms); string r; while (getline(ss, r, '_')) { for (int c = 0; c < 2; c++) { string t = r.substr(3 * c, 3); if (t[0] == '-') tm[ns][c] = {0, 0, 0, false}; else tm[ns][c] = {t[0] - '0', t[1] == 'R' ? 1 : -1, t[2] - 'A', true}; } ns++; } }
  long long SZ = 1LL << 27; vector<uint8_t> tape(SZ, 0); long long off = SZ / 2;
  if (w == "-") w = "";
  for (size_t i = 0; i < w.size(); i++) tape[off + i] = w[i] - '0';
  long long p = off + w.size(); int q = w.empty() ? 0 : 1;
  long long last1 = off + (long long)w.size() - 1; while (last1 > off && !tape[last1]) last1--;
  set<string> seen; long long nextRep = 1;
  for (long long st = 0; st < N; st++) {
    int c = tape[p]; Tr t = tm[q][c];
    if (!t.ok) { printf("HALT at %lld\n", st); break; }
    tape[p] = t.w;
    if (t.w && p > last1) last1 = p;
    if (!t.w && p == last1) { while (last1 > 0 && !tape[last1]) last1--; }
    p += t.d; q = t.q;
    if (p < 2 || p > SZ - 2) { printf("EDGE\n"); break; }
    if (p >= last1 - W) {
      string key; key += char('A' + q); key += ' '; key += to_string(p - last1); key += ' ';
      for (long long k = last1 - W; k <= last1; k++) key += char('0' + tape[k]);
      if (seen.insert(key).second && mode == 2) printf("%lld %s\n", st, key.c_str());
    }
    if (st + 1 == nextRep) { fprintf(stderr, "step %lld distinct %zu\n", st + 1, seen.size()); nextRep *= 2; }
  }
  printf("distinct %zu\n", seen.size());
  if (mode == 1) for (auto& s : seen) printf("%s\n", s.c_str());
}
