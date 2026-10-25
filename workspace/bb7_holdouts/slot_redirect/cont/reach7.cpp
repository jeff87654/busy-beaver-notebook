// reach7: natural blank-tape run with nlp7's macro simulator (K-cell blocks, run-length stacks, self-loop acceleration).
//   reach7 IN OUT MAXMACRO MAXLG [--pilot=30000]
// Pilot: K = 1..6, PILOT macro steps each, K with most base steps wins. Main run: until halt (= first undefined slot reached),
// in-block loop, MAXMACRO macro steps, or base steps >= 10^MAXLG.
// OUT: machine K status(HALT|LOOP|RUN) log10steps macros steps slot ones
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <fstream>
#include <string>
#include <vector>
#include <windows.h>
typedef unsigned long long u64; typedef long double LD;
static int NS, W[16][2], D[16][2], NX[16][2], K;
struct Run { u64 b, n; };
struct MT { u64 nb; u64 steps; int ns, dir, halt, ok, hq, hc; bool done; };
static MT cache[16][2][64];
static MT &macro(int q, int side, u64 b) {
    MT &r = cache[q][side][b];
    if (r.done) return r;
    r.done = true; r.ok = 1; r.halt = 0; r.steps = 0; r.dir = 0;
    int pos = side ? K - 1 : 0; u64 bl = b; int lim = 2000;
    while (true) {
        int c = (bl >> (K - 1 - pos)) & 1;
        if (NX[q][c] < 0) { r.halt = 1; r.hq = q; r.hc = c; break; }
        if (W[q][c]) bl |= (1ULL << (K - 1 - pos)); else bl &= ~(1ULL << (K - 1 - pos));
        pos += D[q][c]; q = NX[q][c]; r.steps++;
        if (pos < 0) { r.dir = -1; break; }
        if (pos >= K) { r.dir = 1; break; }
        if (--lim == 0) { r.ok = 0; break; }
    }
    r.nb = bl; r.ns = q; return r;
}
static inline void push(std::vector<Run> &S, u64 b, u64 n) {
    if (S.empty() && b == 0) return;
    if (!S.empty() && S.back().b == b) S.back().n += n; else S.push_back({b, n});
}
static inline u64 pop(std::vector<Run> &S) { if (S.empty()) return 0; u64 b = S.back().b; if (--S.back().n == 0) S.pop_back(); return b; }
static bool parse(const std::string &s) {
    int n = (int)(s.size() + 1) / 7; if (n < 1 || n > 16 || (int)s.size() != 7 * n - 1) return false;
    NS = n;
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) {
        const char *t = s.c_str() + 7 * q + 3 * c;
        if (t[0] == '-' || t[2] == 'Z' || t[2] == '-') { NX[q][c] = -1; W[q][c] = 1; D[q][c] = 1; continue; }
        W[q][c] = t[0] - '0'; D[q][c] = t[1] == 'R' ? 1 : -1; NX[q][c] = t[2] - 'A';
    }
    return true;
}
struct Res { int halt = 0, loop = 0, hq = -1, hc = -1; LD steps = 0, ones = 0; u64 macros = 0; };
static LD LIM;
static Res runm(u64 maxm) {
    Res R; std::vector<Run> L, Rt; int q = 0, side = 0; u64 cur = 0;
    for (u64 it = 0; it < maxm; ++it) {
        MT &t = macro(q, side, cur);
        if (!t.ok) { R.loop = 1; R.macros = it; return R; }
        if (t.halt) {
            R.halt = 1; R.steps += t.steps + 1; R.macros = it; R.hq = t.hq; R.hc = t.hc;
            LD o = __builtin_popcountll(t.nb);
            for (auto &r : L) o += (LD)__builtin_popcountll(r.b) * r.n;
            for (auto &r : Rt) o += (LD)__builtin_popcountll(r.b) * r.n;
            R.ones = o; return R;
        }
        std::vector<Run> &Ah = t.dir > 0 ? Rt : L; std::vector<Run> &Be = t.dir > 0 ? L : Rt;
        int nside = t.dir > 0 ? 0 : 1;
        if (t.ns == q && nside == side && !Ah.empty() && Ah.back().b == cur) {
            u64 n = Ah.back().n; Ah.pop_back(); push(Be, t.nb, n + 1); R.steps += (LD)t.steps * (n + 1);
        } else { R.steps += t.steps; push(Be, t.nb, 1); }
        cur = pop(Ah); q = t.ns; side = nside;
        if (R.steps >= LIM) { R.macros = it + 1; return R; }
    }
    R.macros = maxm; return R;
}
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    if (argc < 5) { fprintf(stderr, "usage: reach7 IN OUT MAXMACRO MAXLG [--pilot=N] [--K=k]\n"); return 2; }
    u64 maxm = strtoull(argv[3], 0, 10); LIM = powl(10.0L, atof(argv[4])); u64 pilot = 30000; int fixK = 0;
    for (int i = 5; i < argc; ++i) { if (!strncmp(argv[i], "--pilot=", 8)) pilot = strtoull(argv[i] + 8, 0, 10); if (!strncmp(argv[i], "--K=", 4)) fixK = atoi(argv[i] + 4); }
    std::ifstream in(argv[1]); FILE *out = fopen(argv[2], "w");
    std::string line; long long n = 0, nh = 0;
    while (std::getline(in, line)) {
        size_t sp = line.find_first_of(" \t\r"); if (sp != std::string::npos) line.resize(sp);
        if (line.find('_') == std::string::npos || !parse(line)) continue;
        int bestK = fixK ? fixK : 1; LD bests = -1; Res hit; bool ph = false;
        if (!fixK) for (int k = 1; k <= 6; ++k) {
            K = k; memset(cache, 0, sizeof cache);
            Res r = runm(pilot);
            if (r.halt || r.loop) { hit = r; ph = true; bestK = k; break; }
            if (r.steps > bests * 1.05L) { bests = r.steps; bestK = k; }
        }
        Res r;
        if (ph) r = hit; else { K = bestK; memset(cache, 0, sizeof cache); r = runm(maxm); }
        if (r.halt) ++nh;
        fprintf(out, "%s\t%d\t%s\t%.3f\t%llu\t%.6Le\t%s\t%.0Lf\n", line.c_str(), bestK, r.halt ? "HALT" : r.loop ? "LOOP" : "RUN",
                (double)log10l(r.steps + 1), (unsigned long long)r.macros, r.steps,
                r.halt ? (std::string(1, 'A' + r.hq) + char('0' + r.hc)).c_str() : "-", r.ones);
        if (++n % 500 == 0) fflush(out);
    }
    fprintf(out, "#summary\tmachines=%lld\thalts=%lld\n", n, nh);
}
