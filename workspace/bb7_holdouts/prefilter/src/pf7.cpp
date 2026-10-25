// pf7: cheap pre-filter for dlscan2 on the BB(7) holdouts (prefilter/REPORT.txt has the calibration).
//
//   pf7 INPUT OUTPUT [STEPS=300000] [--ct=60] [--csmin=20] [--frac=0.7] [--smallspan=60] [--ctsmall=3]
//                    [--F=4] [--minsnaps=200] [--budget=2]
//
// Signal: a digit-list engine spends most of its time in R1 phases, K(ds; a; b) -> K(ds; a-1; m1 b + c1): seen at
// its tape end in a fixed state, the tape keeps the same block structure while exactly one block (a) shrinks and
// exactly one block (b) grows. pf7 counts such "clean transfers" between consecutive snapshots.
//
// 1. Simulate STEPS steps from the blank tape. A tape-end event is dlscan2's census2 event: head on a blank, a 1
//    within 4 cells inward, no 1 within 4 cells outward nor beyond. Events are grouped in series (end, state).
// 2. A series takes a snapshot of the tape word when min(F*span, STEPS/minsnaps) steps have passed since its last
//    one (span = word length); snapshot work is capped at budget*STEPS cells per machine.
// 3. A snapshot is cut into blocks: maximal periodic stretches of period 1-3 covering >= max(2p, 3) cells, found
//    greedily from the head end (other cells are literals and ignored).
// 4. Clean transfer: two consecutive snapshots of a series have the same number n >= 2 of blocks, exactly one block
//    longer, exactly one shorter and the others equal. Clean insertion (list growth, e.g. champion descendants that
//    append a digit per pass): one more block than before, and removing one block leaves the old list with exactly
//    one block shorter. CS = clean steps (transfers + insertions) of the best series, CSN = its snapshot count.
// Verdict: PASS iff the machine halted within STEPS, or CS >= ct, or (CS >= csmin and CS >= frac*(CSN-1)), or
// (visited span < smallspan and CS >= ctsmall). Clause 2 keeps slow-sweep machines with few snapshots; clause 3 keeps
// the slow small-tape list machines (dlscan2 grades them NOBOUNDARY) whose tiny blocks change in other ways.
// OUTPUT (TSV): machine, verdict, halted_step, span, snaps, maxblocks, CS, CSN, CT2 and CTI (most clean transfers /
// insertions in any series), RESETS (most drops of one block slot from >= 12 cells to <= half; informational).
// Last line "#summary machines=.. pass=..". PF7_TRACE=RA (end, state) prints that series' block lists to stderr.
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
static const int NSIDE = 3;               // reset slots: 1st-3rd block from the head end and from the far end

struct Series {
    long long last = -(1LL << 60); int nsnap = 0;
    std::vector<long long> pb;            // previous snapshot's blocks
    int ct2 = 0, cti = 0;                 // clean transfers, clean insertions
    long long prevslot[2 * NSIDE] = {}; bool grew[2 * NSIDE] = {true, true, true, true, true, true}; int resets[2 * NSIDE] = {};
};

struct Sim {
    std::vector<uint8_t> tape, w;
    std::vector<long long> blocks;        // head end first
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
        long long nb = (long long)blocks.size();
        if (nb > maxnb) maxnb = nb;
        if (s.nsnap > 0 && (long long)s.pb.size() == nb && nb >= 2) {
            int up = 0, dn = 0;
            for (long long i = 0; i < nb; ++i) { if (blocks[i] > s.pb[i]) ++up; else if (blocks[i] < s.pb[i]) ++dn; }
            if (up == 1 && dn == 1) s.ct2++;
        } else if (s.nsnap > 0 && (long long)s.pb.size() + 1 == nb && nb >= 3) {
            // list growth: one new block inserted, exactly one block shorter, the rest unchanged
            const std::vector<long long> &p = s.pb;
            long long a = 0, b = 0, np = (long long)p.size();
            while (a < np && blocks[a] == p[a]) ++a;
            while (b < np && blocks[nb - 1 - b] == p[np - 1 - b]) ++b;
            long long ks[4] = {a, a + 1, nb - 1 - b, nb - 2 - b};
            for (long long k : ks) {
                if (k < 0 || k >= nb) continue;
                int up = 0, dn = 0;
                for (long long i = 0, j = 0; i < nb; ++i) {
                    if (i == k) continue;
                    if (blocks[i] > p[j]) ++up; else if (blocks[i] < p[j]) ++dn;
                    ++j;
                }
                if (up == 0 && dn == 1) { s.cti++; break; }
            }
        }
        for (int i = 0; i < 2 * NSIDE; ++i) {          // resets (informational)
            long long k = i % NSIDE, v = k < nb ? (i < NSIDE ? blocks[k] : blocks[nb - 1 - k]) : 0, p = s.prevslot[i];
            if (s.nsnap > 0) {
                if (v > p) s.grew[i] = true;
                else if (2 * v <= p && p >= 12 && s.grew[i]) { s.resets[i]++; s.grew[i] = false; }
            }
            s.prevslot[i] = v;
        }
        s.pb.assign(blocks.begin(), blocks.end());
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
                        if (g_trace && g_trace[0] == (e ? 'L' : 'R') && g_trace[1] == 'A' + q) {
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

int main(int argc, char **argv) {
    std::vector<std::string> pos;
    long long ct = 60, smallspan = 60, ctsmall = 3, csmin = 20;
    double F = 4.0, minsnaps = 200, W = 2.0, frac = 0.7;
    for (int i = 1; i < argc; ++i) {
        if (!strncmp(argv[i], "--ct=", 5)) ct = atoll(argv[i] + 5);
        else if (!strncmp(argv[i], "--csmin=", 8)) csmin = atoll(argv[i] + 8);
        else if (!strncmp(argv[i], "--frac=", 7)) frac = atof(argv[i] + 7);
        else if (!strncmp(argv[i], "--smallspan=", 12)) smallspan = atoll(argv[i] + 12);
        else if (!strncmp(argv[i], "--ctsmall=", 10)) ctsmall = atoll(argv[i] + 10);
        else if (!strncmp(argv[i], "--F=", 4)) F = atof(argv[i] + 4);
        else if (!strncmp(argv[i], "--minsnaps=", 11)) minsnaps = atof(argv[i] + 11);
        else if (!strncmp(argv[i], "--budget=", 9)) W = atof(argv[i] + 9);
        else if (argv[i][0] == '-' && argv[i][1] == '-') { fprintf(stderr, "unknown option %s\n", argv[i]); return 2; }
        else pos.push_back(argv[i]);
    }
    if (pos.size() < 2) {
        fprintf(stderr, "usage: pf7 INPUT OUTPUT [STEPS=300000] [--ct=60] [--csmin=20] [--frac=0.7] [--smallspan=60] [--ctsmall=3] [--F=4] [--minsnaps=200] [--budget=2]\n");
        return 2;
    }
    long long steps = pos.size() > 2 ? atoll(pos[2].c_str()) : 300000;
    double maxgap = minsnaps > 0 ? (double)steps / minsnaps : 1e18;
    std::ifstream in(pos[0]);
    if (!in) { fprintf(stderr, "cannot read %s\n", pos[0].c_str()); return 2; }
    std::ofstream out(pos[1]);
    out << "machine\tverdict\thalted\tspan\tsnaps\tmaxblocks\tCS\tCSN\tCT2\tCTI\tRESETS\n";
    g_trace = getenv("PF7_TRACE");
    Sim sim; std::string line; long long n = 0, npass = 0;
    while (std::getline(in, line)) {
        size_t sp = line.find_first_of(" \t\r");
        if (sp != std::string::npos) line.resize(sp);
        TM m; if (line.find('_') == std::string::npos || !parse(line, m)) continue;
        long long span = 0;
        long long h = sim.run(m, steps, F, maxgap, W, span);
        int snaps = 0, cs = 0, csn = 0, ct2 = 0, cti = 0, resets = 0;
        for (int e = 0; e < 2; ++e) for (int q = 0; q < MAXQ; ++q) {
            Series &s = sim.ser[e][q];
            snaps += s.nsnap;
            int c = s.ct2 + s.cti;
            if (c > cs || (c == cs && c > 0 && s.nsnap < csn)) { cs = c; csn = s.nsnap; }
            ct2 = std::max(ct2, s.ct2); cti = std::max(cti, s.cti);
            for (int i = 0; i < 2 * NSIDE; ++i) resets = std::max(resets, s.resets[i]);
        }
        bool pass = h >= 0 || cs >= ct || (cs >= csmin && (double)cs >= frac * (csn - 1)) || (span < smallspan && cs >= ctsmall);
        ++n; npass += pass;
        out << line << "\t" << (pass ? "PASS" : "FAIL") << "\t" << h << "\t" << span << "\t" << snaps << "\t" << sim.maxnb
            << "\t" << cs << "\t" << csn << "\t" << ct2 << "\t" << cti << "\t" << resets << "\n";
        if (n % 1000 == 0) out.flush();
    }
    out << "#summary\tmachines=" << n << "\tpass=" << npass << "\n";
    return 0;
}
