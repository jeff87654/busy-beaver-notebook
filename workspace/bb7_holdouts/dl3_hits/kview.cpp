// kview: literal run from the blank tape; at each end event in STATE on SIDE, parse the tape (far end -> head) as
// P u^(al d1+be) s ... u^(al a+be) s u^(alB b+beB) S and print when the digit list (excluding a,b) changes.
//  kview MACHINE SIDE STATE P u s al be alB beB S MAXSTEPS [MAXLINES=200] [PRINTALL=0]
// P/S '-' = empty. Unparsed events print "?" with run-length word (first time per 2^k occurrences).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
int W[16][2], D[16][2], NX[16][2];
static std::string rl(const std::string &w, size_t maxch = 300) {
    std::string o; size_t i = 0;
    while (i < w.size() && o.size() < maxch) { size_t j = i; while (j < w.size() && w[j] == w[i]) ++j;
        size_t n = j - i; if (n >= 4) o += std::string(1, w[i]) + "^" + std::to_string(n) + " "; else o += w.substr(i, n) + " "; i = j; }
    if (i < w.size()) o += "...";
    return o;
}
int main(int argc, char **argv) {
    std::string m = argv[1]; char side = argv[2][0]; int Q = argv[3][0] - 'A';
    std::string P = argv[4], u = argv[5], s = argv[6]; long long al = atoll(argv[7]), be = atoll(argv[8]), alB = atoll(argv[9]), beB = atoll(argv[10]);
    std::string S = argv[11]; if (P == "-") P = ""; if (S == "-") S = "";
    long long maxs = atoll(argv[12]); long long maxl = argc > 13 ? atoll(argv[13]) : 200; int pall = argc > 14 ? atoi(argv[14]) : 0;
    int n = (int)(m.size() + 1) / 7;
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * q + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') { NX[q][c] = -1; continue; } W[q][c] = x[0] - '0'; D[q][c] = x[1] == 'R' ? 1 : -1; NX[q][c] = x[2] - 'A'; }
    if (side == 'L') for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) D[q][c] = -D[q][c];   // mirror: template read on right
    long long size = 1 << 20, off = size / 2; std::vector<unsigned char> t(size, 0);
    long long pos = 0, lo = 1, hi = 0; int q = 0; long long lines = 0; std::string lastd = "#"; long long unp = 0;
    long long stopn = 0, nchg = 0;
    if (argc > 17) { std::string w = argv[15]; if (w == "-") w = ""; long long need = 2 * (long long)w.size() + 4096; while (size < need) size *= 2;
        t.assign(size, 0); off = size / 2; for (size_t z = 0; z < w.size(); ++z) { t[off + z] = w[z] == '1'; if (w[z] == '1') { if (lo > hi) lo = hi = (long long)z; else hi = (long long)z; } }
        pos = atoll(argv[16]); q = argv[17][0] - 'A'; if (argc > 18) stopn = atoll(argv[18]); }
    for (long long st = 0; st < maxs; ++st) {
        if (pos + off < 2 || pos + off + 2 >= size) { std::vector<unsigned char> nt(size * 2, 0); memcpy(nt.data() + size / 2, t.data(), size); off += size / 2; size *= 2; t.swap(nt); }
        unsigned char *T = t.data() + off; int c = T[pos];
        if (c == 0 && q == Q && lo <= hi) {
            while (lo <= hi && !T[hi]) --hi; while (lo <= hi && !T[lo]) ++lo;
            if (pos > hi) {
                std::string w; for (long long i = lo; i < pos; ++i) w += char('0' + T[i]);
                // parse
                bool ok = w.size() >= P.size() + S.size() && w.compare(0, P.size(), P) == 0 && w.compare(w.size() - S.size(), S.size(), S) == 0;
                std::vector<long long> runs;
                if (ok) { size_t i = P.size(), e = w.size() - S.size();
                    while (true) { long long k = 0; size_t i0 = i; while (i + u.size() <= e && w.compare(i, u.size(), u) == 0) { i += u.size(); ++k; }
                        if (i == e) { runs.push_back(k); break; }
                        bool fs = false;
                        for (long long kk = k; kk >= 0; --kk) { size_t j = i0 + kk * u.size(); if (j + s.size() <= e && w.compare(j, s.size(), s) == 0) { runs.push_back(kk); i = j + s.size(); fs = true; break; } }
                        if (!fs) { ok = false; break; } } }
                if (ok && runs.size() >= 2) {
                    long long bl = runs.back(); if ((bl - beB) % alB || bl < beB) ok = false;
                    for (size_t j = 0; j + 1 < runs.size(); ++j) if ((runs[j] - be) % al || runs[j] < be) ok = false;
                }
                if (!ok || runs.size() < 2) { ++unp; if ((unp & (unp - 1)) == 0) { printf("%lld ? %s\n", st, rl(w).c_str()); if (++lines >= maxl) break; } }
                else {
                    std::string ds; for (size_t j = 0; j + 2 < runs.size();) { long long v = (runs[j] - be) / al; size_t r = j; while (r + 2 < runs.size() && (runs[r] - be) / al == v) ++r;
                        ds += std::to_string(v); if (r - j > 1) ds += "^" + std::to_string(r - j); ds += ","; j = r; }
                    long long a = (runs[runs.size() - 2] - be) / al, b = (runs.back() - beB) / alB;
                    if (ds != lastd || pall) { printf("%lld K(%s; %lld; %lld) len=%zu\n", st, ds.c_str(), a, b, runs.size() - 2); lastd = ds; if (++lines >= maxl) break; if (stopn && ++nchg >= stopn) break; }
                }
            }
        }
        if (NX[q][c] < 0) { printf("HALT %lld state %c read %d\n", st, 'A' + q, c); return 0; }
        T[pos] = W[q][c]; if (W[q][c]) { if (lo > hi) lo = hi = pos; else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; } }
        pos += D[q][c]; q = NX[q][c];
    }
    printf("END\n");
}
