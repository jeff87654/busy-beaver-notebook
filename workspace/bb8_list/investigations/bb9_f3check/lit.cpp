// lit.cpp: plain literal simulation of two machines in lockstep from blank; report the first step where the
// configurations differ (state, head, written symbol) or where either enters state H.  No jumps of any kind.
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <windows.h>
typedef long long ll;
struct M { int W[32], D[32], N[32]; bool def[32]; };
static M parse(const std::string &s) { M m; int n = (s.size() + 1) / 7; for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) { const char *x = s.c_str() + 7 * q + 3 * c; int i = 2 * q + c;
    if (x[0] == '-') m.def[i] = false; else { m.def[i] = true; m.W[i] = x[0] - '0'; m.D[i] = x[1] == 'R' ? 1 : -1; m.N[i] = x[2] - 'A'; } } return m; }
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    M a = parse(argv[1]), b = parse(argv[2]); ll N = (ll)atof(argv[3]);
    ll SZ = 1LL << 28; std::vector<unsigned char> ta(SZ, 0), tb(SZ, 0); ll pa = SZ / 2, pb = SZ / 2; int qa = 0, qb = 0; ll hvis = 0;
    for (ll s = 0; s < N; ++s) {
        if (pa < 2 || pa > SZ - 2) { printf("tape edge at step %lld\n", s); return 0; }
        int ca = ta[pa], cb = tb[pb]; int ia = 2 * qa + ca, ib = 2 * qb + cb;
        if (qa == 7 || qb == 7) { ++hvis; if (hvis < 5) printf("state H entered at step %lld (A:%c%d B:%c%d)\n", s, 'A' + qa, ca, 'A' + qb, cb); }
        if (qa != qb || pa != pb || ca != cb) { printf("DIFFER at step %lld\n", s); return 0; }
        if (!a.def[ia] || !b.def[ib]) { printf("undefined at step %lld\n", s); return 0; }
        if (a.W[ia] != b.W[ib] || a.D[ia] != b.D[ib] || a.N[ia] != b.N[ib]) { printf("transition differs at step %lld state %c read %d\n", s, 'A' + qa, ca); return 0; }
        ta[pa] = a.W[ia]; pa += a.D[ia]; qa = a.N[ia]; tb[pb] = b.W[ib]; pb += b.D[ib]; qb = b.N[ib];
    }
    ll ones = 0; for (ll i = 0; i < SZ; ++i) ones += ta[i];
    printf("identical for %lld steps, H visits %lld, ones %lld, head offset %lld, state %c\n", N, hvis, ones, pa - SZ / 2, 'A' + qa);
}
