// kgram.cpp: run one stage literally (like evtrace13, until the K-moment / halt / limit) and print every k-gram of
// consecutive slot reads (k = 2..KMAX) that occurs, with its count and first step.  Slots = 2*state+sym (0..31).
// usage: kgram MACHINE STATE HEAD MAXS Q SUF E KMAX < bits     output lines: "G k s1,s2,..,sk count firststep"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>
struct Tr { signed char w, d, nx; bool def; };
static int NST = 10;
static bool parsem(const char *s, Tr *m) {
    int n = (int)strlen(s); if ((n + 1) % 7) return false;
    NST = (n + 1) / 7; if (NST > 16) return false;
    for (int q = 0; q < NST; ++q) for (int c = 0; c < 2; ++c) {
        const char *x = s + 7 * q + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') m[2 * q + c] = {0, 0, 0, false};
        else m[2 * q + c] = {(signed char)(x[0] - '0'), (signed char)(x[1] == 'R' ? 1 : -1), (signed char)(x[2] - 'A'), true};
    }
    return true;
}
static long long EOFF = 1;
static bool small_process(std::vector<long long> tok, long long cap) {
    long long r = tok[0], a = tok[1];
    std::vector<long long> d(tok.begin() + 2, tok.end());
    for (int it = 0; it < 100000; ++it) {
        if (r > cap || a > cap) return false;
        if (a >= 4) { a -= 3; r = 2 * r + 6 - EOFF; continue; }
        if (a != 1) return true;
        size_t j = 0;
        while (j < d.size() && d[j] == 1) ++j;
        if (j == d.size()) return true;
        if (d[j] == 0 || d[j] == 2) return true;
        d[j] -= 3;
        if (j == 0) { a = 2 * r + 7 - 2 * EOFF; r = EOFF; }
        else { d[j - 1] = 2 * r + 7 - 2 * EOFF; r = EOFF; }
    }
    return false;
}
int main(int argc, char **argv) {
    if (argc < 9) { fprintf(stderr, "usage\n"); return 2; }
    const char *ms = argv[1]; int q0 = argv[2][0] - 'A'; long long head = atoll(argv[3]); long long MAXS = atoll(argv[4]);
    int Q = argv[5][0] - 'A'; std::string SUF = argv[6]; if (SUF == "-") SUF = ""; EOFF = atoll(argv[7]); int KMAX = atoi(argv[8]);
    long long RCAP = argc > 9 ? atoll(argv[9]) : 600;
    Tr m[32]; if (!parsem(ms, m)) { printf("X bad machine\n"); return 1; }
    std::string bits; int ch; while ((ch = getchar()) != EOF) if (ch == '0' || ch == '1') bits += (char)ch;
    std::vector<unsigned char> t(std::max<size_t>(1 << 22, 8 * bits.size() + 4096), 0);
    long long off = t.size() / 4; for (size_t i = 0; i < bits.size(); ++i) t[off + i] = bits[i] - '0';
    long long pos = off + head, lo = off, hi = std::max(off + (long long)bits.size() - 1, pos); int q = q0; long long steps = 0;
    if (pos < lo) lo = pos;
    long long r1 = lo - 1; for (long long i = lo; i <= hi; ++i) if (t[i]) r1 = i;
    std::vector<std::unordered_map<unsigned long long, std::pair<long long, long long>>> G(KMAX + 1);
    unsigned long long hist = 0; int nh = 0;   // last slots, 5 bits each
    const char *end = "?";
    while (true) {
        int s = t[pos]; int sl = 2 * q + s;
        hist = (hist << 5) | (unsigned)sl; if (nh < 12) ++nh;
        for (int k = 2; k <= KMAX && k <= nh; ++k) {
            unsigned long long key = hist & ((1ull << (5 * k)) - 1);
            auto it = G[k].find(key);
            if (it == G[k].end()) G[k][key] = {1, steps}; else ++it->second.first;
        }
        long long L = SUF.size();
        if (q == Q && s == 0 && pos > r1 && pos - L - 1 >= lo && steps > 0) {
            bool match = t[pos - L - 1] == 1;
            for (long long i = 0; i < L && match; ++i) if (t[pos - L + i] != (unsigned char)(SUF[i] - '0')) match = false;
            if (match) {
                std::vector<long long> tok; long long p = pos - L - 1;
                while (p >= lo && t[p] == 1) { long long mm = 0; --p; while (p - 1 >= lo && t[p] == 0 && t[p - 1] == 1) { ++mm; p -= 2; } tok.push_back(mm); }
                if (tok.size() >= 2 && !small_process(tok, RCAP)) { end = "K"; break; }
            }
        }
        const Tr &x = m[sl];
        if (!x.def) { end = "H"; break; }
        t[pos] = x.w;
        if (x.w && pos > r1) r1 = pos; else if (!x.w && pos == r1) { while (r1 >= lo && !t[r1]) --r1; }
        pos += x.d; q = x.nx; ++steps;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (pos < 64 || pos >= (long long)t.size() - 64) { end = "W"; break; }
        if (steps >= MAXS) { end = "T"; break; }
    }
    printf("END %s %lld\n", end, steps);
    for (int k = 2; k <= KMAX; ++k) for (auto &e : G[k]) {
        printf("G %d ", k);
        for (int i = k - 1; i >= 0; --i) { int sl = (e.first >> (5 * i)) & 31; printf("%c%d%s", 'A' + sl / 2, sl % 2, i ? "," : ""); }
        printf(" %lld %lld\n", e.second.first, e.second.second);
    }
}
