// sim.c: literal run of a 10-state machine from a word/head/state; prints tape extent and position snapshots.
// usage: sim MACHINE WORD HEAD STATE STEPS SNAP
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
    const char *m = argv[1]; const char *w = argv[2]; long long head = atoll(argv[3]); int q = argv[4][0]-'A';
    long long N = atoll(argv[5]), SNAP = atoll(argv[6]);
    int W[20], D[20], NX[20], DEF[20]; int n = (strlen(m)+1)/7;
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { const char *x = m + 7*s + 3*c;
        if (x[0]=='-') { DEF[2*s+c]=0; continue; } DEF[2*s+c]=1; W[2*s+c]=x[0]-'0'; D[2*s+c]=x[1]=='R'?1:-1; NX[2*s+c]=x[2]-'A'; }
    long long L = 1LL<<27; unsigned char *t = calloc(L,1); long long off = L/2; long long len = strlen(w);
    for (long long i = 0; i < len; ++i) t[off+i] = w[i]-'0';
    long long h = off+head, lo = off, hi = off+len-1, minh = h, maxh = h;
    for (long long st = 0; st < N; ++st) {
        if (h <= 0 || h >= L-1) { printf("TAPE %lld\n", st); return 0; }
        int c = t[h]; int k = 2*q+c;
        if (!DEF[k]) { printf("HALT %lld %c%d\n", st, 'A'+q, c); return 0; }
        t[h] = W[k]; h += D[k]; q = NX[k];
        if (h < minh) minh = h; if (h > maxh) maxh = h;
        if (SNAP && st % SNAP == 0) printf("%lld pos %lld range [%lld,%lld] state %c\n", st, h-off, minh-off, maxh-off, 'A'+q);
    }
    printf("END pos %lld range [%lld,%lld] wordlen %lld\n", h-off, minh-off, maxh-off, len);
    return 0;
}
