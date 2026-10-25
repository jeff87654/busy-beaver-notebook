// gfollow MACHINE MAXSTEPS MAXEV MODE < "L0 L1 L2 ... Lk"   (block lengths in ones; the a-block is L0; digit d = 2d)
// tape: 0^inf E>0 1 00 1^L0 00 1^L1 00 ... 1^Lk 00 1 0^inf.
// Generalised K-moment: state E, head on 0, right part = 1 00 (1^L 00)* 1 0^inf, left part arbitrary.
// MODE "chg": print when (#blocks, odd-block positions, left) changes; "all": every moment; "odd": when the set of odd blocks changes.
// Output: G step left=.. nb=.. odd=[i:L,...] head=L0,L1,.. (first 10 blocks, with blocks written as L) ; H step ones ; END
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
typedef long long ll;
int W[16][2], Dm[16][2], N[16][2];
static unsigned char *tape; static ll SZ;
std::string rle(ll lo, ll hi) {
    std::string o; ll i = lo; int cnt = 0;
    while (i < hi) { ll j = i; while (j < hi && tape[j] == tape[i]) ++j;
        char b[32]; if (j - i > 1) sprintf(b, "%d^%lld ", tape[i], j - i); else sprintf(b, "%d ", tape[i]);
        o += b; i = j; if (++cnt > 24) { o += "..."; break; } }
    return o;
}
int main(int argc, char **argv) {
    const char *M = argv[1]; ll maxs = atoll(argv[2]); ll maxev = atoll(argv[3]); std::string mode = argc > 4 ? argv[4] : "chg";
    int ns = (strlen(M) + 1) / 7;
    for (int q = 0; q < ns; ++q) for (int b = 0; b < 2; ++b) { const char *p = M + q * 7 + b * 3;
        if (p[0] == '-' || p[2] == '-') { N[q][b] = -1; continue; }
        W[q][b] = p[0] - '0'; Dm[q][b] = p[1] == 'R' ? 1 : -1; N[q][b] = p[2] - 'A'; }
    std::vector<ll> L; ll x; while (scanf("%lld", &x) == 1) L.push_back(x);
    SZ = 1LL << 22; while (SZ < 2 * maxs + 4096 && SZ < (1LL << 31)) SZ <<= 1;
    tape = (unsigned char *)calloc(SZ, 1);
    ll p = SZ / 2, c = p;
    tape[c++] = 0; tape[c++] = 1; tape[c++] = 0; tape[c++] = 0;
    for (ll l : L) { for (ll i = 0; i < l; ++i) tape[c++] = 1; tape[c++] = 0; tape[c++] = 0; }
    tape[c++] = 1;
    ll mn = p, mx = c - 1; int q = 4; ll ev = 0; std::string last = "#";
    for (ll st = 0; st < maxs; ++st) {
        if (p <= 2 || p >= SZ - 3) { printf("END %lld tape\n", st); return 0; }
        int s = tape[p];
        if (N[q][s] < 0) { ll ones = 0; for (ll i = mn; i <= mx; ++i) ones += tape[i]; printf("H %lld ones=%lld %c%d\n", st, ones, 'A' + q, s); return 0; }
        tape[p] = W[q][s]; if (W[q][s]) { if (p < mn) mn = p; if (p > mx) mx = p; }
        p += Dm[q][s]; q = N[q][s];
        if (q != 4 || tape[p] != 0 || tape[p + 1] != 1 || tape[p + 2] != 0 || tape[p + 3] != 0) continue;
        while (mx > p && !tape[mx]) --mx;
        if (tape[mx - 1] != 0 || tape[mx - 2] != 0) continue;
        ll i = p + 4; std::vector<ll> B; bool ok = true;
        while (i < mx) { ll j = i; while (j < mx && tape[j] == 1) ++j;
            if (j + 1 > mx || tape[j] != 0 || tape[j + 1] != 0) { ok = false; break; }
            B.push_back(j - i); i = j + 2; }
        if (!ok || i != mx) continue;
        while (mn < p && !tape[mn]) ++mn;
        std::string left = mn < p ? rle(mn, p) : "-";
        std::string odd;
        for (size_t k = 0; k < B.size(); ++k) if (B[k] & 1) { odd += std::to_string(k) + ":" + std::to_string(B[k]) + " "; }
        std::string key = mode == "odd" ? odd + "|" + left : std::to_string(B.size()) + "|" + odd + "|" + left;
        if (mode == "all" || key != last) {
            printf("G %lld left=%s nb=%zu odd=[%s] blocks=", st + 1, left.c_str(), B.size(), odd.c_str());
            for (size_t k = 0; k < B.size();) { size_t j = k; while (j < B.size() && B[j] == B[k]) ++j;
                if (k > 14) { printf(",.."); break; }
                if (j - k > 1) printf("%s%lld^%zu", k ? "," : "", B[k], j - k); else printf("%s%lld", k ? "," : "", B[k]); k = j; }
            printf("\n"); fflush(stdout); last = key;
            if (++ev >= maxev) { printf("END %lld maxev\n", st + 1); return 0; }
        }
    }
    printf("END %lld steps\n", maxs);
}
