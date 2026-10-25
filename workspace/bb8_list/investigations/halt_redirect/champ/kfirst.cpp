// kfirst.cpp: for each machine (stdin, one per line) and each start (STARTS file: label word head state), run literally
// from the start for at most STEPS steps.  Report per start: H:steps:ones:slot, or the first Kd moment after the start
// (state D, head on 0, 1 to its right, blank to the left; Kd ds a b as in bb10_champion_1RB1RA_0LF0LJ/kd.py) as
// K:step:ndigits:a:b, or T (no Kd moment, no halt), or W (tape limit).  Also exact-cycle detection is NOT done here.
//   kfirst STARTS STEPS < machines.txt
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>
struct Tr { int w, d, nx; bool def; };
struct St { std::string lab, w; long long head; int q; };
static std::vector<Tr> parse(const std::string &M) {
    std::vector<std::string> rows; std::stringstream ss(M); std::string r;
    while (std::getline(ss, r, '_')) rows.push_back(r);
    std::vector<Tr> t;
    for (auto &x : rows) { if (x.size() != 6) { fprintf(stderr, "bad row %s\n", x.c_str()); exit(2); }
        for (int c = 0; c < 2; ++c) { std::string y = x.substr(3 * c, 3);
            if (y == "---" || y[2] == 'Z') { t.push_back({0, 0, 0, false}); continue; }
            if ((y[0] != '0' && y[0] != '1') || (y[1] != 'L' && y[1] != 'R') || y[2] < 'A' || y[2] - 'A' >= (int)rows.size()) { fprintf(stderr, "bad tr %s in %s\n", y.c_str(), M.c_str()); exit(2); }
            t.push_back({y[0] - '0', y[1] == 'R' ? 1 : -1, y[2] - 'A', true}); } }
    return t;
}
int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: kfirst STARTS STEPS < machines\n"); return 2; }
    std::vector<St> sts; { std::ifstream f(argv[1]); std::string l; while (std::getline(f, l)) { std::stringstream s(l); St x; std::string q; if (s >> x.lab >> x.w >> x.head >> q) { x.q = q[0] - 'A'; sts.push_back(x); } } }
    long long N = atoll(argv[2]);
    const long long L = 1 << 24; std::vector<unsigned char> tape(L);
    std::string M;
    std::ifstream mf; if (argc > 3) { mf.open(argv[3]); if (!mf) { fprintf(stderr, "cannot open %s\n", argv[3]); return 2; } }
    std::istream &in = argc > 3 ? static_cast<std::istream &>(mf) : std::cin;
    while (std::getline(in, M)) {
        if (M.empty() || M[0] == '#') continue;
        M = M.substr(0, M.find('\t'));
        auto t = parse(M); printf("%s", M.c_str());
        for (auto &s : sts) {
            std::fill(tape.begin(), tape.end(), 0); long long off = L / 2;
            for (size_t i = 0; i < s.w.size(); ++i) tape[off + i] = s.w[i] - '0';
            long long h = off + s.head, lo = off, hi = off + s.w.size(); int q = s.q; long long n = 0; bool done = false;
            while (n < N) {
                int c = tape[h]; const Tr &tr = t[2 * q + c];
                if (!tr.def) { long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += tape[i];
                    printf("\t%s:H:%lld:%lld:%c%d", s.lab.c_str(), n, ones, 'A' + q, c); done = true; break; }
                tape[h] = tr.w; h += tr.d; q = tr.nx; ++n;
                if (h < lo) lo = h; if (h > hi) hi = h;
                if (h < 4 || h > L - 4) { printf("\t%s:W:%lld", s.lab.c_str(), n); done = true; break; }
                if (q == 3 && tape[h] == 0 && tape[h + 1] == 1) {
                    bool blank = true; for (long long i = lo; i < h; ++i) if (tape[i]) { blank = false; break; }
                    if (!blank) continue;
                    long long e = hi; while (e > h && !tape[e]) --e;
                    std::vector<long long> runs; long long cur = 0;
                    for (long long i = h + 1; i <= e; ++i) { if (tape[i]) ++cur; else { runs.push_back(cur); cur = 0; } }
                    runs.push_back(cur); if (runs.size() < 2) runs.push_back(0);
                    size_t nd = runs.size() - 2; while (nd > 0 && runs[1 + nd] == 0) --nd;
                    long long maxd = 0; for (size_t i = 2; i < 2 + nd; ++i) if (runs[i] > maxd) maxd = runs[i];
                    printf("\t%s:K:%lld:%zu:%lld:%lld:maxd%lld", s.lab.c_str(), n, nd, runs[1], runs[0] - 1, maxd); done = true; break;
                }
            }
            if (!done) printf("\t%s:T:%lld", s.lab.c_str(), n);
        }
        printf("\n"); fflush(stdout);
    }
}
