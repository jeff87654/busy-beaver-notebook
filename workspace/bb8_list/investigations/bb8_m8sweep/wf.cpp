// wf.cpp (bb8_m8sweep): world follower for M8-recipe children of 7-state digit-list rebuilders.
// Derived from bb8_resid/tools/zfg7.cpp (generic zeroing follower).  Literal simulation; at a K-moment of the base's
// template the engine's Ackermann clearing of the near token list is replaced by its outcome (a JUMP):
//   every decoded token (a and the digits) becomes a zero digit, the accumulator becomes R (representative).
// Template  O,Q,P=..,u=..,s=..,d=ALd+BE,b=ALBb+BEB,S=..   (O = L: the machine is mirrored, as in dlscan/rk7)
// Tails     --tail S1/W/S2[,S1/W/S2...] : extra suffix forms S1 W^t S2 (t >= 0) besides S (t preserved by a jump).
// K-moment  state Q, head on a blank, all cells right of the head blank; left of the head: suffix, acc u-run, tokens.
// Policy    phase EXACT (before the first jump): jump only when the segment is >= --slit steps (default 2e7).
//           phase WORLD: jump at once when a token/acc >= --big or the list length >= --kbig, else after --ssmall steps.
//           R = RC + RK*k (k = cleared list length), first jump --R0 if given; rounded up into C mod M (--cls C M).
// Rounds    --x SLOT (e.g. E0, in the ORIGINAL orientation): every read of that slot is counted (rounds).
// Escalation: a jump whose k >= max(--escf * (previous max k), --kmin) .
// Modes     single machine:  wf MACHINE TEMPLATE [opts]          (verbose with --v)
//           batch:           wf --batch FILE TEMPLATE [opts]     (one machine per line; one summary line each)
//           snapshot:        --snapx : stop at the first read of --x and print "SNAP" with the world state;
//                            --from SNAPFILE : start from that world state (the child must equal the base before it).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>
#include <cmath>
#include <windows.h>
typedef long long ll;
struct Tr { int w, d, nx; bool def; };
static int NS;
static std::string Pp, U, S_; static int Q; static ll AL, BE, ALB, BEB;
struct Tail { std::string S1, W, S2; };
static std::vector<Tail> TAILS;
static ll R0 = -1, RC = 20, CLSC = 0, CLSM = 0, JMAX = 100000, MAXS = 300000000, MAXT = 2000000000, SLIT = 20000000, SSMALL = 2000000, BIG = 12, KBIG = 40, KMIN = 8, XMAX = 1000000;
static double RK = 1.0, ESCF = 2.0;
static int XSLOT = -1; static bool MIRROR = false, VERB = false, SNAPX = false;
static ll RCAP = -1; static bool SLOTS = false; static unsigned FREE = 0; static ll NLEAF = 0, MAXLEAF = 100000; static ll TAPEMAX = 1LL << 28; static ll ESCMAX = 0, RCAPW = 0; static bool LOOPDET = false; static ll MAXEXACT = 200000000; static bool ESCOLD = false; static double ESCTH = 0.5;

static std::string fmt(const std::vector<Tr> &t) {
    std::string s;
    for (int q = 0; q < NS; ++q) { if (q) s += '_';
        for (int c = 0; c < 2; ++c) { const Tr &x = t[2 * q + c];
            if (!x.def) s += "---"; else { s += char('0' + x.w); s += (x.d > 0) != MIRROR ? 'R' : 'L'; s += char('A' + x.nx); } } }
    return s;
}
struct Comp { std::vector<std::string> lit; std::vector<std::string> w; std::vector<ll> n; };
struct Snap { Comp c; int q; ll step, nx, k, nj; };
struct World {
    std::vector<Snap> HIST;
    std::string rcur; std::vector<std::string> rsigs, rsigb; ll kesc = 1; std::vector<std::pair<std::string, ll>> rle;
    std::vector<Tr> t;
    std::vector<unsigned char> tape; ll off = 0, h = 0, lo = 0, hi = 0, r1 = 0; int q = 0;
    ll wstep0 = -1, maxR = 0;
    ll step0 = 0, step = 0, vstep = 0, seg = 0, nj = 0, nx = 0, maxk = 0, nesc = 0, lastR = 0;
    std::vector<ll> zeros; std::vector<ll> xat; std::vector<int> escat;
    bool world = false;
    unsigned long long kpair = 0, engpair = 0, exhpair = 0, lexhpair = 0; unsigned lexhmask = 0; int lastsl = -1; bool Elate = false;
    unsigned kmask = 0, engmask = 0, exhmask = 0; bool inE = false, seenK = false; ll nE = 0; std::string kord, exh1;
    ll firstE_step = -1, firstE_n = -1, firstE_b = -1;
};
static void grow(World &W) {
    ll add = std::max<ll>(W.tape.size(), 1 << 16);
    std::vector<unsigned char> nt(W.tape.size() + 2 * add, 0);
    memcpy(&nt[add], W.tape.data(), W.tape.size()); W.tape.swap(nt);
    W.off += add; W.h += add; W.lo += add; W.hi += add; W.r1 += add;
}
static inline bool at(const World &W, ll p, const std::string &s) {   // s occupies cells p-|s|+1 .. p
    ll L = s.size(); if (p - L + 1 < 0) return false;
    const unsigned char *T = W.tape.data() + p - L + 1;
    for (ll i = 0; i < L; ++i) if (T[i] != (unsigned char)(s[i] - '0')) return false;
    return true;
}

// ---------------------------------------------------------------- jump-level acceleration (counter modes)
// tape [a..b] (head at b+1, at a K-moment right after a jump) -> literals + long periodic runs (period <= 8, >= 24 cells)
static bool DOACC = true; static ll NTHR = 20, ACCMAXCELLS = 30000000, NACC = 0;
static Comp compress(const World &W, ll a, ll b) {
    Comp C; std::string cur; ll i = a;
    const unsigned char *T = W.tape.data();
    while (i <= b) {
        int bp = 0; ll bl = 0;
        for (int p = 1; p <= 8; ++p) { ll j = i + p; while (j <= b && T[j] == T[j - p]) ++j; ll L = j - i; if (L >= 24 && L >= 3 * p && L > bl + 0) { if (L > bl) { bl = L; bp = p; } } }
        if (bp) {
            // primitive period: smallest p' dividing structure (bp is the smallest p reaching max length because p increases and we need strict >)
            ll n = bl / bp; std::string w; for (int k = 0; k < bp; ++k) w += char('0' + T[i + k]);
            C.lit.push_back(cur); cur.clear(); C.w.push_back(w); C.n.push_back(n); i += n * bp;
        } else { cur += char('0' + T[i]); ++i; }
    }
    C.lit.push_back(cur);
    return C;
}
static bool samestruct(const Comp &x, const Comp &y) { return x.lit == y.lit && x.w == y.w; }
static void accel(World &W, ll k) {
    if (!DOACC) return;
    ll a = W.lo; while (a < W.h && !W.tape[a]) ++a;
    ll b = W.h - 1;
    Snap s; s.c = compress(W, a, b); s.q = W.q; s.step = W.step; s.nx = W.nx; s.k = k; s.nj = W.nj;
    W.HIST.push_back(s); if (W.HIST.size() > 4) W.HIST.erase(W.HIST.begin());
    if (W.HIST.size() < 4) return;
    for (int i = 1; i < 4; ++i) if (!samestruct(W.HIST[i].c, W.HIST[0].c) || W.HIST[i].k != W.HIST[0].k || W.HIST[i].q != W.HIST[0].q) return;
    size_t m = W.HIST[0].c.n.size(); if (!m) return;
    std::vector<ll> d(m);
    bool anyd = false;
    for (size_t j = 0; j < m; ++j) { d[j] = W.HIST[1].c.n[j] - W.HIST[0].c.n[j];
        for (int i = 2; i < 4; ++i) if (W.HIST[i].c.n[j] - W.HIST[i - 1].c.n[j] != d[j]) return;
        if (d[j]) anyd = true; }
    ll dx = W.HIST[1].nx - W.HIST[0].nx; for (int i = 2; i < 4; ++i) if (W.HIST[i].nx - W.HIST[i - 1].nx != dx) return;
    if (!anyd) return;
    ll N = -1, grow1 = 0;
    for (size_t j = 0; j < m; ++j) { if (d[j] < 0) { ll t = (W.HIST[3].c.n[j] - NTHR) / (-d[j]); if (N < 0 || t < N) N = t; } else grow1 += d[j] * (ll)W.HIST[3].c.w[j].size(); }
    if (grow1 > 0) { ll t = ACCMAXCELLS / grow1; if (N < 0 || t < N) N = t; }
    if (dx > 0) { ll t = (XMAX - W.nx) / dx; if (t < N) N = t; }
    if (N < 2) return;
    // apply N iterations
    Comp c = W.HIST[3].c; for (size_t j = 0; j < m; ++j) c.n[j] += N * d[j];
    std::string nw; for (size_t j = 0; j < m; ++j) { nw += c.lit[j]; for (ll r = 0; r < c.n[j]; ++r) nw += c.w[j]; } nw += c.lit[m];
    for (ll i = a; i <= std::max(W.h, W.r1); ++i) W.tape[i] = 0;
    while (a + (ll)nw.size() + 4 >= (ll)W.tape.size()) { ll s0 = W.off; grow(W); a += W.off - s0; }
    for (size_t i = 0; i < nw.size(); ++i) W.tape[a + i] = nw[i] - '0';
    W.h = a + nw.size(); W.hi = std::max(W.hi, W.h); W.r1 = W.h - 1; while (W.r1 >= W.lo && !W.tape[W.r1]) --W.r1;
    ll dstep = W.HIST[3].step - W.HIST[2].step;
    W.vstep += N * dstep; W.nx += N * dx; W.nj += N; for (ll i = 0; i < std::min<ll>(N, 1000); ++i) W.zeros.push_back(k);
    ++NACC;
    if (VERB) { printf("  DOACC N=%lld runs=%zu dx=%lld dstep=%lld -> J%lld X=%lld\n", N, m, dx, dstep, W.nj, W.nx); fflush(stdout); }
    W.HIST.clear();
}
// returns 0 = not a K-moment, 1 = K-moment, no jump, 2 = jumped, 3 = RCAP
static int kmoment(World &W) {
    ll p = W.h - 1;
    // suffix: S, or S1 W^t S2
    std::string sfx; bool ok = false;
    for (auto &T : TAILS) {
        if (!at(W, p, T.S2)) continue;
        ll pp = p - T.S2.size(); ll tt = 0;
        if (!T.W.empty()) while (at(W, pp, T.W)) { pp -= T.W.size(); ++tt; }
        if (!at(W, pp, T.S1)) continue;
        pp -= T.S1.size();
        sfx = T.S1; for (ll i = 0; i < tt; ++i) sfx += T.W; sfx += T.S2;
        p = pp; ok = true; break;
    }
    if (!ok) return 0;
    ll lu = U.size(), ls = S_.size(), acc = 0;
    while (p - lu + 1 >= W.lo && at(W, p, U)) { ++acc; p -= lu; }
    if (acc < BEB || (acc - BEB) % ALB) return 0;
    acc = (acc - BEB) / ALB;
    std::vector<ll> tok; ll start = p + 1;
    while (true) {
        if (!(p - ls + 1 >= W.lo && at(W, p, S_))) break;
        ll pp = p - ls, m = 0;
        while (pp - lu + 1 >= W.lo && at(W, pp, U)) { ++m; pp -= lu; }
        if (m < BE || (m - BE) % AL) break;
        tok.push_back((m - BE) / AL); p = pp; start = pp + 1;
    }
    if (tok.empty()) return 0;
    bool nz0 = false; for (ll x : tok) if (x) nz0 = true;
    if (W.seenK) { if (W.inE) { W.exhmask |= W.kmask; W.exhpair |= W.kpair; if (W.Elate) { W.lexhmask |= W.kmask; W.lexhpair |= W.kpair; } if (W.nE == 1) W.exh1 = W.kord; } else { W.engmask |= W.kmask; W.engpair |= W.kpair; } }
    W.kpair = 0; W.Elate = W.nj > 0;
    if (!nz0) { if (!W.inE || W.kmask) { ++W.nE; if (W.firstE_step < 0) { W.firstE_step = W.step; W.firstE_n = tok.size() - 1; W.firstE_b = acc; } } }
    W.inE = !nz0; W.seenK = true; W.kmask = 0; W.kord.clear();
    bool nz = false; ll mx = acc; for (ll x : tok) { if (x) nz = true; mx = std::max(mx, x); }
    if (!nz) return 1;
    ll k = tok.size() - 1;   // digits (tok[0] = a)
    // policy
    if (!W.world) { if (W.seg < SLIT) return 1; }
    else { bool big = mx >= BIG || k >= KBIG; if (!big && W.seg < SSMALL) return 1; }
    ll R = (W.nj == 0 && R0 >= 0) ? R0 : RC + (ll)(RK * (double)k);
    if (RCAPW > 0 && R > RCAPW) R = RCAPW;
    if (CLSM > 0) { ll r = ((R - CLSC) % CLSM + CLSM) % CLSM; if (r) R += CLSM - r; }
    if (RCAP >= 0 && R > RCAP) return 3;
    std::string nw;
    for (ll i = 0; i < k + 1; ++i) { for (ll j = 0; j < BE; ++j) nw += U; nw += S_; }
    for (ll j = 0; j < ALB * R + BEB; ++j) nw += U;
    nw += sfx;
    for (ll i = start; i <= std::max(W.h, W.r1); ++i) W.tape[i] = 0;
    while (start + (ll)nw.size() + 4 >= (ll)W.tape.size()) { ll s0 = W.off; grow(W); start += W.off - s0; }
    for (size_t i = 0; i < nw.size(); ++i) W.tape[start + i] = nw[i] - '0';
    W.h = start + nw.size();
    W.hi = std::max(W.hi, W.h); W.r1 = W.h - 1; while (W.r1 >= W.lo && !W.tape[W.r1]) --W.r1;
    W.q = Q;
    ++W.nj; W.zeros.push_back(k); W.lastR = R;
    ll Rprev = W.maxR; W.maxR = std::max(W.maxR, R);
    bool isesc = ESCOLD ? (k >= std::max<ll>((ll)(ESCF * W.maxk), KMIN)) : (k > W.maxk && k >= KMIN && (double)k >= ESCTH * (double)Rprev);
    if (isesc) { ++W.nesc; W.escat.push_back((int)W.nj); if (ESCMAX > 0 && W.nesc >= ESCMAX) { W.maxk = std::max(W.maxk, k); return 4; }
        { std::string se, sb; for (auto &e : W.rle) { se += e.first + std::to_string(e.second) + ","; sb += e.first + std::to_string((int)floor(log2((double)e.second))) + ","; }
          W.rsigs.push_back(se); W.rsigb.push_back(sb); W.rle.clear(); W.rcur = se; }
        W.kesc = k;
        size_t ns = W.rsigs.size();
        if (LOOPDET && ((ns >= 2 && W.rsigs[ns - 1] == W.rsigs[ns - 2]) || (ns >= 3 && W.rsigb[ns - 1] == W.rsigb[ns - 2] && W.rsigb[ns - 2] == W.rsigb[ns - 3]))) { W.maxk = std::max(W.maxk, k); return 5; } }
    else if (W.rle.size() < 5000) { int b = (int)floor(2.0 * log2(((double)k + 1.0) / ((double)W.kesc + 1.0))); std::string t = "j" + std::to_string(b);
        if (!W.rle.empty() && W.rle.back().first == t) ++W.rle.back().second; else W.rle.push_back({t, 1}); }
    W.maxk = std::max(W.maxk, k);
    if (VERB) { printf("  J%lld step=%lld seg=%lld k=%lld R=%lld a=%lld max=%lld X=%lld esc=%lld sfx=%zu\n", W.nj, W.step, W.seg, k, R, tok[0], mx, W.nx, W.nesc, sfx.size()); fflush(stdout); }
    if (!W.world) W.wstep0 = W.step;
    W.world = true; W.seg = 0;
    accel(W, k);
    return 2;
}
static std::string zs(const World &W, size_t lastn = 40) {
    std::string s; size_t i = W.zeros.size() > lastn ? W.zeros.size() - lastn : 0;
    if (i) s += "..";
    while (i < W.zeros.size()) { size_t j = i; while (j < W.zeros.size() && W.zeros[j] == W.zeros[i]) ++j;
        if (!s.empty() && s != "..") s += ' '; s += std::to_string(W.zeros[i]); if (j - i > 1) s += "^" + std::to_string(j - i); i = j; }
    return s;
}
static std::string summary(const World &W) {
    char b[256]; snprintf(b, sizeof b, "J=%lld X=%lld esc=%lld maxk=%lld step=%lld vstep=%.3g", W.nj, W.nx, W.nesc, W.maxk, W.step, (double)(W.step + W.vstep));
    std::string s = b; s += " zeros=[" + zs(W) + "]";
    std::string e; for (int x : W.escat) e += std::to_string(x) + ","; s += " escJ=[" + e + "]";
    if (SLOTS) { auto ms = [](unsigned m) { std::string r; for (int i = 0; i < 2 * NS; ++i) if (m >> i & 1) { r += char('A' + i / 2); r += char('0' + i % 2); } return r.empty() ? std::string("-") : r; };
        char bb[200]; snprintf(bb, sizeof bb, " nE=%lld firstE=%lld/n%lld/b%lld", W.nE, W.firstE_step, W.firstE_n, W.firstE_b); s += bb;
        s += " eng=" + ms(W.engmask) + " exh=" + ms(W.exhmask) + " exh1=" + (W.exh1.empty() ? std::string("-") : W.exh1) + " exhonly=" + ms(W.exhmask & ~W.engmask) + " lexh=" + ms(W.lexhmask) + " lexhonly=" + ms(W.lexhmask & ~W.engmask);
        auto mp = [](unsigned long long m) { std::string r; for (int i = 0; i < 4 * NS; ++i) if (m >> i & 1) { int sl = i / 2; r += char('A' + sl / 2); r += char('0' + sl % 2); r += char('0' + i % 2); r += ','; } return r.empty() ? std::string("-") : r; };
        s += " guard=" + mp(W.exhpair & ~W.engpair) + " lguard=" + mp(W.lexhpair & ~W.engpair) + " engpairs=" + mp(W.engpair); }
    return s;
}
static void dumpsnap(const World &W) {
    ll a = W.lo; while (a < W.h && !W.tape[a]) ++a;
    ll b = std::max(W.r1, W.h);
    std::string w; for (ll i = a; i <= b; ++i) w += char('0' + W.tape[i]);
    printf("SNAP %s %lld %c %lld %lld %lld %lld %lld %d\n", w.c_str(), W.h - a, 'A' + W.q, W.step, W.nj, W.maxk, W.nesc, W.lastR, (int)W.world);
    std::string z; for (ll x : W.zeros) z += std::to_string(x) + ","; printf("SNAPZ %s\n", z.c_str());
    fflush(stdout);
}
// result string
static std::string run(World &W) {
    while (true) {
        if (W.h <= 1 || W.h >= (ll)W.tape.size() - 2) grow(W);
        if ((ll)W.tape.size() > TAPEMAX) return "WIDE " + summary(W);
        int c = W.tape[W.h];
        if (W.q == Q && c == 0 && W.h <= W.r1 && W.step > 0 && !W.tape[W.r1]) {   // r1 is only an upper bound: check cells right of the head
            ll p = W.h + 1; const unsigned char *T = W.tape.data(); while (p <= W.r1 && !T[p]) ++p;
            if (p > W.r1) { W.r1 = W.h - 1; while (W.r1 >= W.lo && !T[W.r1]) --W.r1; }
        }
        if (W.q == Q && c == 0 && W.h > W.r1 && W.step > 0) {
            int r = kmoment(W);
            if ((ll)W.tape.size() > TAPEMAX) return "WIDE " + summary(W);
            if (r == 3) return "RCAP " + summary(W);
            if (r == 4) return "ESCMAX " + summary(W);
            if (r == 5) { std::string sg = W.rsigs.back(); if (sg.size() > 60) sg = sg.substr(0, 60) + ".."; return "LOOP " + summary(W) + " rsig=" + (sg.empty() ? std::string("-") : sg); }
            if (r == 2) { if (W.nj >= JMAX) return "JMAX " + summary(W); continue; }
        }
        int sl = 2 * W.q + c;
        if (sl == XSLOT) {
            if (SNAPX && W.nx == 0) { dumpsnap(W); return "SNAPPED"; }
            ++W.nx; W.xat.push_back(W.nj); if (W.rle.size() < 5000) { if (!W.rle.empty() && W.rle.back().first == "x") ++W.rle.back().second; else W.rle.push_back({"x", 1}); }
            if (VERB) { printf("  X%lld at J%lld step=%lld\n", W.nx, W.nj, W.step); fflush(stdout); }
            if (W.nx >= XMAX) return "XMAX " + summary(W);
        }
        if (W.lastsl >= 0) W.kpair |= 1ULL << (2 * W.lastsl + c);
        W.lastsl = sl;
        if (!(W.kmask >> sl & 1)) { W.kmask |= 1u << sl; W.kord += char('A' + sl / 2); W.kord += char('0' + sl % 2); }
        Tr &x = W.t[sl];
        if (!x.def && (FREE >> sl & 1)) return "BRANCH";
        if (!x.def) {
            if (W.inE) { W.exhmask |= W.kmask; W.exhpair |= W.kpair; if (W.Elate) { W.lexhmask |= W.kmask; W.lexhpair |= W.kpair; } }
            ll ones = 0; for (ll i = W.lo; i <= W.hi; ++i) ones += W.tape[i];
            char b[128]; snprintf(b, sizeof b, "HALT %c%d ones=%lld seg=%lld ", 'A' + W.q, c, ones, W.seg);
            return std::string(b) + summary(W);
        }
        W.tape[W.h] = x.w;
        if (x.w && W.h > W.r1) W.r1 = W.h; else if (!x.w && W.h == W.r1) { ll lim = W.h - 64; while (W.r1 >= W.lo && W.r1 > lim && !W.tape[W.r1]) --W.r1; }   // r1 = upper bound of the rightmost 1
        W.h += x.d; W.q = x.nx; ++W.step; ++W.seg;
        if (W.h < W.lo) W.lo = W.h; if (W.h > W.hi) W.hi = W.h;
        if ((W.world && W.seg >= MAXS) || (W.world ? W.step - std::max(W.step0, W.wstep0) >= MAXT : W.step - W.step0 >= MAXEXACT)) {
            if (W.inE) { W.exhmask |= W.kmask; W.exhpair |= W.kpair; if (W.Elate) { W.lexhmask |= W.kmask; W.lexhpair |= W.kpair; } }
            ll a = W.lo; while (a < W.hi && !W.tape[a]) ++a;
            char b[128]; snprintf(b, sizeof b, "T state=%c width=%lld seg=%lld ", 'A' + W.q, W.r1 - a + 1, W.seg);
            return std::string(b) + summary(W);
        }
    }
}
static void compact(World &W) {   // re-centre the tape on [lo, hi] with margins (cheap world copies at branch points)
    ll a = std::min(W.lo, W.h), b = std::max(W.hi, W.h);
    ll w = b - a + 1, M = std::max<ll>(1 << 15, w);
    std::vector<unsigned char> nt(w + 2 * M, 0);
    memcpy(&nt[M], &W.tape[a], w);
    ll sh = M - a;
    W.tape.swap(nt); W.off += sh; W.h += sh; W.lo += sh; W.hi += sh; W.r1 += sh;
}
static void runrec(World &W) {
    std::string r = run(W);
    if (r == "BRANCH") {
        compact(W);
        int c = W.tape[W.h], sl = 2 * W.q + c;
        { ll ones = 0; for (ll i = W.lo; i <= W.hi; ++i) ones += W.tape[i];
          printf("%s HALT %c%d ones=%lld seg=%lld %s\n", fmt(W.t).c_str(), 'A' + W.q, c, ones, W.seg, summary(W).c_str()); fflush(stdout); ++NLEAF; }
        for (int w = 0; w < 2; ++w) for (int d = -1; d <= 1; d += 2) for (int nx = 0; nx < NS; ++nx) {
            if (NLEAF >= MAXLEAF) { printf("# MAXLEAF\n"); return; }
            World V = W; V.t[sl] = {w, d, nx, true};
            runrec(V);
        }
        return;
    }
    printf("%s %s\n", fmt(W.t).c_str(), r.c_str()); fflush(stdout); ++NLEAF;
}
static bool parse_machine(const std::string &m, std::vector<Tr> &t) {
    std::vector<std::string> rows; { std::stringstream ss(m); std::string r; while (std::getline(ss, r, '_')) rows.push_back(r); }
    NS = rows.size(); t.assign(2 * NS, {0, 0, 0, false});
    for (int s = 0; s < NS; ++s) { if (rows[s].size() != 6) return false;
        for (int c = 0; c < 2; ++c) { std::string x = rows[s].substr(3 * c, 3);
            if (x[2] != '-' && x[2] != 'Z' && x[2] != 'H' + 100) { if (x[2] - 'A' >= NS) { t[2 * s + c] = {0, 0, 0, false}; continue; }
                int d = x[1] == 'R' ? 1 : -1; if (MIRROR) d = -d; t[2 * s + c] = {x[0] - '0', d, x[2] - 'A', true}; } } }
    return true;
}
static std::string FROM;
static void init(World &W) {
    W.tape.assign(1 << 20, 0); W.off = 1 << 19;
    std::string w; ll head = 0; int q0 = 0;
    if (!FROM.empty()) {
        FILE *f = fopen(FROM.c_str(), "r"); if (!f) { fprintf(stderr, "no snap file\n"); exit(2); }
        static char buf[1 << 26]; std::string line;
        while (fgets(buf, sizeof buf, f)) { if (!strncmp(buf, "SNAP ", 5)) { line = buf; break; } }
        std::string zl; while (fgets(buf, sizeof buf, f)) { if (!strncmp(buf, "SNAPZ ", 6)) { zl = buf + 6; break; } }
        fclose(f);
        std::stringstream ss(line.substr(5)); std::string qs; ll st, nj, mk, ne, lr; int wo;
        ss >> w >> head >> qs >> st >> nj >> mk >> ne >> lr >> wo; q0 = qs[0] - 'A';
        W.step = st; W.nj = nj; W.maxk = mk; W.nesc = ne; W.lastR = lr; W.maxR = lr; W.world = wo;
        std::stringstream zz(zl); std::string y; while (std::getline(zz, y, ',')) if (!y.empty() && y[0] != '\n') W.zeros.push_back(atoll(y.c_str()));
    }
    while ((ll)w.size() + 8 >= (ll)W.tape.size() / 2) W.tape.resize(W.tape.size() * 2);
    for (size_t i = 0; i < w.size(); ++i) W.tape[W.off + i] = w[i] - '0';
    W.h = W.off + head; W.q = q0; W.lo = std::min(W.off, W.h); W.hi = std::max<ll>(W.off + (ll)w.size() - 1, W.h);
    W.r1 = W.lo - 1; for (ll i = W.lo; i <= W.hi; ++i) if (W.tape[i]) W.r1 = i;
    if (!FROM.empty() && W.step == 0) W.step = 1;
    W.step0 = W.step; if (W.world) W.wstep0 = W.step;
}
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    if (argc < 3) { fprintf(stderr, "usage: see header\n"); return 2; }
    std::string m = argv[1], tp = argv[2], batch, xs;
    int i0 = 3;
    if (m == "--batch") { batch = argv[2]; tp = argv[3]; i0 = 4; }
    for (int i = i0; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--R0") R0 = atoll(argv[++i]); else if (a == "--rc") RC = atoll(argv[++i]); else if (a == "--rk") RK = atof(argv[++i]);
        else if (a == "--cls") { CLSC = atoll(argv[++i]); CLSM = atoll(argv[++i]); }
        else if (a == "--jumps") JMAX = atoll(argv[++i]); else if (a == "--maxs") MAXS = (ll)atof(argv[++i]); else if (a == "--maxt") MAXT = (ll)atof(argv[++i]);
        else if (a == "--slit") SLIT = (ll)atof(argv[++i]); else if (a == "--ssmall") SSMALL = (ll)atof(argv[++i]);
        else if (a == "--big") BIG = atoll(argv[++i]); else if (a == "--kbig") KBIG = atoll(argv[++i]); else if (a == "--kmin") KMIN = atoll(argv[++i]);
        else if (a == "--escf") ESCF = atof(argv[++i]); else if (a == "--rcap") RCAP = atoll(argv[++i]); else if (a == "--xmax") XMAX = atoll(argv[++i]);
        else if (a == "--x") xs = argv[++i]; else if (a == "--v") VERB = true; else if (a == "--snapx") SNAPX = true; else if (a == "--from") FROM = argv[++i]; else if (a == "--slots") SLOTS = true; else if (a == "--free") { std::stringstream q(argv[++i]); std::string y; while (std::getline(q, y, ',')) FREE |= 1u << (2 * (y[0] - 'A') + (y[1] - '0')); } else if (a == "--maxleaf") MAXLEAF = atoll(argv[++i]); else if (a == "--escmax") ESCMAX = atoll(argv[++i]); else if (a == "--rcapw") RCAPW = atoll(argv[++i]); else if (a == "--loop") LOOPDET = true; else if (a == "--maxexact") MAXEXACT = (ll)atof(argv[++i]); else if (a == "--escold") ESCOLD = true; else if (a == "--tapemax") TAPEMAX = (ll)atof(argv[++i]); else if (a == "--escth") ESCTH = atof(argv[++i]); else if (a == "--noaccel") DOACC = false; else if (a == "--nthr") NTHR = atoll(argv[++i]);
        else if (a == "--tail") { std::stringstream q(argv[++i]); std::string y; while (std::getline(q, y, ',')) { Tail T; size_t p1 = y.find('/'), p2 = y.rfind('/');
                T.S1 = y.substr(0, p1); T.W = y.substr(p1 + 1, p2 - p1 - 1); T.S2 = y.substr(p2 + 1); if (T.S1 == "-") T.S1 = ""; if (T.S2 == "-") T.S2 = ""; if (T.W == "-") T.W = ""; TAILS.push_back(T); } }
        else { fprintf(stderr, "bad option %s\n", a.c_str()); return 2; }
    }
    { std::vector<std::string> f; std::stringstream ss(tp); std::string x; while (std::getline(ss, x, ',')) f.push_back(x);
      if (f.size() < 8) { fprintf(stderr, "template not understood: %s\n", tp.c_str()); return 2; }
      MIRROR = f[0] == "L";
      Q = f[1][0] - 'A'; Pp = f[2].substr(2); U = f[3].substr(2); S_ = f[4].substr(2);
      if (sscanf(f[5].c_str(), "d=%lldd+%lld", &AL, &BE) != 2 || sscanf(f[6].c_str(), "b=%lldb+%lld", &ALB, &BEB) != 2) { fprintf(stderr, "bad d/b\n"); return 2; }
      std::string SUF = f[7].substr(2); if (SUF == "-") SUF = ""; if (Pp == "-") Pp = "";
      // template S is the separator-terminated suffix: K = .. u^acc S
      // NOTE: in dlscan templates the field after b is the suffix S; the separator s is S_ above. Swap names:
      std::string sep = S_; S_ = sep; // separator
      // store suffix in a tail with empty W so the parser tries it first
      TAILS.insert(TAILS.begin(), Tail{SUF, "", ""});
    }
    if (!xs.empty()) XSLOT = 2 * (xs[0] - 'A') + (xs[1] - '0');
    auto doone = [&](const std::string &mm) {
        World W; if (!parse_machine(mm, W.t)) { printf("BADMACHINE %s\n", mm.c_str()); return; }
        init(W);
        if (FREE) { runrec(W); return; }
        std::string r = run(W);
        printf("%s %s\n", mm.c_str(), r.c_str()); fflush(stdout);
    };
    if (batch.empty()) doone(m);
    else { FILE *f = fopen(batch.c_str(), "r"); char buf[4096];
        while (fgets(buf, sizeof buf, f)) { std::string s = buf; while (!s.empty() && (s.back() == '\n' || s.back() == '\r' || s.back() == ' ')) s.pop_back(); if (s.empty() || s[0] == '#') continue; doone(s); }
        fclose(f); }
}
