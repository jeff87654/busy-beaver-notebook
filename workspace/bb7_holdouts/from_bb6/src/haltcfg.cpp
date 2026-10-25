// haltcfg MACHINE MAXSTEPS < "W name tape pos state" lines -> "W name haltingtape pos state" (+ steps on stderr) ; NOHALT lines to stderr
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
int nx[8][2], wr[8][2], dr[8][2];
int main(int argc, char **argv) {
    const char *s = argv[1]; int len = strlen(s), q = 0;
    for (int i = 0; i < len; i += 7, ++q) for (int c = 0; c < 2; ++c) { const char *x = s + i + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') nx[q][c] = -1; else { wr[q][c] = x[0] - '0'; dr[q][c] = x[1] == 'R' ? 1 : -1; nx[q][c] = x[2] - 'A'; } }
    long long N = atoll(argv[2]); long long SZ = 1LL << 26; std::vector<unsigned char> T(SZ, 0);
    static char tape[1 << 20], name[256], st[8]; char cmd[8]; long long pos;
    while (scanf("%7s %255s %1048575s %lld %7s", cmd, name, tape, &pos, st) == 5) {
        long long L = strlen(tape), off = SZ / 2 - L / 2, p = off + pos, lo = off, hi = off + L - 1, t = 0; int qq = st[0] - 'A';
        for (long long i = 0; i < L; ++i) T[off + i] = tape[i] - '0';
        bool h = false;
        while (t < N) { int c = T[p]; if (nx[qq][c] < 0) { h = true; break; }
            T[p] = wr[qq][c]; p += dr[qq][c]; qq = nx[qq][c]; ++t; if (p < lo) lo = p; if (p > hi) hi = p; }
        if (h) { long long a = lo - 2, b = hi + 2; printf("W %s ", name); for (long long i = a; i <= b; ++i) putchar('0' + T[i]);
            printf(" %lld %c\n", p - a, 'A' + qq); fprintf(stderr, "%s halts after %lld at %c%d\n", name, t, 'A' + qq, T[p]); }
        else fprintf(stderr, "%s NOHALT %lld\n", name, t);
        for (long long i = lo; i <= hi; ++i) T[i] = 0;
    }
}
