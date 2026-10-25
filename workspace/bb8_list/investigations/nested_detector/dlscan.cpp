// dlscan: fast screen for digit-list (Ackermann-style) machines. It replaces the slow part of
// scan_ack.py / ack_general.py: stage1's census plus kfit.py's literal probes, in one C++ pass.
//
//   dlscan INPUT OUTPUT [STEPS=5000000] [N=100000] [--all]
//
// For each machine in INPUT (one per line):
// 1. Census (as stage1.cpp, but at BOTH tape ends): run from the blank tape for STEPS steps. Whenever the head
//    reads a blank 1-2 cells beyond the outermost 1, record the shape (state, suffix) and sample the tape word
//    for encoding inference. The left end is handled by
//    reading the tape in mirrored order, so its keys refer to the MIRRORED machine (L and R swapped).
// 2. Candidate keys (orientation, state, suffix, unit, sep): every base shape seen (unit 1, sep 0; a superset
//    of scan_ack.py's 4 most frequent strict shapes) and the 3 best inferred encodings (ack_general.py's
//    candidates()).
// 3. Probes (kfam.run_next / kfit.fit, with step budget N per probe; the known family needs under 1,500 steps,
//    and kfit.py's 1,000,000 is kept for confirming hits): on constructed configurations
//    K(ds; a; b) = unit^d1 sep ... unit^a sep unit^b suffix [state>0], test the necessary conditions of
//      R1  K(2; 2; b)      -> K(2; 1; m b + c)          b = 1..5
//      R2  K(2; 0; b)      -> K(1; m b + c; const)      b = 1..5
//      R3  K(1,2,0; 0; b)  -> K(1,1,x; ..; ..)          for at least 3 of b = 1..4
//    stopping at the first failure. A key that passes all three is "full": kfit.py can fit R1-R3 on it only if
//    it is full, so the full keys are a superset of kfit's hits. A key that passes R1 and R2 only is "partial".
//
// OUTPUT (TSV): machine, halted_step, n_keys, full keys, partial keys (';'-joined "O,state,suffix,unit,sep",
// O = R for the machine as given, L for its mirror image; '-' if none). Without --all only machines with a
// full or partial key are listed. The last line is "#summary ...".
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <tuple>
#include <vector>

static const int MAXQ = 16;   // machines with up to 16 states (BB(8) needs 8; the BB(9) champion was a test case)
struct TM { int w[MAXQ][2], d[MAXQ][2], nx[MAXQ][2]; int n; };

static bool parse(const std::string &s, TM &m) {
    m.n = (int)(s.size() + 1) / 7;
    if (m.n < 1 || m.n > MAXQ || (int)s.size() != 7 * m.n - 1) return false;
    for (int q = 0; q < m.n; ++q)
        for (int c = 0; c < 2; ++c) {
            const char *t = s.c_str() + 7 * q + 3 * c;
            if (t[0] == '-' || t[2] == 'Z') { m.nx[q][c] = -1; m.w[q][c] = 0; m.d[q][c] = 1; continue; }
            m.w[q][c] = t[0] - '0'; m.d[q][c] = t[1] == 'R' ? 1 : -1; m.nx[q][c] = t[2] - 'A';
        }
    return true;
}

static TM mirrored(TM m) {
    for (int q = 0; q < m.n; ++q) for (int c = 0; c < 2; ++c) m.d[q][c] = -m.d[q][c];
    return m;
}

// ---------------------------------------------------------------------------------------------- census
// Snapshot sampling: every 16th end event. With g_snap_backoff (dlnbr) the period doubles after every 64
// snapshots taken, so a machine that sits at a tape end for its whole run costs O(log) rather than O(steps).
static bool g_snap_backoff = false;

struct End {
    long long sh[4 * MAXQ];
    long long rev = 0, period = 16, taken = 0;
    std::vector<std::pair<int, std::string>> snaps;
    End() { memset(sh, 0, sizeof sh); }
};

// One end event: the head (at `pos`, reading a blank) is `gap`+1 cells beyond the outermost 1, which is at
// `near`. `dir` is +1 at the right end and -1 at the left end; T[x] is tape cell x. `farB` is a bound on the
// outermost 1 at the other end and is tightened here when a snapshot is taken. Snapshot words are read from the
// far end to the cell next to the head, i.e. in the orientation where the head is on the right.
static inline void end_event(End &e, const uint8_t *T, int q, int gap, long long &farB, long long near,
                             long long pos, int dir) {
    // Shape = (state, gap, outermost run is a single 1). Unlike stage1.cpp there is no condition on the rest of
    // the tape: zero digits (extra 0s between runs) are normal in a digit list and made stage1 miss machines.
    bool single = T[near - dir] == 0;
    e.sh[q * 4 + gap * 2 + single]++;
    if (++e.rev % e.period != 0) return;
    while (T[farB] == 0) farB += dir;          // stops at `near` at the latest
    long long span = dir > 0 ? pos - farB : farB - pos;
    if (span > 4000) return;
    if (g_snap_backoff && ++e.taken % 64 == 0) e.period *= 2;
    std::string w; w.reserve(span);
    for (long long i = farB; i != pos; i += dir) w += char('0' + T[i]);
    if (e.snaps.size() >= 8) e.snaps.erase(e.snaps.begin());
    e.snaps.push_back({q, w});
}

static long long census(const TM &m, long long steps, End ends[2]) {
    std::vector<uint8_t> tape(1 << 12, 0);
    long long off = tape.size() / 2, pos = 0;
    // Every 1 on the tape lies in [loB, hiB]. The bounds grow when a 1 is written and are only tightened when an
    // end event needs them, so erasing an outermost 1 costs nothing (an exact span made some machines quadratic).
    long long loB = 1, hiB = 0;
    int q = 0;
    for (long long t = 0; t < steps; ++t) {
        long long idx = pos + off;
        if (idx < 2 || idx + 2 >= (long long)tape.size()) {
            std::vector<uint8_t> nt(tape.size() * 2, 0);
            long long shift = tape.size() / 2;
            memcpy(nt.data() + shift, tape.data(), tape.size());
            off += shift; tape.swap(nt); idx = pos + off;
        }
        const uint8_t *T = tape.data() + off;
        int c = T[pos];
        if (c == 0 && loB <= hiB) {
            int gr = T[pos - 1] ? 0 : (T[pos - 2] ? 1 : -1);   // a 1 within two cells on the left
            int gl = T[pos + 1] ? 0 : (T[pos + 2] ? 1 : -1);   // a 1 within two cells on the right
            if (gr >= 0 && gl < 0) {            // right-end event if no 1 lies right of the head
                bool clear = true;
                while (hiB > pos) { if (T[hiB]) { clear = false; break; } --hiB; }
                if (clear) { hiB = pos - 1 - gr; end_event(ends[0], T, q, gr, loB, hiB, pos, 1); }
            } else if (gl >= 0 && gr < 0) {     // left-end event if no 1 lies left of the head
                bool clear = true;
                while (loB < pos) { if (T[loB]) { clear = false; break; } ++loB; }
                if (clear) { loB = pos + 1 + gl; end_event(ends[1], T, q, gl, hiB, loB, pos, -1); }
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

// ------------------------------------------------------------------------------------------ candidates
struct Key {
    int q; std::string suf, unit, sep;
    bool operator<(const Key &o) const { return std::tie(q, suf, unit, sep) < std::tie(o.q, o.suf, o.unit, o.sep); }
    bool operator==(const Key &o) const { return q == o.q && suf == o.suf && unit == o.unit && sep == o.sep; }
};

static const char *UNITS[] = {"1", "10", "11", "100", "101", "110", "111", "1000", "1010", "1100", "1110"};
static const char *SEPS[] = {"0", "1", "00", "01", "10", "11", "000", "001", "011", "100", "110"};

static inline bool ends_with(const char *w, long long e, const std::string &x) {
    long long n = (long long)x.size();
    return e >= n && memcmp(w + e - n, x.data(), n) == 0;
}

// kfam.parse_runs / ack_general.parse_runs on w[0:e): w = unit^d1 sep unit^d2 ... sep unit^dn, parsed greedily
// from the right. `z` = number of leading '0' characters of w (so w[0:x) is blank iff x <= z).
// Returns false if it does not parse; runs are returned first-to-last. `work` counts character comparisons.
static bool parse_runs(const char *w, long long e, long long z, const std::string &u, const std::string &sep,
                       std::vector<long long> &runs, long long &work) {
    runs.clear();
    for (;;) {
        long long k = 0;
        while (ends_with(w, e, u)) { e -= u.size(); ++k; }
        work += k + 1;
        runs.push_back(k);
        if (e <= z) break;
        if (!ends_with(w, e, sep)) return false;
        e -= sep.size();
        if (e <= z) { runs.push_back(0); break; }
    }
    std::reverse(runs.begin(), runs.end());
    return true;
}

// Every (state, suffix) shape seen at this end, most frequent first (scan_ack.py took the top 4 seen >= 3 times).
static std::vector<Key> base_keys(const End &e) {
    std::vector<std::pair<long long, std::string>> cen;
    for (int q = 0; q < MAXQ; ++q) for (int g = 0; g < 2; ++g) for (int l1 = 0; l1 < 2; ++l1) {
        long long cnt = e.sh[q * 4 + g * 2 + l1];
        if (cnt < 1) continue;
        cen.push_back({cnt, std::string(1, char('A' + q)) + "," + (g == 1 ? "0" : (l1 ? "01" : "1"))});
    }
    std::sort(cen.begin(), cen.end(), [](const auto &a, const auto &b) { return a > b; });
    std::vector<Key> out; std::vector<std::string> seen;
    for (auto &x : cen) {
        if (std::find(seen.begin(), seen.end(), x.second) != seen.end()) continue;
        seen.push_back(x.second);
        out.push_back({x.second[0] - 'A', x.second.substr(2), "1", "0"});
    }
    return out;
}

// ack_general.py candidates(): the 3 best (state, suffix, unit, sep) seen in at least 2 snapshots.
// A key counts for a snapshot if the word minus a 1-3 character suffix parses into >= 3 digits, at least two of
// them >= 2 and not all equal. The parse is parse_runs(), with the runs of each unit precomputed per snapshot
// (cnt[e] = number of consecutive units ending at position e) so that a long unary tape costs O(length) once
// per unit instead of once per (unit, separator, suffix).
static std::vector<Key> general_keys(const End &e) {
    const int NU = sizeof UNITS / sizeof *UNITS, NS = sizeof SEPS / sizeof *SEPS;
    std::string units[NU], seps[NS];
    for (int i = 0; i < NU; ++i) units[i] = UNITS[i];
    for (int i = 0; i < NS; ++i) seps[i] = SEPS[i];
    std::vector<Key> order; std::map<Key, int> score;
    std::vector<long long> runs;
    std::vector<std::vector<int>> cnt(NU);
    for (auto &sn : e.snaps) {
        const std::string &w = sn.second;
        long long len = (long long)w.size(), zfull = 0;
        while (zfull < len && w[zfull] == '0') ++zfull;
        for (int ui = 0; ui < NU; ++ui) {
            long long ul = (long long)units[ui].size();
            cnt[ui].assign(len + 1, 0);
            for (long long x = ul; x <= len; ++x)
                if (memcmp(w.data() + x - ul, units[ui].data(), ul) == 0) cnt[ui][x] = cnt[ui][x - ul] + 1;
        }
        std::vector<Key> seen;
        for (int L = 1; L <= 3; ++L) {
            if (len <= L) continue;
            std::string suf = w.substr(len - L);
            long long blen = len - L, z = zfull < blen ? zfull : blen;
            for (int ui = 0; ui < NU; ++ui) for (int si = 0; si < NS; ++si) {
                const std::string &us = units[ui], &ss = seps[si];
                if ((us == "1" && ss == "0") || us == ss) continue;
                runs.clear();
                bool ok = true;
                for (long long x = blen;;) {
                    long long k = cnt[ui][x];
                    x -= k * (long long)us.size();
                    runs.push_back(k);
                    if (x <= z) break;
                    if (!ends_with(w.data(), x, ss)) { ok = false; break; }
                    x -= ss.size();
                    if (x <= z) { runs.push_back(0); break; }
                }
                if (!ok || runs.size() < 3) continue;
                std::reverse(runs.begin(), runs.end());
                int big = 0; bool differ = false;
                for (long long r : runs) { if (r >= 2) ++big; if (r != runs[0]) differ = true; }
                if (big < 2 || !differ) continue;
                Key key{sn.first, suf, us, ss};
                if (std::find(seen.begin(), seen.end(), key) != seen.end()) continue;
                seen.push_back(key);
                if (!score.count(key)) order.push_back(key);
                score[key]++;
            }
        }
    }
    std::stable_sort(order.begin(), order.end(), [&](const Key &a, const Key &b) { return score[a] > score[b]; });
    std::vector<Key> out;
    for (auto &k : order) if (score[k] >= 2 && out.size() < 3) out.push_back(k);
    return out;
}

// ---------------------------------------------------------------------------------------------- probes
struct Probe { int kind; std::vector<long long> ds; long long a = 0, b = 0, steps = 0; };  // kind: 0 K, 1 HALT, 2 TIMEOUT

struct Prober {
    std::vector<uint8_t> tape;
    std::string buf;
    std::vector<long long> runs;
    static constexpr long long PARSE_CAP = 200000000LL;  // per probe; beyond it the probe counts as a timeout

    // kfam.parse_at with the head at p (in state key.q, reading 0): true if the tape is a family configuration;
    // `runs` then holds ds..., a, b. [mn, mx] are the lazy bounds of the 1s and are tightened here.
    bool parse_at(const Key &key, bool base, long long p, long long &mn, long long &mx, long long &work) {
        const std::string &u = key.unit, &sep = key.sep, &suf = key.suf;
        long long n = (long long)suf.size();
        for (long long i = 0; i < n; ++i) if (tape[p - n + i] != (uint8_t)(suf[i] - '0')) return false;
        while (mx > p && !tape[mx]) --mx;                     // everything right of the head must be blank
        if (mx > p) return false;
        while (mn < p && !tape[mn]) ++mn;
        long long lo = mn < p ? mn : p;                       // first non-blank cell left of the head
        long long e = p - n;                                  // the word is tape[lo, e)
        runs.clear();
        if (base) {
            long long cur = 0;
            for (long long i = e - 1; i >= lo; --i) {
                if (tape[i]) ++cur; else { runs.push_back(cur); cur = 0; }
            }
            runs.push_back(cur);
            work += e > lo ? e - lo : 0;
            std::reverse(runs.begin(), runs.end());
        } else {
            long long len = e > lo ? e - lo : 0;
            buf.resize(len);
            for (long long i = 0; i < len; ++i) buf[i] = char('0' + tape[lo + i]);
            work += len;
            long long z = 0;
            while (z < len && buf[z] == '0') ++z;
            if (!parse_runs(buf.data(), len, z, u, sep, runs, work)) runs.clear();
        }
        if (runs.size() < 2) return false;
        if (runs.size() > 2 && runs[0] == 0) return false;
        return true;
    }

    // Literal run from the blank tape (start state A) for `steps` steps: how often is the machine in a family
    // configuration of `key`? nK counts all of them, nDig those with at least one digit, maxDig is the longest
    // digit list seen. Returns the halting step, or -1.
    long long trace(const TM &m, const Key &key, long long steps, long long &nK, long long &nDig, long long &maxDig) {
        bool base = key.unit == "1" && key.sep == "0";
        long long need = 2 * steps + 64;
        if ((long long)tape.size() < need) tape.assign(need, 0);
        long long p = (long long)tape.size() / 2, vlo = p, vhi = p, mn = p, mx = p - 1, work = 0, halted = -1;
        int q = 0;
        nK = nDig = maxDig = 0;
        for (long long t = 0; t < steps; ++t) {
            int c = tape[p];
            if (m.nx[q][c] < 0) { halted = t; break; }
            int wr = m.w[q][c];
            tape[p] = (uint8_t)wr;
            if (wr) {
                if (mn > mx) mn = mx = p;
                else { if (p < mn) mn = p; if (p > mx) mx = p; }
            }
            p += m.d[q][c]; q = m.nx[q][c];
            if (p < vlo) vlo = p;
            if (p > vhi) vhi = p;
            if (q != key.q || tape[p] != 0) continue;
            if (work > 20 * PARSE_CAP) continue;              // parse budget spent: keep running for the halt only
            if (!parse_at(key, base, p, mn, mx, work)) continue;
            ++nK;
            long long nd = (long long)runs.size() - 2;
            if (nd >= 1) ++nDig;
            if (nd > maxDig) maxDig = nd;
        }
        memset(tape.data() + vlo, 0, (size_t)(vhi - vlo + 1));
        return halted;
    }

    // kfam.run_next(tm, ds, a, b, N) for the shape/encoding `key`.
    Probe run_next(const TM &m, const Key &key, const std::vector<int> &ds, int a, int b, long long N) {
        const std::string &u = key.unit, &sep = key.sep, &suf = key.suf;
        bool base = u == "1" && sep == "0";
        std::string w;
        for (int d : ds) { for (int i = 0; i < d; ++i) w += u; w += sep; }
        for (int i = 0; i < a; ++i) w += u;
        w += sep;
        for (int i = 0; i < b; ++i) w += u;
        w += suf;
        size_t first = w.find_first_not_of('0');
        w = first == std::string::npos ? std::string() : w.substr(first);
        long long need = 2 * N + 2 * (long long)w.size() + 64;
        if ((long long)tape.size() < need) tape.assign(need, 0);
        long long p = (long long)tape.size() / 2;
        long long vlo = p - (long long)w.size(), vhi = p;
        // Every 1 lies in [mn, mx]: bounds that grow on writes and are tightened only when a parse needs them.
        long long mn = p, mx = p - 1;
        for (size_t i = 0; i < w.size(); ++i) {
            tape[vlo + i] = (uint8_t)(w[i] - '0');
            if (w[i] == '1') { if (mn > mx) mn = mx = vlo + i; else mx = vlo + i; }
        }
        int q = key.q;
        Probe r; r.kind = 2;
        long long work = 0;
        for (long long t = 0; t < N; ++t) {
            int c = tape[p];
            if (m.nx[q][c] < 0) { r.kind = 1; r.steps = t; break; }
            int wr = m.w[q][c];
            tape[p] = (uint8_t)wr;
            if (wr) {
                if (mn > mx) mn = mx = p;
                else { if (p < mn) mn = p; if (p > mx) mx = p; }
            }
            p += m.d[q][c]; q = m.nx[q][c];
            if (p < vlo) vlo = p;
            if (p > vhi) vhi = p;
            if (q != key.q || tape[p] != 0) continue;
            bool isK = parse_at(key, base, p, mn, mx, work);
            if (work > PARSE_CAP) break;
            if (!isK) continue;
            r.kind = 0; r.steps = t + 1;
            r.ds.assign(runs.begin(), runs.end() - 2);
            r.a = runs[runs.size() - 2]; r.b = runs.back();
            break;
        }
        if (vlo < 0) vlo = 0;
        memset(tape.data() + vlo, 0, (size_t)(vhi - vlo + 1));
        return r;
    }

    // 0: not a candidate, 1: R1 and R2 hold (partial), 2: R1, R2 and the R3 precondition hold (full).
    int screen(const TM &m, const Key &key, long long N) {
        long long v[6], a2[6], b2 = 0;
        for (int b = 1; b <= 5; ++b) {
            Probe r = run_next(m, key, {2}, 2, b, N);
            if (r.kind != 0 || r.ds.size() != 1 || r.ds[0] != 2 || r.a != 1) return 0;
            v[b] = r.b;
        }
        { long long mm = v[2] - v[1], c = v[1] - mm; for (int b = 1; b <= 5; ++b) if (v[b] != mm * b + c) return 0; }
        for (int b = 1; b <= 5; ++b) {
            Probe r = run_next(m, key, {2}, 0, b, N);
            if (r.kind != 0 || r.ds.size() != 1 || r.ds[0] != 1) return 0;
            a2[b] = r.a;
            if (b == 1) b2 = r.b; else if (r.b != b2) return 0;
        }
        { long long mm = a2[2] - a2[1], c = a2[1] - mm; for (int b = 1; b <= 5; ++b) if (a2[b] != mm * b + c) return 0; }
        int good = 0;
        for (int b = 1; b <= 4; ++b) {
            Probe r = run_next(m, key, {1, 2, 0}, 0, b, N);
            if (r.kind == 0 && r.ds.size() == 3 && r.ds[0] == 1 && r.ds[1] == 1) ++good;
        }
        return good >= 3 ? 2 : 1;
    }
};

static std::string key_str(char orient, const Key &k) {
    return std::string(1, orient) + "," + char('A' + k.q) + "," + k.suf + "," + k.unit + "," + k.sep;
}

// Test hook: dlscan --probe FILE N. Each line "machine Q suffix unit sep ds a b" (ds comma-separated or '-')
// prints the result of kfam.run_next for that key, for comparison with the Python tools (test_dlscan.py).
static int probe_mode(const char *path, long long N) {
    std::ifstream in(path); std::string tm, q, suf, u, sep, ds; int a, b; Prober pr;
    while (in >> tm >> q >> suf >> u >> sep >> ds >> a >> b) {
        TM m; if (!parse(tm, m)) return 2;
        std::vector<int> d;
        if (ds != "-") { size_t i = 0; while (i < ds.size()) { size_t j = ds.find(',', i); if (j == std::string::npos) j = ds.size(); d.push_back(atoi(ds.substr(i, j - i).c_str())); i = j + 1; } }
        Probe r = pr.run_next(m, Key{q[0] - 'A', suf, u, sep}, d, a, b, N);
        if (r.kind == 1) printf("HALT %lld\n", r.steps);
        else if (r.kind == 2) printf("TIMEOUT\n");
        else {
            printf("K %lld ", r.steps);
            for (size_t i = 0; i < r.ds.size(); ++i) printf("%s%lld", i ? "," : "", r.ds[i]);
            printf("|%lld|%lld\n", r.a, r.b);
        }
    }
    return 0;
}

#ifndef DLSCAN_NO_MAIN   // dlnbr.cpp includes this file for the census and the probes
int main(int argc, char **argv) {
    if (argc == 4 && !strcmp(argv[1], "--probe")) return probe_mode(argv[2], atoll(argv[3]));
    std::vector<std::string> pos; bool all = false;
    for (int i = 1; i < argc; ++i) { if (!strcmp(argv[i], "--all")) all = true; else pos.push_back(argv[i]); }
    if (pos.size() < 2) { fprintf(stderr, "usage: dlscan INPUT OUTPUT [STEPS] [N] [--all]\n"); return 2; }
    long long steps = pos.size() > 2 ? atoll(pos[2].c_str()) : 5000000LL;
    long long N = pos.size() > 3 ? atoll(pos[3].c_str()) : 100000LL;
    std::ifstream in(pos[0]);
    if (!in) { fprintf(stderr, "cannot read %s\n", pos[0].c_str()); return 2; }
    std::ofstream out(pos[1]);
    out << "machine\thalted_step\tn_keys\tfull\tpartial" << (all ? "\tkeys" : "") << "\n";
    Prober pr;
    long long n = 0, nhalt = 0, nkeyed = 0, nfull = 0, npart = 0;
    std::string line;
    while (std::getline(in, line)) {
        size_t sp = line.find_first_of(" \t\r");
        if (sp != std::string::npos) line.resize(sp);
        TM m; if (line.find('_') == std::string::npos || !parse(line, m)) continue;
        End ends[2];
        long long halted = census(m, steps, ends);
        TM mm = mirrored(m);
        std::string full, part, keys; int nk = 0;
        for (int o = 0; o < 2; ++o) {
            std::vector<Key> ks = base_keys(ends[o]);
            for (auto &k : general_keys(ends[o])) ks.push_back(k);
            for (auto &k : ks) {
                ++nk;
                std::string s = key_str(o ? 'L' : 'R', k);
                if (all) { if (!keys.empty()) keys += ";"; keys += s; }
                int v = pr.screen(o ? mm : m, k, N);
                if (v == 2) { if (!full.empty()) full += ";"; full += s; }
                else if (v == 1) { if (!part.empty()) part += ";"; part += s; }
            }
        }
        ++n; if (halted >= 0) ++nhalt; if (nk) ++nkeyed; if (!full.empty()) ++nfull; if (!part.empty()) ++npart;
        if (all || !full.empty() || !part.empty()) {
            out << line << "\t" << halted << "\t" << nk << "\t" << (full.empty() ? "-" : full) << "\t"
                << (part.empty() ? "-" : part);
            if (all) out << "\t" << (keys.empty() ? "-" : keys);
            out << "\n";
        }
        if (n % 200 == 0) out.flush();
    }
    out << "#summary\tmachines=" << n << "\thalted=" << nhalt << "\twith_keys=" << nkeyed << "\tfull=" << nfull
        << "\tpartial=" << npart << "\n";
    return 0;
}
#endif
