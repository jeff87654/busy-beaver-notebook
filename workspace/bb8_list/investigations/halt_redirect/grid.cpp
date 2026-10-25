// grid.cpp: run every machine of MACHINES.txt from every start of STARTS.txt (label word head state), budget N.
//   grid MACHINES.txt STARTS.txt N [MAXCELLS=20000000]  >  out.tsv
// Output per pair: machine label H steps ones state read  |  machine label T N  |  machine label W steps (tape cap)
// Machines: standard text format, any number of states up to 16, '---' (or Z target) = halt.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
struct Tr { int w, d, nx; bool def; };
static bool parse(const std::string &s, std::vector<Tr> &t, int &n) {
    std::vector<std::string> rows; std::stringstream ss(s); std::string r;
    while (std::getline(ss, r, '_')) rows.push_back(r);
    n = rows.size(); if (n < 1 || n > 16) return false; t.assign(2 * n, {0, 0, 0, false});
    for (int q = 0; q < n; ++q) { if (rows[q].size() != 6) return false;
        for (int c = 0; c < 2; ++c) { std::string x = rows[q].substr(3 * c, 3);
            if (x[2] == '-' || x[2] == 'Z') continue;
            t[2 * q + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; } }
    return true;
}
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: grid MACHINES STARTS N [MAXCELLS]\n"); return 2; }
    long long N = atoll(argv[3]); long long CAP = argc > 4 ? atoll(argv[4]) : 20000000;
    std::vector<std::string> ms; { std::ifstream f(argv[1]); std::string l; while (std::getline(f, l)) if (!l.empty() && l[0] != '#') { while (!l.empty() && (l.back()=='\r'||l.back()==' ')) l.pop_back(); ms.push_back(l.substr(0, l.find('\t'))); } }
    struct St { std::string lab, w; long long head; int q; };
    std::vector<St> sts; { std::ifstream f(argv[2]); std::string l; while (std::getline(f, l)) { std::stringstream ss(l); St s; std::string qs; if (ss >> s.lab >> s.w >> s.head >> qs) { if (s.w == "-") s.w = ""; s.q = qs[0] - 'A'; sts.push_back(s); } } }
    std::vector<unsigned char> tape;
    for (auto &m : ms) {
        std::vector<Tr> t; int n; if (!parse(m, t, n)) { printf("%s\t-\tBAD\n", m.c_str()); continue; }
        for (auto &s : sts) {
            long long L = std::max<long long>(4096, 4 * (long long)s.w.size());
            tape.assign(L, 0); long long off = L / 2 - (long long)s.w.size() / 2;
            for (size_t i = 0; i < s.w.size(); ++i) tape[off + i] = s.w[i] - '0';
            long long h = off + s.head; int q = s.q; long long step = 0; bool done = false;
            while (step < N) {
                if (h < 0 || h >= (long long)tape.size()) {
                    long long add = tape.size(); if ((long long)tape.size() + add > CAP) { printf("%s\t%s\tW\t%lld\n", m.c_str(), s.lab.c_str(), step); done = true; break; }
                    std::vector<unsigned char> nt(tape.size() + 2 * add, 0); memcpy(&nt[add], tape.data(), tape.size()); tape.swap(nt); h += add; }
                int c = tape[h]; const Tr &tr = t[2 * q + c];
                if (!tr.def) { long long ones = 0; for (auto v : tape) ones += v;
                    printf("%s\t%s\tH\t%lld\t%lld\t%c\t%d", m.c_str(), s.lab.c_str(), step, ones, 'A' + q, c);
                    if (getenv("GRID_DUMP")) { long long lo = 0, hi = (long long)tape.size() - 1; while (lo < h && !tape[lo]) ++lo; while (hi > h && !tape[hi]) --hi;
                        std::string w; for (long long i = lo; i <= hi; ++i) w += char('0' + tape[i]); printf("\t%s\t%lld", w.c_str(), h - lo); }
                    printf("\n"); done = true; break; }
                tape[h] = tr.w; h += tr.d; q = tr.nx; ++step;
            }
            if (!done) printf("%s\t%s\tT\t%lld\n", m.c_str(), s.lab.c_str(), N);
            fflush(stdout);
        }
    }
}
