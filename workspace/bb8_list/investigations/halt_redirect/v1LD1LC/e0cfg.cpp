// e0cfg: run MACHINE from (WORD, HEAD, STATE) until an undefined slot is read; print
//   E step STATE SYM HEADOFF | TAPE      (TAPE from the leftmost 1 to the rightmost 1, HEADOFF relative to its start)
// usage: e0cfg MACHINE WORD HEAD STATE MAXSTEPS
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <sstream>
struct Tr { int w, d, nx; bool def; };
int main(int argc, char **argv) {
    std::string m = argv[1], w = argv[2]; long long head = atoll(argv[3]); int q = argv[4][0] - 'A'; long long N = atoll(argv[5]);
    std::vector<std::string> rows; { std::stringstream ss(m); std::string r; while (std::getline(ss, r, '_')) rows.push_back(r); }
    int n = rows.size(); std::vector<Tr> t(2 * n, {0, 0, 0, false});
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { std::string x = rows[s].substr(3 * c, 3);
        if (x[2] != '-' && x[2] != 'Z') t[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    long long L = 16 * (long long)w.size() + (1 << 22); std::vector<unsigned char> tape(L, 0); long long off = L / 2;
    for (size_t i = 0; i < w.size(); ++i) tape[off + i] = w[i] - '0';
    long long h = off + head, lo = off, hi = off + w.size(), step = 0;
    while (step <= N) {
        if (h < 1 || h >= L - 1) { printf("TAPE %lld\n", step); return 1; }
        if (h < lo) lo = h; if (h > hi) hi = h;
        int c = tape[h]; const Tr &tr = t[2 * q + c];
        if (!tr.def) {
            long long a = lo; while (a <= hi && !tape[a]) ++a;
            long long b = hi; while (b >= lo && !tape[b]) --b;
            printf("E %lld %c %d %lld | ", step, 'A' + q, c, h - a);
            for (long long i = a; i <= b; ++i) putchar('0' + tape[i]);
            printf("\n"); return 0;
        }
        tape[h] = tr.w; h += tr.d; q = tr.nx; ++step;
    }
    printf("TIMEOUT %lld\n", N); return 2;
}
