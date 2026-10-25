// nlp7: coding-agnostic chain probe for the BB(7) non-list pool (nonlist/REPORT.txt).
//   nlp7 INPUT OUTPUT [MACRO=2000000] [--K=0] [--pilot=30000] [--shrink=1] [--smin=24] [--mod=6] [--trace]
// 1. Macro simulator: tape of K-cell blocks, run-length stacks, self-loop acceleration over runs of identical blocks
//    (Marxen-Buntrock style). K in 1..6 chosen by a pilot (most base steps simulated in PILOT macro steps), or --K.
// 2. Tape-end events (head on blank beyond all data) give snapshots of the run list (far end -> head), one series per
//    (end, state). Snapshot rate: >= max(8, 2*runs) macro steps since the series' last snapshot.
// 3. Counter shrink (forced exhaustion, generic analogue of hpc's reset): within a series, while the run structure
//    (block ids, aligned from the far end) is unchanged, a run whose count fell at >= 3 snapshots with no rise since
//    and has count >= smin is a COUNTER; its count is cut to the smallest value >= 2 with the same residue mod MOD.
//    Each cut is one forced round. The natural run (no cuts) is done separately.
// 4. Recorded: natural halt, forced halt, rounds, distinct cut positions (far-end index) = levels hit,
//    shallowest far-index that changed between consecutive cuts (mind), refills (a cut run later refilled to
//    >= 2x its pre-cut count = promotion), max count, max runs, peak chain G of the max count (natural run).
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <map>
#include <set>
#include <string>
#include <vector>
typedef unsigned long long u64;
typedef long double LD;
static int NS, W[16][2], D[16][2], NX[16][2], K;
struct Run { u64 b, n; };
struct MT { u64 nb; u64 steps; int ns, dir, halt, ok, hpos; bool done; };
static MT cache[16][2][64];
static MT &macro(int q, int side, u64 b) {
    MT &r = cache[q][side][b];
    if (r.done) return r;
    r.done = true; r.ok = 1; r.halt = 0; r.steps = 0; r.dir = 0;
    int pos = side ? K - 1 : 0; u64 bl = b; int lim = 2000;
    while (true) {
        int c = (bl >> (K - 1 - pos)) & 1;
        if (NX[q][c] < 0) { r.halt = 1; r.hpos = pos; break; }
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
static inline u64 pop(std::vector<Run> &S) {
    if (S.empty()) return 0;
    u64 b = S.back().b; if (--S.back().n == 0) S.pop_back(); return b;
}
static bool parse(const std::string &s) {
    int n = (int)(s.size() + 1) / 7; if (n < 1 || n > 16 || (int)s.size() != 7 * n - 1) return false;
    NS = n;
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) {
        const char *t = s.c_str() + 7 * q + 3 * c;
        if (t[0] == '-' || t[2] == 'Z' || (t[2] == 'H' && n < 8)) { NX[q][c] = -1; W[q][c] = 1; D[q][c] = 1; continue; }
        W[q][c] = t[0] - '0'; D[q][c] = t[1] == 'R' ? 1 : -1; NX[q][c] = t[2] - 'A';
    }
    return true;
}
struct Series {
    u64 last = 0, srh = 0, srstart = 0; int srstreak = 0; bool has = false; std::vector<Run> prev; std::vector<int> fell;
    u64 fdl[16] = {}, fdv[16] = {}; int fds[16] = {}, fdslow[16] = {};
    int ns = 0, resets = 0; std::vector<u64> pkv, refv; std::vector<char> low; std::vector<int> sdec, mark, lds, cnt;
    bool counted(size_t i) const { for (int x : cnt) if (x == (int)i) return true; return false; }
};
struct Res {
    int halt = 0; LD steps = 0; u64 macros = 0; int loop = 0;
    int rounds = 0, promos = 0, fhalt = -1; std::set<int> lv; u64 maxcnt = 0; size_t maxruns = 0; int G = 0, mind = 1 << 30;
    std::vector<u64> pk;
    int sr = 0, srp = 0, srend = 0, srs = 0, sc = 0; u64 scmax = 0, fr = 0; int listcut = 0, cursr = 0, npk = 0, nrd = 0, nsr = 0; LD fr0 = 0, rd0 = 0, sr0 = 0; std::vector<std::pair<u64,u64>> srhist; int srl = 0; u64 srlife = 0; u64 srit = 0, srsit = 0; std::string srshape;
};
static std::string bits(u64 b) { std::string s; for (int i = K - 1; i >= 0; --i) s += ((b >> i) & 1) ? '1' : '0'; return s; }
static std::string shape(const std::vector<Run> &Be) {   // far end -> head, compressed, <= 300 chars
    std::string o;
    for (size_t i = 0; i < Be.size() && o.size() < 300; ++i) { o += bits(Be[i].b); if (Be[i].n > 1) o += "^" + std::to_string(Be[i].n); o += ' '; }
    return o;
}
static u64 SHOW = 0, showNext = 0; static bool LITE = false; static bool LIFE = false, SLOWCUT = false, NOLIST = false; static int MAXCUTS = 1 << 30; static u64 DUMPAT = 0; static int DUMPQ = -1;
static std::string cshape(const std::vector<Run> &Be) {   // far end -> head; repeated run patterns as (..)xN
    std::string o; size_t i = 0, nb = Be.size();
    auto one = [&](size_t j) { std::string x = bits(Be[j].b); if (Be[j].n > 1) x += "^" + std::to_string(Be[j].n); return x; };
    while (i < nb) {
        size_t bp = 0, br = 1;
        for (size_t p = 1; p <= 4; ++p) {
            size_t r = 1;
            while (i + (r + 1) * p <= nb) {
                bool eq = true;
                for (size_t k = 0; k < p && eq; ++k) eq = Be[i + k].b == Be[i + r * p + k].b && Be[i + k].n == Be[i + r * p + k].n;
                if (!eq) break; ++r;
            }
            if (r >= 3 && r * p > br * (bp ? bp : 1)) { bp = p; br = r; }
        }
        if (bp) { o += "("; for (size_t k = 0; k < bp; ++k) { if (k) o += ' '; o += one(i + k); } o += ")x" + std::to_string(br) + " "; i += bp * br; }
        else { o += one(i) + " "; ++i; }
    }
    if (o.size() > 330) o = o.substr(0, 110) + " ... " + o.substr(o.size() - 220);
    return o;
}
static const int FW = 8;
static int MOD = 6; static u64 SMIN = 24; static bool SHRINK = false, TRACE = false, SHRINKLIST = false;
static u64 cutto(u64 n) { u64 r = n % MOD; u64 v = r; while (v < 2) v += MOD; return v < n ? v : n; }

static Res runm(u64 maxm, bool doshrink) {
    Res R; std::vector<Run> L, Rt; int q = 0, side = 0; u64 cur = 0;
    static Series ser[2][16];
    for (int e = 0; e < 2; ++e) for (int k = 0; k < 16; ++k) ser[e][k] = Series();
    std::map<int, u64> cutpre;
    u64 lastpk = 0, peak = 0, rpeak = 0; int g = 0;
    std::vector<Run> roundstart; bool haveRS = false;
    for (u64 it = 0; it < maxm; ++it) {
        MT &t = macro(q, side, cur);
        if (!t.ok) { R.loop = 1; R.macros = it; return R; }
        if (t.halt) { R.halt = 1; R.steps += t.steps + 1; R.macros = it; if (R.rounds > 0) R.fhalt = R.rounds; return R; }
        std::vector<Run> &Ah = t.dir > 0 ? Rt : L; std::vector<Run> &Be = t.dir > 0 ? L : Rt;
        int nside = t.dir > 0 ? 0 : 1;
        if (t.ns == q && nside == side && !Ah.empty() && Ah.back().b == cur) {
            u64 n = Ah.back().n; Ah.pop_back(); push(Be, t.nb, n + 1); R.steps += (LD)t.steps * (n + 1);
        } else { R.steps += t.steps; push(Be, t.nb, 1); }
        cur = pop(Ah); q = t.ns; side = nside;
        if (!Ah.empty() || cur != 0) continue;
        int e = t.dir > 0 ? 0 : 1; Series &s = ser[e][q];
        if (DUMPAT && it >= DUMPAT && (DUMPQ < 0 || DUMPQ == q)) {   // full tape in ms.exe 'i' format, then stop
            printf("DUMP %llu %.6Le\n%c %d |", it, R.steps, 'A' + q, side);
            if (e == 0) { for (auto &r : Be) printf(" %s^%llu", bits(r.b).c_str(), r.n); printf(" [%s]\n", bits(0).c_str()); }
            else { printf(" [%s]", bits(0).c_str()); for (size_t i = Be.size(); i-- > 0;) printf(" %s^%llu", bits(Be[i].b).c_str(), Be[i].n); printf("\n"); }
            exit(0);
        }
        if (SHOW && it >= showNext) { showNext = it + it / SHOW + 50; printf("%10llu %.3Le %c%c | %s\n", it, R.steps, e ? 'L' : 'R', 'A' + q, cshape(Be).c_str()); }
        if (s.has && it - s.last < std::max<u64>(8, 2 * Be.size())) continue;
        s.last = it;
        u64 mx = 0; for (auto &r : Be) mx = std::max(mx, r.n);
        R.maxcnt = std::max(R.maxcnt, mx); R.maxruns = std::max(R.maxruns, Be.size());
        if (!LITE) {   // super-run: maximal repetition of a pattern of p = 2..4 runs (a list of equal digits)
            int nb = (int)Be.size(), best = 0, bp = 0, bs = 0;
            for (int p = 2; p <= 4; ++p) {
                int c = 0;
                for (int j = 0; j + p < nb; ++j) {
                    if (Be[j].b == Be[j + p].b && Be[j].n == Be[j + p].n) { ++c; int reps = 1 + c / p; if (reps > best) { best = reps; bp = p; bs = j - c + 1; } }
                    else c = 0;
                }
            }
            u64 h = (u64)best * 1000003ULL + (u64)bp;
            for (int i = 0; i < bp; ++i) h = h * 1315423911ULL + Be[bs + i].b * 977ULL + Be[bs + i].n;
            if (best >= 2 && h == s.srh) s.srstreak++; else { s.srstreak = 0; s.srstart = it; }
            if (best >= 3 && it - s.srstart > R.srlife) { R.srlife = it - s.srstart; R.srl = best; }
            s.srh = h;
            if (best > R.sr) { R.sr = best; R.srp = bp; R.srit = it; }
            if (s.srstreak >= 5 && best > R.srs) { R.srs = best; R.srsit = it; R.srshape = shape(Be); }
            if (doshrink && SHRINKLIST && !NOLIST && !R.listcut && s.srstreak >= 5 && best >= 4) {   // small instance: list -> 2..3 items
                int keep = 2 + (best % 2);
                Be.erase(Be.begin() + bs + bp * keep, Be.begin() + bs + bp * best);
                R.listcut = best; nb = (int)Be.size();
                if (TRACE) fprintf(stderr, "listcut it=%llu %d -> %d items\n", it, best, keep);
            }
            R.srend = best;
            if (best != R.cursr) { if (R.srhist.size() < 4000) R.srhist.push_back({(u64)R.rounds, (u64)best}); R.cursr = best; }
            if (best >= 4) {   // frontier digits: runs within FW of the list that decrement slowly (refilled digits)
                for (int o = -FW; o < FW; ++o) {
                    int j = o < 0 ? bs + o : bs + bp * best + o, k = o + FW;
                    u64 v = (j >= 0 && j < nb) ? Be[j].n : 0, last = s.fdl[k];
                    if (v == last) s.fds[k]++;
                    else {
                        if (v + 1 == last && s.fds[k] >= 3 && last >= 6 && 2 * last < mx) {
                            if (++s.fdslow[k] >= 2) { R.fr = std::max(R.fr, s.fdv[k] = std::max(s.fdv[k], last)); }
                            else s.fdv[k] = std::max(s.fdv[k], last);
                        } else if (v > last) s.fdslow[k] = 0;
                        s.fds[k] = 0;
                    }
                    s.fdl[k] = v;
                }
            }
        }
        if (mx > peak) peak = mx;
        { u64 nr = Be.size(); if (nr > rpeak) rpeak = nr; if (rpeak >= 8 && 2 * nr <= rpeak) { R.nrd++; if (R.rd0 == 0) R.rd0 = R.steps; rpeak = nr; } }
        if (peak >= 8 && 2 * mx <= peak) {
            if (lastpk && (double)peak >= 1.4 * (double)lastpk) { if (++g > R.G) R.G = g; } else g = 0;
            lastpk = peak; if (R.pk.size() < 400) R.pk.push_back(peak); peak = mx; if (R.fr0 == 0) R.fr0 = R.steps; R.npk++;
        }
        for (auto it2 = cutpre.begin(); it2 != cutpre.end();) {
            int i = it2->first;
            if (i < (int)Be.size() && Be[i].n >= 2 * it2->second + 4) { R.promos++; it2 = cutpre.erase(it2); } else ++it2;
        }
        if (s.has) {
            size_t m = std::min(s.prev.size(), Be.size()), c = 0;
            while (c < m && s.prev[c].b == Be[c].b) ++c;
            s.fell.resize(Be.size());
            for (size_t i = c; i < Be.size(); ++i) s.fell[i] = 0;
            bool cut = false;
            s.ns++;
            size_t nb = Be.size();
            s.pkv.resize(nb); s.low.resize(nb); s.refv.resize(nb); s.sdec.resize(nb); s.mark.resize(nb); s.lds.resize(nb);
            for (size_t i = c; i < nb; ++i) { s.pkv[i] = Be[i].n; s.low[i] = Be[i].n <= 2; s.refv[i] = 0; s.sdec[i] = 0; s.mark[i] = s.resets; s.lds[i] = s.ns; }
            for (size_t i = 0; i < c; ++i) {   // slow refilled counters (Ackermann refill signature)
                u64 v = Be[i].n, pv = s.prev[i].n;
                if (v > s.pkv[i]) s.pkv[i] = v;
                if (s.pkv[i] >= 8 && 2 * v <= s.pkv[i]) { s.resets++; s.pkv[i] = v; R.nsr++; if (R.sr0 == 0) R.sr0 = R.steps; }
                if (v < pv) {
                    if (s.ns - s.lds[i] >= 4) s.sdec[i]++;
                    s.mark[i] = s.resets; s.lds[i] = s.ns;
                    if (s.refv[i] >= 6 && s.sdec[i] >= 2 && !s.counted(i)) { R.sc++; R.scmax = std::max<u64>(R.scmax, s.refv[i]); s.cnt.push_back((int)i); }
                } else if (v > pv) {
                    if (s.low[i] && v >= 6) s.refv[i] = std::max(s.refv[i], v);
                    s.sdec[i] = 0;
                }
                if (v <= 2) { s.low[i] = 1; s.refv[i] = 0; }
            }
            for (size_t i = 0; i < c; ++i) {
                if (Be[i].n < s.prev[i].n) s.fell[i]++; else if (Be[i].n > s.prev[i].n) s.fell[i] = 0;
                if (doshrink && !cut && R.rounds < MAXCUTS && (SLOWCUT ? s.sdec[i] >= 2 : s.fell[i] >= 3) && Be[i].n >= SMIN) {
                    u64 nv = cutto(Be[i].n);
                    if (TRACE) fprintf(stderr, "cut r%d sr=%d it=%llu idx=%zu/%zu %llu->%llu\n", R.rounds, R.cursr, it, i, Be.size(), Be[i].n, nv);
                    cutpre[(int)i] = Be[i].n; Be[i].n = nv; s.fell[i] = 0; cut = true; R.rounds++; R.lv.insert((int)i);
                    if (haveRS) {
                        size_t mm = std::min(roundstart.size(), Be.size()), d = 0;
                        while (d < mm && roundstart[d].b == Be[d].b && roundstart[d].n == Be[d].n) ++d;
                        R.mind = std::min(R.mind, (int)d);
                    }
                    roundstart = Be; haveRS = true;
                }
            }
        }
        s.prev = Be; s.has = true;
    }
    R.macros = maxm; return R;
}
int main(int argc, char **argv) {
    std::vector<std::string> pos; int fixK = 0; u64 pilot = 30000, pilot2 = 300000; bool ponly = false, k2 = false;
    for (int i = 1; i < argc; ++i) {
        if (!strncmp(argv[i], "--K=", 4)) fixK = atoi(argv[i] + 4);
        else if (!strncmp(argv[i], "--pilot=", 8)) pilot = strtoull(argv[i] + 8, 0, 10);
        else if (!strncmp(argv[i], "--shrink=", 9)) SHRINK = atoi(argv[i] + 9) != 0;
        else if (!strncmp(argv[i], "--smin=", 7)) SMIN = strtoull(argv[i] + 7, 0, 10);
        else if (!strncmp(argv[i], "--mod=", 6)) MOD = atoi(argv[i] + 6);
        else if (!strcmp(argv[i], "--trace")) TRACE = true;
        else if (!strcmp(argv[i], "--pilotonly")) { ponly = true; LITE = true; }
        else if (!strcmp(argv[i], "--k2")) k2 = true;
        else if (!strcmp(argv[i], "--small")) { SHRINKLIST = true; }
        else if (!strcmp(argv[i], "--life")) LIFE = true;
        else if (!strcmp(argv[i], "--slowcut")) SLOWCUT = true;
        else if (!strncmp(argv[i], "--dumpat=", 9)) DUMPAT = strtoull(argv[i] + 9, 0, 10);
        else if (!strncmp(argv[i], "--dumpq=", 8)) DUMPQ = argv[i][8] - 'A';
        else if (!strcmp(argv[i], "--nolist")) NOLIST = true;
        else if (!strncmp(argv[i], "--maxcuts=", 10)) MAXCUTS = atoi(argv[i] + 10);
        else if (!strncmp(argv[i], "--show=", 7)) { SHOW = strtoull(argv[i] + 7, 0, 10); }
        else if (!strncmp(argv[i], "--pilot2=", 9)) pilot2 = strtoull(argv[i] + 9, 0, 10);
        else if (argv[i][0] == '-' && argv[i][1] == '-') { fprintf(stderr, "unknown option %s\n", argv[i]); return 2; }
        else pos.push_back(argv[i]);
    }
    if (pos.size() < 2) { fprintf(stderr, "usage: nlp7 INPUT OUTPUT [MACRO]\n"); return 2; }
    u64 maxm = pos.size() > 2 ? strtoull(pos[2].c_str(), 0, 10) : 2000000;
    std::ifstream in(pos[0]); std::ofstream out(pos[1]);
    out << "machine\tK\tnat\tnat_lg\tmaxcnt\tmaxruns\tSRs\tSRmax\tSRK\tSRend\tSRsit_lg\tk2_lg\tSC\tSCmax\tSCK\tk2nat\tFR\tshape\n";
    std::string line; long long n = 0;
    while (std::getline(in, line)) {
        size_t sp = line.find_first_of(" \t\r"); if (sp != std::string::npos) line.resize(sp);
        if (line.find('_') == std::string::npos || !parse(line)) continue;
        int bestK = fixK; LD bests = -1;
        if (!fixK) for (int k = 1; k <= 6; ++k) {
            K = k; memset(cache, 0, sizeof cache);
            Res r = runm(pilot, false);
            LD sc = r.halt ? 1e300L : r.steps;
            if (sc > bests * 1.05L) { bests = sc; bestK = k; }
        }
        if (ponly) {
            double p2 = -1; Res pr;
            if (bests < 1e299L) { K = bestK; memset(cache, 0, sizeof cache); pr = runm(pilot2, false); p2 = pr.halt ? 99.0 : (double)log10l(pr.steps + 1); }
            char pb[320]; snprintf(pb, sizeof pb, "%s\t%d\t%.3f\t%.3f\t%d\t%.2f\t%d\t%.2f\t%llu\t%d\t%.2f\n", line.c_str(), bestK, bests >= 1e299L ? -1.0 : (double)log10l(bests + 1), p2, pr.npk, pr.fr0 > 0 ? (double)log10l(pr.fr0) : -1.0, pr.nrd, pr.rd0 > 0 ? (double)log10l(pr.rd0) : -1.0, pr.maxcnt, pr.nsr, pr.sr0 > 0 ? (double)log10l(pr.sr0) : -1.0); out << pb; if (++n % 1000 == 0) out.flush(); continue; }
        K = bestK; memset(cache, 0, sizeof cache);
        if (LIFE) {
            int Ks = fixK ? fixK : bestK; K = Ks; memset(cache, 0, sizeof cache);
            Res f = runm(maxm, false);
            u64 tot = f.macros ? f.macros : maxm;
            char sb3[300]; snprintf(sb3, sizeof sb3, "%s\t%d\t%d\t%.3f\t%d\t%s\n", line.c_str(), K, f.srl, (double)f.srlife / (double)tot, f.srs, f.halt ? "HALT" : "-");
            out << sb3; out.flush(); continue;
        }
        if (SHRINKLIST) {
            int Ks = fixK ? fixK : bestK; K = Ks; memset(cache, 0, sizeof cache);
            Res f = runm(maxm, true);
            // HT: rounds spent at successive list lengths v, v-1, v-2, ... (list consumed one item at a time)
            std::vector<u64> iv; int ht = 0, run = 0;
            for (size_t i = 0; i + 1 <= f.srhist.size(); ++i) {
                u64 v = f.srhist[i].second, r0 = f.srhist[i].first, r1 = i + 1 < f.srhist.size() ? f.srhist[i + 1].first : (u64)f.rounds;
                if (v < 4) continue;
                if (i + 1 < f.srhist.size() && f.srhist[i + 1].second + 1 != v) { iv.clear(); continue; }
                iv.push_back(r1 - r0 + 1);
            }
            for (size_t i = 1; i < iv.size(); ++i) { if ((double)iv[i] >= 2.5 * (double)iv[i - 1]) { if (++run > ht) ht = run; } else run = 0; }
            std::string ivs; for (size_t i = iv.size() > 8 ? iv.size() - 8 : 0; i < iv.size(); ++i) ivs += std::to_string(iv[i]) + ",";
            if (ivs.empty()) ivs = "-";
            char sb2[300]; snprintf(sb2, sizeof sb2, "%s\t%d\t%s\t%d\t%d\t%zu\t%.2f\n", line.c_str(), K, f.halt ? "HALT" : f.loop ? "LOOP" : "-", f.listcut, f.rounds, f.lv.size(), (double)log10l(f.steps + 1));
            out << std::string(sb2, strlen(sb2) - 1) << "\t" << ht << "\t" << ivs << "\n"; out.flush(); continue;
        }
        Res a = runm(maxm, false);
        auto st = [](const Res &r) { return r.halt ? std::string("HALT") : r.loop ? std::string("LOOP") : std::string("-"); };
        Res c; int srk = K;
        if (k2 && K != 2 && !a.halt && !a.loop) { K = 2; memset(cache, 0, sizeof cache); c = runm(maxm / 2, false); K = srk; }
        const Res &sb = c.srs > a.srs ? c : a; int kk = c.srs > a.srs ? 2 : srk;
        const Res &sx = c.sc > a.sc ? c : a; int kx = c.sc > a.sc ? 2 : srk;
        char buf[600];
        snprintf(buf, sizeof buf, "%s\t%d\t%s\t%.2f\t%llu\t%zu\t%d\t%d\t%d\t%d\t%.2f\t%.2f\t%d\t%llu\t%d\t%s\t", line.c_str(), K, st(a).c_str(),
                 (double)log10l(a.steps + 1), a.maxcnt, a.maxruns, sb.srs, std::max(a.sr, c.sr), kk, sb.srend,
                 (double)log10((double)sb.srsit + 1), c.halt ? 99.0 : (double)log10l(c.steps + 1), sx.sc, sx.scmax, kx, st(c).c_str());
        out << buf << std::max(a.fr, c.fr) << "\t" << (sb.srshape.empty() ? "-" : sb.srshape) << "\n";
        if (++n % 200 == 0) out.flush();
    }
    out << "#summary\tmachines=" << n << "\n";
}
