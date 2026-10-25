// m9s.cpp: 9-state search on Argon's M9 counter engine, with an exact Ch-cascade accelerator.
//
// Engine (M9 labels, verified in BB9_M9_halt.v / BB11_M11_halt.v): 13 core slots
//   A0=1RB A1=1RA B1=1RC C0=0LD C1=1LG D0=0RE D1=1LD E1=1RF F1=0RA G0=1RA G1=0LH H0=1LG H1=1LH
// Rule (Coq CH_CA, uses only core slots):  Ch j b z  -->  Ca j (W j b) z
//   Ch j b z = 0^inf (10)^j [H reading the last 0 of (10)^j] 1^(b+1) 0 z      (j >= 1 here)
//   Ca j b z = 0^inf (10)^j 1^b [A reading 0] z
//   W 0 b = b+3,  W (j+1) b = iter (b+1) (W j) 2;   W j b = b+1 (mod 2);  W (j>=2) b mod 18 = (b even ? 11 : 2)
// When W j b > CAP the value is replaced by a representative R >= RBASE with the same residue mod 18
// (screening only: the run after such a jump is "approximate").
//
// Modes:
//   m9s enum START BUDGET [RBASE CAP]      tree over the free slots B0 E0 F0 I0 I1 from blank, start state START
//                                          (A..I or * for all); every reached undefined slot is branched over the 36
//                                          moves and halt (the last free slot is only branched to halt).
//   m9s mut K START BUDGET [RBASE CAP]     all machines at Hamming distance 1..K from M9 (37 values per slot), start START
//   m9s run BUDGET RBASE CAP [log]         read "machine start" lines from stdin, run each, print leaf (+ jump log)
// Leaf line: LEAF machine start outcome steps sigma tape_span jumps maxj approx firstbig
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
typedef long long ll;
static const int NS = 9, NSL = 18;
struct Tr { signed char w, d, nx; bool def; };   // nx = -1: halt
struct Mach { Tr t[NSL]; };
static const char *M9 = "1RB1RA_0LI1RC_0LD1LG_0RE1LD_1RF1RF_0RB0RA_1RA0LH_1LG1LH_---0LD";
static const int CORE[13] = {0, 1, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15};
static const int FREE[5] = {2, 8, 10, 16, 17};  // B0 E0 F0 I0 I1
static Mach parse(const char *s) {
    Mach m; int k = 0;
    for (int q = 0; q < NS; ++q) {
        for (int c = 0; c < 2; ++c) {
            const char *x = s + 7 * q + 3 * c;
            Tr &t = m.t[2 * q + c];
            if (x[0] == '-' || x[2] == 'Z' || x[2] == '-') { t.w = 1; t.d = 1; t.nx = -1; t.def = (x[0] != '-'); }
            else { t.w = x[0] - '0'; t.d = x[1] == 'R' ? 1 : -1; t.nx = x[2] - 'A'; t.def = true; if (t.nx >= NS) t.nx = -1; }
            ++k;
        }
    }
    return m;
}
static std::string fmt(const Mach &m) {
    std::string s;
    for (int q = 0; q < NS; ++q) {
        if (q) s += '_';
        for (int c = 0; c < 2; ++c) {
            const Tr &t = m.t[2 * q + c];
            if (!t.def) s += "---";
            else if (t.nx < 0) s += "1RZ";
            else { s += char('0' + t.w); s += t.d > 0 ? 'R' : 'L'; s += char('A' + t.nx); }
        }
    }
    return s;
}
static Mach BASE;
static bool core_ok(const Mach &m) {
    for (int i = 0; i < 13; ++i) {
        const Tr &a = m.t[CORE[i]], &b = BASE.t[CORE[i]];
        if (!a.def || a.w != b.w || a.d != b.d || a.nx != b.nx) return false;
    }
    return true;
}
// W with cap: returns -1 if > cap
static ll Wc(int j, ll b, ll cap) {
    if (j == 0) return b + 3 <= cap ? b + 3 : -1;
    if (j == 1) return (b <= (cap - 5) / 3) ? 3 * b + 5 : -1;
    if (j == 2) {  // (3^(b+3) - 5) / 2
        ll p = 1; for (ll i = 0; i < b + 3; ++i) { if (p > (2 * cap + 5) / 3) return -1; p *= 3; }
        ll v = (p - 5) / 2; return v <= cap ? v : -1;
    }
    if (j == 3) return (b == 0 && 119 <= cap) ? 119 : -1;  // W 3 1 = W 2 119 > 10^56
    return -1;                                            // W j b >= W 4 0 = W 2 (W 2 119) for j >= 4
}
static ll RBASE = 40, CAP = 100000;
static ll rep(int j, ll b) {
    ll r = (j >= 2) ? ((b % 2 == 0) ? 11 : 2) : -1;
    if (r < 0) { // j<2 never needs a representative in practice; keep parity
        r = (b + 1) % 2;
        ll R = std::max(RBASE, b + 3); while (R % 2 != r) ++R; return R;
    }
    ll R = std::max(RBASE, b + 3); while (R % 36 != r) ++R; return R;  // mod 36: W mod 4 = (b even ? 3 : 2) too
}
enum { O_HALT = 0, O_UNDEF, O_BUDGET, O_TAPE };
static const char *ONAME[] = {"HALT", "UNDEF", "BUDGET", "TAPE"};
struct Res { int out; ll steps; ll sigma; ll span; int jumps; int maxj; bool approx; int undef_slot; int firstbig; int nrep; int repj[4]; int tj[8]; ll tb[8]; char trep[8]; ll tw[8]; };
static const int TL = 1 << 21;
static std::vector<unsigned char> tape(TL);
static bool LOG = false;
static ll MAXJLOG = 200;
static std::string INIT; static int INITH = 0; static bool NOACC = false;
static int CLO = 0, CHI = TL - 1;  // region dirtied by the previous run
static Res sim(const Mach &m, int start, ll budget) {
    std::fill(tape.begin() + CLO, tape.begin() + CHI + 1, 0);
    int pos = TL / 2, lo = pos, hi = pos, q = start;
    ll lo1 = (ll)1 << 40;  // lower bound of the leftmost 1 (tightened lazily in the accelerator)
    ll ones = 0;
    if (!INIT.empty()) {
        int base = pos - INITH;
        for (size_t i = 0; i < INIT.size(); ++i) if (INIT[i] == '1') { tape[base + i] = 1; ++ones; if (base + (ll)i < lo1) lo1 = base + i; }
        lo = std::min(lo, base); hi = std::max(hi, base + (int)INIT.size() - 1);
    }
    bool acc = core_ok(m) && !NOACC;
    Res r{}; r.undef_slot = -1; r.firstbig = -1;
    ll s = 0;
    while (true) {
        if (s >= budget) { r.out = O_BUDGET; break; }
        if (pos <= 2 || pos >= TL - 3) { r.out = O_TAPE; break; }
        unsigned char c = tape[pos];
        if (acc && q == 7 && c == 0 && tape[pos - 1] == 1) {
            int j = 1;
            while (tape[pos - 2 * j] == 0 && tape[pos - 2 * j - 1] == 1) ++j;
            bool clean = false;
            if (tape[pos + 1] == 1) {  // lo1 is a lower bound of the leftmost 1; tighten lazily
                int L = pos - 2 * j + 1;
                if (lo1 < L) { ll k = std::max<ll>(lo1, lo); while (k < L && !tape[k]) ++k; lo1 = k; }
                clean = (lo1 == L);
            }
            if (clean) {
                ll cnt = 0; int k = pos + 1;
                while (tape[k] == 1) { ++cnt; ++k; }
                ll b = cnt - 1;
                ll W = Wc(j, b, CAP);
                bool big = W < 0;
                if (big) { W = rep(j, b); r.approx = true; if (r.firstbig < 0) r.firstbig = r.jumps;
                    r.repj[0] = r.repj[1]; r.repj[1] = r.repj[2]; r.repj[2] = r.repj[3]; r.repj[3] = j; r.nrep++; }
                ll delta = W - b - 1;
                if ((ll)hi + delta + 4 >= TL) { r.out = O_TAPE; break; }
                // move z = [pos+b+3, hi] right by delta
                int zs = pos + (int)b + 3;
                if (hi >= zs) memmove(&tape[zs + delta], &tape[zs], hi - zs + 1);
                for (int i = 0; i < delta && zs + i <= hi; ++i) tape[zs + i] = 0;  // cleared below anyway
                for (ll i = 1; i <= W; ++i) tape[pos + i] = 1;
                tape[pos + W + 1] = 0;
                if (hi >= zs) hi += (int)delta; else hi = std::max(hi, (int)(pos + W + 1));
                ones += W - (b + 1);
                if (LOG && r.jumps < MAXJLOG)
                    printf("  JUMP %d step %lld: Ch j=%d b=%lld -> W=%lld%s ones=%lld\n", r.jumps, s, j, b, W, big ? " (REP)" : "", ones);
                { int z = r.jumps & 7; r.tj[z] = j; r.tb[z] = b; r.trep[z] = big; r.tw[z] = W; }
                r.jumps++; if (j > r.maxj) r.maxj = j;
                pos = pos + (int)W + 1; q = 0; ++s;
                if (hi < pos) hi = pos;
                continue;
            }
        }
        const Tr &t = m.t[2 * q + c];
        if (!t.def) { r.out = O_UNDEF; r.undef_slot = 2 * q + c; ones += (c == 0); ++s; break; }  // sigma/steps as if halting here
        if (t.nx < 0) { r.out = O_HALT; ones += (c == 0); ++s; break; }
        if (t.w != c) {
            ones += t.w ? 1 : -1;
            tape[pos] = t.w;
            if (t.w) { if (pos < lo1) lo1 = pos; }

        }
        pos += t.d; q = t.nx; ++s;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
    }
    r.steps = s; r.sigma = ones; r.span = hi - lo + 1;
    CLO = std::max(0, lo - 2); CHI = std::min(TL - 1, hi + 2);
    return r;
}
static ll nleaf = 0, nhalt = 0, nhold = 0, nnodes = 0;
static void leaf(const Mach &m, int start, const Res &r) {
    ++nleaf;
    if (r.out == O_HALT) ++nhalt; else ++nhold;
    printf("LEAF %s %c %s %lld %lld %lld %d %d %d %d %d %d,%d,%d,%d\n", fmt(m).c_str(), 'A' + start, ONAME[r.out], r.steps,
           r.sigma, r.span, r.jumps, r.maxj, r.approx ? 1 : 0, r.firstbig, r.nrep, r.repj[0], r.repj[1], r.repj[2], r.repj[3]);
}
static ll BUDGET = 100000;
static bool HALT_ONLY_PRINT = false;
static void explore(Mach &m, int start, int nfree_left, bool has_halt) {
    ++nnodes;
    Res r = sim(m, start, BUDGET);
    if (r.out != O_UNDEF) { leaf(m, start, r); return; }
    int sl = r.undef_slot;
    // halt option
    {
        m.t[sl] = Tr{1, 1, -1, true};
        Res h = r; h.out = O_HALT;
        leaf(m, start, h);
        m.t[sl].def = false;
    }
    if (nfree_left <= 1 && !has_halt) return;  // last free slot must be the halt
    for (int w = 0; w < 2; ++w)
        for (int d = -1; d <= 1; d += 2)
            for (int nx = 0; nx < NS; ++nx) {
                m.t[sl] = Tr{(signed char)w, (signed char)d, (signed char)nx, true};
                explore(m, start, nfree_left - 1, has_halt);
                m.t[sl].def = false;
            }
}
int main(int argc, char **argv) {
    BASE = parse(M9);
    if (argc < 2) { fprintf(stderr, "usage: see header\n"); return 1; }
    std::string mode = argv[1];
    if (mode == "enum") {
        const char *st = argv[2]; BUDGET = atoll(argv[3]);
        if (argc > 4) RBASE = atoll(argv[4]);
        if (argc > 5) CAP = atoll(argv[5]);
        for (int s = 0; s < NS; ++s) {
            if (st[0] != '*' && st[0] - 'A' != s) continue;
            Mach m = BASE;
            for (int i = 0; i < 5; ++i) m.t[FREE[i]].def = false;
            explore(m, s, 5, false);
            fprintf(stderr, "start %c done: nodes=%lld leaves=%lld halt=%lld hold=%lld\n", 'A' + s, nnodes, nleaf, nhalt, nhold);
        }
    } else if (mode == "enumroot") {  // stdin: "partial_machine start"; argv: BUDGET RBASE CAP
        BUDGET = atoll(argv[2]); RBASE = atoll(argv[3]); CAP = atoll(argv[4]);
        char buf[512], stc[8];
        while (scanf("%511s %7s", buf, stc) == 2) {
            Mach m = parse(buf); int nf = 0; bool hh = false;
            for (int i = 0; i < NSL; ++i) { if (!m.t[i].def) ++nf; else if (m.t[i].nx < 0) hh = true; }
            explore(m, stc[0] - 'A', nf, hh);
        }
        fprintf(stderr, "enumroot done: nodes=%lld leaves=%lld halt=%lld hold=%lld\n", nnodes, nleaf, nhalt, nhold);
    } else if (mode == "mut") {
        int K = atoi(argv[2]); const char *st = argv[3]; BUDGET = atoll(argv[4]);
        if (argc > 5) RBASE = atoll(argv[5]);
        if (argc > 6) CAP = atoll(argv[6]);
        int PART = argc > 8 ? atoi(argv[7]) : 0, NPART = argc > 8 ? atoi(argv[8]) : 1; long long combo = 0;
        // value list: 36 moves + halt
        std::vector<Tr> vals;
        for (int w = 0; w < 2; ++w) for (int d = -1; d <= 1; d += 2) for (int nx = 0; nx < NS; ++nx) vals.push_back(Tr{(signed char)w, (signed char)d, (signed char)nx, true});
        vals.push_back(Tr{1, 1, -1, false});  // undefined = halt
        for (int s = 0; s < NS; ++s) {
            if (st[0] != '*' && st[0] - 'A' != s) continue;
            std::vector<int> sl(K);
            // enumerate slot subsets of size k <= K, and values different from base
            for (int k = 1; k <= K; ++k) {
                std::vector<int> idx(k); for (int i = 0; i < k; ++i) idx[i] = i;
                while (true) {
                    std::vector<int> vi(k, 0);
                    while (true) {
                        Mach m = BASE; bool same = (combo++ % NPART) != PART;
                        for (int i = 0; i < k; ++i) {
                            Tr v = vals[vi[i]]; const Tr &b = BASE.t[idx[i]];
                            bool eq = (v.def == b.def) && (!v.def || (v.w == b.w && v.d == b.d && v.nx == b.nx));
                            if (eq) { same = true; break; }
                            m.t[idx[i]] = v;
                        }
                        if (!same) {
                            bool hashalt = false;
                            for (int i = 0; i < NSL; ++i) if (!m.t[i].def || m.t[i].nx < 0) hashalt = true;
                            if (hashalt) {
                                Res r = sim(m, s, BUDGET);
                                if (r.out == O_UNDEF) r.out = O_HALT;  // undefined = halt
                                leaf(m, s, r);
                            }
                        }
                        int p = k - 1;
                        while (p >= 0 && ++vi[p] == (int)vals.size()) { vi[p] = 0; --p; }
                        if (p < 0) break;
                    }
                    int p = k - 1;
                    while (p >= 0 && idx[p] == NSL - k + p) --p;
                    if (p < 0) break;
                    ++idx[p]; for (int i = p + 1; i < k; ++i) idx[i] = idx[i - 1] + 1;
                }
            }
            fprintf(stderr, "start %c done: leaves=%lld halt=%lld hold=%lld\n", 'A' + s, nleaf, nhalt, nhold);
        }
    } else if (mode == "runt") {  // lines: machine start tape headidx ; argv: BUDGET RBASE CAP [log] [noacc]
        BUDGET = atoll(argv[2]); RBASE = atoll(argv[3]); CAP = atoll(argv[4]);
        for (int i = 5; i < argc; ++i) { if (!strcmp(argv[i], "log")) LOG = true; if (!strcmp(argv[i], "noacc")) NOACC = true; }
        char buf[512], stc[8]; static char tb[1 << 16]; int h;
        while (scanf("%511s %7s %65535s %d", buf, stc, tb, &h) == 4) {
            Mach m = parse(buf); INIT = tb; INITH = h;
            if (LOG) printf("MACHINE %s %s\n", buf, stc);
            Res r = sim(m, stc[0] - 'A', BUDGET);
            if (r.out == O_UNDEF) r.out = O_HALT;
            leaf(m, stc[0] - 'A', r);
        }
    } else if (mode == "grade") {  // stdin "machine start"; argv BUDGET RBASE CAP ; prints leaf + last 8 jumps
        BUDGET = atoll(argv[2]); RBASE = atoll(argv[3]); CAP = atoll(argv[4]);
        char buf[512], stc[8];
        while (scanf("%511s %7s", buf, stc) == 2) {
            Mach m = parse(buf);
            Res r = sim(m, stc[0] - 'A', BUDGET);
            if (r.out == O_UNDEF) r.out = O_HALT;
            printf("G %s %c %s %lld %lld %d %d %d |", buf, stc[0], ONAME[r.out], r.steps, r.sigma, r.jumps, r.nrep, r.maxj);
            int n = std::min(r.jumps, 8);
            for (int i = r.jumps - n; i < r.jumps; ++i) { int z = i & 7; printf(" %d:%lld%s", r.tj[z], r.tb[z], r.trep[z] ? "*" : ""); }
            printf("\n");
        }
    } else if (mode == "run") {
        BUDGET = atoll(argv[2]); RBASE = atoll(argv[3]); CAP = atoll(argv[4]);
        LOG = argc > 5;
        char buf[512], stc[8];
        while (scanf("%511s %7s", buf, stc) == 2) {
            Mach m = parse(buf);
            if (LOG) printf("MACHINE %s %s\n", buf, stc);
            Res r = sim(m, stc[0] - 'A', BUDGET);
            if (r.out == O_UNDEF) r.out = O_HALT;
            leaf(m, stc[0] - 'A', r);
        }
    }
    fflush(stdout);
    return 0;
}
