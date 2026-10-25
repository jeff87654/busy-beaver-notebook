// ack7: second filter for the BB(7) non-list pool (nonlist/REPORT.txt). Derived from prefilter/src/pf7.cpp.
//   ack7 INPUT OUTPUT [STEPS=1000000] [--F=4] [--minsnaps=400] [--budget=3] [--ratio=1.4] [--minpk=8]
// Same tape-end events and block cutting as pf7 (periods 1-4 here). For every series (end,state) and every block slot
// (1st-3rd block from the head end, 1st-3rd from the far end, and the LONGEST block of the snapshot), a reset is a
// drop of the slot value to <= half of its running peak (peak >= minpk). The peak sequence P1, P2, ... of a slot is
// recorded. G = longest run of consecutive resets with P(i+1) >= ratio * P(i) (geometric regrowth = Ackermann
// signature); GL = longest run with P(i+1) > P(i) (any growth). OUTPUT: machine halted span G GL nres maxpeak peaks(best slot).
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>

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


static const char *g_trace = nullptr;
static const int NS = 7;                  // 3 head-end slots, 3 far-end slots, longest block
static double g_ratio = 1.4; static long long g_minpk = 8;
struct Slot { long long peak = 0, cur = 0; std::vector<long long> pk; };
struct Series { long long last = -(1LL << 60); int nsnap = 0; Slot sl[NS]; };

struct Sim {
    std::vector<uint8_t> tape, w;
    std::vector<long long> blocks;
    Series ser[2][MAXQ];
    long long maxnb = 0;
    void blocks_of() {
        blocks.clear();
        long long x = (long long)w.size();
        const uint8_t *W = w.data();
        while (x > 0) {
            long long best = 0;
            for (int p = 1; p <= 4 && p <= x; ++p) {
                long long c = p;
                while (x - c - 1 >= 0 && W[x - c - 1] == W[x - c - 1 + p]) ++c;
                long long cells = (c / p) * p;
                if (cells >= 2 * p && cells >= 3 && cells > best) best = cells;
            }
            if (best) { blocks.push_back(best); x -= best; } else --x;
        }
    }
    void update(Series &s) {
        long long nb = (long long)blocks.size(), mx = 0;
        for (long long b : blocks) mx = std::max(mx, b);
        for (int i = 0; i < NS; ++i) {
            long long v;
            if (i == 6) v = mx;
            else { long long k = i % 3; v = k < nb ? (i < 3 ? blocks[k] : blocks[nb - 1 - k]) : 0; }
            Slot &z = s.sl[i];
            if (v > z.peak) z.peak = v;
            if (z.peak >= g_minpk && 2 * v <= z.peak) { if (z.pk.size() < 64) z.pk.push_back(z.peak); z.peak = v; }
            z.cur = v;
        }
        s.nsnap++;
    }
    long long run(const TM &m, long long steps, double F, double maxgap, double W, long long &span_out) {
        long long need = 2 * steps + 64;
        if ((long long)tape.size() < need) tape.assign(need, 0);
        for (int e = 0; e < 2; ++e) for (int q = 0; q < MAXQ; ++q) ser[e][q] = Series();
        maxnb = 0;
        uint8_t *T = tape.data();
        struct Tr { int w, d, nx; } tr[2 * MAXQ];
        for (int i = 0; i < m.n; ++i) for (int c = 0; c < 2; ++c) tr[2 * i + c] = {m.w[i][c], m.d[i][c], m.nx[i][c]};
        long long pos = (long long)tape.size() / 2, vlo = pos, vhi = pos;
        long long loB = 1, hiB = 0;        // all 1s lie in [loB, hiB] (lazy bounds)
        long long work = 0, cap = (long long)(W * (double)steps);
        int q = 0; long long halted = -1;
        for (long long t = 0; t < steps; ++t) {
            int c = T[pos];
            if (c == 0 && loB <= hiB) {
                uint32_t L4, R4;
                memcpy(&L4, T + pos - 4, 4); memcpy(&R4, T + pos + 1, 4);
                bool lft = L4 != 0, rgt = R4 != 0;
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
                    if ((double)(t - s.last) >= std::min(F * (double)span, maxgap)) {
                        s.last = t;
                        w.resize(span);
                        if (e == 0) memcpy(w.data(), T + loB, span);
                        else for (long long i = 0; i < span; ++i) w[i] = T[hiB - i];
                        work += span;
                        blocks_of();
                        if (false && g_trace && g_trace[0] == (e ? 'L' : 'R') && g_trace[1] == 'A' + q) {
                            fprintf(stderr, "%lld %c%c n=%zu:", t, g_trace[0], g_trace[1], blocks.size());
                            for (size_t i = 0; i < blocks.size() && i < 10; ++i) fprintf(stderr, " %lld", blocks[i]);
                            fprintf(stderr, " ..");
                            for (size_t i = blocks.size() > 10 ? blocks.size() - 4 : blocks.size(); i < blocks.size(); ++i)
                                fprintf(stderr, " %lld", blocks[i]);
                            fputc(10, stderr);
                        }
                        update(s);
                    }
                }
            }
            const Tr &x = tr[2 * q + c];
            if (x.nx < 0) { halted = t; break; }
            int wr = x.w;
            T[pos] = (uint8_t)wr;
            if (wr) { if (loB > hiB) loB = hiB = pos; else { if (pos < loB) loB = pos; if (pos > hiB) hiB = pos; } }
            pos += x.d; q = x.nx;
            if (pos < vlo) vlo = pos;
            if (pos > vhi) vhi = pos;
        }
        span_out = vhi - vlo + 1;
        memset(T + vlo, 0, (size_t)(vhi - vlo + 1));
        return halted;
    }
};


static void chain(const std::vector<long long> &p, int &G, int &GL) {
    G = GL = 0; int g = 0, gl = 0;
    for (size_t i = 1; i < p.size(); ++i) {
        g = ((double)p[i] >= g_ratio * (double)p[i - 1]) ? g + 1 : 0;
        gl = p[i] > p[i - 1] ? gl + 1 : 0;
        G = std::max(G, g); GL = std::max(GL, gl);
    }
}
int main(int argc, char **argv) {
    std::vector<std::string> pos;
    double F = 4.0, minsnaps = 400, W = 3.0;
    for (int i = 1; i < argc; ++i) {
        if (!strncmp(argv[i], "--F=", 4)) F = atof(argv[i] + 4);
        else if (!strncmp(argv[i], "--minsnaps=", 11)) minsnaps = atof(argv[i] + 11);
        else if (!strncmp(argv[i], "--budget=", 9)) W = atof(argv[i] + 9);
        else if (!strncmp(argv[i], "--ratio=", 8)) g_ratio = atof(argv[i] + 8);
        else if (!strncmp(argv[i], "--minpk=", 8)) g_minpk = atoll(argv[i] + 8);
        else if (argv[i][0] == '-' && argv[i][1] == '-') { fprintf(stderr, "unknown option %s\n", argv[i]); return 2; }
        else pos.push_back(argv[i]);
    }
    if (pos.size() < 2) { fprintf(stderr, "usage: ack7 INPUT OUTPUT [STEPS]\n"); return 2; }
    long long steps = pos.size() > 2 ? atoll(pos[2].c_str()) : 1000000;
    double maxgap = minsnaps > 0 ? (double)steps / minsnaps : 1e18;
    std::ifstream in(pos[0]);
    if (!in) { fprintf(stderr, "cannot read %s\n", pos[0].c_str()); return 2; }
    std::ofstream out(pos[1]);
    out << "machine\thalted\tspan\tG\tGL\tnres\tmaxpeak\tbest\tpeaks\n";
    Sim sim; std::string line; long long n = 0, ng = 0;
    while (std::getline(in, line)) {
        size_t sp = line.find_first_of(" \t\n");
        if (sp != std::string::npos) line.resize(sp);
        TM m; if (line.find('_') == std::string::npos || !parse(line, m)) continue;
        long long span = 0;
        long long h = sim.run(m, steps, F, maxgap, W, span);
        int G = 0, GL = 0, nres = 0; long long mp = 0; std::string best = "-"; const std::vector<long long> *bp = nullptr;
        for (int e = 0; e < 2; ++e) for (int q = 0; q < MAXQ; ++q) for (int i = 0; i < NS; ++i) {
            const Slot &z = sim.ser[e][q].sl[i];
            int g, gl; chain(z.pk, g, gl);
            nres = std::max(nres, (int)z.pk.size());
            for (long long v : z.pk) mp = std::max(mp, v);
            if (g > G || (g == G && gl > GL)) { G = g; GL = std::max(GL, gl); bp = &z.pk;
                best = std::string(1, e ? 'L' : 'R') + (char)('A' + q) + (char)('0' + i); }
            GL = std::max(GL, gl);
        }
        ++n; ng += G >= 2;
        out << line << "\t" << h << "\t" << span << "\t" << G << "\t" << GL << "\t" << nres << "\t" << mp << "\t" << best << "\t";
        if (bp) { size_t s0 = bp->size() > 12 ? bp->size() - 12 : 0; for (size_t i = s0; i < bp->size(); ++i) out << (i > s0 ? "," : "") << (*bp)[i]; }
        else out << "-";
        out << "\n";
        if (n % 1000 == 0) out.flush();
    }
    out << "#summary\tmachines=" << n << "\tG2=" << ng << "\n";
    return 0;
}
