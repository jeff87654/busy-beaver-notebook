// trace2: run a machine from the blank tape and print every configuration that parses as a family configuration
// K(ds; a; b) of a dlscan2 template (head in state Q on a blank at the tape end, nothing beyond it).
//   trace2 MACHINE O Q P u s alpha beta alphaB betaB S STEPS [MAXPRINT=60]
// Build: g++ -O2 -std=c++17 -static -I . -o trace2.exe trace2.cpp   (includes dlscan2_nomain.inc)
#include "dlscan2_nomain.inc"
int main(int argc, char **argv) {
    if (argc < 13) { fprintf(stderr, "usage: trace2 MACHINE O Q P u s alpha beta alphaB betaB S STEPS [MAXPRINT]\n"); return 2; }
    TM m; if (!parse(argv[1], m)) return 2;
    if (argv[2][0] == 'L') m = mirrored(m);
    Tmpl t; t.q = argv[3][0] - 'A'; t.P = strcmp(argv[4], "-") ? argv[4] : ""; t.u = argv[5]; t.s = argv[6];
    t.al = atoll(argv[7]); t.be = atoll(argv[8]); t.alB = atoll(argv[9]); t.beB = atoll(argv[10]); t.S = strcmp(argv[11], "-") ? argv[11] : "";
    long long S = atoll(argv[12]); int maxp = argc > 13 ? atoi(argv[13]) : 60;
    Prober2 pr; long long N = 1 << 24; pr.tape.assign(N, 0);
    long long p = N / 2, mn = p, mx = p - 1; int q = 0, printed = 0;
    for (long long st = 0; st < S; ++st) {
        int c = pr.tape[p];
        if (m.nx[q][c] < 0) { printf("HALT at step %lld (state %c reading %d)\n", st, 'A' + q, c); return 0; }
        int wr = m.w[q][c]; pr.tape[p] = (uint8_t)wr;
        if (wr) { if (mn > mx) mn = mx = p; else { if (p < mn) mn = p; if (p > mx) mx = p; } }
        p += m.d[q][c]; q = m.nx[q][c];
        if (p < 2 || p > N - 3) { printf("tape exhausted at %lld\n", st); return 0; }
        if (q != t.q || pr.tape[p] != 0) continue;
        while (mx > p && !pr.tape[mx]) --mx;
        if (mx > p) continue;
        while (mn < p && !pr.tape[mn]) ++mn;
        long long lo = mn < p ? mn : p;
        P2 got;
        if (!pr.parse(t, p, lo, got)) continue;
        printf("step %lld: K(", st + 1);
        for (size_t i = 0; i < got.ds.size(); ++i) printf("%s%lld", i ? "," : "", got.ds[i]);
        printf("; %lld; %lld)\n", got.a, got.b);
        if (++printed >= maxp) return 0;
    }
    printf("END after %lld steps\n", S);
}
