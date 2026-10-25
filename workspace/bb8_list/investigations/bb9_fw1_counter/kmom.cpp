// kmom MACHINE SIDE STATE WORD MAXSTEPS [MAXLINES] [EVERY]
// Mirror if SIDE=L (as kview). Start: WORD on tape at 0..len-1, head at len (just right of it) in STATE.
// WORD '-' = blank start with head at 0 in state A. At each K-moment (state STATE reading 0 right of all 1s)
// print step, lo (leftmost 1 position), hi, and the run-length word (from lo). Prints only every EVERY-th moment
// unless the leftmost position changed.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
int W[16][2], D[16][2], NX[16][2];
static std::string rl(const std::string &w, size_t maxch) {
    std::string o; size_t i = 0;
    while (i < w.size() && o.size() < maxch) { size_t j = i; while (j < w.size() && w[j] == w[i]) ++j;
        size_t n = j - i; if (n >= 4) o += std::string(1, w[i]) + "^" + std::to_string(n) + " "; else o += w.substr(i, n) + " "; i = j; }
    if (i < w.size()) o += "...";
    return o;
}
int main(int argc, char **argv) {
    std::string m = argv[1]; char side = argv[2][0]; int Q = argv[3][0] - 'A'; std::string w0 = argv[4];
    long long maxs = atoll(argv[5]); long long maxl = argc > 6 ? atoll(argv[6]) : 100; long long every = argc > 7 ? atoll(argv[7]) : 1;
    int n = (int)(m.size() + 1) / 7;
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * q + 3 * c;
        if (x[0] == '-') { NX[q][c] = -1; continue; } W[q][c] = x[0] - '0'; D[q][c] = x[1] == 'R' ? 1 : -1; NX[q][c] = x[2] - 'A';
        if (side == 'L') D[q][c] = -D[q][c]; }
    long long size = 1 << 22, off = size / 2; std::vector<unsigned char> t(size, 0);
    long long pos = 0; int q = 0;
    if (w0 != "-") { for (size_t i = 0; i < w0.size(); ++i) t[off + i] = w0[i] == '1'; pos = w0.size(); q = Q; }
    long long lines = 0, km = 0, lastlo = 1LL << 60; long long vlo = 0, vhi = w0 == "-" ? 0 : (long long)w0.size();
    for (long long st = 0; st < maxs; ++st) {
        if (pos + off < 2 || pos + off + 2 >= size) { std::vector<unsigned char> nt(size * 2, 0); memcpy(nt.data() + size / 2, t.data(), size); off += size / 2; size *= 2; t.swap(nt); }
        unsigned char *T = t.data() + off; int c = T[pos];
        if (c == 0 && q == Q) {
            long long lo = vlo, hi = vhi; while (lo < hi && !T[lo]) ++lo; while (hi > lo && !T[hi]) --hi;
            if (pos > hi) { ++km;
                if (lo != lastlo || km % every == 0) { std::string w; for (long long i = lo; i <= hi; ++i) w += char('0' + T[i]);
                    printf("%lld lo=%lld hi=%lld %s\n", st, lo, hi, rl(w, 400).c_str()); lastlo = lo; if (++lines >= maxl) break; } }
        }
        if (NX[q][c] < 0) { printf("HALT %lld state %c read %d\n", st, 'A' + q, c); return 0; }
        T[pos] = W[q][c]; pos += D[q][c]; q = NX[q][c]; if (pos < vlo) vlo = pos; if (pos > vhi) vhi = pos;
    }
    printf("END\n");
}
