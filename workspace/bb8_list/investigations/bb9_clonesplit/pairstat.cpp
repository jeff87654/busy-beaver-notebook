// pairstat.cpp: literal TM simulator recording transition-follower pair statistics.
//   pairstat MACHINE < SEGMENTS      SEGMENTS lines: "label word head state steps"   (word '-' = blank)
// For every step with transition X = (state P, symbol s) -> target T, and the symbol t read by T at the next step,
// counts the pair (X, t) and keeps its first occurrence (step within the segment).  Output TSV per segment:
//   label  X(e.g. E0)  T  t  count  first_step
// plus a line "label #END steps outcome" (outcome RUN = budget used, HALT Pq = undefined transition reached).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
#include <sstream>
struct Tr { int w, d, nx; bool def; };
int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: pairstat MACHINE < SEGMENTS\n"); return 2; }
    std::string m = argv[1];
    int n = (int)(m.size() + 1) / 7;
    std::vector<Tr> tr(2 * n);
    for (int q = 0; q < n; ++q)
        for (int c = 0; c < 2; ++c) {
            const char *x = m.c_str() + 7 * q + 3 * c;
            if (x[0] == '-' || x[2] == 'Z') { tr[2 * q + c] = {0, 0, 0, false}; continue; }
            tr[2 * q + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true};
        }
    std::string line;
    while (std::getline(std::cin, line)) {
        std::stringstream ss(line); std::string lab, word, qs; long long head, maxs;
        if (!(ss >> lab >> word >> head >> qs >> maxs)) continue;
        if (word == "-") word = "";
        int q = qs[0] - 'A';
        long long size = std::max<long long>(1 << 20, 4 * (long long)word.size()), off = size / 2;
        std::vector<unsigned char> t(size, 0);
        for (size_t i = 0; i < word.size(); ++i) t[off + i] = word[i] == '1';
        long long pos = off + head;
        std::vector<long long> cnt(4 * n, 0), first(4 * n, -1);
        int prevX = -1; long long steps = 0; std::string outc = "RUN";
        while (true) {
            int c = t[pos];
            if (prevX >= 0) { int k = prevX * 2 + c; if (!cnt[k]++) first[k] = steps - 1; }
            if (steps >= maxs) break;
            const Tr &x = tr[2 * q + c];
            if (!x.def) { outc = std::string("HALT ") + char('A' + q) + char('0' + c); break; }
            prevX = 2 * q + c;
            t[pos] = (unsigned char)x.w; pos += x.d; q = x.nx; ++steps;
            if (pos <= 0 || pos >= size - 1) {
                std::vector<unsigned char> u(2 * size, 0);
                memcpy(u.data() + size / 2, t.data(), size);
                pos += size / 2; off += size / 2; t.swap(u); size *= 2;
            }
        }
        for (int k = 0; k < 4 * n; ++k) if (cnt[k]) {
            int X = k / 2, tt = k % 2;
            printf("%s\t%c%d\t%c\t%d\t%lld\t%lld\n", lab.c_str(), 'A' + X / 2, X % 2, 'A' + tr[X].nx, tt, cnt[k], first[k]);
        }
        printf("%s\t#END\t%lld\t%s\n", lab.c_str(), steps, outc.c_str());
        fflush(stdout);
    }
}
