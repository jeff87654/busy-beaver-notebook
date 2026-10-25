// chain35.cpp: follow the exhaustion -> rebuild -> exhaustion chain of a 10-state extension of the BB(8) record,
// for machines whose rebuilt list is "ideal" (the champion rules clear it completely and end in an exhaustion).
//
// Exhaustion family: X(b, n) = the configuration at the E0 read reached by the record from K(0^n; 0; b).
// Every huge accumulator of the champion process satisfies 2b + 4 = a power of 2 with a huge exponent, so
// b = 6 (mod 840) at every exhaustion of the real run (the BB(8) record's b_f and every later accumulator).
// A visit runs the machine from X(6, n) (n reduced into [NMIN, NMIN+840) when large) until
//   - an undefined slot is read                                  -> HALT (the machine halts at this visit)
//   - a K-moment whose list is ideal: every token D(3d+1) (standard digits) except possibly the farthest one,
//     nothing (blank) beyond it.  The champion rules then clear the whole list and the run reaches the next
//     exhaustion with n' zero digits:
//        farthest token D(3y+1): n' = k (k = number of list digits, a and b excluded)
//        farthest token D(3y+2): it bottoms out at D2, which vanishes when borrowed: n' = k - 1
//        farthest token D(3y)  : it bottoms out at D0 at the far end, whose base-machine event rebuilds
//                                [D0, 0^j | 0 | b] -> [D2, 0^(j+12b+9) | 0 | 0] (b = 6 mod 840):
//                                n' = (k - 1) + 12*6 + 9 = k + 80   (then the D2 is cleared as above)
//     A visit whose ideal list has a zero run growing with b is a full (omega-level) cycle; this is checked by
//     running the same visit at b = 7 as well (the list must get longer).
//   Only K-moments with >= LONG list digits are taken as jump points (shorter lists are simulated literally); an
//   ideal list must also be deep (a nonzero digit at depth >= 3), so that the new accumulator is tower-type.
//   - TIME / WIDE / NONIDEAL (a long K list that is not ideal or not deep: needs the stage follower)
// Output per machine: one line  machine RESULT visits... ; RESULT in HALT@v (v >= 2 is a record-type chain),
// LOOP (n mod 840 repeats), NONIDEAL@v, TIME@v, WIDE@v, MAXV.
// usage: chain35 maxsteps maxextent maxvisits LONG < machines
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <set>
#include <algorithm>

struct Tr { signed char w, d, nx; bool def; };
static const char *BASE = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF_------_------";
static long long MAXS, MAXW; static int LONGT;
static const long long NMIN = 40, MODN = 840;

struct Cfg { std::vector<unsigned char> t; long long pos, lo, hi, r1; int q; long long steps; };

static void grow(Cfg &c) {
    long long n = c.t.size();
    std::vector<unsigned char> nt(3 * n, 0);
    std::copy(c.t.begin(), c.t.end(), nt.begin() + n);
    c.t.swap(nt); c.pos += n; c.lo += n; c.hi += n; c.r1 += n;
}
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

struct Res { int kind; long long steps; int slot; long long k; long long far; std::string list; };
// kind: 0 HALT, 1 IDEAL, 2 NONIDEAL, 3 TIME, 4 WIDE
static Res runvisit(Cfg c, const Tr *m) {
    std::vector<long long> tok; bool clean;
    Res r{3, 0, -1, 0, 0, ""};
    while (true) {
        int s = c.t[c.pos];
        if (c.q == 6 && s == 0 && c.pos > c.r1 && c.pos - 6 >= c.lo) {
            const unsigned char *t = &c.t[c.pos - 6];
            if (t[0] == 1 && t[1] == 1 && t[2] == 0 && t[3] == 1 && t[4] == 0 && t[5] == 1) {
                parse(c, c.pos - 1, tok, clean);
                // tok[0] = tail D2, tok[1] = b-token, tok[2] = a-token, tok[3..] digits nearest-first
                if (tok.size() >= 4 && tok[1] % 3 == 1 && tok[2] % 3 == 1) {
                    long long k = (long long)tok.size() - 3;
                    if (k >= LONGT) {
                        bool ideal = clean;
                        for (size_t i = 3; i + 1 < tok.size() && ideal; ++i) if (tok[i] % 3 != 1) ideal = false;
                        // deep: some nonzero digit (or a non-D1 far token) at depth >= 3
                        bool deep = false;
                        for (size_t i = 6; i < tok.size(); ++i) if (tok[i] != 1) deep = true;
                        r.steps = c.steps; r.k = k; r.far = tok.back(); r.list = fmtitems(tok, clean);
                        r.kind = (ideal && deep) ? 1 : 2;
                        return r;
                    }
                }
            }
        }
        const Tr &x = m[2 * c.q + s];
        if (!x.def) { r.kind = 0; r.steps = c.steps; r.slot = 2 * c.q + s; return r; }
        c.t[c.pos] = x.w;
        if (x.w && c.pos > c.r1) c.r1 = c.pos;
        else if (!x.w && c.pos == c.r1) { while (c.r1 > c.lo && !c.t[c.r1]) --c.r1; }
        c.pos += x.d; c.q = x.nx; ++c.steps;
        if (c.pos < c.lo) { c.lo = c.pos; if (c.pos <= 1) grow(c); }
        if (c.pos > c.hi) { c.hi = c.pos; if (c.pos >= (long long)c.t.size() - 2) grow(c); }
        if (c.steps >= MAXS) { r.kind = 3; r.steps = c.steps; return r; }
        if (c.hi - c.lo > MAXW) { r.kind = 4; r.steps = c.steps; return r; }
    }
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

// X(b, n): run the base record from K(0^n; 0; b) to its E0 read
static Cfg xcfg(long long n, long long b) {
    Tr m[20]; parsem(BASE, m);
    std::string w = "1";
    for (long long i = 0; i < n; ++i) w += "011";
    w += "011";
    for (long long i = 0; i < 3 * b + 1; ++i) w += "01";
    w += "10101";
    Cfg c; c.t.assign(std::max<size_t>(1 << 16, 8 * w.size()), 0);
    long long off = c.t.size() / 4;
    for (size_t i = 0; i < w.size(); ++i) c.t[off + i] = w[i] - '0';
    c.pos = off + w.size(); c.lo = off; c.hi = c.pos; c.r1 = c.pos - 1; c.q = 6; c.steps = 0;
    while (true) {
        int s = c.t[c.pos];
        const Tr &x = m[2 * c.q + s];
        if (!x.def) break;
        c.t[c.pos] = x.w;
        if (x.w && c.pos > c.r1) c.r1 = c.pos;
        else if (!x.w && c.pos == c.r1) { while (c.r1 > c.lo && !c.t[c.r1]) --c.r1; }
        c.pos += x.d; c.q = x.nx; ++c.steps;
        if (c.pos < c.lo) { c.lo = c.pos; if (c.pos <= 1) grow(c); }
        if (c.pos > c.hi) { c.hi = c.pos; if (c.pos >= (long long)c.t.size() - 2) grow(c); }
    }
    if (c.q != 4 || c.t[c.pos] != 0) { fprintf(stderr, "X(%lld,%lld) did not reach E0\n", b, n); exit(1); }
    c.steps = 0;
    return c;
}

static const char *SLOTN[20] = {"A0","A1","B0","B1","C0","C1","D0","D1","E0","E1","F0","F1","G0","G1","H0","H1","I0","I1","J0","J1"};

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: chain35 maxsteps maxextent maxvisits LONG < machines\n"); return 2; }
    MAXS = atoll(argv[1]); MAXW = atoll(argv[2]); int MAXV = atoi(argv[3]); LONGT = atoi(argv[4]);
    char line[8192];
    while (fgets(line, sizeof line, stdin)) {
        char ms[128]; if (sscanf(line, "%127s", ms) != 1) continue;
        Tr m[20]; if (!parsem(ms, m)) continue;
        long long n = 35;
        std::string hist, result;
        std::set<long long> seen;
        for (int v = 1; v <= MAXV; ++v) {
            Res r = runvisit(xcfg(n, 6), m);
            char buf[512];
            if (r.kind == 0) { snprintf(buf, sizeof buf, "[v%d n=%lld HALT %s s=%lld]", v, n, SLOTN[r.slot], r.steps); hist += buf; result = "HALT@" + std::to_string(v); break; }
            if (r.kind >= 2) {
                snprintf(buf, sizeof buf, "[v%d n=%lld %s s=%lld k=%lld %s]", v, n, r.kind == 2 ? "NONIDEAL" : r.kind == 3 ? "TIME" : "WIDE", r.steps, r.k, r.list.c_str());
                hist += buf; result = std::string(r.kind == 2 ? "NONIDEAL@" : r.kind == 3 ? "TIME@" : "WIDE@") + std::to_string(v); break;
            }
            // ideal: growth check at b = 7 (first two visits)
            long long grow_ = -1;
            if (v <= 2) { Res r7 = runvisit(xcfg(n, 7), m); grow_ = (r7.kind == 1) ? r7.k - r.k : -999; }
            long long far = r.far, np;
            if (far % 3 == 1) np = r.k;
            else if (far % 3 == 2) np = r.k - 1;
            else np = r.k + 80;
            snprintf(buf, sizeof buf, "[v%d n=%lld IDEAL k=%lld far=%lld dk/db=%lld s=%lld -> n'=%lld]", v, n, r.k, far, grow_, r.steps, np);
            if (v <= 3 || v == MAXV) hist += buf;
            else if (v == 4) hist += "...";
            if (np < 1) { result = "EMPTY@" + std::to_string(v); break; }
            if (np >= NMIN + MODN) np = NMIN + (np - NMIN) % MODN;
            long long key = np;   // the chain state is n mod 840 (b is always 6 mod 840)
            if (seen.count(key)) { result = "LOOP"; break; }
            seen.insert(key);
            n = np;
            if (v == MAXV) result = "MAXV";
        }
        printf("%s %s %s\n", ms, result.c_str(), hist.c_str());
        fflush(stdout);
    }
    return 0;
}
