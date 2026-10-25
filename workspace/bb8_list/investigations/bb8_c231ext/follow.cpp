// follow: literal run of an (extended) champ_231 machine from K(a; ds) with blank left.
//   follow MACHINE MAXSTEPS MAXEV < "a d1,d2,...|-"   (or  "a Z n" for n zero digits)
// Prints events:
//   K step left=<rle of left part> a=<a> n=<#digits> ds=<first 8>,..  (on every K-moment whose (left, n) differs from the previous,
//      plus every K-moment where left is nonblank and changes)
//   H step ones state sym   (halt)
//   END step reason
// K-moment: state E, head on 0, right part = 1 00 (11)^a 00 [(11)^d 00]* 1 0^inf. Left part arbitrary (reported RLE, max 60 chars).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
typedef long long ll;
int W[16][2], Dm[16][2], N[16][2]; int ns;
static unsigned char *tape; static ll SZ;
std::string rle(ll lo, ll hi) { // [lo,hi)
    std::string o; ll i = lo; int cnt = 0;
    while (i < hi) { ll j = i; while (j < hi && tape[j] == tape[i]) ++j;
        char b[32]; if (j - i > 1) sprintf(b, "%d^%lld ", tape[i], j - i); else sprintf(b, "%d ", tape[i]);
        o += b; i = j; if (++cnt > 40) { o += "..."; break; } }
    return o;
}
int main(int argc, char **argv) {
    const char *M = argv[1]; ll maxs = atoll(argv[2]); ll maxev = atoll(argv[3]); bool firstmode = argc > 4 && !strcmp(argv[4], "first"); bool allmode = argc > 4 && !strcmp(argv[4], "all"); bool hseen = false; ll hent = 0;
    ns = (strlen(M) + 1) / 7;
    for (int q = 0; q < ns; ++q) for (int b = 0; b < 2; ++b) { const char *p = M + q * 7 + b * 3;
        if (p[0] == '-' || p[2] == '-' || p[2] == 'Z') { N[q][b] = -1; continue; }
        W[q][b] = p[0] - '0'; Dm[q][b] = p[1] == 'R' ? 1 : -1; N[q][b] = p[2] - 'A'; }
    ll a; char buf[1 << 16]; if (scanf("%lld %65535s", &a, buf) != 2) return 2;
    std::vector<ll> ds;
    if (buf[0] == 'Z') { ll n; scanf("%lld", &n); ds.assign(n, 0); }
    else if (strcmp(buf, "-")) { char *x = buf; while (*x) { ds.push_back(strtoll(x, &x, 10)); if (*x == ',') ++x; } }
    SZ = 1LL << 22; while (SZ < 2 * maxs + 4096 && SZ < (1LL << 30)) SZ <<= 1; tape = (unsigned char *)calloc(SZ, 1);
    ll p = SZ / 2; ll c = p;
    tape[c++] = 0; tape[c++] = 1; tape[c++] = 0; tape[c++] = 0;
    for (ll i = 0; i < a; ++i) { tape[c++] = 1; tape[c++] = 1; } tape[c++] = 0; tape[c++] = 0;
    for (ll d : ds) { for (ll i = 0; i < d; ++i) { tape[c++] = 1; tape[c++] = 1; } tape[c++] = 0; tape[c++] = 0; }
    tape[c++] = 1;
    ll mn = p, mx = c - 1; int q = 4; ll ev = 0; ll lastn = -2; std::string lastleft = "#";
    for (ll st = 0; st < maxs; ++st) {
        if (p <= 2 || p >= SZ - 3) { printf("END %lld tape\n", st); return 0; }
        int s = tape[p];
        if (N[q][s] < 0) { ll ones = 0; for (ll i = mn; i <= mx; ++i) ones += tape[i]; printf("H %lld %lld %c%d\n", st, ones, 'A' + q, s); return 0; }
        tape[p] = W[q][s]; if (W[q][s]) { if (p < mn) mn = p; if (p > mx) mx = p; }
        int oq = q; p += Dm[q][s]; q = N[q][s]; if (q == 7) { hseen = true; if (oq != 7) ++hent; }
        if (q != 4 || tape[p] != 0 || tape[p + 1] != 1 || tape[p + 2] != 0 || tape[p + 3] != 0) continue;
        while (mx > p && !tape[mx]) --mx;
        if (tape[mx - 1] != 0 || tape[mx - 2] != 0) continue;
        // parse
        ll i = p + 4; ll aa = 0; while (i + 1 < mx && tape[i] == 1 && tape[i + 1] == 1) { aa++; i += 2; }
        if (tape[i] != 0 || tape[i + 1] != 0) continue; i += 2;
        std::vector<ll> d; bool ok = true;
        while (i < mx) { ll v = 0; while (i + 1 < mx && tape[i] == 1 && tape[i + 1] == 1) { v++; i += 2; }
            if (i + 1 >= mx + 1 || tape[i] != 0 || tape[i + 1] != 0) { ok = false; break; } i += 2; d.push_back(v); }
        if (!ok || i != mx) continue;
        while (mn < p && !tape[mn]) ++mn;
        std::string left = mn < p ? rle(mn, p) : "-";
        if (firstmode || allmode) { if (!hseen) continue;
            printf("K %lld hent=%lld left=%s a=%lld n=%zu ds=", st + 1, hent, left.c_str(), aa, d.size());
            for (size_t k = 0; k < d.size();) { size_t j = k; while (j < d.size() && d[j] == d[k]) ++j;
                if (j - k > 1) printf("%s%lld^%zu", k ? "," : "", d[k], j - k); else printf("%s%lld", k ? "," : "", d[k]); k = j; }
            printf("\n"); return 0; }
        if ((ll)d.size() != lastn || left != lastleft) {
            printf("K %lld left=%s a=%lld n=%zu ds=", st + 1, left.c_str(), aa, d.size());
            for (size_t k = 0; k < d.size() && k < 8; ++k) printf("%s%lld", k ? "," : "", d[k]);
            if (d.size() > 8) printf(",..");
            printf("\n"); fflush(stdout);
            lastn = d.size(); lastleft = left;
            if (++ev >= maxev) { printf("END %lld maxev\n", st + 1); return 0; }
        }
    }
    printf("END %lld steps\n", maxs);
}
