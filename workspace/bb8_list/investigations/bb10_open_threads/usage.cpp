// usage.cpp: literal run; counts how often each transition fires and prints the first N tape windows (+-W cells)
// at which a given state is entered.
//   usage MACHINE WORDFILE HEAD STATE MAXSTEPS [WATCHSTATE N W]
// Build: g++ -O2 -std=c++17 -static -o usage.exe usage.cpp
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
struct Tr { int w, d, nx; bool def; };
int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: usage MACHINE WORDFILE HEAD STATE MAXSTEPS [WATCH N W]\n"); return 2; }
    std::string m = argv[1];
    int n = (int)(m.size() + 1) / 7;
    std::vector<Tr> tr(2 * n);
    for (int s = 0; s < n; ++s)
        for (int c = 0; c < 2; ++c) {
            const char *x = m.c_str() + 7 * s + 3 * c;
            if (x[0] == '-' || x[2] - 'A' >= n) { tr[2 * s + c] = {0, 0, 0, false}; continue; }
            tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true};
        }
    std::string word;
    if (std::string(argv[2]) != "-") {
        FILE *f = fopen(argv[2], "r"); int ch;
        while ((ch = fgetc(f)) != EOF) if (ch == '0' || ch == '1') word += (char)ch;
        fclose(f);
    }
    long long head = atoll(argv[3]); int q = argv[4][0] - 'A'; long long maxs = atoll(argv[5]);
    int watch = argc > 6 ? argv[6][0] - 'A' : -1; long long nw = argc > 7 ? atoll(argv[7]) : 0; long long W = argc > 8 ? atoll(argv[8]) : 12;
    long long sz = 1 << 22; std::vector<unsigned char> t(sz, 0); long long off = sz / 2;
    for (size_t i = 0; i < word.size(); ++i) t[off + i] = word[i] == '1';
    long long pos = off + head; std::vector<long long> cnt(2 * n, 0); long long steps = 0, shown = 0;
    while (steps < maxs) {
        int c = t[pos]; const Tr &x = tr[2 * q + c];
        if (!x.def) { printf("HALT at step %lld state %c read %d\n", steps, 'A' + q, c); break; }
        ++cnt[2 * q + c];
        t[pos] = x.w; pos += x.d; q = x.nx; ++steps;
        if (q == watch && shown < nw) {
            std::string s; for (long long i = pos - W; i <= pos + W; ++i) s += (i == pos ? '[' : ' '), s += char('0' + t[i]), s += (i == pos ? ']' : ' ');
            printf("enter %c at step %lld: %s\n", 'A' + q, steps, s.c_str()); ++shown;
        }
        if (pos < 2 || pos > sz - 3) { printf("tape limit\n"); break; }
    }
    for (int s = 0; s < n; ++s) printf("%c0 %lld  %c1 %lld\n", 'A' + s, cnt[2 * s], 'A' + s, cnt[2 * s + 1]);
    printf("steps %lld\n", steps);
}
