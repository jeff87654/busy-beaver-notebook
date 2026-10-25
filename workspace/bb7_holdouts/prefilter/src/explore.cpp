// explore MACHINE STEPS [MAXLINES]: print tokenised tape words at sampled tape-end events (census2 definition).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
static const int MAXQ = 16;
struct TM { int w[MAXQ][2], d[MAXQ][2], nx[MAXQ][2]; int n; };
static bool parse(const std::string &s, TM &m) {
    m.n = (int)(s.size() + 1) / 7;
    if (m.n < 1 || m.n > MAXQ || (int)s.size() != 7 * m.n - 1) return false;
    for (int q = 0; q < m.n; ++q) for (int c = 0; c < 2; ++c) {
        const char *t = s.c_str() + 7 * q + 3 * c;
        if (t[0] == '-' || t[2] == 'Z') { m.nx[q][c] = -1; m.w[q][c] = 0; m.d[q][c] = 1; continue; }
        m.w[q][c] = t[0] - '0'; m.d[q][c] = t[1] == 'R' ? 1 : -1; m.nx[q][c] = t[2] - 'A';
    }
    return true;
}
// tokenise w read from the head end inward: greedy, at each point pick period p<=4 with most repeated cells
static std::string tok(const std::string &w) {
    std::string out; long long x = (long long)w.size();
    std::string lit;
    while (x > 0) {
        int bp = 0; long long bc = 0;
        for (int p = 1; p <= 4 && p <= x; ++p) {
            long long c = p;
            while (x - c - 1 >= 0 && w[x - c - 1] == w[x - c - 1 + p]) ++c;
            long long reps = c / p;
            if (reps >= 3 && reps * p > bc) { bc = reps * p; bp = p; }
        }
        if (bp) {
            if (!lit.empty()) { out += " " + std::string(lit.rbegin(), lit.rend()); lit.clear(); }
            std::string pat = w.substr(x - bp, bp);
            out += " (" + pat + ")^" + std::to_string(bc / bp);
            x -= bc;
        } else { lit += w[x - 1]; --x; }
    }
    if (!lit.empty()) out += " " + std::string(lit.rbegin(), lit.rend());
    return out;
}
int main(int argc, char **argv) {
    TM m; if (!parse(argv[1], m)) return 2;
    long long steps = atoll(argv[2]); long long maxl = argc > 3 ? atoll(argv[3]) : 200;
    std::vector<unsigned char> tape(1 << 22, 0); long long pos = tape.size() / 2; int q = 0;
    long long lo = pos, hi = pos, lines = 0, budget = 0;
    for (long long t = 0; t < steps; ++t) {
        int c = tape[pos];
        budget += 1;
        if (c == 0) {
            bool l = tape[pos-1]|tape[pos-2]|tape[pos-3]|tape[pos-4], r = tape[pos+1]|tape[pos+2]|tape[pos+3]|tape[pos+4];
            int dir = 0;
            if (l && !r) { while (hi > pos && !tape[hi]) --hi; if (hi <= pos) dir = 1; }
            else if (r && !l) { while (lo < pos && !tape[lo]) ++lo; if (lo >= pos) dir = -1; }
            if (dir) {
                while (!tape[lo]) ++lo; while (!tape[hi]) --hi;
                long long span = hi - lo + 1;
                if (budget >= span * 4) {
                    budget = 0;
                    std::string w;
                    if (dir > 0) for (long long i = lo; i < pos; ++i) w += char('0' + tape[i]);
                    else for (long long i = hi; i > pos; --i) w += char('0' + tape[i]);
                    printf("%lld %c %c len=%lld:%s\n", t, dir > 0 ? 'R' : 'L', 'A' + q, (long long)w.size(), tok(w).c_str());
                    if (++lines >= maxl) return 0;
                }
            }
        }
        if (m.nx[q][c] < 0) { printf("HALT %lld\n", t); return 0; }
        tape[pos] = m.w[q][c]; if (m.w[q][c]) { if (pos < lo) lo = pos; if (pos > hi) hi = pos; }
        pos += m.d[q][c]; q = m.nx[q][c];
        if (pos < 8 || pos + 8 >= (long long)tape.size()) { printf("tape out\n"); return 0; }
    }
    return 0;
}
