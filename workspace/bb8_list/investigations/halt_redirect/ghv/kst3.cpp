// kst3.cpp: literal runner stopping at the next G-frame K-moment, gap-aware.
// K-moment: state G, head on blank cell, all cells right of the head blank, the 8 cells left of the head are 10101010.
// The word left of the tail (from the leftmost 1) is decomposed uniquely into tokens D(m) = (10)^m 1 and gaps 0^k (k >= 2);
// gaps are printed as negative numbers -k. The word must end with a token (the accumulator).
// stdin lines: "word head state maxsteps"; out: "K steps n items..." | "H steps state read ones" | "T steps" | "X steps"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
#include <sstream>
struct Tr { int w, d, nx; bool def; };
int main(int argc, char **argv) {
    std::string m = argv[1]; const int QG = 6;
    std::vector<std::string> rows; { std::stringstream ss(m); std::string r; while (std::getline(ss, r, '_')) rows.push_back(r); }
    int n = rows.size(); std::vector<Tr> t(2 * n, {0, 0, 0, false});
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) { std::string x = rows[q].substr(3 * c, 3);
        if (x[2] >= 'A' && x[2] <= 'Z' && x[0] != '-') t[2 * q + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    std::string line;
    while (std::getline(std::cin, line)) {
        std::stringstream ss(line); std::string w, qs; long long head, N;
        if (!(ss >> w >> head >> qs >> N)) { if (line.size()) { printf("BADINPUT\n"); fflush(stdout); } continue; }
        int q = qs[0] - 'A';
        long long L = 6 * (long long)w.size() + (1 << 22);
        std::vector<unsigned char> tape(L, 0); long long off = L / 3;
        for (size_t i = 0; i < w.size(); ++i) tape[off + i] = w[i] - '0';
        long long h = off + head, lo = off, hi = off + (long long)w.size(); long long step = 0; bool done = false;
        long long rmost = off + (long long)w.size() - 1; while (rmost > lo && !tape[rmost]) --rmost;
        static const unsigned char TL[8] = {1,0,1,0,1,0,1,0};
        while (step < N) {
            if (h < 9 || h >= L - 2) { printf("X %lld\n", step); done = true; break; }
            if (h < lo) lo = h; if (h > hi) hi = h;
            if (step > 0 && q == QG && tape[h] == 0 && h > rmost && memcmp(&tape[h - 8], TL, 8) == 0) {
                long long s = lo; while (s < h && !tape[s]) ++s;
                long long e = h - 9; std::vector<long long> items; bool ok = (s <= e && tape[e] == 1);
                long long p = s;
                while (ok && p <= e) {
                    if (tape[p] == 1) {
                        long long mm = 0;
                        while (p + 2 <= e && tape[p + 1] == 0 && tape[p + 2] == 1) { ++mm; p += 2; }
                        items.push_back(mm); ++p;
                    } else {
                        long long k = 0; while (p <= e && tape[p] == 0) { ++k; ++p; }
                        if (k < 2) { ok = false; break; }
                        items.push_back(-k);
                    }
                }
                if (ok) {
                    std::string out = "K " + std::to_string(step) + " " + std::to_string(items.size());
                    for (auto v : items) { out += ' '; out += std::to_string(v); }
                    printf("%s\n", out.c_str()); done = true; break;
                }
            }
            int c = tape[h]; const Tr &tr = t[2 * q + c];
            if (!tr.def) { long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += tape[i];
                printf("H %lld %c %d %lld\n", step, 'A' + q, c, ones); done = true; break; }
            tape[h] = tr.w; if (tr.w && h > rmost) rmost = h;
            if (!tr.w && h == rmost) { while (rmost > lo && !tape[rmost]) --rmost; }
            h += tr.d; q = tr.nx; ++step;
        }
        if (!done) printf("T %lld\n", N);
        fflush(stdout);
    }
}
