// nlp7_fr_gen.cpp: Generalized frontier-decrement & glitch-safe HT probe for Tier-4 analysis.
// Based on nonlist/nlp7.cpp.
// Modes:
//   --frgen : Blank-tape run (default 1M macro steps at K and 0.5M at K=2, or fixed --K=k) checking:
//             FR1 (step -1), FR2 (step -2), FR3 (step -3), FR46 (step -4..-6), FRpair (2-run sum step -1..-4),
//             and whether the frontier slot also REFILLED (v >= last + 4) after a slow decrement.
//   --htsafe: Forced run (--small --nolist) that records both standard HT and max-before-clear HT_max
//             (so iv.clear() at list exhaustion v=4->2/0 cannot hide an earlier HT>=3 cascade).
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
static const int FW = 8;
struct Series {
    u64 last = 0, srh = 0, srstart = 0; int srstreak = 0; bool has = false; std::vector<Run> prev; std::vector<int> fell;
    u64 fdl[16] = {}, fdv1[16] = {}, fdv2[16] = {}, fdv3[16] = {}, fdv46[16] = {};
    int fds[16] = {}, fds1[16] = {}, fds2[16] = {}, fds3[16] = {}, fds46[16] = {};
    bool fdhas_sdec[16] = {};
    // Pair sum tracking around frontier
    u64 fpl[16] = {}, fpv[16] = {}; int fps[16] = {}, fpslow[16] = {};
    int ns = 0, resets = 0; std::vector<u64> pkv, refv; std::vector<char> low; std::vector<int> sdec, mark, lds, cnt;
    bool counted(size_t i) const { for (int x : cnt) if (x == (int)i) return true; return false; }
};
struct Res {
    int halt = 0; LD steps = 0; u64 macros = 0; int loop = 0;
    int rounds = 0, promos = 0, fhalt = -1; std::set<int> lv; u64 maxcnt = 0; size_t maxruns = 0; int G = 0, mind = 1 << 30;
    int sr = 0, srp = 0, srend = 0, srs = 0, sc = 0; u64 scmax = 0;
    u64 fr1 = 0, fr2 = 0, fr3 = 0, fr46 = 0, frref = 0, frpair = 0;
    int listcut = 0, cursr = 0;
    std::vector<std::pair<u64,u64>> srhist;
    int srl = 0; u64 srlife = 0;
};
static int MOD = 6; static u64 SMIN = 24; static bool NOLIST = false; static int MAXCUTS = 1 << 30;
static u64 cutto(u64 n) { u64 r = n % MOD; u64 v = r; while (v < 2) v += MOD; return v < n ? v : n; }

static Res runm(u64 maxm, bool doshrink) {
    Res R; std::vector<Run> L, Rt; int q = 0, side = 0; u64 cur = 0;
    static Series ser[2][16];
    for (int e = 0; e < 2; ++e) for (int k = 0; k < 16; ++k) ser[e][k] = Series();
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
        if (s.has && it - s.last < std::max<u64>(8, 2 * Be.size())) continue;
        s.last = it;
        u64 mx = 0; for (auto &r : Be) mx = std::max(mx, r.n);
        R.maxcnt = std::max(R.maxcnt, mx); R.maxruns = std::max(R.maxruns, Be.size());
        {
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
            if (best > R.sr) { R.sr = best; R.srp = bp; }
            if (s.srstreak >= 5 && best > R.srs) { R.srs = best; }
            R.srend = best;
            if (best != R.cursr) { if (R.srhist.size() < 8000) R.srhist.push_back({(u64)R.rounds, (u64)best}); R.cursr = best; }
            if (best >= 4) {
                for (int o = -FW; o < FW; ++o) {
                    int j = o < 0 ? bs + o : bs + bp * best + o, k = o + FW;
                    u64 v = (j >= 0 && j < nb) ? Be[j].n : 0, last = s.fdl[k];
                    if (v == last) s.fds[k]++;
                    else {
                        if (v < last && s.fds[k] >= 3 && last >= 6 && 2 * last < mx) {
                            u64 diff = last - v;
                            if (diff == 1) {
                                if (++s.fds1[k] >= 2) R.fr1 = std::max(R.fr1, s.fdv1[k] = std::max(s.fdv1[k], last));
                                else s.fdv1[k] = std::max(s.fdv1[k], last);
                                s.fdhas_sdec[k] = true;
                            } else if (diff == 2) {
                                if (++s.fds2[k] >= 2) R.fr2 = std::max(R.fr2, s.fdv2[k] = std::max(s.fdv2[k], last));
                                else s.fdv2[k] = std::max(s.fdv2[k], last);
                                s.fdhas_sdec[k] = true;
                            } else if (diff == 3) {
                                if (++s.fds3[k] >= 2) R.fr3 = std::max(R.fr3, s.fdv3[k] = std::max(s.fdv3[k], last));
                                else s.fdv3[k] = std::max(s.fdv3[k], last);
                                s.fdhas_sdec[k] = true;
                            } else if (diff >= 4 && diff <= 6) {
                                if (++s.fds46[k] >= 2) R.fr46 = std::max(R.fr46, s.fdv46[k] = std::max(s.fdv46[k], last));
                                else s.fdv46[k] = std::max(s.fdv46[k], last);
                                s.fdhas_sdec[k] = true;
                            }
                        } else if (v > last) {
                            if (s.fdhas_sdec[k] && v >= last + 4 && 2 * v < mx) {
                                R.frref = std::max(R.frref, v);
                            }
                            s.fds1[k] = s.fds2[k] = s.fds3[k] = s.fds46[k] = 0;
                        }
                        s.fds[k] = 0;
                    }
                    s.fdl[k] = v;

                    // Adjacent 2-run sum check (j, j+1)
                    u64 pv = (j >= 0 && j + 1 < nb) ? (Be[j].n + Be[j + 1].n) : 0, plast = s.fpl[k];
                    if (pv == plast) s.fps[k]++;
                    else {
                        if (pv < plast && plast - pv <= 4 && s.fps[k] >= 3 && plast >= 8 && 2 * plast < mx) {
                            if (++s.fpslow[k] >= 2) R.frpair = std::max(R.frpair, s.fpv[k] = std::max(s.fpv[k], plast));
                            else s.fpv[k] = std::max(s.fpv[k], plast);
                        } else if (pv > plast) s.fpslow[k] = 0;
                        s.fps[k] = 0;
                    }
                    s.fpl[k] = pv;
                }
            }
        }
        if (s.has) {
            size_t m = std::min(s.prev.size(), Be.size()), c = 0;
            while (c < m && s.prev[c].b == Be[c].b) ++c;
            s.fell.resize(Be.size());
            for (size_t i = c; i < Be.size(); ++i) s.fell[i] = 0;
            bool cut = false;
            for (size_t i = 0; i < c; ++i) {
                if (Be[i].n < s.prev[i].n) s.fell[i]++; else if (Be[i].n > s.prev[i].n) s.fell[i] = 0;
                if (doshrink && !cut && R.rounds < MAXCUTS && s.fell[i] >= 3 && Be[i].n >= SMIN) {
                    u64 nv = cutto(Be[i].n);
                    Be[i].n = nv; s.fell[i] = 0; cut = true; R.rounds++; R.lv.insert((int)i);
                }
            }
        }
        s.prev = Be; s.has = true;
    }
    R.macros = maxm; return R;
}

static int calc_ht(const std::vector<u64> &iv) {
    int ht = 0, run = 0;
    for (size_t i = 1; i < iv.size(); ++i) {
        if ((double)iv[i] >= 2.5 * (double)iv[i - 1]) { if (++run > ht) ht = run; } else run = 0;
    }
    return ht;
}

int main(int argc, char **argv) {
    std::vector<std::string> pos; int fixK = 0; bool htsafe = false;
    for (int i = 1; i < argc; ++i) {
        if (!strncmp(argv[i], "--K=", 4)) fixK = atoi(argv[i] + 4);
        else if (!strcmp(argv[i], "--htsafe")) htsafe = true;
        else pos.push_back(argv[i]);
    }
    if (pos.size() < 2) { fprintf(stderr, "usage: nlp7_fr_gen INPUT OUTPUT [MACRO] [--K=k] [--htsafe]\n"); return 2; }
    u64 maxm = pos.size() > 2 ? strtoull(pos[2].c_str(), 0, 10) : 1000000;
    std::ifstream in(pos[0]); std::ofstream out(pos[1]);
    std::string line;
    while (std::getline(in, line)) {
        size_t sp = line.find_first_of(" \t\r"); if (sp != std::string::npos) line.resize(sp);
        if (line.find('_') == std::string::npos || !parse(line)) continue;
        K = fixK ? fixK : 2;
        memset(cache, 0, sizeof cache);
        if (htsafe) {
            NOLIST = true;
            Res f = runm(maxm, true);
            std::vector<u64> iv, best_iv;
            int max_ht = 0;
            for (size_t i = 0; i + 1 <= f.srhist.size(); ++i) {
                u64 v = f.srhist[i].second, r0 = f.srhist[i].first, r1 = i + 1 < f.srhist.size() ? f.srhist[i + 1].first : (u64)f.rounds;
                if (v < 4) continue;
                iv.push_back(r1 - r0 + 1);
                int hcur = calc_ht(iv);
                if (hcur >= max_ht) { max_ht = hcur; best_iv = iv; }
                if (i + 1 < f.srhist.size() && f.srhist[i + 1].second + 1 != v) { iv.clear(); continue; }
            }
            int std_ht = calc_ht(iv);
            std::string ivs; for (size_t i = best_iv.size() > 8 ? best_iv.size() - 8 : 0; i < best_iv.size(); ++i) ivs += std::to_string(best_iv[i]) + ",";
            if (ivs.empty()) ivs = "-";
            out << line << "\t" << K << "\t" << (f.halt ? "HALT" : f.loop ? "LOOP" : "-") << "\t"
                << f.rounds << "\t" << f.lv.size() << "\t" << std_ht << "\t" << max_ht << "\t" << ivs << "\n";
        } else {
            Res f = runm(maxm, false);
            out << line << "\t" << K << "\t" << (f.halt ? "HALT" : f.loop ? "LOOP" : "-") << "\t"
                << f.srl << "\t" << f.srs << "\t" << f.fr1 << "\t" << f.fr2 << "\t" << f.fr3 << "\t"
                << f.fr46 << "\t" << f.frref << "\t" << f.frpair << "\n";
        }
    }
    return 0;
}
