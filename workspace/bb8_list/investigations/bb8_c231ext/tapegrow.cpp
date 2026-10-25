// tapegrow MACHINE MAXSTEPS < "a Z n": run from K(a;0^n); report at checkpoints: step, tape span, ones, head pos rel, state
#include <cstdio>
#include <cstdlib>
#include <cstring>
typedef long long ll;
int W[16][2], Dm[16][2], N[16][2];
int main(int argc, char **argv) {
    const char *M = argv[1]; ll maxs = atoll(argv[2]);
    int ns = (strlen(M) + 1) / 7;
    for (int q = 0; q < ns; ++q) for (int b = 0; b < 2; ++b) { const char *p = M + q * 7 + b * 3;
        if (p[0] == '-' || p[2] == '-') { N[q][b] = -1; continue; }
        W[q][b] = p[0] - '0'; Dm[q][b] = p[1] == 'R' ? 1 : -1; N[q][b] = p[2] - 'A'; }
    ll a, n; char z[8]; scanf("%lld %7s %lld", &a, z, &n);
    ll SZ = 4 * maxs + 100000; if (SZ > (1LL << 31)) SZ = 1LL << 31;
    unsigned char *t = (unsigned char *)calloc(SZ, 1);
    ll p = SZ / 2, c = p, base = p;
    t[c++] = 0; t[c++] = 1; t[c++] = 0; t[c++] = 0;
    for (ll i = 0; i < a; ++i) { t[c++] = 1; t[c++] = 1; } t[c++] = 0; t[c++] = 0;
    for (ll i = 0; i < n; ++i) { t[c++] = 0; t[c++] = 0; } t[c++] = 1;
    ll lo = p, hi = c; int q = 4; ll ck = 100000; ll hstep = -1;
    for (ll st = 0; st < maxs; ++st) {
        if (p <= 1 || p >= SZ - 2) { printf("TAPE %lld\n", st); return 0; }
        int s = t[p];
        if (N[q][s] < 0) { printf("H %lld\n", st); return 0; }
        t[p] = W[q][s]; p += Dm[q][s]; q = N[q][s]; if (p < lo) lo = p; if (p > hi) hi = p;
        if (q == 7 && hstep < 0) hstep = st;
        if (st + 1 == ck) { ll ones = 0; for (ll i = lo; i <= hi; ++i) ones += t[i];
            printf("%lld span=[%lld,%lld] ones=%lld head=%lld state=%c hfirst=%lld\n", st + 1, lo - base, hi - base, ones, p - base, 'A' + q, hstep); ck *= 10; }
    }
    return 0;
}
