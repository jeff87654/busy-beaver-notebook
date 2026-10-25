// sweeps MACHINE MAXSTEPS MAXEV [mode]  < "a Z n" : print the tape (RLE of right part, digit-ish) at each moment where
// state==E, head on 0 and all cells left of the head are blank, after state H was first visited (or all if mode=all).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
typedef long long ll;
int W[16][2], Dm[16][2], N[16][2];
static unsigned char *tape; static ll SZ;
int main(int argc, char **argv) {
    const char *M = argv[1]; ll maxs = atoll(argv[2]); ll maxev = atoll(argv[3]); bool all = argc > 4;
    int ns = (strlen(M) + 1) / 7;
    for (int q = 0; q < ns; ++q) for (int b = 0; b < 2; ++b) { const char *p = M + q * 7 + b * 3;
        if (p[0] == '-' || p[2] == '-') { N[q][b] = -1; continue; }
        W[q][b] = p[0] - '0'; Dm[q][b] = p[1] == 'R' ? 1 : -1; N[q][b] = p[2] - 'A'; }
    ll a, n; char z[8]; if (scanf("%lld %7s %lld", &a, z, &n) != 3) return 2;
    SZ = 1LL << 22; while (SZ < 2 * maxs + 4096 && SZ < (1LL << 30)) SZ <<= 1;
    tape = (unsigned char *)calloc(SZ, 1);
    ll p = SZ / 2, c = p;
    tape[c++] = 0; tape[c++] = 1; tape[c++] = 0; tape[c++] = 0;
    for (ll i = 0; i < a; ++i) { tape[c++] = 1; tape[c++] = 1; } tape[c++] = 0; tape[c++] = 0;
    for (ll i = 0; i < n; ++i) { tape[c++] = 0; tape[c++] = 0; }
    tape[c++] = 1;
    ll mn = p, mx = c - 1; int q = 4; ll ev = 0; bool hs = all;
    for (ll st = 0; st < maxs; ++st) {
        if (p <= 2 || p >= SZ - 3) { printf("END %lld tape\n", st); return 0; }
        int s = tape[p];
        if (N[q][s] < 0) { ll ones = 0; for (ll i = mn; i <= mx; ++i) ones += tape[i]; printf("H %lld ones=%lld %c%d\n", st, ones, 'A' + q, s); return 0; }
        tape[p] = W[q][s]; if (W[q][s]) { if (p < mn) mn = p; if (p > mx) mx = p; }
        p += Dm[q][s]; q = N[q][s]; if (q == 7) hs = true;
        if (!hs || q != 4 || tape[p] != 0 || p > mn) continue;
        while (mn < p && !tape[mn]) ++mn;
        if (mn < p) continue;
        while (mx > p && !tape[mx]) --mx;
        printf("S %lld |", st + 1);
        ll i = p + 1; int cnt = 0;
        while (i <= mx) { ll j = i; while (j <= mx && tape[j] == tape[i]) ++j;
            if (cnt < 70) { if (j - i > 1) printf(" %d^%lld", tape[i], j - i); else printf(" %d", tape[i]); }
            ++cnt; i = j; }
        if (cnt >= 70) printf(" ...(%d runs)", cnt);
        printf("\n"); fflush(stdout);
        if (++ev >= maxev) { printf("END %lld maxev\n", st + 1); return 0; }
    }
    printf("END %lld steps\n", maxs);
}
