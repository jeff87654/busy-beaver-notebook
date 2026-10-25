// lsim.cpp: independent literal TM simulator (verifier's own; not derived from igstage).
// stdin job: MACHINE STATE HEADOFS MAXSTEPS KMODE   then a line of bits (the word); head = word start + HEADOFS.
// Runs until halt / step limit.  KMODE>0: stop at the KMODE-th "K-moment" = state G reading 0 at a cell right of
// every 1, with the 5 cells to its left equal to 1,1,0,1,0 (i.e. ...1 1010 suffix), excluding step 0.
// Output: outcome, steps, state, symbol, slot-read counts for slots of states >= J, leftmost visited cell rel. to word
// start, and the final word (leftmost 1..rightmost 1) and head offset.
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
using namespace std;
int main() {
    char ms[512], st[8]; long long hofs, maxs; int kmode;
    while (scanf("%511s %7s %lld %lld %d", ms, st, &hofs, &maxs, &kmode) == 5) {
        string bits; cin >> bits;
        vector<long long> target; if (kmode < 0) { long long nt, v; scanf("%lld", &nt); for (long long j = 0; j < nt; ++j) { scanf("%lld", &v); target.push_back(v); } }
        long long kcount = 0;
        int ns = (strlen(ms) + 1) / 7;
        int W[32], Dd[32], N[32]; bool def[32];
        for (int q = 0; q < ns; ++q) for (int s = 0; s < 2; ++s) {
            const char *x = ms + 7 * q + 3 * s; int i = 2 * q + s;
            def[i] = x[0] != '-'; if (def[i]) { W[i] = x[0] - '0'; Dd[i] = x[1] == 'R' ? 1 : -1; N[i] = x[2] - 'A'; }
        }
        long long L = bits.size(), cap = 4 * L + (1 << 20);
        vector<unsigned char> t(cap, 0); long long off = cap / 4;
        for (long long i = 0; i < L; ++i) t[off + i] = bits[i] - '0';
        long long pos = off + hofs, lo = pos, r1 = off + L - 1; int q = st[0] - 'A';
        while (r1 >= 0 && !t[r1]) --r1;
        long long steps = 0, cnt[32] = {0}; int kseen = 0; const char *res = "T";
        while (true) {
            if (pos <= 1 || pos >= (long long)t.size() - 2) {
                long long n = t.size(); vector<unsigned char> nt(3 * n, 0);
                memcpy(&nt[n], &t[0], n); t.swap(nt); pos += n; lo += n; r1 += n; off += n;
            }
            int s = t[pos], i = 2 * q + s;
            if (kmode && q == 6 && s == 0 && pos > r1 && steps > 0 && t[pos-1]==0 && t[pos-2]==1 && t[pos-3]==0 && t[pos-4]==1 && t[pos-5]==1) {
                ++kcount;
                if (kmode > 0) { if (++kseen >= kmode) { res = "K"; break; } }
                else if (kmode == -2) {
                    // RSIG: tokens farthest-first contain 2 5 1^c (c>=6) 0 0 0 9 1^z (to the a-token)
                    vector<long long> tk; long long p = pos - 5;
                    while (p > 1 && t[p]) { long long mm = 0; --p; while (t[p] == 0 && t[p - 1] == 1) { ++mm; p -= 2; } tk.push_back(mm); }
                    // tk nearest-first: tk[0]=r, tk[1]=a, digits after
                    long long n = tk.size(); bool ok = false;
                    for (long long i = n - 1; i >= 3 && !ok; --i) {
                        if (tk[i] == 2 && tk[i - 1] == 5) {
                            long long j = i - 2, c = 0; while (j >= 0 && tk[j] == 1) { ++c; --j; }
                            if (c >= 6 && j >= 3 && tk[j] == 0 && tk[j - 1] == 0 && tk[j - 2] == 0 && tk[j - 3] == 9) {
                                bool allone = true; for (long long u = j - 4; u >= 2; --u) if (tk[u] != 1) allone = false;
                                ok = allone;
                            }
                        }
                    }
                    if (ok) { res = "K"; break; }
                }
                else {
                    // parse tokens nearest-first from pos-6 leftwards and compare with the target prefix
                    long long p = pos - 5; size_t j = 0; bool ok = true;
                    while (j < target.size()) {
                        if (!t[p]) { ok = false; break; }
                        long long mm = 0; --p;
                        while (t[p] == 0 && t[p - 1] == 1) { ++mm; p -= 2; }
                        if (mm != target[j]) { ok = false; break; }
                        ++j;
                    }
                    if (ok) { res = "K"; break; }
                }
            }
            cnt[i]++;
            if (!def[i]) { res = "H"; break; }
            if (steps >= maxs) { res = "T"; break; }
            t[pos] = W[i];
            if (W[i] && pos > r1) r1 = pos; else if (!W[i] && pos == r1) { while (r1 > 0 && !t[r1]) --r1; }
            pos += Dd[i]; q = N[i]; ++steps; if (pos < lo) lo = pos;
        }
        long long a = 0; while (a < (long long)t.size() && !t[a]) ++a;
        printf("%s %lld %c%d lo=%lld", res, steps, 'A' + q, t[pos], lo - off);
        printf(" cnt");
        for (int i = 18; i < 2 * ns; ++i) printf(" %c%d:%lld", 'A' + i / 2, i % 2, cnt[i]);
        long long ones = 0; for (long long j = a; j <= r1; ++j) ones += t[j];
        printf(" kmom=%lld", kcount); printf(" ones=%lld wordstart=%lld head=%lld\n", ones, a - off, pos - a);
        for (long long j = a; j <= r1; ++j) putchar('0' + t[j]);
        putchar('\n'); fflush(stdout);
    }
}
