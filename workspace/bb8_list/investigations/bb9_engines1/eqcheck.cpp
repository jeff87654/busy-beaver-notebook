// eqcheck BASE STARTS N < machines : for each machine (one per line) run it and BASE in lockstep from every start
// (lines "label word head state") for N steps; print machine <TAB> first divergence step per start (tape/head/halt
// behaviour; state names may differ) or "eq" if none.  Used to check that a redirect preserves the clearing rules.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>
struct Tr { int w, d, nx; bool def; };
static std::vector<Tr> parse(const std::string &m) {
    std::vector<Tr> t; std::stringstream ss(m); std::string r;
    while (std::getline(ss, r, '_')) for (int c = 0; c < 2; ++c) { std::string x = r.substr(3 * c, 3);
        if (x[2] == '-' || x[2] == 'Z') t.push_back({0, 0, 0, false}); else t.push_back({x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}); }
    return t;
}
int main(int argc, char **argv) {
    std::vector<Tr> B = parse(argv[1]); long long N = atoll(argv[3]);
    struct St { std::string w; long long h; int q; }; std::vector<St> sts;
    { std::ifstream f(argv[2]); std::string l; while (std::getline(f, l)) { std::stringstream ss(l); std::string lab, w, q; long long h; if (ss >> lab >> w >> h >> q) sts.push_back({w, h, q[0] - 'A'}); } }
    std::string m;
    while (std::cin >> m) {
        std::vector<Tr> M = parse(m);
        printf("%s", m.c_str());
        for (auto &s : sts) {
            long long L = 4 * (long long)s.w.size() + 2 * N + 16;
            std::vector<unsigned char> ta(L, 0), tb(L, 0);
            long long off = L / 2 - s.w.size() / 2;
            for (size_t i = 0; i < s.w.size(); ++i) ta[off + i] = tb[off + i] = s.w[i] - '0';
            long long pa = off + s.h, pb = pa; int qa = s.q, qb = s.q; long long st = 0; long long div = -1;
            for (; st < N; ++st) {
                const Tr &x = M[2 * qa + ta[pa]], &y = B[2 * qb + tb[pb]];
                if (!x.def || !y.def) { if (x.def != y.def) div = st; break; }
                if (x.w != y.w || x.d != y.d) { div = st; break; }
                ta[pa] = x.w; tb[pb] = y.w; pa += x.d; pb += y.d; qa = x.nx; qb = y.nx;
            }
            if (div < 0) printf("\teq"); else printf("\t%lld", div);
        }
        printf("\n"); fflush(stdout);
    }
}
