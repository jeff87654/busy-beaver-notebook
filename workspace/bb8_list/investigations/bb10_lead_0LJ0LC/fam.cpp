// fam: batch literal simulator for the n-list family of
//   1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC  (or argv[1])
// Config N(n_1..n_k) = 0^inf 1 ((10)^n_1 1) ... ((10)^n_k 1) G> 0^inf.
// stdin lines: "MAXSTEPS NEV n_1 ... n_k"; for each line prints the first NEV events (head on the blank right of all
// 1s in state G), each as "EV steps k | n_1 .. n_k" (raw units), "PARSEFAIL steps <first 300 cells>", "HALT steps
// state read ones", or "TIMEOUT steps". Every parse failure is printed (fail loudly).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <sstream>
#include <iostream>
using namespace std;
int W[16][2], D[16][2], NX[16][2];
int main(int argc, char **argv) {
    string m = argc > 1 ? argv[1] : "1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC";
    int n = (m.size() + 1) / 7;
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) {
        const char *x = m.c_str() + 7 * q + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') { NX[q][c] = -1; continue; }
        W[q][c] = x[0] - '0'; D[q][c] = x[1] == 'R' ? 1 : -1; NX[q][c] = x[2] - 'A';
    }
    string line;
    vector<unsigned char> t;
    while (getline(cin, line)) {
        istringstream is(line);
        long long maxs, nev; if (!(is >> maxs >> nev)) continue;
        vector<long long> ns; long long v; while (is >> v) ns.push_back(v);
        string w = "1"; for (auto x : ns) { for (long long i = 0; i < x; ++i) w += "10"; w += "1"; }
        long long size = 1 << 16; while (size < (long long)w.size() * 4 + 65536) size *= 2;
        t.assign(size, 0);
        long long off = size / 4;
        for (size_t i = 0; i < w.size(); ++i) t[off + i] = w[i] == '1';
        long long pos = off + w.size(), lo = off, hi = pos; int q = 6;
        long long steps = 0, ev = 0; bool done = false;
        string out;
        while (steps < maxs) {
            int c = t[pos];
            if (NX[q][c] < 0) {
                long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += t[i];
                char buf[200]; snprintf(buf, 200, "HALT %lld %c %d %lld", steps, 'A' + q, c, ones); out += buf; done = true; break;
            }
            t[pos] = W[q][c]; pos += D[q][c]; q = NX[q][c]; ++steps;
            if (pos < lo) lo = pos; if (pos > hi) hi = pos;
            if (pos <= 1 || pos >= size - 2) {
                vector<unsigned char> u(2 * size, 0);
                memcpy(u.data() + size / 2, t.data(), size);
                pos += size / 2; lo += size / 2; hi += size / 2; t.swap(u); size *= 2;
            }
            if (nev > 0 && q == 6 && t[pos] == 0) {
                bool rend = true; for (long long i = pos + 1; i <= hi; ++i) if (t[i]) { rend = false; break; }
                if (!rend) continue;
                long long L = lo; while (L < pos && !t[L]) ++L;
                bool ok = true; long long i = L; vector<long long> got;
                if (i >= pos || t[i] != 1) ok = false; else ++i;
                while (ok && i < pos) { long long k = 0; while (i + 1 < pos && t[i] == 1 && t[i + 1] == 0) { k++; i += 2; } if (i < pos && t[i] == 1) { got.push_back(k); ++i; } else ok = false; }
                char buf[100];
                if (ok) {
                    snprintf(buf, 100, "EV %lld %zu |", steps, got.size()); out += buf;
                    for (auto x : got) { snprintf(buf, 100, " %lld", x); out += buf; }
                } else {
                    snprintf(buf, 100, "PARSEFAIL %lld ", steps); out += buf;
                    for (long long j = L; j < pos && j < L + 120; ++j) out += char('0' + t[j]);
                }
                if (++ev >= nev) { done = true; break; }
                out += " ;; ";
            }
        }
        if (!done) { char buf[100]; snprintf(buf, 100, "TIMEOUT %lld", steps); out += buf; }
        printf("%s\n", out.c_str()); fflush(stdout);
    }
    return 0;
}
