// r4probe.cpp: literal R4 probes for Kd-family machines.
//   r4probe MACHINE B0 B1 [LIMIT_MUL=4 LIMIT_ADD=5000 | fixed: LIMIT_FIXED]
// For each b in [B0, B1): start from Kd [] 0 b = 0^inf [D on 0] 1^(b+1) 0^inf and run to the next Kd configuration
// (state D on a 0 with everything to its left blank and a 1 to its right), a halt, or the step limit
// LIMIT_MUL*(b+4)^2+LIMIT_ADD.  Output one line per b:
//   K b steps a b' d1,d2,...     |  HALT b steps STATE SYM ones   |  TIMEOUT b steps
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
struct Tr { int w, d, nx; bool def; };
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: r4probe MACHINE B0 B1 [LIMIT_MUL LIMIT_ADD]\n"); return 2; }
    std::string m = argv[1];
    int n = (int)(m.size() + 1) / 7;
    if ((int)m.size() != 7 * n - 1) { fprintf(stderr, "bad machine string\n"); return 2; }
    std::vector<Tr> tr(2 * n);
    for (int q = 0; q < n; ++q)
        for (int c = 0; c < 2; ++c) {
            const char *x = m.c_str() + 7 * q + 3 * c;
            if (x[0] == '-' || x[2] == 'Z' || x[2] - 'A' >= n) { tr[2 * q + c] = {0, 0, 0, false}; continue; }
            tr[2 * q + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true};
        }
    long long B0 = atoll(argv[2]), B1 = atoll(argv[3]);
    long long mul = argc > 4 ? atoll(argv[4]) : 4, add = argc > 5 ? atoll(argv[5]) : 5000;
    for (long long b = B0; b < B1; ++b) {
        long long lim = mul * (b + 4) * (b + 4) + add;
        long long size = 4 * (b + 64) + 4 * 4096;
        std::vector<unsigned char> t(size, 0);
        long long pos = size / 2;
        for (long long i = 1; i <= b + 1; ++i) t[pos + i] = 1;
        long long minOne = pos + 1, maxOne = pos + b + 1;
        int q = 3;  // D
        long long steps = 0;
        bool done = false;
        while (steps < lim) {
            unsigned char s = t[pos];
            const Tr &x = tr[2 * q + s];
            if (!x.def) {
                long long ones = 0; for (long long i = minOne; i <= maxOne && maxOne >= 0; ++i) ones += t[i];
                printf("HALT %lld %lld %c %d %lld\n", b, steps, 'A' + q, s, ones);
                done = true; break;
            }
            t[pos] = (unsigned char)x.w;
            if (x.w == 1) { if (pos < minOne) minOne = pos; if (pos > maxOne) maxOne = pos; }
            else if (s == 1) {
                if (pos == minOne) { while (minOne <= maxOne && !t[minOne]) ++minOne; if (minOne > maxOne) { minOne = size; maxOne = -1; } }
                else if (pos == maxOne) { while (maxOne >= minOne && !t[maxOne]) --maxOne; }
            }
            pos += x.d; q = x.nx; ++steps;
            if (pos <= 1 || pos >= size - 2) {
                std::vector<unsigned char> u(2 * size, 0);
                memcpy(u.data() + size / 2, t.data(), size);
                pos += size / 2; if (maxOne >= 0) { minOne += size / 2; maxOne += size / 2; }
                t.swap(u); size *= 2;
                if (maxOne < 0) minOne = size;
            }
            if (q == 3 && t[pos] == 0 && minOne == pos + 1) {
                std::vector<long long> runs; long long cur = 0;
                for (long long i = pos + 1; i <= maxOne; ++i) { if (t[i]) ++cur; else { runs.push_back(cur); cur = 0; } }
                runs.push_back(cur);
                if (runs.size() < 2) runs.push_back(0);
                std::vector<long long> ds(runs.begin() + 2, runs.end());
                while (!ds.empty() && ds.back() == 0) ds.pop_back();
                printf("K %lld %lld %lld %lld ", b, steps, runs[1], runs[0] - 1);
                for (size_t i = 0; i < ds.size(); ++i) printf(i ? ",%lld" : "%lld", ds[i]);
                printf("\n");
                done = true; break;
            }
        }
        if (!done) printf("TIMEOUT %lld %lld\n", b, steps);
    }
    return 0;
}
