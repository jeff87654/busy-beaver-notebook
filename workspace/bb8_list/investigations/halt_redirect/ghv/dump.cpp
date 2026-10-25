// dump MACHINE WORD HEAD STATE T1 T2 ... : print tape (as string, head marked) at the given step counts
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <sstream>
struct Tr { int w, d, nx; bool def; };
int main(int argc, char **argv) {
    std::string m = argv[1], w = argv[2]; long long head = atoll(argv[3]); int q = argv[4][0] - 'A';
    std::vector<std::string> rows; { std::stringstream ss(m); std::string r; while (std::getline(ss, r, '_')) rows.push_back(r); }
    int n = rows.size(); std::vector<Tr> t(2 * n, {0, 0, 0, false});
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { std::string x = rows[s].substr(3 * c, 3);
        if (x[0] != '-') t[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    long long L = 4 * w.size() + (1 << 24), off = L / 2; std::vector<unsigned char> tape(L, 0);
    for (size_t i = 0; i < w.size(); ++i) tape[off + i] = w[i] - '0';
    long long h = off + head, lo = off, hi = off + w.size(), step = 0;
    for (int a = 5; a < argc; ++a) {
        long long T = atoll(argv[a]);
        while (step < T) { int c = tape[h]; const Tr &tr = t[2 * q + c]; if (!tr.def) { printf("HALT %lld %c%d\n", step, 'A' + q, c); return 0; }
            tape[h] = tr.w; h += tr.d; q = tr.nx; ++step; if (h < lo) lo = h; if (h > hi) hi = h; }
        long long s = lo; while (s < hi && !tape[s]) ++s; long long e = hi; while (e > s && !tape[e]) --e;
        if (h < s) s = h; if (h > e) e = h;
        std::string out;
        for (long long i = s; i <= e; ++i) { if (i == h) { out += '['; out += char('A' + q); out += char('0' + tape[i]); out += ']'; } else out += char('0' + tape[i]); }
        printf("%lld: %s\n", step, out.c_str());
    }
}
