// kst.cpp (gh0LH verifier, independent of stage35g/hyb10): literal runner that stops at the next K-moment.
// K-moment: state Q (arg), head on a blank cell, the 8 cells left of the head are 10101010 (tail (10)^4),
// every cell right of the head is blank, and the word left of the tail parses as tokens D(m) = (10)^m 1.
// Server mode: argv[1] = machine, argv[2] = K state letter. stdin lines: "word head state maxsteps".
// Output per line: "K steps n t1..tn" | "H steps state read ones" | "T steps" | "X steps" (tape overflow).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
#include <sstream>
struct Tr { int w, d, nx; bool def; };
int main(int argc, char **argv) {
    std::string m = argv[1]; int Q = argv[2][0] - 'A';
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
        for (size_t i = 0; i < w.size(); ++i) { if (w[i] != '0' && w[i] != '1') { printf("BADWORD\n"); goto next; } tape[off + i] = w[i] - '0'; }
        {
        long long h = off + head, lo = off, hi = off + (long long)w.size(); long long step = 0; bool done = false;
        static const unsigned char TL[8] = {1,0,1,0,1,0,1,0};
        while (step < N) {
            if (h < 2 || h >= L - 2) { printf("X %lld\n", step); done = true; break; }
            if (h < lo) lo = h; if (h > hi) hi = h;
            if (step > 0 && q == Q && tape[h] == 0 && h - 8 >= lo && memcmp(&tape[h - 8], TL, 8) == 0) {
                bool ok = true;
                for (long long i = h + 1; i <= hi && ok; ++i) if (tape[i]) ok = false;
                if (ok) {
                    long long s = lo; while (s < h - 8 && !tape[s]) ++s;
                    long long e = h - 9; std::vector<long long> toks;
                    long long p = s;
                    if (s > e) ok = false;
                    while (ok && p <= e) {
                        if (tape[p] != 1) { ok = false; break; }
                        long long mm = 0;
                        while (p + 1 <= e && tape[p + 1] == 0) { ++mm; p += 2; if (p > e || tape[p] != 1) { ok = false; break; } }
                        if (!ok) break;
                        toks.push_back(mm); ++p;
                    }
                    if (ok) {
                        std::string out = "K " + std::to_string(step) + " " + std::to_string(toks.size());
                        for (auto v : toks) { out += ' '; out += std::to_string(v); }
                        printf("%s\n", out.c_str()); done = true; break;
                    }
                }
            }
            int c = tape[h]; const Tr &tr = t[2 * q + c];
            if (!tr.def) { long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += tape[i];
                printf("H %lld %c %d %lld\n", step, 'A' + q, c, ones); done = true; break; }
            tape[h] = tr.w; h += tr.d; q = tr.nx; ++step;
        }
        if (!done) printf("T %lld\n", N);
        }
        next:
        fflush(stdout);
    }
}
