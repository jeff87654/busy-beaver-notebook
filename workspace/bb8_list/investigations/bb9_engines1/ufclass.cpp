// ufclass STARTFILE LABEL N < machines: literal run for N steps from one start; prints machine, outcome (H step slot|T),
// left growth, right growth (cells beyond the start word), number of E0 reads, and per-state count of reads of a blank
// right of every 1 ("right-end visits"), at checkpoints N/4, N/2, N for left/right growth.
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>
#include <map>
struct Tr { int w, d, nx; bool def; };
int main(int argc, char **argv) {
    std::string w; long long h0 = 0; char q0 = 'A';
    { std::ifstream f(argv[1]); std::string l; while (std::getline(f, l)) { std::stringstream ss(l); std::string lab, ww, q; long long h; ss >> lab >> ww >> h >> q; if (lab == argv[2]) { w = ww; h0 = h; q0 = q[0]; } } }
    long long N = atoll(argv[3]); std::string m;
    while (std::cin >> m) {
        std::vector<Tr> t; { std::stringstream ss(m); std::string r; while (std::getline(ss, r, '_')) for (int c = 0; c < 2; ++c) { std::string x = r.substr(3 * c, 3);
            if (x[2] == '-') t.push_back({0,0,0,false}); else t.push_back({x[0]-'0', x[1]=='R'?1:-1, x[2]-'A', true}); } }
        long long L = 2 * N + 4 * w.size() + 16; std::vector<unsigned char> tp(L, 0); long long off = L / 2;
        for (size_t i = 0; i < w.size(); ++i) tp[off + i] = w[i] - '0';
        long long p = off + h0, lo = off, hi = off + w.size() - 1, r1 = hi; int q = q0 - 'A';
        while (r1 >= lo && !tp[r1]) --r1;
        std::map<std::string, long long> hist; long long e0 = 0, st = 0; long long rv[16] = {0}; std::string out = "T"; std::string cps;
        for (; st < N; ++st) {
            int c = tp[p];
            if (c == 0 && p <= r1) { while (r1 >= p && !tp[r1]) --r1; }
            if (c == 0 && p > r1) { rv[q]++; if (p - 12 >= lo) { std::string k(1, char('A' + q)); k += ':'; for (long long i = p - 12; i < p; ++i) k += char('0' + tp[i]); hist[k]++; } }
            const Tr &x = t[2 * q + c];
            if (!x.def) { out = "H" + std::to_string(st) + ":" + char('A' + q) + std::to_string(c); break; }
            if (q == 4 && c == 0) ++e0;
            tp[p] = x.w; if (x.w && p > r1) r1 = p;
            p += x.d; q = x.nx; if (p < lo) lo = p; if (p > hi) hi = p;
            if (st + 1 == N / 4 || st + 1 == N / 2) cps += std::to_string(off - lo) + "/" + std::to_string(hi - off - (long long)w.size()) + " ";
        }
        cps += std::to_string(off - lo) + "/" + std::to_string(hi - off - (long long)w.size());
        printf("%s\t%s\tLR=%s\tE0=%lld\tRV=", m.c_str(), out.c_str(), cps.c_str(), e0);
        for (int i = 0; i < 9; ++i) if (rv[i]) printf("%c%lld,", 'A' + i, rv[i]);
        std::string bk; long long bv = 0;
        for (auto &kv : hist) if (kv.second > bv) { bv = kv.second; bk = kv.first; }
        printf("\tTOP=%s:%lld\n", bk.c_str(), bv); fflush(stdout);
    }
}
