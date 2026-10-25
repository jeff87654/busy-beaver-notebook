// evtrace13.cpp: literal tracer for one stage, machines up to 16 states.
// usage: evtrace13 MACHINE STATE HEAD MAXS Q SUF E MAXEV WATCHSTATES(e.g. "IJ" or "-") [WINDOW] < bits
// prints EV lines for E0 reads and every read in a watched state (up to MAXEV), then the stage end
// (K/H/T as stage35g), then per-slot read counts and the leftmost cell (relative to the initial leftmost 1) at which
// each slot was read: "SLOT A0 n=.. minpos=.. maxpos=..".  Positions are relative to the first input bit.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
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
    if (argc < 10) { fprintf(stderr, "usage\n"); return 2; }
    const char *ms = argv[1]; int q0 = argv[2][0] - 'A'; long long head = atoll(argv[3]); long long MAXS = atoll(argv[4]);
    int Q = argv[5][0] - 'A'; std::string SUF = argv[6]; if (SUF == "-") SUF = ""; EOFF = atoll(argv[7]);
    long long MAXEV = atoll(argv[8]); std::string W = argv[9]; int WIN = argc > 10 ? atoi(argv[10]) : 30;
    bool watch[16] = {false}; if (W != "-") for (char c : W) watch[c - 'A'] = true;
    long long RCAP = 600;
    Tr m[32]; if (!parsem(ms, m)) { printf("X bad machine\n"); return 1; }
    std::string bits; int ch; while ((ch = getchar()) != EOF) if (ch == '0' || ch == '1') bits += (char)ch;
    std::vector<unsigned char> t(std::max<size_t>(1 << 20, 8 * bits.size() + 4096), 0);
    long long off = t.size() / 4; for (size_t i = 0; i < bits.size(); ++i) t[off + i] = bits[i] - '0';
    long long pos = off + head, lo = off, hi = std::max(off + (long long)bits.size() - 1, pos); int q = q0; long long steps = 0;
    if (pos < lo) lo = pos;
    long long r1 = lo - 1; for (long long i = lo; i <= hi; ++i) if (t[i]) r1 = i;
    long long nev = 0;
    long long cnt[32] = {0}, mn[32], mx[32]; static long long pc[32][32]; int prev = -1; for (int i = 0; i < 32; ++i) { mn[i] = 1LL << 60; mx[i] = -(1LL << 60); }
    auto show = [&](const char *tag) {
        printf("%s %lld %c%d pos=%lld  ", tag, steps, 'A' + q, t[pos], pos - off);
        long long a = std::max(lo, pos - WIN), b = std::min(hi, pos + WIN);
        for (long long i = a; i <= b; ++i) { if (i == pos) putchar('['); putchar('0' + t[i]); if (i == pos) putchar(']'); }
        putchar('\n');
    };
    auto summary = [&]() {
        for (int i = 0; i < 2 * NST; ++i) if (cnt[i]) printf("SLOT %c%d n=%lld minpos=%lld maxpos=%lld\n", 'A' + i / 2, i % 2, cnt[i], mn[i] - off, mx[i] - off);
        for (int i = 0; i < 2 * NST; ++i) for (int j = 0; j < 2 * NST; ++j) if (pc[i][j]) printf("PAIR %c%d>%c%d %lld\n", 'A' + i / 2, i % 2, 'A' + j / 2, j % 2, pc[i][j]);
        printf("LEFTMOST %lld\n", lo - off);
    };
    while (true) {
        int s = t[pos];
        int sl = 2 * q + s; ++cnt[sl]; if (prev >= 0) ++pc[prev][sl]; prev = sl; if (pos < mn[sl]) mn[sl] = pos; if (pos > mx[sl]) mx[sl] = pos;
        if (nev < MAXEV && ((q == 4 && s == 0) || watch[q])) { show("EV"); ++nev; }
        long long L = SUF.size();
        if (q == Q && s == 0 && pos > r1 && pos - L - 1 >= lo && steps > 0) {
            bool match = t[pos - L - 1] == 1;
            for (long long i = 0; i < L && match; ++i) if (t[pos - L + i] != (unsigned char)(SUF[i] - '0')) match = false;
            if (match) {
                std::vector<long long> tok; long long p = pos - L - 1;
                while (p >= lo && t[p] == 1) { long long mm = 0; --p; while (p - 1 >= lo && t[p] == 0 && t[p - 1] == 1) { ++mm; p -= 2; } tok.push_back(mm); }
                long long l1 = lo; while (l1 <= p && !t[l1]) ++l1;
                bool sm = tok.size() < 2 || small_process(tok, RCAP);
                if (!sm) {
                    printf("K %lld |", steps);
                    for (long long x : tok) printf(" %lld", x);
                    printf(" | "); for (long long i = l1; i <= p; ++i) putchar('0' + t[i]); printf("  (far starts at %lld)\n", l1 - off);
                    summary(); return 0;
                }
            }
        }
        const Tr &x = m[sl];
        if (!x.def) { long long k = 0; for (long long i = lo; i <= hi; ++i) k += t[i]; show("HALT"); printf("H %lld %c %d %lld\n", steps, 'A' + q, s, k); summary(); return 0; }
        t[pos] = x.w;
        if (x.w && pos > r1) r1 = pos; else if (!x.w && pos == r1) { while (r1 >= lo && !t[r1]) --r1; }
        pos += x.d; q = x.nx; ++steps;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (pos < 64 || pos >= (long long)t.size() - 64) { printf("W %lld\n", steps); summary(); return 0; }
        if (steps >= MAXS) { printf("T %lld\n", steps); summary(); return 0; }
    }
}
