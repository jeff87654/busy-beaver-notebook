// enum35.cpp: TNF enumeration of the free slots of the BB(8) record extended to 10 states.
// The record 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF uses every slot except E0 before its first list
// exhaustion, so the free slots are E0 (first reached at the exhaustion) and I0 I1 J0 J1.
// Start: the K configuration K(0^n; 0; b) (the real run's exhaustion family, small b), run literally with the base
// machine to the first E0 read (so the start is exactly what the run reaches), then branch TNF-style:
// E0 in {0LI,0RI,1LI,1RI} (anything else never reaches I and never halts), every later first-reached slot over
// 40 transitions (targets A..J) plus "halt".
// Each leaf prints one line:  OUTCOME machine steps ones extent nE0 nK maxtok | first-long-K / last K items
//   HALT  : the first-reached undefined slot is the halt
//   KLONG : a K-moment (state G, reading 0, no 1 to the right, tail D2 D(3b+1) D(3a+1)) whose D-token list (from the
//           right, until 00 or the left end) has >= LONG tokens: a rebuilt list (the champion phase from there is
//           left to the stage follower)
//   TIME  : step limit;  WIDE : tape extent limit
// usage: enum35 n b maxsteps maxextent LONG [E0,I0,I1,J0,J1]   fixed slot values, "..." = free, e.g. 1LI,...,...,...,...
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>

struct Tr { signed char w, d, nx; bool def; };
static const char *BASE = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF_------_------";
static long long MAXS, MAXW; static int LONGT;
static long long nleaf = 0, nnode = 0;

struct Cfg {
    std::vector<unsigned char> t; long long pos, lo, hi, r1; int q; long long steps;
    int nE0, nK, maxtok; std::string firstlong, lastK;
};

static std::string mstr(const Tr *m) {
    std::string s;
    for (int q = 0; q < 10; ++q) {
        if (q) s += '_';
        for (int c = 0; c < 2; ++c) {
            const Tr &x = m[2 * q + c];
            if (!x.def) s += "---";
            else { s += char('0' + x.w); s += x.d > 0 ? 'R' : 'L'; s += char('A' + x.nx); }
        }
    }
    return s;
}

// D-token parse right-to-left from cell p (inclusive): tokens D(m) = (10)^m 1. Returns tokens nearest-first.
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
static std::string fmtitems(const std::vector<long long> &tok, bool clean, size_t maxn = 40) {
    // farthest first, run-length compressed
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

// run until an undefined slot is read (returns 0), or a stop (1 = KLONG, 2 = TIME, 3 = WIDE)
static int run(Cfg &c, const Tr *m, bool track) {
    std::vector<long long> tok; bool clean;
    while (true) {
        int s = c.t[c.pos];
        if (track && c.q == 6 && s == 0 && c.pos > c.r1) {
            ++c.nK;
            parse(c, c.pos - 1, tok, clean);
            bool kform = tok.size() >= 3 && tok[0] == 2 && tok[1] % 3 == 1 && tok[2] % 3 == 1;
            int ntok = (int)tok.size();
            if (kform && ntok > c.maxtok) c.maxtok = ntok;
            c.lastK = fmtitems(tok, clean);
            if (kform && ntok >= LONGT) { c.firstlong = c.lastK; return 1; }
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

static void leaf(const char *what, const Cfg &c, const Tr *m) {
    ++nleaf;
    printf("%s %s %lld %lld %lld %d %d %d | %s\n", what, mstr(m).c_str(), c.steps, ones(c), c.hi - c.lo, c.nE0, c.nK, c.maxtok,
           (c.firstlong.empty() ? c.lastK : c.firstlong).c_str());
}

static void dfs(Cfg c, Tr *m, const std::vector<std::string> &fixed) {
    ++nnode;
    int r = run(c, m, true);
    if (r == 1) { leaf("KLONG", c, m); return; }
    if (r == 2) { leaf("TIME", c, m); return; }
    if (r == 3) { leaf("WIDE", c, m); return; }
    int slot = 2 * c.q + c.t[c.pos];
    leaf("HALT", c, m);
    int si = c.q == 4 ? 0 : c.q == 8 ? 1 + c.t[c.pos] : c.q == 9 ? 3 + c.t[c.pos] : -1;
    if (si < 0) { fprintf(stderr, "unexpected slot %d\n", slot); return; }
    std::vector<Tr> opts;
    if (si < (int)fixed.size() && fixed[si] != "...") {
        const std::string &f = fixed[si];
        if (f == "---") return;
        opts.push_back({(signed char)(f[0] - '0'), (signed char)(f[1] == 'R' ? 1 : -1), (signed char)(f[2] - 'A'), true});
    } else if (si == 0) {
        for (int w = 0; w < 2; ++w) for (int d = -1; d <= 1; d += 2) opts.push_back({(signed char)w, (signed char)d, 8, true});
    } else {
        // targets A..J (J is the next new state if it is not yet used; I is already used by E0)
        for (int w = 0; w < 2; ++w) for (int d = -1; d <= 1; d += 2) for (int nx = 0; nx < 10; ++nx)
            opts.push_back({(signed char)w, (signed char)d, (signed char)nx, true});
    }
    for (const Tr &o : opts) {
        m[slot] = o;
        dfs(c, m, fixed);
        m[slot] = {0, 0, 0, false};
    }
}

static Cfg startcfg(int n, long long b, const Tr *base) {
    std::string w = "1";
    for (int i = 0; i < n; ++i) w += "011";
    w += "011";
    for (long long i = 0; i < 3 * b + 1; ++i) w += "01";
    w += "10101";
    Cfg c; c.t.assign(1 << 16, 0);
    long long off = 1 << 14;
    for (size_t i = 0; i < w.size(); ++i) c.t[off + i] = w[i] - '0';
    c.pos = off + w.size(); c.lo = off; c.hi = c.pos; c.r1 = c.pos - 1; c.q = 6; c.steps = 0;
    c.nE0 = c.nK = c.maxtok = 0;
    Tr m[20];
    std::copy(base, base + 20, m);
    m[8] = {0, 0, 0, false};
    long long ms = MAXS; MAXS = 1LL << 60;
    int r = run(c, m, false);
    MAXS = ms;
    if (r != 0 || c.q != 4 || c.t[c.pos] != 0) { fprintf(stderr, "start-up did not reach E0\n"); exit(1); }
    c.steps = 0;
    return c;
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

// grade mode: enum35 grade n LONG maxsteps maxextent b1,b2,.. < machines ; one line per machine and b
static int grade(int argc, char **argv) {
    int n = atoi(argv[2]); LONGT = atoi(argv[3]); MAXS = atoll(argv[4]); MAXW = atoll(argv[5]);
    std::vector<long long> bs; { std::string s = argv[6]; size_t p = 0; while (p <= s.size()) { size_t q = s.find(',', p); if (q == std::string::npos) q = s.size(); bs.push_back(atoll(s.substr(p, q - p).c_str())); p = q + 1; } }
    Tr base[20]; parsem(BASE, base);
    std::vector<Cfg> starts; for (long long b : bs) starts.push_back(startcfg(n, b, base));
    char line[4096];
    while (fgets(line, sizeof line, stdin)) {
        char ms[128]; if (sscanf(line, "%127s", ms) != 1) continue;
        Tr m[20]; if (!parsem(ms, m)) continue;
        for (size_t i = 0; i < bs.size(); ++i) {
            Cfg c = starts[i];
            int r = run(c, m, true);
            const char *what = r == 0 ? "HALT" : r == 1 ? "KLONG" : r == 2 ? "TIME" : "WIDE";
            printf("%s b=%lld %s %lld %lld %lld %d %d %d | %s\n", ms, bs[i], what, c.steps, ones(c), c.hi - c.lo, c.nE0, c.nK, c.maxtok,
                   (c.firstlong.empty() ? c.lastK : c.firstlong).c_str());
        }
        fflush(stdout);
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc > 1 && !strcmp(argv[1], "grade")) return grade(argc, argv);
    if (argc < 6) { fprintf(stderr, "usage: enum35 n b maxsteps maxextent LONG [E0,I0,I1,J0,J1 fixed]\n"); return 2; }
    int n = atoi(argv[1]); long long b = atoll(argv[2]); MAXS = atoll(argv[3]); MAXW = atoll(argv[4]); LONGT = atoi(argv[5]);
    std::vector<std::string> fixed;
    if (argc > 6) {
        std::string s = argv[6]; size_t p = 0;
        while (p <= s.size()) { size_t q = s.find(',', p); if (q == std::string::npos) q = s.size(); fixed.push_back(s.substr(p, q - p)); p = q + 1; }
    }
    Tr m[20];
    for (int q = 0; q < 10; ++q) for (int c = 0; c < 2; ++c) {
        const char *x = BASE + 7 * q + 3 * c;
        if (x[0] == '-') m[2 * q + c] = {0, 0, 0, false};
        else m[2 * q + c] = {(signed char)(x[0] - '0'), (signed char)(x[1] == 'R' ? 1 : -1), (signed char)(x[2] - 'A'), true};
    }
    // K(0^n; 0; b) = 1 [(01)^1 1]^n (01)^(3*0+1) 1 (01)^(3b+1) 1 (01)^2 G>
    std::string w = "1";
    for (int i = 0; i < n; ++i) w += "011";
    w += "011";
    for (long long i = 0; i < 3 * b + 1; ++i) w += "01";
    w += "10101";
    Cfg c; c.t.assign(1 << 16, 0);
    long long off = 1 << 14;
    for (size_t i = 0; i < w.size(); ++i) c.t[off + i] = w[i] - '0';
    c.pos = off + w.size(); c.lo = off; c.hi = c.pos; c.r1 = c.pos - 1; c.q = 6; c.steps = 0;
    c.nE0 = c.nK = c.maxtok = 0;
    // run the base machine (E0 undefined) to the exhaustion's E0 read
    long long ms = MAXS; MAXS = 1LL << 60;
    int r = run(c, m, false);
    MAXS = ms;
    if (r != 0 || c.q != 4 || c.t[c.pos] != 0) { fprintf(stderr, "start-up did not reach E0\n"); return 1; }
    fprintf(stderr, "E0 reached after %lld steps, extent %lld\n", c.steps, c.hi - c.lo);
    c.steps = 0;
    dfs(c, m, fixed);
    fprintf(stderr, "nodes %lld leaves %lld\n", nnode, nleaf);
}
