// pf7: cheap reset-signal pre-filter for dlscan2 (BB(7) holdout triage).
//
//   pf7 INPUT OUTPUT [STEPS=300000] [--dmin=D] [--big=B] [--F=F] [--budget=W]
//
// Simulates each machine from the blank tape for STEPS steps. At every tape-end event (dlscan2's census2
// definition: head on a blank, a 1 within 4 cells inward, no 1 within 4 cells outward nor beyond) of series
// (end, state), a snapshot of the tape word is taken if at least F*span steps passed since that series' previous
// snapshot (total snapshot work is capped at W*STEPS cells). A snapshot is cut into blocks: maximal periodic
// stretches of period 1-3 covering at least max(2p, 3) cells, found greedily from the head end; the rest are
// literal cells. Six slots are followed per series: the 1st-3rd block counted from the head end and from the far
// end (block length in cells, 0 if absent).
// A "reset" in a slot: its length drops from >= B cells to <= half of it, with growth in that slot since the
// previous reset. A digit-list engine resets its accumulator (R2) and grows it again (R1), so it shows resets.
// Statistic D_B = most resets in any one slot; verdict PASS iff D_B >= dmin, or the machine halted in STEPS steps.
// OUTPUT (TSV): machine, verdict, halted_step, snaps, D6, D12, D24, best slot (end,state,slot), span.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>
#include <chrono>

static const int MAXQ = 16;
struct TM { int w[MAXQ][2], d[MAXQ][2], nx[MAXQ][2]; int n; };
static bool parse(const std::string &s, TM &m) {
    m.n = (int)(s.size() + 1) / 7;
    if (m.n < 1 || m.n > MAXQ || (int)s.size() != 7 * m.n - 1) return false;
    for (int q = 0; q < m.n; ++q) for (int c = 0; c < 2; ++c) {
        const char *t = s.c_str() + 7 * q + 3 * c;
        if (t[0] == '-' || t[2] == 'Z') { m.nx[q][c] = -1; m.w[q][c] = 0; m.d[q][c] = 1; continue; }
        m.w[q][c] = t[0] - '0'; m.d[q][c] = t[1] == 'R' ? 1 : -1; m.nx[q][c] = t[2] - 'A';
    }
    return true;
}

static double g_maxgap = 1e18;          // --minsnaps=K: snapshot at least every STEPS/K steps per series
static const char *g_trace = nullptr;   // PF7_TRACE=RA etc.: print the blocks of that series
static const int NB = 3;                  // thresholds
static const long long BIGS[NB] = {6, 12, 24};
static const int NSIDE = 6, NSLOT = 2 * NSIDE;   // 1st-6th block from the head end, 1st-6th from the far end
static const int NK = 4;    // reset kinds: 0 any, 1 both snapshots have >= 3 blocks, 2 transfer, 3 transfer with >= 3 blocks

struct Slot { bool grew = true; int resets[NK][NB] = {}; };
struct Series { long long last = -(1LL << 60); int nsnap = 0; long long prev[NSLOT] = {}; long long nprev = 0; Slot sl[NSLOT];
                 std::vector<long long> pb; int ct2 = 0, ct3 = 0, ctx = 0; };

struct Sim {
    std::vector<uint8_t> tape;
    std::vector<uint8_t> w;               // snapshot word, head end at w.back()
    std::vector<long long> blocks;        // block lengths, head end first
    Series ser[2][MAXQ];
    long long maxnb = 0;

    void blocks_of() {
        blocks.clear();
        long long x = (long long)w.size();
        const uint8_t *W = w.data();
        while (x > 0) {
            long long best = 0;
            for (int p = 1; p <= 3 && p <= x; ++p) {
                long long c = p;
                while (x - c - 1 >= 0 && W[x - c - 1] == W[x - c - 1 + p]) ++c;
                long long cells = (c / p) * p;
                if (cells >= 2 * p && cells >= 3 && cells > best) best = cells;
            }
            if (best) { blocks.push_back(best); x -= best; } else --x;
        }
    }

    void update(Series &s) {
        long long v[NSLOT];
        long long nb = (long long)blocks.size();
        if (nb > maxnb) maxnb = nb;
        for (int i = 0; i < NSIDE; ++i) {
            v[i] = i < nb ? blocks[i] : 0;
            v[NSIDE + i] = i < nb ? blocks[nb - 1 - i] : 0;
        }
        if (s.nsnap > 0) {
            bool three = nb >= 3 && s.nprev >= 3;
            for (int i = 0; i < NSLOT; ++i) {
                Slot &sl = s.sl[i];
                long long p = s.prev[i];
                if (v[i] > p) { sl.grew = true; continue; }
                if (!(2 * v[i] <= p && sl.grew && p >= BIGS[0])) continue;
                sl.grew = false;
                // transfer: another block on the same side grew by at least a quarter of the reset block
                bool tr = false;
                int g0 = i < NSIDE ? 0 : NSIDE;
                for (int j = g0; j < g0 + NSIDE; ++j) if (j != i && 4 * (v[j] - s.prev[j]) >= p) tr = true;
                for (int b = 0; b < NB; ++b) if (p >= BIGS[b]) {
                    sl.resets[0][b]++;
                    if (three) sl.resets[1][b]++;
                    if (tr) sl.resets[2][b]++;
                    if (tr && three) sl.resets[3][b]++;
                }
            }
        }
        for (int i = 0; i < NSLOT; ++i) s.prev[i] = v[i];
        // clean transfer: same block count, exactly one block shorter, exactly one longer, the rest unchanged
        if (s.nsnap > 0 && (long long)s.pb.size() == nb && nb >= 2) {
            int up = 0, dn = 0;
            for (long long i = 0; i < nb; ++i) { if (blocks[i] > s.pb[i]) ++up; else if (blocks[i] < s.pb[i]) ++dn; }
            if (up == 1 && dn == 1) { s.ct2++; if (nb >= 3) s.ct3++; }
            if (up >= 1 && dn == 1 && nb >= 3) s.ctx++;
        }
        s.pb.assign(blocks.begin(), blocks.end());
        s.nprev = nb;
        s.nsnap++;
    }

    // returns the halting step or -1
    long long run(const TM &m, long long steps, double F, double W, long long &span_out) {
        long long need = 2 * steps + 64;
        if ((long long)tape.size() < need) tape.assign(need, 0);
        for (int e = 0; e < 2; ++e) for (int q = 0; q < MAXQ; ++q) ser[e][q] = Series();
        uint8_t *T = tape.data();
        long long pos = (long long)tape.size() / 2, vlo = pos, vhi = pos;
        long long loB = 1, hiB = 0;        // all 1s lie in [loB, hiB] (lazy bounds)
        long long work = 0, cap = (long long)(W * steps);
        int q = 0; long long halted = -1;
        for (long long t = 0; t < steps; ++t) {
            int c = T[pos];
            if (c == 0 && loB <= hiB) {
                bool lft = T[pos - 1] | T[pos - 2] | T[pos - 3] | T[pos - 4];
                bool rgt = T[pos + 1] | T[pos + 2] | T[pos + 3] | T[pos + 4];
                int e = -1;
                if (lft && !rgt) {
                    while (hiB > pos && !T[hiB]) --hiB;
                    if (hiB <= pos) { while (!T[hiB]) --hiB; e = 0; }
                } else if (rgt && !lft) {
                    while (loB < pos && !T[loB]) ++loB;
                    if (loB >= pos) { while (!T[loB]) ++loB; e = 1; }
                }
                if (e >= 0 && work <= cap) {
                    Series &s = ser[e][q];
                    if (e == 0) { while (!T[loB]) ++loB; } else { while (!T[hiB]) --hiB; }
                    long long span = e == 0 ? pos - loB : hiB - pos;
                    if ((double)(t - s.last) >= std::min(F * (double)span, g_maxgap)) {
                        s.last = t;
                        w.resize(span);
                        if (e == 0) memcpy(w.data(), T + loB, span);
                        else for (long long i = 0; i < span; ++i) w[i] = T[hiB - i];
                        work += span;
                        blocks_of();
                        if (g_trace && g_trace[0] == (e ? 'L' : 'R') && g_trace[1] == 'A' + q) {
                            fprintf(stderr, "%lld %c%c n=%zu:", t, g_trace[0], g_trace[1], blocks.size());
                            for (size_t i = 0; i < blocks.size() && i < 10; ++i) fprintf(stderr, " %lld", blocks[i]);
                            fprintf(stderr, " ..");
                            for (size_t i = blocks.size() > 10 ? blocks.size() - 4 : blocks.size(); i < blocks.size(); ++i) fprintf(stderr, " %lld", blocks[i]);
                            fputc(10, stderr);
                        }
                        update(s);
                    }
                }
            }
            if (m.nx[q][c] < 0) { halted = t; break; }
            int wr = m.w[q][c];
            T[pos] = (uint8_t)wr;
            if (wr) { if (loB > hiB) loB = hiB = pos; else { if (pos < loB) loB = pos; if (pos > hiB) hiB = pos; } }
            pos += m.d[q][c]; q = m.nx[q][c];
            if (pos < vlo) vlo = pos;
            if (pos > vhi) vhi = pos;
        }
        span_out = vhi - vlo + 1;
        memset(T + vlo, 0, (size_t)(vhi - vlo + 1));
        return halted;
    }
};

int main(int argc, char **argv) {
    std::vector<std::string> pos; double g_minsnaps = 0;
    int dmin = 2; int bigi = 1, kind = 3; double F = 4.0, W = 1.0;
    for (int i = 1; i < argc; ++i) {
        if (!strncmp(argv[i], "--dmin=", 7)) dmin = atoi(argv[i] + 7);
        else if (!strncmp(argv[i], "--kind=", 7)) kind = atoi(argv[i] + 7);
        else if (!strncmp(argv[i], "--big=", 6)) {
            long long b = atoll(argv[i] + 6); bigi = -1;
            for (int k = 0; k < NB; ++k) if (BIGS[k] == b) bigi = k;
            if (bigi < 0) { fprintf(stderr, "big must be 6, 12 or 24\n"); return 2; }
        }
        else if (!strncmp(argv[i], "--F=", 4)) F = atof(argv[i] + 4);
        else if (!strncmp(argv[i], "--minsnaps=", 11)) g_minsnaps = atof(argv[i] + 11);
        else if (!strncmp(argv[i], "--budget=", 9)) W = atof(argv[i] + 9);
        else pos.push_back(argv[i]);
    }
    if (pos.size() < 2) { fprintf(stderr, "usage: pf7 INPUT OUTPUT [STEPS] [--dmin=2] [--big=12] [--F=4] [--budget=1]\n"); return 2; }
    long long steps = pos.size() > 2 ? atoll(pos[2].c_str()) : 300000;
    if (g_minsnaps > 0) g_maxgap = (double)steps / g_minsnaps;
    std::ifstream in(pos[0]);
    if (!in) { fprintf(stderr, "cannot read %s\n", pos[0].c_str()); return 2; }
    std::ofstream out(pos[1]);
    out << "machine\tverdict\thalted\tsnaps\tspan\tmaxblocks\tbest";
    const char *KN[NK] = {"R", "R3", "T", "T3"};
    for (int k = 0; k < NK; ++k) for (int b = 0; b < NB; ++b) out << "\t" << KN[k] << BIGS[b];
    out << "\tCT2\tCT3\tCTX\tCTSN";
    out << "\n";
    g_trace = getenv("PF7_TRACE");
    Sim sim; std::string line; long long n = 0, npass = 0;
    while (std::getline(in, line)) {
        size_t sp = line.find_first_of(" \t\r");
        if (sp != std::string::npos) line.resize(sp);
        TM m; if (line.find('_') == std::string::npos || !parse(line, m)) continue;
        long long span = 0;
        sim.maxnb = 0;
        auto t0 = std::chrono::steady_clock::now();
        long long h = sim.run(m, steps, F, W, span);
        long long us = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - t0).count();
        int D[NK][NB] = {}; int snaps = 0, ct2 = 0, ct3 = 0, ctx = 0, ctsn = 0; std::string best = "-"; int bestv = -1;
        for (int e = 0; e < 2; ++e) for (int q = 0; q < MAXQ; ++q) {
            Series &s = sim.ser[e][q]; snaps += s.nsnap;
            if (s.ct2 > ct2) { ct2 = s.ct2; ctsn = s.nsnap; } ct3 = std::max(ct3, s.ct3); ctx = std::max(ctx, s.ctx);
            for (int i = 0; i < NSLOT; ++i) {
                for (int k = 0; k < NK; ++k) for (int b = 0; b < NB; ++b) D[k][b] = std::max(D[k][b], s.sl[i].resets[k][b]);
                if (s.sl[i].resets[kind][bigi] > bestv) {
                    bestv = s.sl[i].resets[kind][bigi];
                    best = std::string(1, e ? 'L' : 'R') + "," + char('A' + q) + "," + (i < NSIDE ? "n" : "f") + char('0' + i % NSIDE);
                }
            }
        }
        bool pass = h >= 0 || D[kind][bigi] >= dmin;
        ++n; npass += pass;
        out << line << "\t" << (pass ? "PASS" : "FAIL") << "\t" << h << "\t" << snaps << "\t" << span << "\t" << sim.maxnb << "\t" << best;
        for (int k = 0; k < NK; ++k) for (int b = 0; b < NB; ++b) out << "\t" << D[k][b];
        out << "\t" << ct2 << "\t" << ct3 << "\t" << ctx << "\t" << ctsn;
        out << "\n";
        if (n % 1000 == 0) out.flush();
    }
    out << "#summary\tmachines=" << n << "\tpass=" << npass << "\n";
    return 0;
}
