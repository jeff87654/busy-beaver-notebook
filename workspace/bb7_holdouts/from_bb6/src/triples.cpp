// triples N < machines: run each from blank for N steps; for every defined transition (q,c)->(w,d,X) and next read c',
// record count and first time. Peek variant P(q,c,c') = (q,c)->(w,d,NEW), NEW = row X with slot c' := halt.
// It halts exactly at the first occurrence of the triple. Output: machine, then per triple "qc>c':count:first".
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
int nx[8][2], wr[8][2], dr[8][2], NS;
int main(int argc, char **argv) {
    long long N = atoll(argv[1]); long long SZ = 1LL << 26; std::vector<unsigned char> T(SZ, 0); char s[256];
    while (scanf("%255s", s) == 1) {
        int len = strlen(s), q = 0; for (int i = 0; i < len && q < 8; i += 7, ++q) for (int c = 0; c < 2; ++c) { const char *x = s + i + 3 * c;
            if (x[0] == '-' || x[2] == 'Z') nx[q][c] = -1; else { wr[q][c] = x[0] - '0'; dr[q][c] = x[1] == 'R' ? 1 : -1; nx[q][c] = x[2] - 'A'; } }
        NS = q; long long cnt[8][2][2] = {}, first[8][2][2]; for (int a = 0; a < 8; ++a) for (int b = 0; b < 2; ++b) first[a][b][0] = first[a][b][1] = -1;
        long long p = SZ / 2, lo = p, hi = p, t = 0; int st = 0, pq = -1, pc = -1; const char *status = "RUN";
        while (t < N) { int c = T[p];
            if (pq >= 0) { if (!cnt[pq][pc][c]++) first[pq][pc][c] = t; }
            if (nx[st][c] < 0) { status = "HALT"; break; }
            T[p] = wr[st][c]; p += dr[st][c]; pq = st; pc = c; st = nx[st][c]; ++t; if (p < lo) lo = p; if (p > hi) hi = p;
            if (p <= 1 || p >= SZ - 2) { status = "OOB"; break; } }
        printf("%s %s", s, status);
        for (int a = 0; a < NS; ++a) for (int b = 0; b < 2; ++b) if (nx[a][b] >= 0) for (int c = 0; c < 2; ++c)
            printf(" %c%d>%d:%lld:%lld", 'A' + a, b, c, cnt[a][b][c], first[a][b][c]);
        printf("\n"); fflush(stdout); for (long long z = lo; z <= hi; ++z) T[z] = 0;
    }
}
