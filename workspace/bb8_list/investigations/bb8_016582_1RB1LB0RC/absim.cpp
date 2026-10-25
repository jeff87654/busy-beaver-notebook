// absim N : run the canonical abstract F-turn system from S(4) for N abstract steps; report Stuck or progress.
// L: bit stack (back = nearest). G: gap stack stored reversed (back = nearest). P: 0=111 1=011 2=11 3=01.
#include <bits/stdc++.h>
using namespace std;
const long long INF = 1LL << 60;
int main(int argc, char** argv) {
  long long N = atoll(argv[1]);
  vector<char> L; vector<long long> G; int P = 3;
  for (int i = 0; i < 3; i++) G.push_back(2);  // S(4): P=01, G=[2,2,2]
  long long maxL = 0, maxG = 0; int lastk = 0;
  for (long long it = 0; it < N; it++) {
    if (P == 0 || P == 1) {
      int x = 0; if (!L.empty()) { x = L.back(); L.pop_back(); }
      if (G.empty()) G.push_back(INF);
      if (P == 0) { G.back() += (G.back() >= INF ? 0 : 1); P = x ? 0 : 1; }
      else { G.back() += (G.back() >= INF ? 0 : 2); P = x ? 2 : 3; }
      if (G.back() >= INF) G.pop_back();
      continue;
    }
    // consume a 2-run
    long long m = 0; while (!G.empty() && G.back() == 2) { G.pop_back(); m++; }
    long long h = INF; if (!G.empty()) { h = G.back(); G.pop_back(); }
    if (P == 2) {
      if (h < 4) { printf("STUCK R3 h=%lld m=%lld at %lld\n", h, m, it); return 1; }
      L.push_back(0); for (long long j = 0; j < m; j++) { L.push_back(1); L.push_back(1); L.push_back(0); } L.push_back(1);
      if (h < INF) G.push_back(h - 3);
      P = 0;
    } else {
      if (h < 3) { printf("STUCK R4 h=%lld m=%lld at %lld\n", h, m, it); return 1; }
      if (h < INF) G.push_back(h - 2);
      G.push_back(0);
      if (m == 0) P = 1;
      else { L.push_back(0); L.push_back(0); for (long long j = 0; j < m - 1; j++) { L.push_back(1); L.push_back(1); L.push_back(0); } L.push_back(1); P = 0; }
      // left extension S(k): L empty-ish and m large: report
      if (m >= 3 && h >= INF) { int k = m + 1; if (k > lastk) { lastk = k; printf("S(%d) at abstract step %lld, |L|=%zu\n", k, it, L.size()); fflush(stdout); } }
    }
    maxL = max(maxL, (long long)L.size()); maxG = max(maxG, (long long)G.size());
  }
  printf("no stuck in %lld steps; maxL %lld maxG %lld\n", N, maxL, maxG);
}
