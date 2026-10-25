// Stage 1 of the neighbor search: compare each neighbor's literal run with the parent's, and look for
// the digit-list tape signature.
//
//   stage1 PARENT INPUT OUTPUT [STEPS]
// For each machine in INPUT (one per line), simulate from the blank tape for up to STEPS steps
// (default 2e7) and report as TSV:
//   machine, halted_step (or -1), divergence_step (first step whose (state, read symbol) differs from the
//   parent's; -1 if none within STEPS), k_events, max_runs, k_states.
// k_events counts steps where the head is just right of the rightmost 1, reading blank, and the
// non-blank tape is runs of 1s separated by single 0s ending in a run of length 1: the parent's
// K(ds; a; b) = 1^d1 0 ... 1^a 0 1^b 0 1 [q>0]. max_runs is the largest number of 1-runs seen in such
// a configuration; k_states lists the states in which they occurred.
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <iostream>

struct TM { int w[8][2], d[8][2], nx[8][2]; int n; };

static bool parse(const std::string &s, TM &m) {
    m.n = (int)(s.size() + 1) / 7;
    if (m.n < 1 || m.n > 8 || (int)s.size() != 7 * m.n - 1) return false;
    for (int q = 0; q < m.n; ++q)
        for (int c = 0; c < 2; ++c) {
            const char *t = s.c_str() + 7 * q + 3 * c;
            if (t[0] == '-' || t[2] == 'Z') { m.nx[q][c] = -1; continue; }
            m.w[q][c] = t[0] - '0'; m.d[q][c] = t[1] == 'R' ? 1 : -1; m.nx[q][c] = t[2] - 'A';
        }
    return true;
}

struct Res { long long halted = -1, diverge = -1, kev = 0; int maxruns = 0; unsigned kstates = 0; };

static Res run(const TM &m, long long steps, const std::vector<uint8_t> *ref, std::vector<uint8_t> *rec,
               std::vector<long long> *shapes = nullptr,
               std::vector<std::pair<int, std::string>> *snaps = nullptr) {
    long long rev = 0;  // right-end events seen (for snapshot sampling)
    Res r;
    std::vector<uint8_t> tape(1 << 12, 0);
    long long off = tape.size() / 2, pos = 0, lo = 0, hi = -1;  // lo..hi: range of cells possibly nonzero
    int q = 0;
    for (long long t = 0; t < steps; ++t) {
        long long idx = pos + off;
        if (idx < 0 || idx >= (long long)tape.size()) {
            std::vector<uint8_t> nt(tape.size() * 2, 0);
            long long shift = tape.size() / 2;
            memcpy(nt.data() + shift, tape.data(), tape.size());
            off += shift; tape.swap(nt); idx = pos + off;
        }
        int c = tape[idx];
        uint8_t key = (uint8_t)(q * 2 + c);
        if (rec) rec->push_back(key);
        if (ref && r.diverge < 0 && (t >= (long long)ref->size() || (*ref)[t] != key)) r.diverge = t;
        // Shape census for kfit: head 1 or 2 cells right of the rightmost 1, on a tape of 1-runs separated
        // by single 0s (at least 3 runs). Shape key = state*4 + (gap-1)*2 + (last run == 1).
        if (c == 0 && hi >= lo && (pos == hi + 1 || pos == hi + 2) && shapes) {
            int runs = 0, zeros = 0; bool ok = true; long long run = 0, lastrun = 0;
            for (long long i = lo; i <= hi && ok; ++i) {
                if (tape[i + off]) { if (run == 0 && runs > 0 && zeros != 1) ok = false; ++run; zeros = 0; }
                else { if (run) { ++runs; lastrun = run; run = 0; } ++zeros; }
            }
            if (run) { ++runs; lastrun = run; }
            if (ok && runs >= 3) (*shapes)[q * 4 + (int)(pos - hi - 1) * 2 + (lastrun == 1)]++;
        }
        // K-signature check: head just right of the nonzero region, reading 0.
        if (c == 0 && pos == hi + 1 && hi >= lo) {
            int runs = 0; bool ok = true; long long run = 0, lastrun = 0; int zeros = 0;
            for (long long i = lo; i <= hi && ok; ++i) {
                if (tape[i + off]) { if (run == 0 && runs > 0 && zeros != 1) ok = false; ++run; zeros = 0; }
                else { if (run) { ++runs; lastrun = run; run = 0; } ++zeros; }
            }
            if (run) { ++runs; lastrun = run; }
            if (ok && lastrun == 1 && runs >= 3) {
                ++r.kev; if (runs > r.maxruns) r.maxruns = runs; r.kstates |= 1u << q;
            }
        }
        // Snapshot for encoding inference: head 1-2 cells right of the rightmost 1, reading blank. Keep the
        // last 8 sampled words (tape from the leftmost 1 to the cell left of the head), at most 4000 cells.
        if (snaps && c == 0 && hi >= lo && (pos == hi + 1 || pos == hi + 2) && (++rev % 16 == 0)
            && pos - lo <= 4000) {
            std::string w; w.reserve(pos - lo);
            for (long long i = lo; i < pos; ++i) w += char('0' + tape[i + off]);
            if (snaps->size() >= 8) snaps->erase(snaps->begin());
            snaps->push_back({q, w});
        }
        if (m.nx[q][c] < 0) { r.halted = t; break; }
        int w = m.w[q][c], d = m.d[q][c], nq = m.nx[q][c];
        tape[idx] = (uint8_t)w;
        if (w) {  // [lo, hi] is exactly the span from the leftmost to the rightmost 1
            if (hi < lo) lo = hi = pos;
            else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; }
        } else if (hi >= lo && (pos == lo || pos == hi)) {
            while (hi >= lo && tape[hi + off] == 0) --hi;
            while (lo <= hi && tape[lo + off] == 0) ++lo;
            if (hi < lo) { lo = 0; hi = -1; }
        }
        pos += d; q = nq;
    }
    return r;
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: stage1 PARENT INPUT OUTPUT [STEPS]\n"); return 2; }
    long long steps = argc > 4 ? atoll(argv[4]) : 20000000LL;
    TM p; if (!parse(argv[1], p)) { fprintf(stderr, "bad parent\n"); return 2; }
    std::vector<uint8_t> ref; ref.reserve(steps);
    Res pr = run(p, steps, nullptr, &ref);
    std::ifstream in(argv[2]); std::ofstream out(argv[3]);
    std::ofstream dump; if (argc > 5) dump.open(argv[5]);  // optional: right-end tape snapshots per machine
    out << "machine\thalted_step\tdivergence_step\tk_events\tmax_runs\tk_states\n";
    out << "#parent\t" << pr.halted << "\t-1\t" << pr.kev << "\t" << pr.maxruns << "\t" << pr.kstates << "\n";
    std::string line; long long n = 0;
    while (std::getline(in, line)) {
        while (!line.empty() && (line.back() == '\r' || line.back() == ' ')) line.pop_back();
        TM m; if (!parse(line, m)) continue;
        std::vector<long long> sh(32, 0);
        std::vector<std::pair<int, std::string>> sn;
        Res r = run(m, steps, &ref, nullptr, &sh, dump.is_open() ? &sn : nullptr);
        for (auto &x : sn) dump << line << "\t" << char('A' + x.first) << "\t" << x.second << "\n";
        std::string ks; for (int q = 0; q < 8; ++q) if (r.kstates >> q & 1) ks += char('A' + q);
        // Shape candidates for kfit (state,suffix): gap 1 and last run 1 -> "01"; gap 1, longer last run -> "1";
        // gap 2 -> "0". Listed only if seen at least 3 times.
        std::string shs;
        for (int q = 0; q < 8; ++q) for (int g = 0; g < 2; ++g) for (int l1 = 0; l1 < 2; ++l1) {
            long long cnt = sh[q * 4 + g * 2 + l1];
            if (cnt < 3) continue;
            const char *suf = g == 1 ? "0" : (l1 ? "01" : "1");
            if (!shs.empty()) shs += ";";
            shs += std::string(1, char('A' + q)) + "," + suf + ":" + std::to_string(cnt);
        }
        out << line << "\t" << r.halted << "\t" << r.diverge << "\t" << r.kev << "\t" << r.maxruns << "\t"
            << (ks.empty() ? "-" : ks) << "\t" << (shs.empty() ? "-" : shs) << "\n";
        if (++n % 200 == 0) { out.flush(); fprintf(stderr, "%lld done\n", n); }
    }
    return 0;
}
