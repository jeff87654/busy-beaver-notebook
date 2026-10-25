// stage35.cpp: literal stage runner for the mini-follower mf35.py.
// Runs a 10-state machine literally from a given tape until
//   H step STATE SYM ones            an undefined slot is read (the machine halts)
//   J step | t0 t1 ... | FARBITS     a K-moment (state G reading 0, nothing to the right, tape ending in 110101) whose
//                                    champion process would leave small numbers: an exact abstract run of R1/R2/R3
//                                    (token values, accumulator token r <= RCAP) does not reach its next event.
//                                    Tokens D(m) = (10)^m 1 nearest-first (t0 = tail 2, t1 = r, t2 = a-token, ...);
//                                    FARBITS = the cells from the leftmost 1 to the cell left of the farthest token.
//   T step                           step limit;   W step   tape extent limit
// Also prints "E step" for every E0 read (exhaustion-type events) if -e is given.
// K-moments whose champion process stays small are simulated literally (they are cheap).
// Abstract champion process (token form, accumulator offset e = 1):
//   R1: a-token m >= 4 (any residue): m -= 3, r = 2r + 5
//   a-token 2 or 3 (bottom of a non-standard a-token): event
//   R2: a-token 1 and nearest digit d >= 3: d -= 3, a-token = 2r + 5, r = 1
//   R3: a-token 1, zeros (1) then a digit d >= 3: d -= 3, the zero next to it = 2r + 5, r = 1
//   blocker (0 or 2) or the far end reached by the borrow: event
// usage: stage35 FILE maxsteps maxextent rcap
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>

struct Tr { signed char w, d, nx; bool def; };
struct Cfg { std::vector<unsigned char> t; long long pos, lo, hi, r1; int q; long long steps; };
static void grow(Cfg &c) {
    long long n = c.t.size();
    std::vector<unsigned char> nt(3 * n, 0);
    std::copy(c.t.begin(), c.t.end(), nt.begin() + n);
    c.t.swap(nt); c.pos += n; c.lo += n; c.hi += n; c.r1 += n;
}
static bool parsem(const char *s, Tr *m) {
    if (strlen(s) < 69) return false;
    for (int q = 0; q < 10; ++q) for (int c = 0; c < 2; ++c) {
        const char *x = s + 7 * q + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') m[2 * q + c] = {0, 0, 0, false};
        else m[2 * q + c] = {(signed char)(x[0] - '0'), (signed char)(x[1] == 'R' ? 1 : -1), (signed char)(x[2] - 'A'), true};
    }
    return true;
}
// returns true if the abstract process from this K-moment reaches its event with r <= cap (small: simulate literally)
static bool small_process(std::vector<long long> tok, long long cap, bool clean) {
    // tok nearest-first: [2, r, a, d1, d2, ...]
    long long r = tok[1], a = tok[2];
    std::vector<long long> d(tok.begin() + 3, tok.end());
    for (int it = 0; it < 100000; ++it) {
        if (r > cap || a > cap) return false;
        if (a >= 4) { a -= 3; r = 2 * r + 5; continue; }
        if (a != 1) return true;                          // a-block event
        size_t j = 0;
        while (j < d.size() && d[j] == 1) ++j;
        if (j == d.size()) return true;                   // far end (exhaustion or junk)
        if (d[j] == 0 || d[j] == 2) return true;          // blocker
        d[j] -= 3;
        if (j == 0) { a = 2 * r + 5; r = 1; }
        else { d[j - 1] = 2 * r + 5; r = 1; }
    }
    return false;
}
static void run_one(const char *ms, const char *st, long long head, const std::string &bits, long long MAXS,
                    long long MAXW, long long RCAP, bool showE) {
    Tr m[20]; if (!parsem(ms, m)) { printf("X bad machine\n"); return; }
    Cfg c; c.t.assign(std::max<size_t>(1 << 16, 8 * bits.size() + 1024), 0);
    long long off = c.t.size() / 4;
    for (size_t i = 0; i < bits.size(); ++i) c.t[off + i] = bits[i] - '0';
    c.pos = off + head; c.lo = off; c.hi = std::max(off + (long long)bits.size() - 1, c.pos); c.q = st[0] - 'A'; c.steps = 0;
    if (c.pos < c.lo) c.lo = c.pos;
    c.r1 = c.lo - 1; for (long long i = c.lo; i <= c.hi; ++i) if (c.t[i]) c.r1 = i;
    std::vector<long long> tok;
    unsigned used = 0;     // bit 2*state+symbol for every slot read in this stage
    while (true) {
        int s = c.t[c.pos];
        used |= 1u << (2 * c.q + s);
        if (c.q == 6 && s == 0 && c.pos > c.r1 && c.pos - 6 >= c.lo && c.steps > 0) {
            const unsigned char *t = &c.t[c.pos - 6];
            if (t[0] == 1 && t[1] == 1 && t[2] == 0 && t[3] == 1 && t[4] == 0 && t[5] == 1) {
                tok.clear();
                long long p = c.pos - 1;
                while (p >= c.lo && c.t[p] == 1) {
                    long long mm = 0; --p;
                    while (p - 1 >= c.lo && c.t[p] == 0 && c.t[p - 1] == 1) { ++mm; p -= 2; }
                    tok.push_back(mm);
                }
                long long l1 = c.lo; while (l1 <= p && !c.t[l1]) ++l1;
                bool clean = l1 > p;
                if (tok.size() >= 3 && tok[0] == 2 && !small_process(tok, RCAP, clean)) {
                    printf("J %lld |", c.steps);
                    for (long long x : tok) printf(" %lld", x);
                    printf(" | ");
                    for (long long i = l1; i <= p; ++i) putchar('0' + c.t[i]);
                    printf(" | U=%x\n", used);
                    return;
                }
            }
        }
        const Tr &x = m[2 * c.q + s];
        if (!x.def) {
            long long k = 0; for (long long i = c.lo; i <= c.hi; ++i) k += c.t[i];
            printf("H %lld %c %d %lld | U=%x\n", c.steps, 'A' + c.q, s, k, used);
            return;
        }
        if (showE && c.q == 4 && s == 0) printf("E %lld\n", c.steps);
        c.t[c.pos] = x.w;
        if (x.w && c.pos > c.r1) c.r1 = c.pos;
        else if (!x.w && c.pos == c.r1) { while (c.r1 >= c.lo && !c.t[c.r1]) --c.r1; }
        c.pos += x.d; c.q = x.nx; ++c.steps;
        if (c.pos < c.lo) { c.lo = c.pos; if (c.pos <= 1) grow(c); }
        if (c.pos > c.hi) { c.hi = c.pos; if (c.pos >= (long long)c.t.size() - 2) grow(c); }
        if (c.steps >= MAXS) { printf("T %lld | U=%x\n", c.steps, used); return; }
        if (c.hi - c.lo > MAXW) { printf("W %lld | U=%x\n", c.steps, used); return; }
    }
}

// server mode (no FILE argument, "-s"): jobs on stdin, one per two lines:
//   MACHINE STATE HEAD MAXS MAXW RCAP
//   BITS
// one result line per job on stdout (flushed)
int main(int argc, char **argv) {
    if (argc >= 2 && !strcmp(argv[1], "-s")) {
        static char ms[256], st[8];
        long long head, MAXS, MAXW, RCAP;
        std::string bits;
        while (scanf("%255s %7s %lld %lld %lld %lld", ms, st, &head, &MAXS, &MAXW, &RCAP) == 6) {
            bits.clear(); int ch;
            while ((ch = getchar()) != EOF && ch != '\n') {}
            while ((ch = getchar()) != EOF && ch != '\n') if (ch == '0' || ch == '1') bits += (char)ch;
            run_one(ms, st, head, bits, MAXS, MAXW, RCAP, false);
            fflush(stdout);
        }
        return 0;
    }
    if (argc < 5) { fprintf(stderr, "usage: stage35 FILE maxsteps maxextent rcap [-e]  |  stage35 -s\n"); return 2; }
    long long MAXS = atoll(argv[2]), MAXW = atoll(argv[3]), RCAP = atoll(argv[4]);
    bool showE = argc > 5 && !strcmp(argv[5], "-e");
    FILE *f = fopen(argv[1], "r"); if (!f) { fprintf(stderr, "no file\n"); return 2; }
    char ms[256]; char st[8]; long long head;
    if (fscanf(f, "%255s %7s %lld", ms, st, &head) != 3) { fprintf(stderr, "bad file\n"); return 2; }
    std::string bits; int ch;
    while ((ch = fgetc(f)) != EOF) if (ch == '0' || ch == '1') bits += (char)ch;
    fclose(f);
    run_one(ms, st, head, bits, MAXS, MAXW, RCAP, showE);
    return 0;
}
