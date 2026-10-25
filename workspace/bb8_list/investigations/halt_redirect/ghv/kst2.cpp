// kst2.cpp: literal runner stopping at the next K-moment in either frame.
//  G-frame: state G, head on blank right of all nonblank cells, word = D(t1)..D(tn) 10101010          -> "K G steps n t1..tn"
//  B-frame: state B, head on blank right of all nonblank cells, word = D(t1)..D(tn) (10)^r 01          -> "K B steps n+1 t1..tn r"
// stdin lines: "word head state maxsteps". Other outputs: "H steps state read ones" | "T steps" | "X steps".
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
#include <sstream>
struct Tr { int w, d, nx; bool def; };
static bool parse(const std::vector<unsigned char> &tape, long long s, long long e, std::vector<long long> &toks) {
    long long p = s; if (s > e) return false;
    while (p <= e) {
        if (tape[p] != 1) return false;
        long long mm = 0;
        while (p + 1 <= e && tape[p + 1] == 0) { ++mm; p += 2; if (p > e || tape[p] != 1) return false; }
        toks.push_back(mm); ++p;
    }
    return true;
}
int main(int argc, char **argv) {
    std::string m = argv[1]; const int QG = 6, QB = 1; std::string fr = argc > 2 ? argv[2] : "GB"; bool useG = fr.find('G') != std::string::npos, useB = fr.find('B') != std::string::npos;
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
            if (h < 2 || h >= L - 2) { printf("X %lld\n", step); done = true; break; }
            if (h < lo) lo = h; if (h > hi) hi = h;
            if (step > 0 && (q == QG || q == QB) && tape[h] == 0 && h > rmost && (q == QG || h == rmost + 1)) {
                long long s = lo; while (s < h && !tape[s]) ++s;
                std::vector<long long> toks; bool ok = false;
                if (useG && q == QG && h - 8 >= s && memcmp(&tape[h - 8], TL, 8) == 0) {
                    ok = parse(tape, s, h - 9, toks);
                    if (ok) { std::string out = "K G " + std::to_string(step) + " " + std::to_string(toks.size());
                        for (auto v : toks) { out += ' '; out += std::to_string(v); } printf("%s\n", out.c_str()); done = true; break; }
                } else if (useB && q == QB && h - 2 >= s && tape[h - 1] == 1 && tape[h - 2] == 0) {
                    long long e = h - 3, r = 0;
                    while (e - 1 >= s && tape[e] == 0 && tape[e - 1] == 1) { ++r; e -= 2; }
                    if (e >= s && tape[e] == 1) {
                        ok = parse(tape, s, e, toks);
                        if (ok) { std::string out = "K B " + std::to_string(step) + " " + std::to_string(toks.size() + 1);
                            for (auto v : toks) { out += ' '; out += std::to_string(v); } out += ' '; out += std::to_string(r);
                            printf("%s\n", out.c_str()); done = true; break; }
                    }
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
