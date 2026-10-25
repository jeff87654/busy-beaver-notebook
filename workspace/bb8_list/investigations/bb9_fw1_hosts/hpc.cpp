// hpc: host probe CHAIN. Start from WORD (head at POS, STATE). Each round: run until the first stable K-moment
// after a change (two consecutive K-moments with equal (outer prefix O, digit count n), after the key changed at
// least once in this round), print it, then reset the list to an exhaustion: tape right of O := (u^be s)^n u^be s
// u^(alB*b1+beB) S (all digits 0, a = 0, b = b1), head right of it in state Q, and start the next round.
// K-moment: state Q reads 0 right of all 1s; parse from the right: S, b-run, (s, run)*; O = unparsed left part.
//  hpc MACHINE SIDE Q u s S be alB beB WORD POS STATE b1 ROUNDS MAXSTEPS_PER_ROUND [STAB=6] [MINND=1] [MODE=0]
// MODE 1: reset keeps O and the first (most significant) digit run literally, then a = 0, b = b1: list [d1; 0; b1];
// the machine itself runs it down and reaches a genuine exhaustion.
// stable = the same key at STAB consecutive K-moments with n >= MINND (and a key change earlier in the round,
// except in round 0).
// Output per round: R<i> steps lo vis hi | n= a= b= |O|= O=[rl]      (vis = leftmost head position in the round)
// or R<i> HALT state read / R<i> TIMEOUT.  Positions: WORD at 0..len-1.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
int W[16][2], D[16][2], NX[16][2]; long long CNT[16][2]; int NST = 0; bool SLOTS = getenv("HPC_SLOTS") != nullptr; long long WMAX = getenv("HPC_WMAX") ? atoll(getenv("HPC_WMAX")) : (1LL << 40); long long KMAX = getenv("HPC_KMAX") ? atoll(getenv("HPC_KMAX")) : (1LL << 60); long long KCNT = 0;
static void pslots(int r) { if (!SLOTS) return; printf("S%d", r); for (int a = 0; a < NST; ++a) for (int c = 0; c < 2; ++c) { printf(" %c%d:%lld", 'A' + a, c, CNT[a][c]); CNT[a][c] = 0; } putchar(10); }
static std::string rl(const std::string &w, size_t maxch = 300) {
    std::string o; size_t i = 0;
    while (i < w.size() && o.size() < maxch) { size_t j = i; while (j < w.size() && w[j] == w[i]) ++j;
        size_t n = j - i; if (n >= 4) o += std::string(1, w[i]) + "^" + std::to_string(n) + " "; else o += w.substr(i, n) + " "; i = j; }
    if (i < w.size()) o += "...";
    if (!o.empty() && o.back() == ' ') o.pop_back();
    return o;
}
static std::string rep(const std::string &x, long long k) { std::string o; for (long long i = 0; i < k; ++i) o += x; return o; }
int main(int argc, char **argv) {
    if (argc < 16) { fprintf(stderr, "usage\n"); return 1; }
    std::string m = argv[1]; char side = argv[2][0]; int Q = argv[3][0] - 'A';
    std::string u = argv[4], s = argv[5], S = argv[6]; if (S == "-") S = "";
    long long be = atoll(argv[7]), alB = atoll(argv[8]), beB = atoll(argv[9]);
    std::string w0 = argv[10]; if (w0 == "-") w0 = "";
    long long pos = atoll(argv[11]); int q = argv[12][0] - 'A'; long long b1 = atoll(argv[13]); int R = atoi(argv[14]); long long maxs = atoll(argv[15]); int STAB = argc > 16 ? atoi(argv[16]) : 6; long long MINND = argc > 17 ? atoll(argv[17]) : 1; int MODE = argc > 18 ? atoi(argv[18]) : 0; int PRW = argc > 19 ? atoi(argv[19]) : 0;
    int n = (int)(m.size() + 1) / 7; NST = n;
    for (int qq = 0; qq < n; ++qq) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * qq + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') { NX[qq][c] = -1; continue; } W[qq][c] = x[0] - '0'; D[qq][c] = x[1] == 'R' ? 1 : -1; NX[qq][c] = x[2] - 'A'; }
    if (side == 'L') for (int qq = 0; qq < n; ++qq) for (int c = 0; c < 2; ++c) D[qq][c] = -D[qq][c];
    long long size = 1 << 20; while (size < 4 * (long long)w0.size() + 4096) size *= 2; long long off = size / 2;
    std::vector<unsigned char> t(size, 0);
    long long lo = 1, hi = 0;
    auto put = [&](long long p, int v) { t[off + p] = v; if (v) { if (lo > hi) lo = hi = p; else { if (p < lo) lo = p; if (p > hi) hi = p; } } };
    for (size_t z = 0; z < w0.size(); ++z) put((long long)z, w0[z] == '1');
    for (int r = 0; r < R; ++r) {
        KCNT = 0; long long vis = pos; std::string key0 = "#", lastkey = "#"; bool changed = (r == 0); long long st; int same = 0;
        bool done = false;
        for (st = 0; st < maxs; ++st) {
            if (pos + off < 2 || pos + off + 2 >= size) { std::vector<unsigned char> nt(size * 2, 0); memcpy(nt.data() + size / 2, t.data(), size); off += size / 2; size *= 2; t.swap(nt); }
            unsigned char *T = t.data() + off; int c = T[pos];
            if (c == 0 && q == Q && lo <= hi) {
                while (lo <= hi && !T[hi]) --hi; while (lo <= hi && !T[lo]) ++lo;
                if (pos > hi) {
                    if (++KCNT > KMAX) { printf("R%d WIDE K %lld\n", r, KCNT); return 0; }
                    if (hi - lo > WMAX) { printf("R%d WIDE %lld\n", r, hi - lo); return 0; }
                    std::string w; for (long long i = lo; i < pos; ++i) w += char('0' + T[i]);
                    if (w.size() >= S.size() && w.compare(w.size() - S.size(), S.size(), S) == 0) {
                        long long e = (long long)w.size() - (long long)S.size(); std::vector<long long> rr;
                        while (true) { long long k = 0; while (e - (long long)u.size() >= 0 && w.compare(e - u.size(), u.size(), u) == 0) { e -= u.size(); ++k; }
                            rr.push_back(k); if (e - (long long)s.size() >= 0 && w.compare(e - s.size(), s.size(), s) == 0 && rr.size() < 10000000) e -= s.size(); else break; }
                        long long nd = (long long)rr.size() - 2;
                        std::string O = w.substr(0, e);
                        std::string key = O + "|" + std::to_string(nd);
                        if (nd >= 0) { if (key0 == "#") key0 = key; else if (key != key0) changed = true;
                        if (key == lastkey) ++same; else same = 1; }
                        if (nd >= 0 && changed && same >= STAB && nd >= MINND) {
                            std::string ds; long long shown = 0;
                            for (long long j = (long long)rr.size() - 1; j >= 2 && shown < 10; ) { long long v = rr[j]; long long rq = j; while (rq >= 2 && rr[rq] == v) --rq;
                                ds += std::to_string(v); if (j - rq > 1) ds += "^" + std::to_string(j - rq); ds += ","; j = rq; ++shown; }
                            printf("R%d %lld %lld %lld %lld | n=%lld a=%lld b=%lld |O|=%zu O=[%s] d=%s\n", r, st, lo, vis, hi, nd, rr[1], rr[0], O.size(), rl(O, 240).c_str(), ds.c_str());
                            fflush(stdout);
                            // reset: exhaustion
                            for (long long i = lo; i <= std::max(hi, pos) + 2; ++i) T[i] = 0;
                            long long l0 = lo; lo = 1; hi = 0;
                            std::string nw = MODE == 0 ? O + rep(rep(u, be) + s, nd) + rep(u, be) + s + rep(u, alB * b1 + beB) + S
                                : w.substr(0, O.size() + rr.back() * u.size() + s.size()) + rep(u, be) + s + rep(u, alB * b1 + beB) + S;
                            // ensure room
                            while (l0 + off + (long long)nw.size() + 8 >= size) { std::vector<unsigned char> nt(size * 2, 0); memcpy(nt.data() + size / 2, t.data(), size); off += size / 2; size *= 2; t.swap(nt); }
                            for (size_t z = 0; z < nw.size(); ++z) put(l0 + (long long)z, nw[z] == '1');
                            pslots(r);
                            if (PRW) printf("W%d %lld %s\n", r, l0, nw.c_str());
                            pos = l0 + (long long)nw.size(); q = Q; done = true; break;
                        }
                        if (nd >= 0) lastkey = key;
                    }
                }
            }
            if (NX[q][c] < 0) { pslots(r); printf("R%d HALT %lld state %c read %d lo %lld vis %lld\n", r, st, 'A' + q, c, lo, vis); return 0; }
            CNT[q][c]++;
            T[pos] = W[q][c]; if (W[q][c]) { if (lo > hi) lo = hi = pos; else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; } }
            pos += D[q][c]; q = NX[q][c]; if (pos < vis) vis = pos;
        }
        if (!done) { printf("R%d TIMEOUT lo %lld vis %lld\n", r, lo, vis); return 0; }
    }
    printf("END\n");
}
