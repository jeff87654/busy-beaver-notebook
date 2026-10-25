// grade35.cpp: grade 10-state extensions of the BB(8) record from its exhaustion family at several accumulator values.
// For each machine (stdin, one per line, first field) and each b in the list, start from K(0^n; 0; b), run the base
// record (E0 undefined) to the E0 read, then run the machine itself for MAXS steps and report:
//   machine b= OUT steps ones extent nE0 nK maxrun maxtok | list at the first K-moment where maxrun was reached || last K list
// OUT: HALT (an undefined slot was read; 'slot' given), TIME, WIDE (tape extent limit).
// K-moment: state G reading 0, no 1 to the right, tape ending in 110101 (tail D2 = (10)^2 1 right after a token).
// maxrun: longest run of D1 tokens (zero digits) in any K-moment's token list (tokens D(m) = (10)^m 1, parsed from the
// right until 00 or the left end).
// usage: grade35 n maxsteps maxextent b1,b2,... < machines
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>

struct Tr { signed char w, d, nx; bool def; };
static const char *BASE = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF_------_------";
static long long MAXS, MAXW;

struct Cfg {
    std::vector<unsigned char> t; long long pos, lo, hi, r1; int q; long long steps;
    int nE0, nK, maxtok, maxrun; std::string atmax, lastK;
};

static void parse(const Cfg &c, long long p, std::vector<long long> &tok, bool &clean) {
    tok.clear();
    long long lo = c.lo;
    while (p >= lo) {
        if (c.t[p] != 1) break;
        long long m = 0; --p;
        while (p - 1 >= lo && c.t[p] == 0 && c.t[p - 1] == 1) { ++m; p -= 2; }
        tok.push_back(m);
    }
    clean = true;
    for (long long i = lo; i <= p; ++i) if (c.t[i]) { clean = false; break; }
}
static std::string fmtitems(const std::vector<long long> &tok, bool clean, size_t maxn = 60) {
    std::string s = clean ? "| " : "<junk> ";
    std::vector<long long> v(tok.rbegin(), tok.rend());
    size_t shown = 0;
    for (size_t k = 0; k < v.size();) {
        size_t l = k; while (l < v.size() && v[l] == v[k]) ++l;
        s += std::to_string(v[k]); if (l - k > 1) s += "*" + std::to_string(l - k); s += ' ';
        k = l; if (++shown > maxn) { s += "..."; break; }
    }
    return s;
}
static void grow(Cfg &c) {
    long long n = c.t.size();
    std::vector<unsigned char> nt(3 * n, 0);
    std::copy(c.t.begin(), c.t.end(), nt.begin() + n);
    c.t.swap(nt); c.pos += n; c.lo += n; c.hi += n; c.r1 += n;
}

// returns 0 = undefined slot read, 2 = TIME, 3 = WIDE
static int run(Cfg &c, const Tr *m, bool track) {
    std::vector<long long> tok; bool clean;
    while (true) {
        int s = c.t[c.pos];
        if (track && c.q == 6 && s == 0 && c.pos > c.r1 && c.pos - 6 >= c.lo) {
            const unsigned char *t = &c.t[c.pos - 6];
            if (t[0] == 1 && t[1] == 1 && t[2] == 0 && t[3] == 1 && t[4] == 0 && t[5] == 1) {
                ++c.nK;
                parse(c, c.pos - 1, tok, clean);
                int run = 0, best = 0;
                for (long long x : tok) { if (x == 1) { if (++run > best) best = run; } else run = 0; }
                int ntok = (int)tok.size();
                if (ntok > c.maxtok) c.maxtok = ntok;
                if (best > c.maxrun) { c.maxrun = best; c.atmax = fmtitems(tok, clean); }
                c.lastK = fmtitems(tok, clean);
            }
        }
        const Tr &x = m[2 * c.q + s];
        if (!x.def) return 0;
        if (track && c.q == 4 && s == 0) ++c.nE0;
        c.t[c.pos] = x.w;
        if (x.w && c.pos > c.r1) c.r1 = c.pos;
        else if (!x.w && c.pos == c.r1) { while (c.r1 > c.lo && !c.t[c.r1]) --c.r1; }
        c.pos += x.d; c.q = x.nx; ++c.steps;
        if (c.pos < c.lo) { c.lo = c.pos; if (c.pos <= 1) grow(c); }
        if (c.pos > c.hi) { c.hi = c.pos; if (c.pos >= (long long)c.t.size() - 2) grow(c); }
        if (c.steps >= MAXS) return 2;
        if (c.hi - c.lo > MAXW) return 3;
    }
}
static long long ones(const Cfg &c) { long long k = 0; for (long long i = c.lo; i <= c.hi; ++i) k += c.t[i]; return k; }

static bool parsem(const char *s, Tr *m) {
    if (strlen(s) < 69) return false;
    for (int q = 0; q < 10; ++q) for (int c = 0; c < 2; ++c) {
        const char *x = s + 7 * q + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') m[2 * q + c] = {0, 0, 0, false};
        else m[2 * q + c] = {(signed char)(x[0] - '0'), (signed char)(x[1] == 'R' ? 1 : -1), (signed char)(x[2] - 'A'), true};
    }
    return true;
}

static Cfg startcfg(int n, long long b) {
    Tr m[20]; parsem(BASE, m);
    std::string w = "1";
    for (int i = 0; i < n; ++i) w += "011";
    w += "011";
    for (long long i = 0; i < 3 * b + 1; ++i) w += "01";
    w += "10101";
    Cfg c; c.t.assign(1 << 16, 0);
    long long off = 1 << 14;
    for (size_t i = 0; i < w.size(); ++i) c.t[off + i] = w[i] - '0';
    c.pos = off + w.size(); c.lo = off; c.hi = c.pos; c.r1 = c.pos - 1; c.q = 6; c.steps = 0;
    c.nE0 = c.nK = c.maxtok = c.maxrun = 0;
    long long ms = MAXS; MAXS = 1LL << 60;
    int r = run(c, m, false);
    MAXS = ms;
    if (r != 0 || c.q != 4 || c.t[c.pos] != 0) { fprintf(stderr, "start-up did not reach E0\n"); exit(1); }
    c.steps = 0;
    return c;
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: grade35 n maxsteps maxextent b1,b2,... < machines\n"); return 2; }
    int n = atoi(argv[1]); MAXS = atoll(argv[2]); MAXW = atoll(argv[3]);
    std::vector<long long> bs;
    { std::string s = argv[4]; size_t p = 0; while (p <= s.size()) { size_t q = s.find(',', p); if (q == std::string::npos) q = s.size(); bs.push_back(atoll(s.substr(p, q - p).c_str())); p = q + 1; } }
    std::vector<Cfg> starts; for (long long b : bs) starts.push_back(startcfg(n, b));
    char line[8192];
    while (fgets(line, sizeof line, stdin)) {
        char ms[128]; if (sscanf(line, "%127s", ms) != 1) continue;
        Tr m[20]; if (!parsem(ms, m)) continue;
        for (size_t i = 0; i < bs.size(); ++i) {
            Cfg c = starts[i];
            int r = run(c, m, true);
            std::string what = r == 2 ? "TIME" : r == 3 ? "WIDE" : std::string("HALT:") + char('A' + c.q) + char('0' + c.t[c.pos]);
            printf("%s b=%lld %s %lld %lld %lld %d %d %d %d | %s|| %s\n", ms, bs[i], what.c_str(), c.steps, ones(c), c.hi - c.lo,
                   c.nE0, c.nK, c.maxrun, c.maxtok, c.atmax.c_str(), c.lastK.c_str());
        }
        fflush(stdout);
    }
    return 0;
}
