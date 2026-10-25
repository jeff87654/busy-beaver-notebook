// dlscan3: nested digit-list detector (f_{omega+1} class), built on dlscan2.            (v4, 2026-10-07)
//
//   dlscan3 INPUT OUTPUT [CENSUS=1000000] [N=20000] [--all] [--span=32768] [--chainN=1000000] [--cap=40000000]
//           [--post=0] [--debug]
//   dlscan3 --tmpl MACHINE O Q P u s alpha beta alphaB betaB S [N [KOBS]]   outer analysis of one hand-written template
//
// dlscan2 recognises an f_omega engine: configurations K(ds; a; b) = P u^(al d1+be) s ... u^(al a+be) s u^(alB b+beB) S
// with rules R1-R3 fitted on probes. The f_{omega+1} champions (BB(13)-BB(16); see ../nested_detector.md) keep such
// an engine to the right of an OUTER part (a counter) and, when the inner list is used up, consume one unit of the
// counter and rebuild an inner list whose LENGTH grows with the accumulator b:
//   BB(13)  (110)^n 1 0 [inner] 1^b       -> (110)^(n-1) 1 0 [about b digits] ...,   n = 0 halts
//   BB(14)  1^(2n+r) 00 1 0 [inner] 1^b   -> 1^(2n-2+r) 00 [about b/2 digits] ...,   n = 0: r = 1 halts, r = 0
//                                              creates a new counter 1^(b-2)
//   BB(15)  10 1 0 1^b                    -> 1^(b+3) 00 [small list]  (the counter is created from b)
// dlscan3 adds:
// 1. Census snapshots up to --span cells (dlscan2: 4000; BB(13)'s counter alone is 6,000 cells), and the 6 most
//    recently sampled end kinds besides the 12 commonest (a late phase is not crowded out).
// 2. Long-prefix templates: the list is parsed from the head end as far as its runs decode, and the rest of the
//    snapshot, however long, becomes the template prefix P (dlscan2 allows at most 4 cells). R1-R3 are fitted
//    as in dlscan2 with that P. (dlscan2's own templates come from a memoised copy of its inference.)
// 3. Outer analysis of every fitted template: "exhaustion probes" E(P; k; b) = P (u^be s)^k u^be s u^(alB b+beB) S
//    (list used up: k zero digits, a = 0) are run until a STABLE family configuration (two consecutive
//    configurations with the same outer part and digit count, b increasing: the engine is running again). Its
//    outer part P' is whatever is left of the decodable list. Probe pairs b, b + 1 classify one step:
//      H halt, R rebuild (same P', digit count larger for b+1), C counter creation (P' longer for b+1),
//      F refill (same P', same count), T timeout / no stable configuration, r (only b+1 halts), X other.
//    A CHAIN repeats this from the outer part each step leaves (with k = its digit count), b = b1 fixed (2..5), up
//    to 40 steps, stopping at H, T or a loop L (an outer state repeats, 3 R steps leave P unchanged, or the
//    sequence of (P', step) becomes periodic). Leading-digit chains keep the list's first digit (from 2) instead
//    of zeroing it. Long periodic blocks of P (an observed counter) are shrunk to 6..11 periods (residue mod 6 kept).
// 4. Grades (best first):
//      W1-HALTER   a chain halts after >= 1 rebuild, the halt is confirmed with b > k at the halting exhaustion,
//                  and the number of rebuilds before the halt grows strictly over three variants of an identified
//                  counter: the periodic block of P (+6, +12 periods), b at counter-creation steps (+6, +12), or
//                  the leading digit (2, 8, 14). f_{omega+1}-class halter.
//      W1-HALT?    as W1-HALTER, but the halt needs b <= k (not reachable in a real run, where b >> k)
//      W1-LOOPER   a created counter is consumed by >= 2 rebuilds, and no chain halts
//      MULTI k     a chain halts (confirmed) after k >= 1 rebuilds, k not counter-driven: f_omega^(k+1) class
//      MULTI?      the same, unconfirmed (the halt needs b <= k: e.g. the 76450 family, proved non-halting)
//      LOOPER      a chain loops with rebuilds (each rebuild clears and rebuilds the list forever; rec14 loopers)
//      REBUILD     some exhaustion step rebuilds, no conclusion
//      then dlscan2's grades for the rest (CHAMPION, R4-SOME, HALT?, HALT-SOME, CHECK, NOBOUNDARY, SAFE).
// --post=S: when no outer grade was found and an exhaustion probe timed out, run an S-step census from that used-up
// configuration and analyse the list families it shows (off by default: costly, and nothing new in tests).
// OUTPUT (TSV): machine, halted_step, n_templates, grade, template, w1 (chain summary), dlscan2 params; only machines
// with an R1-R3 fit unless --all. Chain summary: per b1 "b1:events/nR", lead chains, the counter tests ("|...")
// and the b > k confirmation ("b>k:H...").
// Debug hooks (environment): DL3_NOLONG, DL3_OLDCOLLECT, DL3_SNAPSTAT, DL3_CMPINF (check the memoised inference).
#include "dlscan2_core.inc"

#include <unordered_map>
#include <string_view>
#include <chrono>
static double g_t[6];   // seconds in census, template inference, R1-R3 fits, outer analysis
static double now_s() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }

static long long g_span = 32768;
static bool g_debug = false;
static long long g_cap = 40000000;      // steps of exhaustion probes per machine

// ------------------------------------------------------------------------------------------------- census
// As dlscan2's End2, plus the time of each kind's latest snapshot: collect3() keeps the 12 commonest kinds AND the
// 6 kinds with the most recent snapshots (BB(13) reaches its nested phase after 1.2e7 steps, when the early kinds
// have thousands of events and the new ones a dozen).
static long long g_step = 0;    // the census step, for snapshot times
struct End3 : End2 {
    std::map<std::pair<int, std::string>, long long> last;
    std::map<std::pair<int, std::string>, long long> lastocc;    // kind -> census step of its latest event
    std::unordered_map<size_t, std::pair<int, std::string>> kindof;   // hash(state, snapshot) -> its kind
    long long ev = 0;
    static size_t h(int q, const std::string &w) { return std::hash<std::string>()(w) * 31 + (size_t)q; }
    // the latest event of the kind this snapshot was taken from
    long long step_of(int q, const std::string &w) const {
        auto it = kindof.find(h(q, w));
        if (it == kindof.end()) return -1;
        auto jt = lastocc.find(it->second);
        return jt == lastocc.end() ? -1 : jt->second;
    }
    void collect3() {
        collect();
        std::set<std::pair<int, std::string>> taken;
        std::vector<std::pair<long long, long long>> cnt;
        for (auto &kv : kinds) cnt.push_back({kv.second.n, 0});
        // the kinds collect() took: the 12 commonest
        std::vector<std::pair<long long, std::pair<int, std::string>>> order;
        for (auto &kv : kinds) order.push_back({kv.second.n, kv.first});
        std::sort(order.begin(), order.end(), [](const auto &a, const auto &b) { return a.first > b.first; });
        for (size_t i = 0; i < order.size() && i < 12; ++i) taken.insert(order[i].second);
        std::vector<std::pair<long long, std::pair<int, std::string>>> rec;
        for (auto &kv : last) if (!taken.count(kv.first)) rec.push_back({kv.second, kv.first});
        std::sort(rec.begin(), rec.end(), [](const auto &a, const auto &b) { return a.first > b.first; });
        for (size_t i = 0; i < rec.size() && i < 6; ++i)
            for (auto &w : kinds[rec[i].second].snaps) snaps.push_back({rec[i].second.first, w});
    }
};

static void end_event3(End3 &e, const uint8_t *T, int q, long long &farB, long long pos, int dir) {
    std::string tail(12, '0');
    for (int i = 0; i < 12; ++i) tail[11 - i] = char('0' + T[pos - dir * (i + 1)]);
    auto key = std::make_pair(q, tail);
    auto it = e.kinds.find(key);
    if (it == e.kinds.end()) {
        if (e.kinds.size() >= 64) return;
        it = e.kinds.emplace(key, Kind()).first;
    }
    Kind &k = it->second;
    long long n = ++k.n;
    e.lastocc[key] = g_step;
    if ((n & (n - 1)) != 0 && n % 256 != 0) return;
    while (T[farB] == 0) farB += dir;
    long long span = dir > 0 ? pos - farB : farB - pos;
    if (span > g_span) return;
    std::string w; w.reserve(span);
    for (long long i = farB; i != pos; i += dir) w += char('0' + T[i]);
    if (!k.snaps.empty() && k.snaps.back() == w) return;
    if (k.snaps.size() >= 2) k.snaps.erase(k.snaps.begin());
    k.snaps.push_back(w);
    e.last[key] = ++e.ev;
    e.kindof[End3::h(q, w)] = key;
}

// word: optional start tape, left of the head (head on the blank right of it, in state q0)
static long long census3(const TM &m, long long steps, End3 ends[2], const std::string *word = nullptr, int q0 = 0) {
    std::vector<uint8_t> tape(1 << 12, 0);
    while (word && (long long)tape.size() < 4 * (long long)word->size() + 64) tape.assign(tape.size() * 2, 0);
    long long off = tape.size() / 2, pos = 0, loB = 1, hiB = 0;
    int q = 0;
    if (word) {
        q = q0;
        long long L = (long long)word->size();
        for (long long i = 0; i < L; ++i) if ((*word)[i] == '1') {
            tape[off - L + i] = 1;
            if (loB > hiB) loB = hiB = i - L; else hiB = i - L;
        }
    }
    for (long long t = 0; t < steps; ++t) {
        g_step = t;
        long long idx = pos + off;
        if (idx < 4 || idx + 4 >= (long long)tape.size()) {
            std::vector<uint8_t> nt(tape.size() * 2, 0);
            long long shift = tape.size() / 2;
            memcpy(nt.data() + shift, tape.data(), tape.size());
            off += shift; tape.swap(nt); idx = pos + off;
        }
        const uint8_t *T = tape.data() + off;
        int c = T[pos];
        if (c == 0 && loB <= hiB) {
            bool lft = T[pos - 1] | T[pos - 2] | T[pos - 3] | T[pos - 4];
            bool rgt = T[pos + 1] | T[pos + 2] | T[pos + 3] | T[pos + 4];
            if (lft && !rgt) {
                bool clear = true;
                while (hiB > pos) { if (T[hiB]) { clear = false; break; } --hiB; }
                if (clear) { while (!T[hiB]) --hiB; end_event3(ends[0], T, q, loB, pos, 1); }
            } else if (rgt && !lft) {
                bool clear = true;
                while (loB < pos) { if (T[loB]) { clear = false; break; } ++loB; }
                if (clear) { while (!T[loB]) ++loB; end_event3(ends[1], T, q, hiB, pos, -1); }
            }
        }
        if (m.nx[q][c] < 0) return t;
        int w = m.w[q][c], d = m.d[q][c], nq = m.nx[q][c];
        tape[idx] = (uint8_t)w;
        if (w) {
            if (loB > hiB) loB = hiB = pos;
            else { if (pos < loB) loB = pos; if (pos > hiB) hiB = pos; }
        }
        pos += d; q = nq;
    }
    return -1;
}

// dlscan2's infer_templates with the same result, faster: for a unit and separator, the suffix length L only changes
// the first (accumulator) run, so the parse after its separator is memoised by its start.
static std::vector<Tmpl> infer_templates_fast(const End2 &e) {
    const int NU = sizeof UNITS2 / sizeof *UNITS2, NS = sizeof SEPS2 / sizeof *SEPS2;
    std::map<std::tuple<int, std::string, std::string, std::string, std::string>, Cand> cands;
    std::vector<std::vector<int>> cnt(NU);
    for (auto &sn : e.snaps) {
        const std::string &w = sn.second;
        long long len = (long long)w.size();
        for (int ui = 0; ui < NU; ++ui) {
            long long ul = (long long)strlen(UNITS2[ui]);
            cnt[ui].assign(len + 1, 0);
            for (long long x = ul; x <= len; ++x)
                if (memcmp(w.data() + x - ul, UNITS2[ui], ul) == 0) cnt[ui][x] = cnt[ui][x - ul] + 1;
        }
        std::set<std::tuple<int, std::string, std::string, std::string, std::string>> seen;
        struct M { bool ok = false; std::vector<long long> runs; long long x = 0; };
        for (int ui = 0; ui < NU; ++ui) for (int si = 0; si < NS; ++si) {
            std::string u = UNITS2[ui], s = SEPS2[si];
            if (u == s) continue;
            long long ul = (long long)u.size(), sl = (long long)s.size();
            std::unordered_map<long long, M> memo;
            for (int L = 0; L <= 12 && L < len; ++L) {
                long long x0 = len - L, k0 = cnt[ui][x0], xa = x0 - k0 * ul;
                if (!ends_with(w.data(), xa, s)) continue;
                long long x1 = xa - sl;
                if (x1 < 0) continue;
                auto it = memo.find(x1);
                if (it == memo.end()) {
                    M mm;
                    long long x = x1;
                    for (int guard = 1; guard < 4000; ++guard) {
                        long long k = cnt[ui][x];
                        x -= k * ul;
                        mm.runs.push_back(k);
                        if (mm.runs.size() + 1 >= 4 && x <= 4 && (x == 0 || w[0] == '1')) { mm.ok = true; break; }
                        if (!ends_with(w.data(), x, s)) break;
                        x -= sl;
                        if (x < 0) break;
                    }
                    mm.x = x;
                    it = memo.emplace(x1, std::move(mm)).first;
                }
                const M &mm = it->second;
                if (!mm.ok) continue;
                int big = 0;
                for (long long r : mm.runs) if (r >= 2) ++big;
                if (big < 2) continue;
                std::string S = w.substr(len - L);
                auto key = std::make_tuple(sn.first, S, w.substr(0, mm.x), u, s);
                if (seen.count(key)) continue;
                seen.insert(key);
                Cand &c = cands[key];
                c.q = sn.first; c.S = S; c.P = w.substr(0, mm.x); c.u = u; c.s = s; c.score++;
                c.accraw.push_back(k0);
                for (long long r : mm.runs) c.digraw.push_back(r);
            }
        }
    }
    // Group the candidates by (state, prefix, unit, separator); keep the best groups and, in each, the shortest
    // suffixes with the best score. (A longer suffix that swallows part of the accumulator cannot express an
    // empty accumulator, so the shortest suffix is the safe reading.)
    std::map<std::tuple<int, std::string, std::string, std::string>, std::vector<Cand>> groups;
    for (auto &kv : cands) if (kv.second.score >= 2)
        groups[std::make_tuple(kv.second.q, kv.second.P, kv.second.u, kv.second.s)].push_back(kv.second);
    std::vector<std::pair<int, std::vector<Cand>>> gl;
    for (auto &kv : groups) {
        int best = 0;
        for (auto &c : kv.second) best = std::max(best, c.score);
        std::vector<Cand> cs = kv.second;
        std::stable_sort(cs.begin(), cs.end(), [](const Cand &a, const Cand &b) {
            if (a.score != b.score) return a.score > b.score;
            return a.S.size() < b.S.size();
        });
        if (cs.size() > 6) cs.resize(6);
        gl.push_back({best, cs});
    }
    std::stable_sort(gl.begin(), gl.end(), [](const auto &a, const auto &b) { return a.first > b.first; });
    if (gl.size() > 8) gl.resize(8);
    // Encodings: alpha = 1, plus every alpha up to 6 whose most common residue covers 80% of the run lengths
    // (transitional configurations sampled at the same tape end can spoil an exact gcd).
    auto enc = [](const std::vector<long long> &raw, std::vector<std::pair<long long, long long>> &res) {
        res.push_back({1, 0});
        for (long long al = 2; al <= 6; ++al) {
            std::map<long long, int> cnt;
            for (long long r : raw) cnt[r % al]++;
            auto top = std::max_element(cnt.begin(), cnt.end(), [](const auto &a, const auto &b) { return a.second < b.second; });
            if (top->second * 5 >= (int)raw.size() * 4) res.push_back({al, top->first});
        }
        if (res.size() > 3) res.resize(3);
    };
    std::vector<Tmpl> out;
    for (auto &g : gl) for (auto &c : g.second) {
        std::vector<std::pair<long long, long long>> ed, eb;
        enc(c.digraw, ed); enc(c.accraw, eb);
        for (auto &d : ed) for (auto &b : eb) {
            Tmpl t; t.q = c.q; t.P = c.P; t.u = c.u; t.s = c.s; t.S = c.S;
            t.al = d.first; t.be = d.second; t.alB = b.first; t.beB = b.second;
            out.push_back(t);
        }
    }
    return out;
}


// ---------------------------------------------------------------------------------- long-prefix templates
static bool dec1(long long raw, long long al, long long be, long long &v) {
    if (raw < be || (raw - be) % al) return false;
    v = (raw - be) / al; return true;
}

// Encodings of the rightmost digit runs (as dlscan2's enc: alpha = 1 plus every alpha <= 6 whose commonest residue
// covers 80% of the runs).
static void enc3(const std::vector<long long> &raw, std::vector<std::pair<long long, long long>> &res) {
    res.push_back({1, 0});
    for (long long al = 2; al <= 6; ++al) {
        int cnt[6] = {0, 0, 0, 0, 0, 0};
        for (long long r : raw) cnt[r % al]++;
        int top = 0;
        for (int i = 1; i < al; ++i) if (cnt[i] > cnt[top]) top = i;
        if (cnt[top] * 5 >= (int)raw.size() * 4) res.push_back({al, (long long)top});
    }
    if (res.size() > 3) res.resize(3);
}

// For each snapshot and (suffix, unit, separator, digit encoding): parse runs from the head end while they decode;
// at least a and 2 digits, two of them >= 2. The rest of the snapshot is P (any length).
static std::vector<Tmpl> infer_long(const End2 &e) {
    const int NU = sizeof UNITS2 / sizeof *UNITS2, NS = sizeof SEPS2 / sizeof *SEPS2;
    struct LC { int q; std::string P, u, s, S; long long al, be; int score = 0; std::vector<long long> accraw; };
    // keys: (state, suffix length, unit, separator, alpha, beta, prefix length, prefix hash); the strings live in LC
    typedef std::tuple<int, int, int, int, long long, long long, size_t, size_t> LKey;
    std::map<LKey, LC> cands;
    std::vector<std::vector<int>> cnt(NU);
    for (auto &sn : e.snaps) {
        const std::string &w = sn.second;
        long long len = (long long)w.size();
        for (int ui = 0; ui < NU; ++ui) {
            long long ul = (long long)strlen(UNITS2[ui]);
            cnt[ui].assign(len + 1, 0);
            for (long long x = ul; x <= len; ++x)
                if (memcmp(w.data() + x - ul, UNITS2[ui], ul) == 0) cnt[ui][x] = cnt[ui][x - ul] + 1;
        }
        std::set<LKey> seen;
        // Runs are parsed from the head end. For a given unit and separator, the suffixes L only change the first
        // (accumulator) run, so everything after its separator is memoised by its start x1.
        struct Memo { std::vector<long long> runs, starts; std::vector<std::pair<long long, long long>> encs;
                      std::vector<size_t> Ks, hs; };
        for (int ui = 0; ui < NU; ++ui) for (int si = 0; si < NS; ++si) {
            std::string u = UNITS2[ui], s = SEPS2[si];
            if (u == s) continue;
            long long ul = (long long)u.size(), sl = (long long)s.size();
            std::unordered_map<long long, Memo> memo;
            for (int L = 0; L <= 12 && L < len; ++L) {
                long long x0 = len - L, k0 = cnt[ui][x0], xa = x0 - k0 * ul;
                if (xa <= 0 || !ends_with(w.data(), xa, s)) continue;
                long long x1 = xa - sl;
                auto it = memo.find(x1);
                if (it == memo.end()) {
                    Memo mm;
                    long long x = x1;
                    bool more = true;
                    auto step = [&]() {
                        long long k = cnt[ui][x];
                        x -= k * ul;
                        mm.runs.push_back(k); mm.starts.push_back(x);
                        if (x <= 0 || !ends_with(w.data(), x, s)) more = false; else x -= sl;
                    };
                    while (more && mm.runs.size() < 9) step();
                    if (mm.runs.size() >= 3) {
                        enc3(mm.runs, mm.encs);
                        mm.Ks.assign(mm.encs.size(), 0);
                        std::vector<char> live(mm.encs.size(), 1);
                        for (size_t i = 0;; ++i) {
                            if (i >= mm.runs.size()) { if (!more || mm.runs.size() >= 20000) break; step(); }
                            bool any = false;
                            long long v;
                            for (size_t e2 = 0; e2 < mm.encs.size(); ++e2) if (live[e2]) {
                                if (dec1(mm.runs[i], mm.encs[e2].first, mm.encs[e2].second, v)) { mm.Ks[e2] = i + 1; any = true; }
                                else live[e2] = 0;
                            }
                            if (!any) break;
                        }
                        mm.hs.assign(mm.encs.size(), 0);     // prefix hashes, computed when first needed
                    }
                    it = memo.emplace(x1, std::move(mm)).first;
                }
                Memo &mm = it->second;
                if (mm.runs.size() < 3) continue;
                for (size_t e2 = 0; e2 < mm.encs.size(); ++e2) {
                    const auto &en = mm.encs[e2];
                    size_t K = mm.Ks[e2];          // digits including a
                    if (K < 3) continue;
                    int big = 0;
                    for (size_t i = 0; i < K; ++i) if (mm.runs[i] >= 2) ++big;
                    if (big < 2) continue;
                    size_t Pl = (size_t)mm.starts[K - 1];
                    if (!mm.hs[e2]) mm.hs[e2] = std::hash<std::string_view>()(std::string_view(w.data(), Pl)) | 1;
                    size_t h = mm.hs[e2] ^ (std::hash<std::string_view>()(std::string_view(w.data() + len - L, L)) * 31);
                    LKey key = std::make_tuple(sn.first, L, ui, si, en.first, en.second, Pl, h);
                    if (seen.count(key)) continue;
                    seen.insert(key);
                    LC &c = cands[key];
                    if (c.score == 0) {
                        c.q = sn.first; c.S = w.substr(len - L); c.P = w.substr(0, Pl); c.u = u; c.s = s; c.al = en.first; c.be = en.second;
                    }
                    c.score++; c.accraw.push_back(k0);
                }
            }
        }
    }
    // group by (state, prefix, unit, separator, encoding): best score, shortest suffix
    std::map<std::tuple<int, std::string, std::string, std::string, long long, long long>, std::vector<LC>> groups;
    for (auto &kv : cands) if (kv.second.score >= 2) {
        const LC &c = kv.second;
        groups[std::make_tuple(c.q, c.P, c.u, c.s, c.al, c.be)].push_back(c);
    }
    std::vector<std::pair<int, LC>> gl;
    for (auto &kv : groups) {
        std::vector<LC> cs = kv.second;
        std::stable_sort(cs.begin(), cs.end(), [](const LC &a, const LC &b) {
            if (a.score != b.score) return a.score > b.score;
            return a.S.size() < b.S.size();
        });
        gl.push_back({cs[0].score, cs[0]});
    }
    std::stable_sort(gl.begin(), gl.end(), [](const auto &a, const auto &b) { return a.first > b.first; });
    {   // at most 2 groups per state (a rare late-phase state must not be crowded out by frequent early ones), 8 in all
        std::map<int, int> perq;
        std::vector<std::pair<int, LC>> keep;
        for (auto &g : gl) if (perq[g.second.q]++ < 2 && keep.size() < 8) keep.push_back(g);
        gl.swap(keep);
    }
    std::vector<Tmpl> out;
    for (auto &g : gl) {
        std::vector<std::pair<long long, long long>> eb;
        enc3(g.second.accraw, eb);
        for (auto &b : eb) {
            Tmpl t; t.q = g.second.q; t.P = g.second.P; t.u = g.second.u; t.s = g.second.s; t.S = g.second.S;
            t.al = g.second.al; t.be = g.second.be; t.alB = b.first; t.beB = b.second;
            out.push_back(t);
        }
    }
    return out;
}

// --------------------------------------------------------------------------------------- flexible parse
struct FCfg { std::string P; std::vector<long long> ds; long long a = 0, b = 0; };

// buf = the tape from the far end to the head (exclusive). Parse acc, a and then digits leftwards while they decode;
// stop at the template prefix if the remainder equals it. P = the rest.
static bool fparse(const Tmpl &t, const std::string &buf, FCfg &c, bool loose = false) {
    long long len = (long long)buf.size(), ul = (long long)t.u.size(), sl = (long long)t.s.size();
    long long Sl = (long long)t.S.size();
    if (len < Sl || buf.compare(len - Sl, Sl, t.S) != 0) return false;
    long long x = len - Sl;
    auto readrun = [&](long long &y) { long long k = 0; while (y - ul >= 0 && buf.compare(y - ul, ul, t.u) == 0) { y -= ul; ++k; } return k; };
    long long kb = readrun(x);
    if (!dec1(kb, t.alB, t.beB, c.b) && !loose) return false;
    if (x - sl < 0 || buf.compare(x - sl, sl, t.s) != 0) return false;
    x -= sl;
    long long ka = readrun(x);
    if (!dec1(ka, t.al, t.be, c.a) && !loose) return false;
    c.ds.clear();
    long long Pl = (long long)t.P.size();
    for (;;) {
        if (x == Pl && buf.compare(0, Pl, t.P) == 0) break;
        if (x - sl < 0 || buf.compare(x - sl, sl, t.s) != 0) break;
        long long y = x - sl;
        long long k = readrun(y), v;
        if (!dec1(k, t.al, t.be, v)) break;
        c.ds.push_back(v); x = y;
        if (x == 0) break;
    }
    std::reverse(c.ds.begin(), c.ds.end());
    c.P = buf.substr(0, x);
    return true;
}

// lead >= 0: the leftmost digit keeps the value lead (a counter kept in the list's first digit), the other k-1 are 0
static std::string eword(const Tmpl &t, const std::string &P, long long k, long long b, long long lead = -1) {
    std::string w = P, z;
    for (long long i = 0; i < t.be; ++i) z += t.u;
    z += t.s;
    long long kz = k;
    if (lead >= 0) {
        for (long long i = 0; i < t.al * lead + t.be; ++i) w += t.u;
        w += t.s;
        kz = k > 0 ? k - 1 : 0;
    }
    for (long long i = 0; i <= kz; ++i) w += z;     // kz zero digits and a = 0
    for (long long i = 0; i < t.alB * b + t.beB; ++i) w += t.u;
    w += t.S;
    return w;
}

// ------------------------------------------------------------------------------------- exhaustion probes
struct ORes { int kind = 2; FCfg c; long long steps = 0; };   // 0 stable, 1 halt, 2 timeout / nothing, 3 unstable

struct OProber {
    std::vector<uint8_t> tape;
    std::string buf;
    long long used = 0, cap = g_cap;     // steps spent on exhaustion probes for the current machine, and the cap
    ORes run(const TM &m, const Tmpl &t, const std::string &w, long long N) {
        long long need = 2 * N + 2 * (long long)w.size() + 64;
        if ((long long)tape.size() < need) tape.assign(need, 0);
        long long p = (long long)tape.size() / 2, vlo = p - (long long)w.size(), vhi = p;
        long long mn = p, mx = p - 1;
        for (size_t i = 0; i < w.size(); ++i) {
            tape[vlo + i] = (uint8_t)(w[i] - '0');
            if (w[i] == '1') { if (mn > mx) mn = mx = vlo + i; else mx = vlo + i; }
        }
        int q = t.q;
        ORes r;
        FCfg prev; bool have = false; long long prevst = 0, work = 0, nfam = 0;
        long long st = 0;
        for (; st < N; ++st) {
            int c = tape[p];
            if (m.nx[q][c] < 0) { r.kind = 1; r.steps = st; break; }
            int wr = m.w[q][c];
            tape[p] = (uint8_t)wr;
            if (wr) { if (mn > mx) mn = mx = p; else { if (p < mn) mn = p; if (p > mx) mx = p; } }
            p += m.d[q][c]; q = m.nx[q][c];
            if (p < vlo) vlo = p;
            if (p > vhi) vhi = p;
            if (q != t.q || tape[p] != 0) continue;
            while (mx > p && !tape[mx]) --mx;
            if (mx > p) continue;
            while (mn < p && !tape[mn]) ++mn;
            long long lo = mn < p ? mn : p;
            work += p - lo;
            if (work > 200000000LL) break;
            buf.resize(p - lo);
            for (long long i = lo; i < p; ++i) buf[i - lo] = char('0' + tape[i]);
            FCfg cur;
            if (!fparse(t, buf, cur)) continue;
            ++nfam;
            if (have && cur.P == prev.P && cur.ds.size() == prev.ds.size() && cur.b > prev.b) {
                r.kind = 0; r.c = prev; r.steps = prevst; break;
            }
            prev = cur; have = true; prevst = st + 1;
            if (nfam > 4000) break;
        }
        if (r.kind == 2 && have) { r.kind = 3; r.c = prev; r.steps = prevst; }
        used += st;
        if (vlo < 0) vlo = 0;
        memset(tape.data() + vlo, 0, (size_t)(vhi - vlo + 1));
        return r;
    }
};

// ------------------------------------------------------------------------------------------------- chains
struct ChainRes {
    std::string ev; int nR = 0, nC = 0; bool halted = false, looped = false, limit = false;
    std::string hP; long long hk = 0, hlead = -1;       // the exhaustion that halted: outer part, zero digits, lead
};
// a variant chain that halted, or was still rebuilding when it ran out of steps (its count is then a lower bound)
static bool grows(const ChainRes &v, const ChainRes &than) { return (v.halted || v.limit) && v.nR > than.nR; }

static std::string short_word(const std::string &w) {      // run-length view for debugging
    std::string o;
    for (size_t i = 0; i < w.size();) {
        size_t j = i; while (j < w.size() && w[j] == w[i]) ++j;
        if (j - i >= 4) o += std::string(1, w[i]) + "^" + std::to_string(j - i) + " ";
        else o += w.substr(i, j - i) + " ";
        i = j;
        if (o.size() > 160) { o += "..."; break; }
    }
    return o;
}

static std::string tkey(const Tmpl &t) {
    return std::to_string(t.q) + "|" + t.P + "|" + t.u + "|" + t.s + "|" + t.S + "|" + std::to_string(t.al) + "," +
           std::to_string(t.be) + "," + std::to_string(t.alB) + "," + std::to_string(t.beB);
}
// as Tmpl::str, with a run-length view of a long prefix
static std::string tstr3(const Tmpl &t, char o) {
    Tmpl c = t;
    if (c.P.size() > 12) c.P = "";
    std::string s = c.str(o);
    if (t.P.size() > 12) {
        std::string pv = short_word(t.P);
        for (auto &ch : pv) if (ch == ' ') ch = '.';
        size_t i = s.find(",P=-");
        if (i != std::string::npos) s = s.substr(0, i) + ",P=" + pv + s.substr(i + 4);
    }
    return s;
}

// bC: the accumulator used instead of b1 at counter-creation (C) steps, so that a created counter can be varied alone.
// lead >= 0: a "leading-digit counter" chain: each exhaustion keeps the first digit of the list (initially lead).
static ChainRes run_chain(OProber &op, const TM &m, const Tmpl &t, std::string P, long long k, long long b1, long long N,
                          int maxT, long long bC = -1, long long lead = -1, int bmode = 0) {
    ChainRes cr;
    std::set<std::pair<std::string, long long>> seen;
    std::vector<std::string> hist;
    int sameP = 0;
    for (int it = 0; it < maxT; ++it) {
        if (op.used > op.cap) { cr.ev += 'W'; cr.limit = true; break; }
        // bmode 1: the accumulator exceeds the number of zero digits (b = b1 + k), as in a real run, where b at an
        // exhaustion is far larger than the list it has just run through
        long long bb = bmode ? b1 + k : b1, bbC = bC >= 0 && bmode ? bC + k : bC;
        ORes r1 = op.run(m, t, eword(t, P, k, bb, lead), N);
        if (r1.kind == 1) { cr.ev += 'H'; cr.halted = true; cr.hP = P; cr.hk = k; cr.hlead = lead; break; }
        if (r1.kind != 0) { cr.ev += 'T'; break; }
        ORes r2 = op.run(m, t, eword(t, P, k, bb + 1, lead), N);
        char e;
        if (r2.kind == 0) {
            if (r2.c.P == r1.c.P) e = r2.c.ds.size() > r1.c.ds.size() ? 'R' : r2.c.ds.size() == r1.c.ds.size() ? 'F' : 'X';
            else e = r2.c.P.size() > r1.c.P.size() ? 'C' : 'X';
        } else e = r2.kind == 1 ? 'r' : 'u';
        if (e == 'C' && bC >= 0 && bC != b1) {
            r1 = op.run(m, t, eword(t, P, k, bbC, lead), N);
            if (r1.kind == 1) { cr.ev += "CH"; cr.halted = true; ++cr.nC; break; }
            if (r1.kind != 0) { cr.ev += "CT"; ++cr.nC; break; }
        }
        cr.ev += e;
        if (e == 'R') ++cr.nR;
        if (e == 'C') ++cr.nC;
        if (g_debug) {
            std::string dl;
            for (size_t i = 0; i < r1.c.ds.size() && i < 24; ++i) dl += (i ? "," : "") + std::to_string(r1.c.ds[i]);
            fprintf(stderr, "    chain b1=%lld step %d: %c  P'=%s digits=%zu [%s] a=%lld b=%lld (%lld steps)\n", b1, it, e,
                    short_word(r1.c.P).c_str(), r1.c.ds.size(), dl.c_str(), r1.c.a, r1.c.b, r1.steps);
        }
        if (r1.c.P == P && e == 'R') { if (++sameP >= 3) { cr.ev += 'L'; cr.looped = true; break; } }
        else sameP = 0;
        long long nl = lead >= 0 ? (r1.c.ds.empty() ? 0 : r1.c.ds[0]) : -1;     // the next exhaustion's first digit
        std::string skey = r1.c.P + "|" + std::to_string(nl);
        if (!seen.insert({skey, (long long)r1.c.ds.size()}).second) { cr.ev += 'L'; cr.looped = true; break; }
        // the outer parts and step kinds repeat with a period of up to 8 steps, three times (the list may grow)
        hist.push_back(skey + "|" + e);
        bool per = false;
        for (size_t pp = 1; pp <= 8 && !per && hist.size() >= 3 * pp; ++pp) {
            per = true;
            for (size_t j = hist.size() - 2 * pp; j < hist.size() && per; ++j) if (hist[j] != hist[j - pp]) per = false;
        }
        if (per && cr.nR) { cr.ev += 'L'; cr.looped = true; break; }
        P = r1.c.P; k = (long long)r1.c.ds.size();
        lead = nl;
        if (P.size() > 20000) { cr.ev += 'B'; break; }
        if (it + 1 == maxT) cr.limit = true;
    }
    return cr;
}

// The longest periodic block of P (period <= 8, >= 4 periods): position, period, number of whole periods.
struct Block { long long pos = -1, per = 0, reps = 0; };
static Block find_block(const std::string &P) {
    Block best;
    long long n = (long long)P.size();
    for (long long p = 1; p <= 8; ++p) {
        long long i = 0;
        while (i + p < n) {
            long long j = i;
            while (j + p < n && P[j] == P[j + p]) ++j;
            long long len = j - i + p, reps = len / p;
            if (reps >= 4 && reps > best.reps) { best.pos = i; best.per = p; best.reps = reps; }
            i = j + 1;
        }
    }
    return best;
}
static std::string set_reps(const std::string &P, const Block &bl, long long reps) {
    std::string unit = P.substr(bl.pos, bl.per), mid;
    for (long long i = 0; i < reps; ++i) mid += unit;
    return P.substr(0, bl.pos) + mid + P.substr(bl.pos + bl.per * bl.reps);
}

struct Outer { int grade = -1; std::string info; };
static const char *GRADE3[] = {"W1-HALTER", "W1-HALT?", "W1-LOOPER", "MULTI", "MULTI?", "LOOPER", "REBUILD"};
static const int NGRADE3 = 7;

static std::string evstr(const ChainRes &c) { return c.ev + "/" + std::to_string(c.nR); }

// A created counter consumed by rebuilds: a C step followed by at least 2 R steps.
static bool consumes(const ChainRes &c) {
    size_t i = c.ev.find('C');
    while (i != std::string::npos) {
        int r = 0;
        for (size_t j = i + 1; j < c.ev.size() && c.ev[j] != 'C'; ++j) if (c.ev[j] == 'R') ++r;
        if (r >= 2) return true;
        i = c.ev.find('C', i + 1);
    }
    return false;
}

// kobs: the number of digits of the family's latest census snapshot. A real exhaustion leaves that many zero
// digits (K(0^n; 0; b)), and they can matter (a zero list can act as a counter), so chains with b1 = 2, 3 also
// start from k = kobs zero digits ("z" chains, reported as "zB:...").
static Outer outer_analysis(OProber &op, const TM &m, const Tmpl &t, long long N, long long kobs = 0) {
    Outer o;
    std::string P0 = t.P;
    Block bl = find_block(P0);
    if (bl.reps > 12) { P0 = set_reps(P0, bl, bl.reps % 6 + 6); bl.reps = bl.reps % 6 + 6; }
    std::vector<long long> B = {2, 3, 4, 5}, K0 = {0, 0, 0, 0};
    if (kobs > 0) { B.push_back(2); B.push_back(3); K0.push_back(kobs); K0.push_back(kobs); }
    std::vector<ChainRes> base;
    bool any = false;
    for (size_t i = 0; i < B.size(); ++i) {
        ChainRes cr = run_chain(op, m, t, P0, K0[i], B[i], N, 40);
        base.push_back(cr);
        if (cr.nR || cr.nC) any = true;
    }
    // Leading-digit counter chains (the first digit of the list is kept, initially 2), for b1 = 2, 3.
    std::vector<ChainRes> leadc;
    for (size_t i = 0; i < 2; ++i) {
        leadc.push_back(run_chain(op, m, t, P0, 1, B[i], N, 40, -1, 2));
        if (leadc.back().nR || leadc.back().nC) any = true;
    }
    std::string info;
    for (size_t i = 0; i < base.size(); ++i)
        info += (i ? " " : "") + std::string(K0[i] ? "z" : "") + std::to_string(B[i]) + ":" + evstr(base[i]);
    for (size_t i = 0; i < leadc.size(); ++i) info += " lead2," + std::to_string(B[i]) + ":" + evstr(leadc[i]);
    o.info = info;
    if (!any) return o;
    // Counter test on each chain that halts after a rebuild: the number of rebuilds before the halt must grow
    // strictly over three variants: the periodic block of P with +6 and +12 periods, or b1 + 6 and b1 + 12 (a
    // counter created from b). The variants must halt too.
    bool w1 = false, halted_r = false, looped_r = false, created = false, confirmed = false, zhalted = false,
         leadhalt = false;
    int maxR = 0;
    // A halting chain is confirmed if its final exhaustion also halts with an accumulator larger than the number of
    // zero digits there (b = k+1 .. k+4), as in a real run, where b at an exhaustion is far larger than the list it
    // has just cleared. (The 76450 family "halts" in constant-b chains only because it halts at exactly 4b+1 zeros.)
    auto confirm = [&](const ChainRes &c) {
        if (confirmed || !c.halted) return;
        std::string r;
        for (long long j = 1; j <= 4 && !confirmed; ++j) {
            ORes h = op.run(m, t, eword(t, c.hP, c.hk, c.hk + j, c.hlead), N);
            r += h.kind == 1 ? 'H' : h.kind == 0 ? 'K' : 'T';
            if (h.kind == 1) confirmed = true;
        }
        info += " |b>k:" + r;
    };
    for (size_t i = 0; i < base.size() && !w1; ++i) {
        const ChainRes &cr = base[i];
        if (cr.looped && cr.nR >= 1) looped_r = true;
        if (consumes(cr)) created = true;
        if (!(cr.halted && cr.nR >= 1)) continue;
        halted_r = true; maxR = std::max(maxR, cr.nR);
        if (K0[i]) zhalted = true;
        confirm(cr);
        if (bl.reps >= 4) {
            ChainRes v6 = run_chain(op, m, t, set_reps(P0, bl, bl.reps + 6), K0[i], B[i], N, 80);
            info += " |" + std::to_string(B[i]) + " blk+6:" + evstr(v6);
            if (grows(v6, cr)) {
                ChainRes v12 = run_chain(op, m, t, set_reps(P0, bl, bl.reps + 12), K0[i], B[i], N, 120);
                info += " blk+12:" + evstr(v12);
                if (grows(v12, v6)) w1 = true;
            }
        }
        if (!w1 && cr.nC) {
            ChainRes v6 = run_chain(op, m, t, P0, K0[i], B[i], N, 80, B[i] + 6);
            info += " |" + std::to_string(B[i]) + " bC+6:" + evstr(v6);
            if (grows(v6, cr)) {
                ChainRes v12 = run_chain(op, m, t, P0, K0[i], B[i], N, 120, B[i] + 12);
                info += " bC+12:" + evstr(v12);
                if (grows(v12, v6)) w1 = true;
            }
        }
    }
    // a leading-digit chain that halts after rebuilds: the number of rebuilds must grow when the digit starts at 8, 14
    for (size_t i = 0; i < leadc.size() && !w1; ++i) {
        const ChainRes &lc = leadc[i];
        if (lc.looped && lc.nR >= 1) looped_r = true;
        if (!(lc.halted && lc.nR >= 1)) continue;
        leadhalt = true;      // a lead-chain halt counts for the counter test only, not for MULTI
        confirm(lc);
        ChainRes v6 = run_chain(op, m, t, P0, 1, B[i], N, 80, -1, 8);
        info += " |lead8," + std::to_string(B[i]) + ":" + evstr(v6);
        if (grows(v6, lc)) {
            ChainRes v12 = run_chain(op, m, t, P0, 1, B[i], N, 120, -1, 14);
            info += " lead14:" + evstr(v12);
            if (grows(v12, v6)) w1 = true;
        }
    }
    // if W1 came from a chain that was not confirmed, try to confirm the other halting chains too
    for (size_t i = 0; i < base.size() && halted_r && !confirmed; ++i) if (base[i].halted && base[i].nR >= 1) confirm(base[i]);
    for (size_t i = 0; i < leadc.size() && (halted_r || leadhalt) && !confirmed; ++i) if (leadc[i].halted && leadc[i].nR >= 1) confirm(leadc[i]);
    o.info = info;
    if (w1) o.grade = confirmed ? 0 : 1;
    else if (created && !halted_r) o.grade = 2;
    // MULTI needs a confirmed halt; when the family's census list had digits, a chain started from that many zero
    // digits (the real exhaustion K(0^n; 0; b)) must also halt after a rebuild: c35m14 machines whose empty-list
    // chains rebuild once and halt, but whose z chains halt at once, halt at the first exhaustion in reality.
    else if (halted_r) o.grade = confirmed && (kobs == 0 || zhalted) ? 3 : 4;
    else if (looped_r) o.grade = 5;
    else o.grade = 6;
    if (o.grade == 3 || o.grade == 4) o.info = "k=" + std::to_string(maxR) + " " + o.info;
    return o;
}

// ------------------------------------------------------------------------------------------------- driver
static Tmpl tmpl_from_args(char **a, TM &m) {
    Tmpl t; t.q = a[4][0] - 'A'; t.P = strcmp(a[5], "-") ? a[5] : ""; t.u = a[6]; t.s = a[7];
    t.al = atoll(a[8]); t.be = atoll(a[9]); t.alB = atoll(a[10]); t.beB = atoll(a[11]); t.S = strcmp(a[12], "-") ? a[12] : "";
    if (a[3][0] == 'L') m = mirrored(m);
    return t;
}

struct Analysis {
    Fit2 best; std::string bestT; Outer bestO; std::string bestOT; int nt = 0;
    bool hasT = false; Tmpl tT; int oT = 0;      // first fitted template whose exhaustion probe timed out
};
// The latest census step at which a snapshot of this template's family (same state, same prefix) was taken, or -1.
static long long template_last(const Tmpl &t, const End3 &e) {
    long long last = -1;
    FCfg c;
    (void)c;
    for (auto &sn : e.snaps) {
        const std::string &w = sn.second;
        if (sn.first != t.q || w.size() <= t.P.size() + t.S.size()) continue;
        if (w.compare(0, t.P.size(), t.P) != 0 || w.compare(w.size() - t.S.size(), t.S.size(), t.S) != 0) continue;
        last = std::max(last, e.step_of(sn.first, w));
    }
    return last;
}
static long long g_census = 0;
// The number of digit runs (undecoded) in the family's latest snapshot: runs of u separated by s between the template
// prefix and the accumulator.
static long long template_kobs(const Tmpl &t, const End3 &e) {
    long long best = -2, k = 0;
    long long ul = (long long)t.u.size(), sl = (long long)t.s.size();
    for (auto &sn : e.snaps) {
        const std::string &w = sn.second;
        if (sn.first != t.q || w.size() <= t.P.size() + t.S.size()) continue;
        if (w.compare(0, t.P.size(), t.P) != 0 || w.compare(w.size() - t.S.size(), t.S.size(), t.S) != 0) continue;
        long long st = e.step_of(sn.first, w);
        if (st < best) continue;
        long long x = (long long)(w.size() - t.S.size()), runs = 0, Pl = (long long)t.P.size();
        for (;;) {
            while (x - ul >= Pl && w.compare(x - ul, ul, t.u) == 0) x -= ul;
            ++runs;
            if (x <= Pl || x - sl < Pl || w.compare(x - sl, sl, t.s) != 0) break;
            x -= sl;
        }
        best = st; k = std::max<long long>(0, runs - 2);      // minus the accumulator and a
    }
    return k;
}

// Does the family describe the machine's real tape? True if some snapshot of the template's latest kind parses
// completely (flexible parse ends exactly at the template prefix). A template read off a few early or partial
// snapshots (encoding chosen by the 80% rule) can fit R1-R3 on constructed configurations whose "used-up" form never
// occurs in the real run (c35m14: a P=11, 2d+1 reading of the BB(8) record's list).
static bool template_anchored(const Tmpl &t, const End3 &e) {
    // any snapshot of the template's state and prefix from the later half of the family's life parses completely
    long long last = -1;
    for (auto &sn : e.snaps)
        if (sn.first == t.q && sn.second.compare(0, t.P.size(), t.P) == 0) last = std::max(last, e.step_of(sn.first, sn.second));
    FCfg c;
    for (auto &sn : e.snaps) {
        const std::string &w = sn.second;
        if (sn.first != t.q || w.size() <= t.P.size() + t.S.size()) continue;
        if (w.compare(0, t.P.size(), t.P) != 0) continue;
        if (e.step_of(sn.first, w) < last / 2) continue;
        // loose: the accumulator and a may use another encoding than the digits (the BB(7) champion's family
        // writes a as (01)^(3a), digits as (01)^(3d+1)); the digits must decode right up to the prefix
        if (fparse(t, w, c, true) && c.P == t.P) return true;
    }
    return false;
}

static long long g_post = 0;                     // post-exhaustion census steps (0: off; --post=2000000 to try)

static void analyse(Analysis &A, End3 ends[2], const TM &m, const TM &mm, Prober2 &pr, OProber &op, long long N,
                    long long chainN, const std::string &line, const std::string &tag) {
        for (int o = 0; o < 2; ++o) {
            if (g_debug)
                for (auto &sn : ends[o].snaps)
                    fprintf(stderr, "snap %c %c %s\n", o ? 'L' : 'R', 'A' + sn.first, short_word(sn.second).c_str());
            if (getenv("DL3_SNAPSTAT")) {
                size_t tot = 0, mx = 0;
                for (auto &sn : ends[o].snaps) { tot += sn.second.size(); mx = std::max(mx, sn.second.size()); }
                fprintf(stderr, "snapstat %c n=%zu total=%zu max=%zu kinds=%zu\n", o ? 'L' : 'R', ends[o].snaps.size(), tot, mx, ends[o].kinds.size());
            }
            double t1 = now_s();
            std::vector<Tmpl> ts = infer_templates_fast(ends[o]);
            if (getenv("DL3_CMPINF")) {
                std::vector<Tmpl> ref = infer_templates(ends[o]);
                bool same = ref.size() == ts.size();
                for (size_t i = 0; same && i < ref.size(); ++i) same = tkey(ref[i]) == tkey(ts[i]);
                if (!same) fprintf(stderr, "INFER MISMATCH %s %c: %zu vs %zu\n", line.c_str(), o ? 'L' : 'R', ref.size(), ts.size());
            }
            std::set<std::string> have;
            for (auto &t : ts) have.insert(tkey(t));
            double t2 = now_s();
            g_t[4] += t2 - t1;
            if (!getenv("DL3_NOLONG"))
                for (auto &t : infer_long(ends[o])) if (!have.count(tkey(t))) { have.insert(tkey(t)); ts.push_back(t); }
            g_t[5] += now_s() - t2;
            // fit R1-R3 on every template; then the outer analysis on the fitted ones, long prefixes first, one per
            // (state, prefix, unit, separator, digit encoding), at most 6
            g_t[1] += now_s() - t1; t1 = now_s();
            std::vector<std::pair<int, size_t>> fitted;
            for (size_t i = 0; i < ts.size(); ++i) {
                const Tmpl &t = ts[i];
                ++A.nt;
                Fit2 f = fit2(pr, o ? mm : m, t, N);
                if (!f.ok) continue;
                if (A.best.grade < 0 || f.grade < A.best.grade) { A.best = f; A.bestT = tag + tstr3(t, o ? 'L' : 'R'); }
                fitted.push_back({(int)ts[i].P.size(), i});
            }
            g_t[2] += now_s() - t1; t1 = now_s();
            std::stable_sort(fitted.begin(), fitted.end(), [](const auto &a, const auto &b) { return a.first > b.first; });
            std::set<std::string> done;
            int outer_runs = 0;
            for (auto &fi : fitted) {
                const Tmpl &t = ts[fi.second];
                std::string g = std::to_string(t.q) + "|" + t.P + "|" + t.u + "|" + t.s + "|" + std::to_string(t.al) + "," + std::to_string(t.be);
                if (done.count(g) || outer_runs >= 6 || A.bestO.grade == 0) continue;
                done.insert(g);
                ++outer_runs;
                if (g_debug) fprintf(stderr, "%s template %s\n", line.c_str(), tstr3(t, o ? 'L' : 'R').c_str());
                Outer oa = outer_analysis(op, o ? mm : m, t, chainN, std::min<long long>(template_kobs(t, ends[o]), 64));
                {   // the family's last census appearance: an early family is one the machine left (its rebuilds
                    // happen at small b, so MULTI or W1 there says little about the growth)
                    long long last = template_last(t, ends[o]);
                    std::string tagl = (last >= 0 && g_census > 0 && last < g_census / 2) ? "early(last " : "(last ";
                    bool anch = template_anchored(t, ends[o]);
                    oa.info = std::string(anch ? "" : "unanchored ") + tagl + std::to_string(last) + ") " + oa.info;
                    // an unanchored family's halting grades are not evidence about the real run
                    if (!anch && oa.grade == 0) oa.grade = 1;          // W1-HALTER -> W1-HALT?
                    else if (!anch && oa.grade == 3) oa.grade = 4;     // MULTI -> MULTI?
                }
                if (!A.hasT && oa.grade < 0 && oa.info.size() >= 3 && oa.info.compare(0, 3, "2:T") == 0) { A.hasT = true; A.tT = t; A.oT = o; }
                if (oa.grade >= 0 && (A.bestO.grade < 0 || oa.grade < A.bestO.grade)) { A.bestO = oa; A.bestOT = tag + tstr3(t, o ? 'L' : 'R'); }
                else if (A.bestO.grade < 0 && A.bestO.info.empty()) { A.bestO.info = oa.info; A.bestOT = tag + tstr3(t, o ? 'L' : 'R'); }
            }
            g_t[3] += now_s() - t1;
        }
}

int main(int argc, char **argv) {
    if (argc >= 13 && !strcmp(argv[1], "--tmpl")) {
        TM m; if (!parse(argv[2], m)) return 2;
        Tmpl t = tmpl_from_args(argv, m);
        long long N = argc > 13 ? atoll(argv[13]) : 200000;
        g_debug = true;
        Prober2 pr; OProber op;
        Fit2 f = fit2(pr, m, t, 20000);
        printf("fit ok=%d grade=%s %s\n", f.ok, f.grade >= 0 ? GRADE2[f.grade] : "-", params(f).c_str());
        Outer o = outer_analysis(op, m, t, N);
        printf("outer grade=%s %s\n", o.grade >= 0 ? GRADE3[o.grade] : "-", o.info.c_str());
        return 0;
    }
    std::vector<std::string> pos; bool all = false;
    long long chainN = 1000000;
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--all")) all = true;
        else if (!strcmp(argv[i], "--debug")) g_debug = true;
        else if (!strncmp(argv[i], "--span=", 7)) g_span = atoll(argv[i] + 7);
        else if (!strncmp(argv[i], "--chainN=", 9)) chainN = atoll(argv[i] + 9);
        else if (!strncmp(argv[i], "--cap=", 6)) g_cap = atoll(argv[i] + 6);
        else if (!strncmp(argv[i], "--post=", 7)) g_post = atoll(argv[i] + 7);
        else pos.push_back(argv[i]);
    }
    if (pos.size() < 2) { fprintf(stderr, "usage: dlscan3 INPUT OUTPUT [CENSUS] [N] [--all] [--span=S] [--chainN=N] [--debug]\n"); return 2; }
    long long steps = pos.size() > 2 ? atoll(pos[2].c_str()) : 1000000LL;
    long long N = pos.size() > 3 ? atoll(pos[3].c_str()) : 20000LL;
    std::ifstream in(pos[0]);
    if (!in) { fprintf(stderr, "cannot read %s\n", pos[0].c_str()); return 2; }
    std::ofstream out(pos[1]);
    out << "machine\thalted_step\tn_templates\tgrade\ttemplate\tw1\tparams\n";
    Prober2 pr; OProber op;
    long long n = 0, nhalt = 0, ng3[NGRADE3] = {0}, ng2[NGRADE2] = {0};
    std::string line;
    while (std::getline(in, line)) {
        size_t sp = line.find_first_of(" \t\r");
        if (sp != std::string::npos) line.resize(sp);
        TM m; if (line.find('_') == std::string::npos || !parse(line, m)) continue;
        End3 ends[2];
        double t0 = now_s();
        g_census = steps;
        long long halted = census3(m, steps, ends);
        g_t[0] += now_s() - t0;
        if (getenv("DL3_OLDCOLLECT")) { ends[0].collect(); ends[1].collect(); }
        else { ends[0].collect3(); ends[1].collect3(); }
        ++n; if (halted >= 0) ++nhalt;
        TM mm = mirrored(m);
        Analysis A;
        op.used = 0; op.cap = g_cap;
        analyse(A, ends, m, mm, pr, op, N, chainN, line, "");
        // Post-exhaustion census: if no outer grade, and a fitted template's exhaustion probe found no family
        // configuration (T), the used-up list may lead into ANOTHER list family. Run a census from that used-up
        // configuration (b = 3) and analyse the families it shows.
        if (A.bestO.grade < 0 && A.hasT && g_post > 0) {
            End3 e2[2];
            std::string w = eword(A.tT, A.tT.P, 0, 3);
            const TM &mo = A.oT ? mm : m;
            census3(mo, g_post, e2, &w, A.tT.q);
            e2[0].collect3(); e2[1].collect3();
            Analysis B;
            TM mmo = mirrored(mo);
            analyse(B, e2, mo, mmo, pr, op, N, chainN, line, A.oT ? "post(L):" : "post(R):");
            if (B.bestO.grade >= 0) { A.bestO = B.bestO; A.bestOT = B.bestOT; }
            if (A.best.grade < 0 && B.best.grade >= 0) { A.best = B.best; A.bestT = B.bestT; }
            A.nt += B.nt;
        }
        Fit2 &best = A.best; std::string &bestT = A.bestT; Outer &bestO = A.bestO; std::string &bestOT = A.bestOT;
        int nt = A.nt;
        if (bestO.grade >= 0) ++ng3[bestO.grade];
        else if (best.grade >= 0) ++ng2[best.grade];
        if (all || best.grade >= 0) {
            std::string grade = bestO.grade >= 0 ? GRADE3[bestO.grade] : best.grade >= 0 ? GRADE2[best.grade] : "-";
            std::string tm = bestO.grade >= 0 ? bestOT : bestT;
            if (tm.size() > 200) tm = tm.substr(0, 200) + "...";
            out << line << "\t" << halted << "\t" << nt << "\t" << grade << "\t" << (tm.empty() ? "-" : tm) << "\t"
                << (bestO.info.empty() ? "-" : bestO.info) << "\t" << (best.grade >= 0 ? params(best) : "-") << "\n";
        }
        if (n % 20 == 0) out.flush();
    }
    fprintf(stderr, "time: census %.1f s, templates %.1f s, R1-R3 fits %.1f s, outer %.1f s (dlscan2 templates %.1f s, long %.1f s)\n", g_t[0], g_t[1], g_t[2],
            g_t[3], g_t[4], g_t[5]);
    out << "#summary\tmachines=" << n << "\thalted=" << nhalt;
    for (int g = 0; g < NGRADE3; ++g) out << "\t" << GRADE3[g] << "=" << ng3[g];
    for (int g = 0; g < NGRADE2; ++g) out << "\t" << GRADE2[g] << "=" << ng2[g];
    out << "\n";
    return 0;
}
