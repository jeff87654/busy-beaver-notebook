// snap.c: run machine from word/head/state; at given step counts print compressed tape (runs of 10 compressed).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
    const char *m = argv[1]; const char *w = argv[2]; long long head = atoll(argv[3]); int q = argv[4][0]-'A';
    int ns = argc - 5; long long snaps[64]; for (int i = 0; i < ns; ++i) snaps[i] = atoll(argv[5+i]);
    int W[20], D[20], NX[20], DEF[20];
    for (int s = 0; s < 10; ++s) for (int c = 0; c < 2; ++c) { const char *x = m + 7*s + 3*c;
        if (x[0]=='-') { DEF[2*s+c]=0; continue; } DEF[2*s+c]=1; W[2*s+c]=x[0]-'0'; D[2*s+c]=x[1]=='R'?1:-1; NX[2*s+c]=x[2]-'A'; }
    long long L = 1LL<<26; unsigned char *t = calloc(L,1); long long off = L/4; long long len = strlen(w);
    for (long long i = 0; i < len; ++i) t[off+i] = w[i]-'0';
    long long h = off+head, lo = off, hi = off+len; int si = 0;
    for (long long st = 0; si < ns; ++st) {
        if (st == snaps[si]) {
            printf("== step %lld state %c head %lld\n", st, 'A'+q, h-off);
            long long i = lo; int col = 0;
            while (i <= hi) {
                if (i == h) printf("<H>");
                long long j = i; while (j+1 <= hi && t[j]==1 && t[j+1]==0 && !(j<=h && h<=j+1)) j += 2;
                long long k = (j-i)/2; if (k >= 3) { printf("(10)^%lld ", k); i = j; continue; }
                printf("%d", t[i]); i++;
            }
            printf("\n"); si++;
        }
        int c = t[h]; int kk = 2*q+c;
        if (!DEF[kk]) { printf("HALT %lld\n", st); return 0; }
        t[h] = W[kk]; h += D[kk]; q = NX[kk]; if (h<lo) lo=h; if (h>hi) hi=h;
    }
    return 0;
}
