// lockstep.cpp: literal lockstep comparison of two TMs under a state map.
// usage: lockstep M9 M8 MAP N [F] (F: M9 state whose 0-transition opens a 2-step silent gadget)
//   MAP = for each M9 state its M8 image or '.' (gadget-internal state, not a sync point)
// Runs M9; at every step where M9 enters a state with an image, runs M8 until it enters some state (one step) and
// compares state image, head position and the whole tape.  Reports mismatch or OK after N M9 steps.
#include <cstdio>
#include <cstring>
#include <vector>
#include <string>
using namespace std;
struct TM { int ns; int w[16][2], d[16][2], q[16][2]; };
bool parse(const char *s, TM &m) {
    m.ns = 0; int i = 0; while (s[i]) {
        for (int c = 0; c < 2; ++c) {
            const char *t = s + i + 3 * c;
            if (t[0] == '-') { m.w[m.ns][c] = -1; m.d[m.ns][c] = 0; m.q[m.ns][c] = -1; }
            else { m.w[m.ns][c] = t[0] - '0'; m.d[m.ns][c] = t[1] == 'R' ? 1 : -1; m.q[m.ns][c] = (t[2] >= 'A' && t[2] <= 'P') ? t[2] - 'A' : -1; }
        }
        m.ns++; i += 6; if (s[i] == '_') ++i; else break;
    }
    return true;
}
int main(int argc, char **argv) {
    TM a, b; parse(argv[1], a); parse(argv[2], b); const char *map = argv[3]; long long N = atoll(argv[4]);
    const int SZ = 1 << 26; vector<unsigned char> ta(SZ, 0), tb(SZ, 0);
    long long pa = SZ / 2, pb = SZ / 2; int sa = 0, sb = 0, silent = 0, sprev = 0; int gadgetF = argc > 5 ? argv[5][0] - 'A' : -1; long long syncs = 0, stepsB = 0;
    long long lo = pa, hi = pa;
    for (long long n = 0; n < N; ++n) {
        sprev = sa; int c = ta[pa]; if (a.q[sa][c] < 0 && a.w[sa][c] < 0) { printf("M9 halts at step %lld state %c reading %d\n", n, 'A' + sa, c);
            int cb = tb[pb]; printf("M8 state %c reading %d (undefined=%d) steps %lld\n", 'A' + sb, cb, b.w[sb][cb] < 0, stepsB);
            long long s1 = 0, s2 = 0; for (long long i = 0; i < SZ; ++i) { s1 += ta[i]; s2 += tb[i]; } printf("sigma %lld %lld\n", s1, s2); return 0; }
        ta[pa] = a.w[sa][c]; int ns = a.q[sa][c]; pa += a.d[sa][c]; sa = ns;
        if (pa < lo) lo = pa; if (pa > hi) hi = pa;
        if (pa <= 1 || pa >= SZ - 2) { printf("tape overflow at %lld\n", n); return 0; }
        if (silent > 0) { --silent; continue; }
        if (gadgetF >= 0 && sprev == gadgetF && c == 0) silent = 2;
        {
            int cb = tb[pb]; if (b.w[sb][cb] < 0) { printf("M8 halts early at M9 step %lld\n", n); return 1; }
            tb[pb] = b.w[sb][cb]; int nb = b.q[sb][cb]; pb += b.d[sb][cb]; sb = nb; ++stepsB; ++syncs;
            if (map[sa] - 'A' != sb || pa != pb) { printf("MISMATCH at M9 step %lld: M9 %c@%lld M8 %c@%lld\n", n, 'A' + sa, pa, 'A' + sb, pb); return 1; }
            if ((syncs & 0xFFFFF) == 0) { for (long long i = lo; i <= hi; ++i) if (ta[i] != tb[i]) { printf("TAPE MISMATCH at step %lld cell %lld\n", n, i); return 1; } }
        }
    }
    for (long long i = lo; i <= hi; ++i) if (ta[i] != tb[i]) { printf("TAPE MISMATCH at end cell %lld\n", i); return 1; }
    printf("OK %lld M9 steps, %lld M8 steps, span %lld\n", N, stepsB, hi - lo + 1);
}
