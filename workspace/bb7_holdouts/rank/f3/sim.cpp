// sim MACHINE O Q MAXSTEPS MAXEV LASTRUN
// stdin: one start per line: "RUNS" = comma list of run lengths (x^n = n copies); tape = 1^r1 0 1^r2 0 ... 0 1^rk,
// head directly right of it (on a blank), in state Q (machine mirrored if O == L).
// Events: head in Q on a blank with nothing to the right.  An event is reported if its last run (cells between the last 0
// left of the head and the head) has length LASTRUN (-1 = all events).  Output per start: one line per reported event
// "E step gap runs" (gap = blanks between last 1 and head; runs as RLE "v^n" list) up to MAXEV, then "H step ones" /
// "T step" (step budget) / "X" (MAXEV reached), then a line "." .
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <cstdint>
using namespace std;
int W[8][2], D[8][2], NX[8][2];
int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage\n"); return 2; }
    const char *M = argv[1]; bool mir = argv[2][0] == 'L'; int Q = argv[3][0] - 'A';
    long long maxs = atoll(argv[4]), maxev = atoll(argv[5]); long long fgap = -1, lastrun = -1; sscanf(argv[6], "%lld:%lld", &fgap, &lastrun);
    int ns = 0;
    for (const char *p = M; *p;) {
        for (int c = 0; c < 2; ++c) {
            if (p[0] == '-') { NX[ns][c] = -1; W[ns][c] = 0; D[ns][c] = 0; }
            else { W[ns][c] = p[0] - '0'; D[ns][c] = (p[1] == 'R') ? 1 : -1; if (mir) D[ns][c] = -D[ns][c]; NX[ns][c] = p[2] - 'A'; }
            p += 3;
        }
        ++ns; if (*p == '_') ++p;
    }
    static char line[1 << 22];
    vector<uint8_t> T;
    while (fgets(line, sizeof line, stdin)) {
        vector<long long> runs;
        char *x = line; if (!strncmp(line, "BLANK", 5)) x = line + 5;
        while (*x && *x != '\n' && *x != '\r') {
            long long v = strtoll(x, &x, 10), n = 1;
            if (*x == '^') { ++x; n = strtoll(x, &x, 10); }
            for (long long i = 0; i < n; ++i) runs.push_back(v);
            if (*x == ',') ++x;
        }
        string w;
        for (size_t i = 0; i < runs.size(); ++i) { if (i) w += '0'; w.append(runs[i], '1'); }
        long long SZ = 4 * (long long)w.size() + (maxs < (1LL<<27) ? 2*maxs : (1LL<<28)) + 1000;
        if (SZ > (1LL << 31)) SZ = 1LL << 31;
        T.assign(SZ, 0);
        long long base = SZ / 2;
        // if machine moves mostly right (mirrored or not), we place tape in middle
        long long p = base + (long long)w.size();
        for (size_t i = 0; i < w.size(); ++i) T[base + i] = w[i] == '1';
        long long mn = base, mx = base + (long long)w.size() - 1;
        int q = Q; long long nev = 0; bool done = false;
        if (!strncmp(line, "BLANK", 5)) { q = 0; T.assign(SZ, 0); p = base; mn = base; mx = base - 1; }
        for (long long st = 0; st < maxs; ++st) {
            if (p <= 1 || p >= SZ - 2) { printf("TAPE %lld\n", st); done = true; break; }
            int c = T[p];
            if (NX[q][c] < 0) {
                long long ones = 0; for (long long i = mn; i <= mx; ++i) ones += T[i];
                printf("H %lld %lld\n", st, ones); done = true; break;
            }
            T[p] = W[q][c];
            if (W[q][c]) { if (p < mn) mn = p; if (p > mx) mx = p; }
            p += D[q][c]; q = NX[q][c];
            if (q != Q || T[p]) continue;
            while (mx > mn && !T[mx]) --mx;
            if (mx > p) continue;
            while (mn < mx && !T[mn]) ++mn;
            long long hi = p - 1; while (hi >= mn && !T[hi]) --hi;
            if (fgap >= 0 && p - 1 - hi != fgap) continue;
            long long j = hi, lr = 0;
            while (j >= mn && T[j]) { --j; ++lr; }
            if (lastrun >= 0 && lr != lastrun) continue;
            string o; long long i = mn;
            vector<long long> rr; long long cur = 0;
            for (long long k = mn; k <= hi; ++k) { if (T[k]) ++cur; else { rr.push_back(cur); cur = 0; } }
            rr.push_back(cur);
            for (size_t a = 0; a < rr.size();) {
                size_t b = a; while (b < rr.size() && rr[b] == rr[a]) ++b;
                if (a) o += ',';
                o += to_string(rr[a]); if (b - a > 1) o += "^" + to_string(b - a);
                a = b;
                if (o.size() > 3000) { o += ",..."; break; }
            }
            (void)i;
            printf("E %lld %lld %s\n", st + 1, p - 1 - hi, o.c_str());
            if (++nev >= maxev) { printf("X\n"); done = true; break; }
        }
        if (!done) printf("T %lld\n", maxs);
        printf(".\n"); fflush(stdout);
    }
    return 0;
}
