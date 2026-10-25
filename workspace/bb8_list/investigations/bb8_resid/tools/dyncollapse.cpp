// dyncollapse.cpp: dynamic (invariant-aware) gadget detection.
// usage: dyncollapse MACHINE [N=1e8] [K=3] [CAP=64]
// For every set G of non-start states with |G| <= K, every entry into G from outside (S,c)->(w,d,X) at cell p is tracked
// literally until the first moment the head is at p-1 or p+1 in a state outside G with every cell other than p holding its
// pre-entry value.  The net effect (cell p value, side, state) is recorded per entry slot.  G is reported if every tracked
// entry finished within CAP steps with a single net effect per slot (OBSERVED evidence only: the reduced machine is valid on
// the observed run; validity in general needs an invariant or a syntactic proof, see collapse2.py).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <map>
using namespace std;
typedef long long ll;
int n; int W[16][2], D[16][2], Q[16][2]; bool DEF[16][2];
struct Trk { bool on = false; int slot; ll p; int steps; vector<pair<ll, unsigned char>> ch; };
int main(int argc, char **argv) {
    string m = argv[1]; ll N = argc > 2 ? (ll)atof(argv[2]) : 100000000; int K = argc > 3 ? atoi(argv[3]) : 3; int CAP = argc > 4 ? atoi(argv[4]) : 64;
    n = (m.size() + 1) / 7;
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * s + 3 * c;
        DEF[s][c] = !(x[0] == '-' || x[2] == 'Z' || x[2] - 'A' >= n); if (DEF[s][c]) { W[s][c] = x[0] - '0'; D[s][c] = x[1] == 'R' ? 1 : -1; Q[s][c] = x[2] - 'A'; } }
    vector<int> sets;
    for (int msk = 1; msk < (1 << n); ++msk) { if (msk & 1) continue; if (__builtin_popcount(msk) <= K) sets.push_back(msk); }
    int S = sets.size();
    vector<Trk> tr(S); vector<char> failed(S, 0); vector<string> why(S);
    vector<map<int, tuple<int, int, int>>> net(S); vector<map<int, ll>> cnt(S);
    // start lists: for (q, q2): sets containing q2 but not q
    vector<vector<int>> startL(n * n);
    for (int i = 0; i < S; ++i) for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) if (!(sets[i] >> a & 1) && (sets[i] >> b & 1)) startL[a * n + b].push_back(i);
    vector<int> active;
    const ll SZ = 1LL << 27; vector<unsigned char> t(SZ, 0); ll pos = SZ / 2; int q = 0; ll lo = pos, hi = pos;
    vector<ll> used(2 * n, 0);
    ll step = 0; bool halted = false;
    for (; step < N; ++step) {
        int c = t[pos];
        if (!DEF[q][c]) { halted = true; break; }
        used[2 * q + c]++;
        int w = W[q][c], d = D[q][c], q2 = Q[q][c];
        // record writes for active trackers
        for (int i : active) { Trk &T = tr[i]; bool f = false; for (auto &e : T.ch) if (e.first == pos) { f = true; break; } if (!f) T.ch.push_back({pos, (unsigned char)c}); }
        t[pos] = w; ll np = pos + d;
        if (np < 2 || np > SZ - 3) { printf("# tape overflow at %lld\n", step); break; }
        if (np < lo) lo = np; if (np > hi) hi = np;
        // advance active trackers
        vector<int> keep;
        for (int i : active) { Trk &T = tr[i]; T.steps++;
            bool sync = false;
            if (!(sets[i] >> q2 & 1) && (np == T.p - 1 || np == T.p + 1)) { sync = true; for (auto &e : T.ch) if (e.first != T.p && t[e.first] != e.second) { sync = false; break; } }
            if (sync) { auto v = make_tuple((int)t[T.p], (int)(np - T.p), q2); auto it = net[i].find(T.slot);
                if (it == net[i].end()) net[i][T.slot] = v; else if (it->second != v) { failed[i] = 1; why[i] = "conflict slot " + string(1, 'A' + T.slot / 2) + to_string(T.slot % 2); }
                cnt[i][T.slot]++; T.on = false; continue; }
            if (T.steps > CAP) { failed[i] = 1; why[i] = "cap slot " + string(1, 'A' + T.slot / 2) + to_string(T.slot % 2); T.on = false; continue; }
            keep.push_back(i); }
        active.swap(keep);
        // start new trackers
        for (int i : startL[q * n + q2]) { if (failed[i] || tr[i].on) continue; Trk &T = tr[i]; T.on = true; T.slot = 2 * q + c; T.p = pos; T.steps = 1; T.ch.clear(); T.ch.push_back({pos, (unsigned char)c}); active.push_back(i); }
        pos = np; q = q2;
    }
    for (int i : active) { failed[i] = 1; why[i] = "halt/end inside"; }
    printf("# %s steps=%lld halted=%d span=%lld\n# unused slots:", m.c_str(), step, (int)halted, hi - lo + 1);
    for (int s = 0; s < 2 * n; ++s) if (!used[s]) printf(" %c%d", 'A' + s / 2, s % 2); printf("\n");
    for (int i = 0; i < S; ++i) {
        if (failed[i] || net[i].empty()) continue;
        string g; for (int a = 0; a < n; ++a) if (sets[i] >> a & 1) g += char('A' + a);
        // build reduced table: entries replaced, unobserved outside entries into G flagged
        string unob;
        for (int a = 0; a < n; ++a) if (!(sets[i] >> a & 1)) for (int c = 0; c < 2; ++c) if (DEF[a][c] && (sets[i] >> Q[a][c] & 1) && !net[i].count(2 * a + c)) unob += string(1, 'A' + a) + to_string(c) + " ";
        printf("G=%s nets:", g.c_str());
        for (auto &e : net[i]) printf(" %c%d->%d%c%c(x%lld)", 'A' + e.first / 2, e.first % 2, get<0>(e.second), get<1>(e.second) > 0 ? 'R' : 'L', 'A' + get<2>(e.second), cnt[i][e.first]);
        printf("%s%s\n", unob.empty() ? "" : "  UNOBSERVED-ENTRIES ", unob.c_str());
    }
}
