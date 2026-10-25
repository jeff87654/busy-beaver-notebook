// lockpair.cpp: run two TMs step by step from blank; after every step require (state1,state2) in the allowed pair list and equal
// head positions; compare the whole tape every 2^20 steps and at the end.  usage: lockpair M1 M2 PAIRS N   (PAIRS like AA,BB,HF)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
using namespace std;
struct TM { int w[16][2], d[16][2], q[16][2]; };
void parse(const char *s, TM &m) { int n = (strlen(s) + 1) / 7; for (int i = 0; i < n; ++i) for (int c = 0; c < 2; ++c) { const char *t = s + 7 * i + 3 * c;
    if (t[0] == '-' || t[2] == 'Z') m.q[i][c] = -1; else { m.w[i][c] = t[0] - '0'; m.d[i][c] = t[1] == 'R' ? 1 : -1; m.q[i][c] = t[2] - 'A'; } } }
int main(int argc, char **argv) {
    TM a, b; parse(argv[1], a); parse(argv[2], b); bool ok[16][16] = {}; const char *p = argv[3];
    while (*p) { ok[p[0] - 'A'][p[1] - 'A'] = true; p += 2; if (*p == ',') ++p; }
    long long N = atoll(argv[4]); const long long SZ = 1LL << 26; vector<unsigned char> ta(SZ), tb(SZ); long long pa = SZ / 2, pb = SZ / 2, lo = pa, hi = pa; int sa = 0, sb = 0;
    for (long long n = 0; n < N; ++n) {
        int ca = ta[pa], cb = tb[pb];
        if (a.q[sa][ca] < 0 || b.q[sb][cb] < 0) { printf("step %lld: M1 %c%d %s, M2 %c%d %s\n", n, 'A' + sa, ca, a.q[sa][ca] < 0 ? "HALTS" : "runs", 'A' + sb, cb, b.q[sb][cb] < 0 ? "HALTS" : "runs");
            for (long long i = lo; i <= hi; ++i) if (ta[i] != tb[i]) { printf("tapes differ at %lld\n", i); return 1; } printf("tapes equal so far\n"); return 0; }
        ta[pa] = a.w[sa][ca]; int na = a.q[sa][ca]; pa += a.d[sa][ca]; sa = na;
        tb[pb] = b.w[sb][cb]; int nb = b.q[sb][cb]; pb += b.d[sb][cb]; sb = nb;
        if (pa < lo) lo = pa; if (pa > hi) hi = pa; if (pa < 2 || pa > SZ - 3) { printf("overflow\n"); return 1; }
        if (pa != pb || !ok[sa][sb]) { printf("MISMATCH step %lld: %c@%lld vs %c@%lld\n", n, 'A' + sa, pa, 'A' + sb, pb); return 1; }
        if ((n & 0xFFFFF) == 0) for (long long i = lo; i <= hi; ++i) if (ta[i] != tb[i]) { printf("TAPE MISMATCH step %lld\n", n); return 1; }
    }
    for (long long i = lo; i <= hi; ++i) if (ta[i] != tb[i]) { printf("TAPE MISMATCH end\n"); return 1; }
    printf("OK %lld steps\n", N);
}
