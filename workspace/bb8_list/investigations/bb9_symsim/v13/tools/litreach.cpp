// litreach MACHINE STEPS : stdin line1 = start "cells head state", line2 = target "cells head state" (cells anchored at
// their first cell; both strings start at the same absolute tape cell).  Simulates literally and reports the first step
// at which the configuration equals the target (incremental mismatch count), or NOT REACHED.
#include <bits/stdc++.h>
using namespace std; typedef long long ll;
int main(int argc, char **argv) {
    string m = argv[1]; ll steps = atoll(argv[2]);
    int ns = (m.size() + 1) / 7; int W[16][2], D[16][2], N[16][2];
    for (int q = 0; q < ns; ++q) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * q + 3 * c; if (x[0] == '-') N[q][c] = -1; else { W[q][c] = x[0] - '0'; D[q][c] = x[1] == 'R' ? 1 : -1; N[q][c] = x[2] - 'A'; } }
    string sc, tc, sq, tq; ll sh, th; cin >> sc >> sh >> sq >> tc >> th >> tq;
    const ll SZ = 1 << 26, off = SZ / 2; vector<unsigned char> t(SZ, 0), g(SZ, 0);
    for (size_t i = 0; i < sc.size(); ++i) t[off + i] = sc[i] - '0';
    for (size_t i = 0; i < tc.size(); ++i) g[off + i] = tc[i] - '0';
    ll diff = 0; for (ll i = 0; i < SZ; ++i) if (t[i] != g[i]) ++diff;
    ll pos = off + sh, tpos = off + th; int q = sq[0] - 'A', qt = tq[0] - 'A';
    for (ll s = 0; s <= steps; ++s) {
        if (diff == 0 && q == qt && pos == tpos) { printf("REACHED at step %lld\n", s); return 0; }
        int c = t[pos]; if (N[q][c] < 0) { printf("HALT at step %lld\n", s); return 0; }
        int w = W[q][c];
        if (t[pos] != g[pos]) --diff; t[pos] = w; if (t[pos] != g[pos]) ++diff;
        pos += D[q][c]; q = N[q][c];
        if (pos < 1 || pos >= SZ - 1) { printf("OUT at %lld\n", s); return 0; }
    }
    printf("NOT REACHED in %lld\n", steps); return 0;
}
