// traj: follow the REAL run from the blank tape; at every G right-end event parse the n-list and check it equals the
// predicted successor (R1 / R23) of the previous family configuration. Reports the first family configuration, every
// parse failure after it, every mismatch, and a summary.   traj MAXSTEPS
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
using namespace std;
int W[16][2], D[16][2], NX[16][2];
typedef vector<long long> VL;
// prediction on raw units (see verify_rules.py); returns false if no family successor (exhaustion / halt)
bool predict(const VL &ns, VL &out) {
    out = ns; int k = ns.size(); long long b = ns[k - 1]; int nd = k - 1;
    auto iszero = [&](int i) { return ns[i] == ((i == 0 && ns[0] % 2 == 0) ? 0 : 1); };
    if (nd >= 1 && !iszero(nd - 1)) { out[nd - 1] -= 2; out[k - 1] = b + 4; return true; }
    int j = -1; for (int i = nd - 1; i >= 0; --i) if (!iszero(i)) { j = i; break; }
    if (j < 0) return false;
    out[j] -= 2; out[j + 1] = b + 4; out[k - 1] = 1; return true;
}
int main(int argc, char **argv) {
    string m = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC";
    long long maxs = atoll(argv[1]);
    int n = (m.size() + 1) / 7;
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) {
        const char *x = m.c_str() + 7 * q + 3 * c;
        if (x[0] == '-') { NX[q][c] = -1; continue; }
        W[q][c] = x[0] - '0'; D[q][c] = x[1] == 'R' ? 1 : -1; NX[q][c] = x[2] - 'A';
    }
    long long size = 1 << 24; vector<unsigned char> t(size, 0);
    long long pos = size / 2, lo = pos, hi = pos; int q = 0; long long steps = 0;
    bool have = false; VL prev; long long nfam = 0, nmatch = 0, nbad = 0, nfail = 0, maxb = 0;
    while (steps < maxs) {
        int c = t[pos];
        if (NX[q][c] < 0) { printf("HALT at %lld\n", steps); break; }
        t[pos] = W[q][c]; pos += D[q][c]; q = NX[q][c]; ++steps;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (pos <= 1 || pos >= size - 2) { fprintf(stderr, "tape overflow\n"); return 1; }
        if (q == 6 && t[pos] == 0) {
            bool rend = true; for (long long i = pos + 1; i <= hi; ++i) if (t[i]) { rend = false; break; }
            if (!rend) continue;
            long long L = lo; while (L < pos && !t[L]) ++L;
            bool ok = true; long long i = L; VL got;
            if (i >= pos || t[i] != 1) ok = false; else ++i;
            while (ok && i < pos) { long long k = 0; while (i + 1 < pos && t[i] == 1 && t[i + 1] == 0) { k++; i += 2; } if (i < pos && t[i] == 1) { got.push_back(k); ++i; } else ok = false; }
            if (!ok) { if (have) { ++nfail; if (nfail <= 5) printf("PARSEFAIL after family start at step %lld\n", steps); } continue; }
            ++nfam;
            if (!have) {
                printf("first family configuration at step %lld: %zu entries:", steps, got.size());
                for (auto x : got) printf(" %lld", x); printf("\n"); have = true; prev = got; continue;
            }
            VL pr; bool okp = predict(prev, pr);
            if (okp && pr == got) ++nmatch;
            else { ++nbad; if (nbad <= 10) { printf("MISMATCH at %lld: got", steps); for (auto x : got) printf(" %lld", x); printf("\n"); } }
            if (got.back() > maxb) maxb = got.back();
            prev = got;
        }
    }
    printf("steps %lld family events %lld matches %lld mismatches %lld parse failures after start %lld max acc units %lld\n", steps, nfam, nmatch, nbad, nfail, maxb);
    printf("last config:"); for (auto x : prev) printf(" %lld", x); printf("\n");
    return 0;
}
