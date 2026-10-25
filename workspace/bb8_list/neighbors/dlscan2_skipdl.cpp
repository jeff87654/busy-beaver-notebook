// dlscan2: generalised digit-list screen, written to catch BB(7)-champion-style counters as well.
//
//   dlscan2 INPUT OUTPUT [STEPS=5000000] [N=100000] [--all]
//
// dlscan.cpp's family K(ds; a; b) = unit^d1 sep ... unit^a sep unit^b suffix [state>0] cannot describe the BB(7)
// champion 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF, whose configurations are
//   111 (01)^(3 b_k + 1) 1 ... (01)^(3 b_1 + 1) 1 (01)^(3 a) 1010011100 A>        (checked on literal runs)
// This program uses templates T = (state, prefix P, unit u, separator s, digit encoding alpha d + beta,
// accumulator encoding alphaB b + betaB, suffix S):
//   K_T(ds; a; b) = P  u^(alpha d1 + beta) s ... u^(alpha dn + beta) s  u^(alpha a + beta) s  u^(alphaB b + betaB)  S
// with the head in `state` on the blank cell right of S (S may end in blanks).
// 1. Census at both tape ends (the head reading a blank up to 4 cells beyond the outermost 1), with snapshots.
// 2. Template inference: a snapshot supports (state, S, P, u, s) if, after removing S (0-12 cells), it parses from
//    the right into at least 4 runs of u separated by s, leaving a prefix P of at most 4 cells. The encodings
//    come from the run lengths seen: alpha divides the gcd of their differences (each divisor up to 6 is
//    tried; 1, 2 and 3 when the lengths are all equal),
//    beta = their residue; likewise for the accumulator.
// 3. Probes on constructed configurations (N steps each), stopping at the first failure:
//      R1  K(2; 2; b)          -> K(2; 1; m1 b + c1)                        b = 1..5
//      R2  K(2; 0; b)          -> K(1; m2 b + c2; b2)                       b = 1..5
//      R3  K(1,2,0^k; 0; b)    -> K(1,1, m3 b + c3 + e3 k, t^(k-1); a3; b3) t = 1 (dlscan's refill) or t = 0
//                                                                           (the champion's), k = 1.., b = 1..4
//      R4  K(; 0; b)           -> halts, or rebuilds a list                 b = 1..5
// Grades: CHAMPION (R1-R3 fit and R4 always halts: the machine halts when its list is used up, the BB(7)
//   champion's way to a record), R4-SOME (R4 halts for some b only: the BB(9) champion halts for odd b),
//   then for rebuilding machines the grades of dlscan.py from the halting boundary of R3: HALT?, HALT-SOME
//   (some reset probes halt, but not on a line in b), CHECK, NOBOUNDARY, SAFE.
// OUTPUT (TSV): machine, halted_step, n_templates, grade, template, params; only machines with an R1-R3 fit
// unless --all. Last line "#summary ...".
#define DLSCAN_NO_MAIN
#include "dlscan.cpp"
#include <chrono>

// ---- --skipdl (dlscan2_skipdl.cpp): drop every template that dlscan's first pass already screened.
// dlscan's base keys are (orientation, state q, suffix) for every end shape its census saw (head on a blank, a 1 one
// or two cells inward, no 1 outward; suffix "0" if the gap is one blank, else "01" if the outermost run is a single
// 1, else "1"), probed with unit "1", separator "0". The dlscan2 template (q, P empty, u "1", s "0", d = 1d+0,
// b = 1b+0, S = that suffix) builds the same probe tapes and stops at the same first family configuration (both
// parses split the word at every 0, and the word starts at the first 1, so dlscan's leading-zero rejection never
// fires), so R1/R2 are the same tests and dlscan2's R3 (k = 1 probes for >= 3 values of b) implies dlscan's "full".
// Hence a fit on such a template means dlscan listed the machine with that full key. Conditions for the claim:
// the shape must have been seen within dlscan's census length (g_dl_steps, first pass 1,000,000) and dlscan2's
// probe budget N must not exceed dlscan's (g_dl_N, first pass 100,000). The only residual difference is the parse
// work cap per probe (dlscan 2e8 compared characters, dlscan2 4e8 scanned cells), which needs > 2e8 parse work.
static long long g_dl_steps = 1000000, g_dl_N = 100000;
static bool g_skipdl = false;
static bool g_dlsh[2][MAXQ * 4];
static double g_t[4];   // census, inference, fits, other (seconds), printed with DLSCAN2_PROF

#include <numeric>
#include <set>

// ------------------------------------------------------------------------------------------------- census
// Snapshots are kept per "kind" of end event: the state and the 12 cells next to the head. A rare kind (the
// BB(7) champion reaches its family configuration once per pass over a long accumulator, among many transitional
// configurations at the same tape end) is then still represented. Each kind keeps its last two snapshots, taken
// at its 1st, 2nd, 4th, 8th, ... occurrence and then every 256th.
struct Kind { long long n = 0; std::vector<std::string> snaps; };
struct End2 {
    std::map<std::pair<int, std::string>, Kind> kinds;
    std::vector<std::pair<int, std::string>> snaps;       // filled by collect()
    void collect() {
        std::vector<std::pair<long long, std::pair<int, std::string>>> order;
        for (auto &kv : kinds) order.push_back({kv.second.n, kv.first});
        std::sort(order.begin(), order.end(), [](const auto &a, const auto &b) { return a.first > b.first; });
        snaps.clear();
        for (size_t i = 0; i < order.size() && i < 12; ++i)
            for (auto &w : kinds[order[i].second].snaps) snaps.push_back({order[i].second.first, w});
    }
};

static void end_event2(End2 &e, const uint8_t *T, int q, long long &farB, long long pos, int dir) {
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
    if ((n & (n - 1)) != 0 && n % 256 != 0) return;
    while (T[farB] == 0) farB += dir;
    long long span = dir > 0 ? pos - farB : farB - pos;
    if (span > 4000) return;
    std::string w; w.reserve(span);
    for (long long i = farB; i != pos; i += dir) w += char('0' + T[i]);
    if (!k.snaps.empty() && k.snaps.back() == w) return;
    if (k.snaps.size() >= 2) k.snaps.erase(k.snaps.begin());
    k.snaps.push_back(w);
}

// As dlscan.cpp's census, but an end event is the head reading a blank 1-4 cells beyond the outermost 1.
static long long census2(const TM &m, long long steps, End2 ends[2]) {
    memset(g_dlsh, 0, sizeof g_dlsh);
    std::vector<uint8_t> tape(1 << 12, 0);
    long long off = tape.size() / 2, pos = 0, loB = 1, hiB = 0;
    int q = 0;
    for (long long t = 0; t < steps; ++t) {
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
                if (clear) {
                    if (g_skipdl && t < g_dl_steps) {       // dlscan's right-end shape, if this is one of its events
                        int gr = T[pos - 1] ? 0 : (T[pos - 2] ? 1 : -1);
                        if (gr >= 0) { long long near = pos - 1 - gr; g_dlsh[0][q * 4 + gr * 2 + (T[near - 1] == 0)] = true; }
                    }
                    while (!T[hiB]) --hiB; end_event2(ends[0], T, q, loB, pos, 1);
                }
            } else if (rgt && !lft) {
                bool clear = true;
                while (loB < pos) { if (T[loB]) { clear = false; break; } ++loB; }
                if (clear) {
                    if (g_skipdl && t < g_dl_steps) {       // dlscan's left-end shape
                        int gl = T[pos + 1] ? 0 : (T[pos + 2] ? 1 : -1);
                        if (gl >= 0) { long long near = pos + 1 + gl; g_dlsh[1][q * 4 + gl * 2 + (T[near + 1] == 0)] = true; }
                    }
                    while (!T[loB]) ++loB; end_event2(ends[1], T, q, hiB, pos, -1);
                }
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

// ---------------------------------------------------------------------------------------------- templates
struct Tmpl;
static bool dl_covered(int o, const Tmpl &t);
struct Tmpl {
    int q = 0; std::string P, u, s, S;
    long long al = 1, be = 0, alB = 1, beB = 0;
    std::string str(char o) const {
        char buf[96];
        snprintf(buf, sizeof buf, ",%c,P=%s,u=%s,s=%s,d=%lldd+%lld,b=%lldb+%lld,S=%s", 'A' + q, P.empty() ? "-" : P.c_str(),
                 u.c_str(), s.c_str(), al, be, alB, beB, S.empty() ? "-" : S.c_str());
        return std::string(1, o) + buf;
    }
};

static const char *UNITS2[] = {"1", "01", "10", "11", "001", "010", "011", "100", "101", "110", "0101", "0011", "1010"};
static const char *SEPS2[] = {"0", "1", "00", "01", "10", "11", "000", "001", "011", "100", "110", "111"};

struct Cand { int q; std::string P, u, s, S; int score = 0; std::vector<long long> digraw, accraw; };

static std::vector<Tmpl> infer_templates(const End2 &e) {
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
        for (int L = 0; L <= 12 && L < len; ++L) {
            std::string S = w.substr(len - L);
            for (int ui = 0; ui < NU; ++ui) for (int si = 0; si < NS; ++si) {
                std::string u = UNITS2[ui], s = SEPS2[si];
                if (u == s) continue;
                std::vector<long long> runs;
                long long x = len - L; bool ok = false;
                for (int guard = 0; guard < 4000; ++guard) {
                    long long k = cnt[ui][x];
                    x -= k * (long long)u.size();
                    runs.push_back(k);
                    if (runs.size() >= 4 && x <= 4 && (x == 0 || w[0] == '1')) { ok = true; break; }
                    if (!ends_with(w.data(), x, s)) break;
                    x -= s.size();
                    if (x < 0) break;
                }
                if (!ok) continue;
                // at least two runs other than the accumulator must be non-trivial, and the runs must vary
                int big = 0; bool differ = false;
                for (size_t i = 1; i < runs.size(); ++i) { if (runs[i] >= 2) ++big; if (runs[i] != runs[1]) differ = true; }
                if (big < 2) continue;
                (void)differ;
                auto key = std::make_tuple(sn.first, S, w.substr(0, x), u, s);
                if (seen.count(key)) continue;
                seen.insert(key);
                Cand &c = cands[key];
                c.q = sn.first; c.S = S; c.P = w.substr(0, x); c.u = u; c.s = s; c.score++;
                c.accraw.push_back(runs[0]);
                for (size_t i = 1; i < runs.size(); ++i) c.digraw.push_back(runs[i]);
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

static bool dl_covered(int o, const Tmpl &t) {
    if (!t.P.empty() || t.u != "1" || t.s != "0" || t.al != 1 || t.be != 0 || t.alB != 1 || t.beB != 0) return false;
    int gap, single;
    if (t.S == "0") { gap = 1; return g_dlsh[o][t.q * 4 + 2] || g_dlsh[o][t.q * 4 + 3]; }
    else if (t.S == "01") { gap = 0; single = 1; }
    else if (t.S == "1") { gap = 0; single = 0; }
    else return false;
    return g_dlsh[o][t.q * 4 + gap * 2 + single];
}

// ------------------------------------------------------------------------------------------------- probes
struct P2 { int kind = 2; std::vector<long long> ds; long long a = 0, b = 0, steps = 0; };

struct Prober2 {
    std::vector<uint8_t> tape;
    std::string buf;
    std::vector<long long> runs;

    std::string word(const Tmpl &t, const std::vector<long long> &ds, long long a, long long b) {
        std::string w = t.P;
        auto rep = [&](long long n) { for (long long i = 0; i < n; ++i) w += t.u; };
        for (long long d : ds) { rep(t.al * d + t.be); w += t.s; }
        rep(t.al * a + t.be); w += t.s;
        rep(t.alB * b + t.beB);
        w += t.S;
        return w;
    }

    // Is the tape left of p (head in state t.q on a blank, nothing to the right) a configuration K_T(ds; a; b)?
    bool parse(const Tmpl &t, long long p, long long lo, P2 &r) {
        long long len = p - lo;
        if (len < (long long)(t.P.size() + t.S.size())) return false;
        buf.resize(len);
        for (long long i = 0; i < len; ++i) buf[i] = char('0' + tape[lo + i]);
        if (buf.compare(len - t.S.size(), t.S.size(), t.S) != 0) return false;
        if (buf.compare(0, t.P.size(), t.P) != 0) return false;
        long long x = len - (long long)t.S.size(), z = (long long)t.P.size();
        runs.clear();
        long long ul = (long long)t.u.size(), sl = (long long)t.s.size();
        for (;;) {
            long long k = 0;
            while (x - ul >= z && buf.compare(x - ul, ul, t.u) == 0) { x -= ul; ++k; }
            runs.push_back(k);
            if (x == z) break;
            if (x - sl < z || buf.compare(x - sl, sl, t.s) != 0) return false;
            x -= sl;
        }
        if (runs.size() < 2) return false;
        auto dec = [](long long raw, long long al, long long be, long long &v) {
            if (raw < be || (raw - be) % al) return false;
            v = (raw - be) / al; return true;
        };
        if (!dec(runs[0], t.alB, t.beB, r.b) || !dec(runs[1], t.al, t.be, r.a)) return false;
        r.ds.clear();
        for (size_t i = runs.size(); i-- > 2;) { long long v; if (!dec(runs[i], t.al, t.be, v)) return false; r.ds.push_back(v); }
        if (t.P.empty()) while (!r.ds.empty() && r.ds[0] == 0) r.ds.erase(r.ds.begin());
        return true;
    }

    P2 run_next(const TM &m, const Tmpl &t, const std::vector<long long> &ds, long long a, long long b, long long N) {
        std::string w = word(t, ds, a, b);
        size_t first = w.find_first_not_of('0');
        long long need = 2 * N + 2 * (long long)w.size() + 64;
        if ((long long)tape.size() < need) tape.assign(need, 0);
        long long p = (long long)tape.size() / 2, vlo = p - (long long)w.size(), vhi = p;
        long long mn = p, mx = p - 1;
        for (size_t i = 0; i < w.size(); ++i) {
            tape[vlo + i] = (uint8_t)(w[i] - '0');
            if (w[i] == '1') { if (mn > mx) mn = mx = vlo + i; else mx = vlo + i; }
        }
        (void)first;
        int q = t.q;
        P2 r;
        long long work = 0;
        for (long long st = 0; st < N; ++st) {
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
            if (work > 400000000LL) break;
            P2 got;
            if (!parse(t, p, lo, got)) continue;
            got.kind = 0; got.steps = st + 1; r = got;
            break;
        }
        if (vlo < 0) vlo = 0;
        memset(tape.data() + vlo, 0, (size_t)(vhi - vlo + 1));
        return r;
    }
};

static long long floordiv2(long long a, long long b) { long long q = a / b; if (a % b && ((a < 0) != (b < 0))) --q; return q; }
static bool lin2(const std::vector<std::pair<long long, long long>> &v, long long &m, long long &c) {
    if (v.size() < 2) return false;
    m = floordiv2(v[1].second - v[0].second, v[1].first - v[0].first);
    c = v[0].second - m * v[0].first;
    for (auto &x : v) if (x.second != m * x.first + c) return false;
    return true;
}

struct Fit2 {
    bool ok = false; int tail = -1;
    long long m1 = 0, c1 = 0, m2 = 0, c2 = 0, b2 = 0, m3 = 0, c3 = 0, e3 = 0, a3 = 0, b3 = 0, mh = 0, ch = 0;
    bool h = false; std::string r4;
    int grade = -1;
};
// grade order: most interesting first
static const char *GRADE2[] = {"CHAMPION", "R4-SOME", "HALT?", "HALT-SOME", "CHECK", "NOBOUNDARY", "SAFE"};
static const int NGRADE2 = 7;

static Fit2 fit2(Prober2 &pr, const TM &m, const Tmpl &t, long long N) {
    Fit2 f;
    std::vector<std::pair<long long, long long>> v;
    for (long long b = 1; b <= 5; ++b) {
        P2 r = pr.run_next(m, t, {2}, 2, b, N);
        if (r.kind != 0 || r.ds.size() != 1 || r.ds[0] != 2 || r.a != 1) return f;
        v.push_back({b, r.b});
    }
    if (!lin2(v, f.m1, f.c1)) return f;
    v.clear();
    for (long long b = 1; b <= 5; ++b) {
        P2 r = pr.run_next(m, t, {2}, 0, b, N);
        if (r.kind != 0 || r.ds.size() != 1 || r.ds[0] != 1) return f;
        if (b == 1) f.b2 = r.b; else if (r.b != f.b2) return f;
        v.push_back({b, r.a});
    }
    if (!lin2(v, f.m2, f.c2)) return f;
    // R3: refill x(b, k) = m3 b + c3 + e3 k, tail of k-1 ones or zeros, constants a3, b3
    std::vector<std::tuple<long long, long long, long long>> pts;     // (b, k, x)
    std::vector<std::pair<long long, long long>> kh;
    bool first = true, consts = true; int tail = -1; int bs_with = 0;
    for (long long b = 1; b <= 4; ++b) {
        bool any = false;
        for (long long k = 1; k <= 8 * b + 7; ++k) {     // as kfit.py: far enough to see the boundary
            std::vector<long long> ds = {1, 2};
            ds.insert(ds.end(), k, 0);
            P2 r = pr.run_next(m, t, ds, 0, b, N);
            if (r.kind == 1) { kh.push_back({b, k}); break; }
            if (r.kind != 0 || (long long)r.ds.size() != 2 + k || r.ds[0] != 1 || r.ds[1] != 1) break;
            int tt = -1; bool uni = true;
            for (size_t i = 3; i < r.ds.size(); ++i) {
                int vv = r.ds[i] == 1 ? 1 : r.ds[i] == 0 ? 0 : 2;
                if (tt < 0) tt = vv; else if (vv != tt) uni = false;
            }
            if (!uni || tt == 2) break;
            if (tt >= 0) { if (tail < 0) tail = tt; else if (tail != tt) consts = false; }
            if (first) { f.a3 = r.a; f.b3 = r.b; first = false; }
            else if (r.a != f.a3 || r.b != f.b3) consts = false;
            pts.push_back({b, k, r.ds[2]});
            any = true;
        }
        if (any) ++bs_with;
    }
    if (!consts || bs_with < 3) return f;
    // fit x = m3 b + c3 + e3 k: e3 from two points with the same b, m3 from k = 1 across b
    std::map<long long, std::vector<std::pair<long long, long long>>> byb;
    for (auto &p : pts) byb[std::get<0>(p)].push_back({std::get<1>(p), std::get<2>(p)});
    bool have_e = false;
    for (auto &kv : byb) if (kv.second.size() >= 2) { f.e3 = kv.second[1].second - kv.second[0].second; have_e = true; break; }
    if (!have_e) f.e3 = 0;
    std::vector<std::pair<long long, long long>> k1;
    for (auto &kv : byb) k1.push_back({kv.first, kv.second[0].second - f.e3 * kv.second[0].first});
    if (!lin2(k1, f.m3, f.c3)) return f;
    for (auto &p : pts) if (std::get<2>(p) != f.m3 * std::get<0>(p) + f.c3 + f.e3 * std::get<1>(p)) return f;
    f.tail = tail < 0 ? 1 : tail;
    f.ok = true;
    // R4
    int halts = 0, conts = 0;
    for (long long b = 1; b <= 5; ++b) {
        P2 r = pr.run_next(m, t, {}, 0, b, N);
        f.r4 += r.kind == 1 ? 'H' : r.kind == 0 ? 'K' : 'T';
        if (r.kind == 1) ++halts; else if (r.kind == 0) ++conts;
    }
    if (halts == 5) { f.grade = 0; return f; }
    if (halts > 0) { f.grade = 1; return f; }
    f.h = kh.size() >= 3 && lin2(kh, f.mh, f.ch);
    // no linear boundary: if some reset probes halted anyway (for instance only for odd b, as the BB(9) champion
    // does), that is HALT-SOME, not harmless
    if (!f.h) { f.grade = kh.empty() ? 5 : 3; return f; }
    bool s1 = true, s2 = true, s3 = true, s4 = true;
    for (long long b = 1; b < 200; ++b) {
        if (!(f.m1 * b + f.c1 >= b + 1)) s1 = false;
        if (!(f.m2 * b + f.c2 >= b)) s2 = false;
        if (!(f.m3 * b + f.c3 - (b - 1) >= 2)) s3 = false;
        if (!(f.mh * b + f.ch > b - 1)) s4 = false;
    }
    bool s5 = f.a3 == 1 && f.b3 == 1 && f.b2 == 1 && f.tail == 1 && f.e3 == -1;
    f.grade = !s4 ? 2 : (!(s1 && s2 && s3 && s5) ? 4 : 6);
    return f;
}

static std::string params(const Fit2 &f) {
    char buf[200];
    snprintf(buf, sizeof buf, "R1 %lldb%+lld | R2 a=%lldb%+lld b=%lld | R3 %lldb%+lld%+lldk tail=%d a=%lld b=%lld | R4 %s | H %s",
             f.m1, f.c1, f.m2, f.c2, f.b2, f.m3, f.c3, f.e3, f.tail, f.a3, f.b3, f.r4.c_str(),
             f.h ? (std::to_string(f.mh) + "b" + (f.ch >= 0 ? "+" : "") + std::to_string(f.ch)).c_str() : "-");
    return buf;
}

// Test hook: dlscan2 --tmpl MACHINE O Q P u s alpha beta alphaB betaB S N   (P or S may be '-')
// prints the probe results and the fit for one hand-written template.
static int tmpl_mode(char **a) {
    TM m; if (!parse(a[2], m)) return 2;
    if (a[3][0] == 'L') m = mirrored(m);
    Tmpl t; t.q = a[4][0] - 'A'; t.P = strcmp(a[5], "-") ? a[5] : ""; t.u = a[6]; t.s = a[7];
    t.al = atoll(a[8]); t.be = atoll(a[9]); t.alB = atoll(a[10]); t.beB = atoll(a[11]); t.S = strcmp(a[12], "-") ? a[12] : "";
    long long N = atoll(a[13]);
    Prober2 pr;
    auto show = [&](const std::vector<long long> &ds, long long aa, long long bb) {
        P2 r = pr.run_next(m, t, ds, aa, bb, N);
        printf("K(");
        for (size_t i = 0; i < ds.size(); ++i) printf("%s%lld", i ? "," : "", ds[i]);
        printf("; %lld; %lld) -> ", aa, bb);
        if (r.kind == 1) printf("HALT after %lld\n", r.steps);
        else if (r.kind == 2) printf("TIMEOUT\n");
        else { printf("K("); for (size_t i = 0; i < r.ds.size(); ++i) printf("%s%lld", i ? "," : "", r.ds[i]); printf("; %lld; %lld) in %lld\n", r.a, r.b, r.steps); }
    };
    for (long long b = 1; b <= 3; ++b) show({2}, 2, b);
    for (long long b = 1; b <= 3; ++b) show({2}, 0, b);
    for (long long b = 1; b <= 2; ++b) for (long long k = 1; k <= 3; ++k) { std::vector<long long> ds = {1, 2}; ds.insert(ds.end(), k, 0); show(ds, 0, b); }
    for (long long b = 1; b <= 3; ++b) show({}, 0, b);
    Fit2 f = fit2(pr, m, t, N);
    printf("fit ok=%d grade=%s %s\n", f.ok, f.grade >= 0 ? GRADE2[f.grade] : "-", params(f).c_str());
    return 0;
}

int main(int argc, char **argv) {
    if (argc == 14 && !strcmp(argv[1], "--tmpl")) return tmpl_mode(argv);
    std::vector<std::string> pos; bool all = false;
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--all")) all = true;
        else if (!strcmp(argv[i], "--skipdl")) g_skipdl = true;
        else if (!strncmp(argv[i], "--dlsteps=", 10)) g_dl_steps = atoll(argv[i] + 10);
        else if (!strncmp(argv[i], "--dlN=", 6)) g_dl_N = atoll(argv[i] + 6);
        else pos.push_back(argv[i]);
    }
    if (pos.size() < 2) { fprintf(stderr, "usage: dlscan2 INPUT OUTPUT [STEPS] [N] [--all]\n"); return 2; }
    long long steps = pos.size() > 2 ? atoll(pos[2].c_str()) : 5000000LL;
    long long N = pos.size() > 3 ? atoll(pos[3].c_str()) : 100000LL;
    if (g_skipdl && N > g_dl_N) {
        fprintf(stderr, "--skipdl: probe budget %lld exceeds dlscan's %lld, nothing is skipped\n", N, g_dl_N);
        g_skipdl = false;
    }
    bool prof = getenv("DLSCAN2_PROF") != nullptr;
    long long nskipped = 0;
    std::ifstream in(pos[0]);
    if (!in) { fprintf(stderr, "cannot read %s\n", pos[0].c_str()); return 2; }
    std::ofstream out(pos[1]);
    out << "machine\thalted_step\tn_templates\tgrade\ttemplate\tparams" << (all ? "\ttemplates" : "") << "\n";
    Prober2 pr;
    long long n = 0, nhalt = 0, ngr[NGRADE2] = {0, 0, 0, 0, 0, 0, 0};
    std::string line;
    while (std::getline(in, line)) {
        size_t sp = line.find_first_of(" \t\r");
        if (sp != std::string::npos) line.resize(sp);
        TM m; if (line.find('_') == std::string::npos || !parse(line, m)) continue;
        End2 ends[2];
        auto t0 = std::chrono::steady_clock::now();
        long long halted = census2(m, steps, ends);
        ends[0].collect(); ends[1].collect();
        auto t1 = std::chrono::steady_clock::now();
        g_t[0] += std::chrono::duration<double>(t1 - t0).count();
        ++n; if (halted >= 0) ++nhalt;
        TM mm = mirrored(m);
        Fit2 best; std::string bestT, alls; int nt = 0;
        for (int o = 0; o < 2; ++o) {
            if (getenv("DLSCAN2_SNAPS"))     // debugging: the snapshots the template inference sees
                for (auto &sn : ends[o].snaps) fprintf(stderr, "%c %c %s\n", o ? 'L' : 'R', 'A' + sn.first, sn.second.c_str());
            auto ti0 = std::chrono::steady_clock::now();
            std::vector<Tmpl> ts = infer_templates(ends[o]);
            auto ti1 = std::chrono::steady_clock::now();
            g_t[1] += std::chrono::duration<double>(ti1 - ti0).count();
            for (auto &t : ts) {
                if (g_skipdl && dl_covered(o, t)) { ++nskipped; continue; }
                ++nt;
                if (all) { if (!alls.empty()) alls += ";"; alls += t.str(o ? 'L' : 'R'); }
                auto tf0 = std::chrono::steady_clock::now();
                Fit2 f = fit2(pr, o ? mm : m, t, N);
                g_t[2] += std::chrono::duration<double>(std::chrono::steady_clock::now() - tf0).count();
                if (!f.ok) continue;
                if (best.grade < 0 || f.grade < best.grade) { best = f; bestT = t.str(o ? 'L' : 'R'); }
            }
        }
        if (best.grade >= 0) ++ngr[best.grade];
        if (all || best.grade >= 0) {
            out << line << "\t" << halted << "\t" << nt << "\t" << (best.grade >= 0 ? GRADE2[best.grade] : "-") << "\t"
                << (bestT.empty() ? "-" : bestT) << "\t" << (best.grade >= 0 ? params(best) : "-");
            if (all) out << "\t" << (alls.empty() ? "-" : alls);
            out << "\n";
        }
        if (n % 100 == 0) out.flush();
    }
    out << "#summary\tmachines=" << n << "\thalted=" << nhalt;
    for (int g = 0; g < NGRADE2; ++g) out << "\t" << GRADE2[g] << "=" << ngr[g];
    out << "\tskipped_dl_templates=" << nskipped << "\n";
    if (prof) fprintf(stderr, "prof machines=%lld census=%.3fs infer=%.3fs fits=%.3fs skipped=%lld\n", n, g_t[0], g_t[1], g_t[2], nskipped);
    return 0;
}
