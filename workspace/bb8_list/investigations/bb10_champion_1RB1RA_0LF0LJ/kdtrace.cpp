// kdtrace.cpp: literal simulator (any number of states <= 16) that reports Kd configurations
//   Kd ds a b = 0^inf [D on 0] 1^(b+1) 0 1^a 0 1^d1 0 ... 0 1^dn 0^inf   (head in state D on the 0 left of everything)
// usage: kdtrace MACHINE MAXSTEPS [TAPE HEAD STATE]   (default: blank tape, state A)
// Output: every Kd configuration with a == 0 and the configuration after it ("K step a b d1,d2,..."), plus
// R1 transitions are checked inline (Kd ds a b, a >= 1, must be followed by Kd ds (a-1) (b+3)); a violation
// prints "R1FAIL" and exits 3.  Ends with "HALT step state sym ones" or "TIMEOUT step".
// Option env KDT_ALL=1 prints every Kd configuration.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
struct Tr { int w, d, nx; bool def; };
int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: kdtrace MACHINE MAXSTEPS [TAPE HEAD STATE]\n"); return 2; }
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
    long long maxs = atoll(argv[2]);
    bool all = getenv("KDT_ALL") && atoi(getenv("KDT_ALL"));
    long long size = 1 << 22;
    std::vector<unsigned char> t(size, 0);
    long long pos = size / 2;
    int q = 0;
    if (argc >= 6) {
        std::string w = argv[3];
        for (size_t i = 0; i < w.size(); ++i) t[pos + i] = w[i] == '1';
        pos += atoll(argv[4]);
        q = argv[5][0] - 'A';
    }
    long long minOne = size, maxOne = -1;
    for (long long i = 0; i < size; ++i) if (t[i]) { if (i < minOne) minOne = i; maxOne = i; }
    long long steps = 0;
    // previous K config
    bool havePrev = false; long long pa = 0, pb = 0; std::vector<long long> pds; bool printNext = false;
    std::vector<long long> runs; runs.reserve(1 << 16);
    while (steps < maxs) {
        unsigned char s = t[pos];
        const Tr &x = tr[2 * q + s];
        if (!x.def) {
            long long ones = 0; for (long long i = minOne; i <= maxOne && i >= 0; ++i) ones += t[i];
            printf("HALT %lld %c %d %lld\n", steps, 'A' + q, s, ones);
            return 0;
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
            pos += size / 2; if (maxOne >= 0) { minOne += size / 2; maxOne += size / 2; } else minOne = 2 * size;
            t.swap(u); size *= 2;
            if (maxOne < 0) minOne = size;
        }
        if (q == 3 && t[pos] == 0 && minOne == pos + 1) {
            // parse
            runs.clear();
            long long cur = 0;
            for (long long i = pos + 1; i <= maxOne; ++i) { if (t[i]) ++cur; else { runs.push_back(cur); cur = 0; } }
            runs.push_back(cur);
            if (runs.size() < 2) runs.push_back(0);
            long long b = runs[0] - 1, a = runs[1];
            std::vector<long long> ds(runs.begin() + 2, runs.end());
            while (!ds.empty() && ds.back() == 0) ds.pop_back();
            if (havePrev && pa >= 1) {
                if (!(a == pa - 1 && b == pb + 3 && ds == pds)) {
                    printf("R1FAIL %lld prev a=%lld b=%lld now a=%lld b=%lld\n", steps, pa, pb, a, b);
                    return 3;
                }
            }
            if (all || a == 0 || printNext || !havePrev) {
                printf("K %lld %lld %lld ", steps, a, b);
                for (size_t i = 0; i < ds.size(); ++i) printf(i ? ",%lld" : "%lld", ds[i]);
                printf("\n");
            }
            printNext = (a == 0);
            havePrev = true; pa = a; pb = b; pds.swap(ds);
            fflush(stdout);
        }
    }
    printf("TIMEOUT %lld\n", steps);
    return 0;
}
