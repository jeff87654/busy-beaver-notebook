// walk.cpp: run MACHINES from STARTS for N steps; per pair print
//   machine label kind steps jvisits lastJ hash lmin_rel rmax_rel qmin_rel qmax_rel
// kind H/T; *_rel: head extremes relative to the start word [0,len) over the whole run (l/r) and over the last quarter (q).
// hash: FNV of (state, head-lo offset, tape lo..hi) at the stop.  J = the 10th state (index 9).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <algorithm>
struct Tr { int w, d, nx; bool def; };
static bool parse(const std::string &s, std::vector<Tr> &t, int &n) {
    std::vector<std::string> rows; std::stringstream ss(s); std::string r;
    while (std::getline(ss, r, '_')) rows.push_back(r);
    n = rows.size(); if (n < 1 || n > 16) return false; t.assign(2 * n, {0, 0, 0, false});
    for (int q = 0; q < n; ++q) { if (rows[q].size() != 6) return false;
        for (int c = 0; c < 2; ++c) { std::string x = rows[q].substr(3 * c, 3);
            if (x[2] == '-' || x[2] == 'Z') continue;
            if (x[0] != '0' && x[0] != '1') return false; if (x[1] != 'L' && x[1] != 'R') return false;
            t[2 * q + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; } }
    return true;
}
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: walk MACHINES STARTS N\n"); return 2; }
    long long N = atoll(argv[3]);
    std::vector<std::string> ms; { std::ifstream f(argv[1]); std::string l; while (std::getline(f, l)) if (!l.empty() && l[0] != '#') { while (!l.empty() && (l.back()=='\r'||l.back()==' ')) l.pop_back(); ms.push_back(l.substr(0, l.find('\t'))); } }
    struct St { std::string lab, w; long long head; int q; };
    std::vector<St> sts; { std::ifstream f(argv[2]); std::string l; while (std::getline(f, l)) { std::stringstream ss(l); St s; std::string qs; if (ss >> s.lab >> s.w >> s.head >> qs) { s.q = qs[0] - 'A'; sts.push_back(s); } } }
    if (sts.empty()) { fprintf(stderr, "no starts\n"); return 2; }
    const long long L = 1LL << 27;  // 134M cells: enough for N <= 60M from the middle
    if (N > 60000000) { fprintf(stderr, "N too large\n"); return 2; }
    std::vector<unsigned char> tape(L);
    for (auto &m : ms) {
        std::vector<Tr> t; int n; if (!parse(m, t, n)) { fprintf(stderr, "BAD machine %s\n", m.c_str()); return 3; }
        for (auto &s : sts) {
            std::fill(tape.begin(), tape.end(), 0);
            long long off = L / 2;
            for (size_t i = 0; i < s.w.size(); ++i) tape[off + i] = s.w[i] - '0';
            long long h = off + s.head, lo = off, hi = off + s.w.size(); int q = s.q; long long step = 0;
            long long jv = 0, lastJ = -1, lmin = h, rmax = h, qmin = h, qmax = h; char kind = 'T';
            long long qstart = N - N / 4;
            while (step < N) {
                int c = tape[h]; const Tr &tr = t[2 * q + c];
                if (!tr.def) { kind = 'H'; break; }
                tape[h] = tr.w; h += tr.d; q = tr.nx; ++step;
                if (q == 9) { ++jv; lastJ = step; }
                if (h < lmin) lmin = h; if (h > rmax) rmax = h;
                if (step >= qstart) { if (step == qstart) { qmin = qmax = h; } if (h < qmin) qmin = h; if (h > qmax) qmax = h; }
                if (h < lo) lo = h; if (h > hi) hi = h;
            }
            unsigned long long hs = 1469598103934665603ULL;
            long long a = lo, b = hi; while (a < b && !tape[a]) ++a; while (b > a && !tape[b]) --b;
            auto mix = [&](unsigned long long v) { hs ^= v; hs *= 1099511628211ULL; };
            mix(q); mix(h - a); for (long long i = a; i <= b; ++i) mix(tape[i]);
            long long W = s.w.size();
            printf("%s\t%s\t%c\t%lld\t%lld\t%lld\t%016llx\t%lld\t%lld\t%lld\t%lld\n", m.c_str(), s.lab.c_str(), kind, step, jv, lastJ, hs,
                   lmin - off, rmax - off - W, qmin - off, qmax - off - W);
            fflush(stdout);
        }
    }
}
