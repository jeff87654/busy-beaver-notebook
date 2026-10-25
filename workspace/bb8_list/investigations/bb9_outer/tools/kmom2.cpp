// kmom.cpp: literal tracer printing K-moments (state Q, head right of every nonzero cell).
//   kmom MACHINE Q STEPS EVERY BLOCKWORD < tapecells-line ("cells headindex")
// prints a K-moment when the count of leading BLOCKWORD repeats changes, or every EVERY-th K-moment; run-length compressed.
#include <bits/stdc++.h>
using namespace std; typedef long long ll;
static string comp(const string &x) {   // greedy periodic compression, periods 1..12, >=4 repeats
    string o; size_t i = 0, n = x.size();
    while (i < n) {
        int bp = 0; size_t bc = 0;
        for (int p = 1; p <= 12 && i + 4 * p <= n; ++p) { size_t r = 1; while (i + (r + 1) * p <= n && x.compare(i + r * p, p, x, i, p) == 0) ++r; if (r >= 4 && r * p > bc) { bc = r * p; bp = p; } }
        if (bp) { o += "(" + x.substr(i, bp) + ")^" + to_string(bc / bp) + "."; i += bc; } else o += x[i++];
    }
    return o;
}
int main(int argc, char **argv) {
    string m = argv[1]; int Q = argv[2][0] - 'A'; ll steps = atoll(argv[3]), every = atoll(argv[4]); string BW = argv[5];
    int ns = (m.size() + 1) / 7; int W[16][2], D[16][2], N[16][2];
    for (int q = 0; q < ns; ++q) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * q + 3 * c; if (x[0] == '-') N[q][c] = -1; else { W[q][c] = x[0] - '0'; D[q][c] = x[1] == 'R' ? 1 : -1; N[q][c] = x[2] - 'A'; } }
    string cells; ll head; cin >> cells >> head; int q; string qs; cin >> qs; q = qs[0] - 'A';
    const ll SZ = 1LL << 27; vector<unsigned char> t(SZ, 0); ll off = SZ / 2; for (size_t i = 0; i < cells.size(); ++i) t[off + i] = cells[i] - '0';
    ll pos = off + head, lo = off, hi = off + (ll)cells.size() - 1, km = 0; ll lastk = -1; string lastK; ll lastKs = -1; bool quiet = BW == "-";
    for (ll s = 0; s < steps; ++s) {
        int c = t[pos];
        if (N[q][c] < 0) { ll a = lo; while (!t[a]) ++a; ll b = hi; while (!t[b]) --b; ll sig = 1; string x; for (ll i = a; i <= b; ++i) { sig += t[i]; x += char('0' + t[i]); }
            printf("HALT %lld sigma %lld %s\n", s, sig, comp(x).substr(0, 600).c_str()); return 0; }
        t[pos] = W[q][c]; pos += D[q][c]; q = N[q][c];
        if (pos < lo) lo = pos; if (pos > hi) { hi = pos; }
        if (pos <= 1 || pos >= SZ - 2) { printf("TAPE OVERFLOW %lld km=%lld lastK@%lld %s\n", s, km, lastKs, comp(lastK).substr(0, 600).c_str()); return 0; }
        if (q == Q && pos >= hi && t[pos] == 0) {
            ll a = lo; while (!t[a]) ++a; ll b = pos; while (b > a && !t[b]) --b;
            ++km; string x; for (ll i = a; i <= b; ++i) x += char('0' + t[i]);
            if (quiet) { lastK = x; lastKs = s; continue; }
            ll k = 0; size_t p = 1; while (x.compare(p, BW.size(), BW) == 0) { ++k; p += BW.size(); }
            if (k != lastk || (every && km % every == 0)) { printf("%lld km=%lld k=%lld gap=%lld %s\n", s, km, k, pos - b - 1, comp(x).substr(0, 600).c_str()); fflush(stdout); lastk = k; }
        }
    }
    printf("BUDGET %lld km=%lld lastK@%lld %s\n", steps, km, lastKs, comp(lastK).substr(0, 600).c_str());
}
