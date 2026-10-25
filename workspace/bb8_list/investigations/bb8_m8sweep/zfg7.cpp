// zfg7 (bb8_resid): + --rmodc M C (every R rounded up to C mod M).
// zfg6.cpp (bb9_c04_sib copy of bb9_n1f0_complete/zfg.cpp): + order-faithful R policy --rk F --rc C [--rpow P]
//   (R = C + F*k^P at every jump after the first; k = cleared depth), --rcap X (stop with RCAP), R printed per jump, Idle priority.
// zfg.cpp: generic "zeroing follower" (C++ port/generalisation of bb9_c7m12_loopers/zf.py) driven by a dlscan3
// template, with an optional TNF completion search of the undefined slots (renum-style, but across jumps).
//
//   zfg MACHINE TEMPLATE [options]
//     TEMPLATE  dlscan3 template string, e.g. "R,A,P=1,u=01,s=1,d=3d+1,b=3b+0,S=10101010" (only O = R supported):
//               K(ds; a; b) = P u^(al d1+be) s ... u^(al a+be) s u^(alB b+beB) S, head on the blank right of S, state Q.
//     --R0 N      accumulator representative used at the FIRST jump (default = --R)
//     --R N       accumulator representative at every later jump (default 20)
//     --jumps N   stop after N jumps (default 40)
//     --maxs N    literal step budget per segment between jumps (default 3e8)
//     --start W:H:Q   start word, head index, state (default blank tape, state A)
//     --complete  TNF completion: at every undefined read branch over all values (targets < min(used+1, NS));
//                 every node is also a leaf (slot left undefined = halt there).  --maxund N limits branchings.
//     --quiet     one summary line per leaf only
//     --far N     characters of far-region view printed per jump (default 160)
// Literal simulation; at every K-moment (state Q, reading 0, all cells right of the head blank) the tape left of the
// head is parsed right-to-left as S, acc u-run, then tokens "u^m s" while m = be (mod al), m >= be: a, d1, ..., dk.
// If a > 0 or some digit > 0 the engine's Ackermann process is replaced by its outcome (a JUMP): every decoded digit
// and a become zero digits, the accumulator becomes R.  The undecoded rest (the far region) is untouched.
// Per jump it prints k (= the length of the list the jump clears = "zeros"), the slots read in the segment before it,
// and a D-token view of the far region (nearest part).  Screening only: R is a single representative.
// Leaf summary: LEAF machine outcome jumps zeros-seq [halt slot@jump]
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
static std::string Pp, U, S_, SUF; static std::vector<std::string> SUFS; static int Q; static ll AL, BE, ALB, BEB;
static ll DUMPJ = -1, SNAP = 0, KDBG = 0, R0 = -1, RR = 20, JMAX = 40, MAXS = 300000000, MAXUND = 6, FARV = 160, MAXT = 2000000000;
static double RKF = -1, RPOW = 1; static ll RKC = 0, RCAP = -1, RMODM = 0, RMODC = 0;
static bool COMPLETE = false, QUIET = false, ALLJ = false, LOOSE = false;
static ll leaves = 0;

static std::string fmt(const std::vector<Tr> &t) {
    std::string s;
    for (int q = 0; q < NS; ++q) { if (q) s += '_';
        for (int c = 0; c < 2; ++c) { const Tr &x = t[2 * q + c];
            if (!x.def) s += "---"; else { s += char('0' + x.w); s += x.d > 0 ? 'R' : 'L'; s += char('A' + x.nx); } } }
    return s;
}
static std::string dtoks(const std::string &w) {
    std::vector<std::string> tok; std::string raw; size_t i = 0, n = w.size();
    while (i < n && w[i] == '0') ++i;
    while (i < n) {
        size_t j = i; ll m = 0;
        while (j + 1 < n && w[j] == '1' && w[j + 1] == '0') { j += 2; ++m; }
        if (j < n && w[j] == '1') { if (!raw.empty()) { tok.push_back("<" + raw + ">"); raw.clear(); } tok.push_back(std::to_string(m)); i = j + 1; }
        else { raw += w[i]; ++i; }
    }
    if (!raw.empty()) tok.push_back("<" + raw + ">");
    std::string out; size_t k = 0;
    while (k < tok.size()) { size_t l = k; while (l < tok.size() && tok[l] == tok[k]) ++l;
        if (!out.empty()) out += ' '; out += tok[k]; if (l - k > 1) out += "*" + std::to_string(l - k); k = l; }
    return out;
}

struct World {
    std::vector<Tr> t;
    std::vector<unsigned char> tape; ll off = 0, h = 0, lo = 0, hi = 0, r1 = 0; int q = 0;
    ll step = 0, seg = 0, nj = 0, step0 = 0; unsigned segused = 0, used = 0;
    std::vector<ll> zeros; std::string log;
    int nund = 0; unsigned lastused = 0;
};

static void grow(World &W) {
    ll add = std::max<ll>(W.tape.size(), 1 << 16);
    std::vector<unsigned char> nt(W.tape.size() + 2 * add, 0);
    memcpy(&nt[add], W.tape.data(), W.tape.size()); W.tape.swap(nt);
    W.off += add; W.h += add; W.lo += add; W.hi += add; W.r1 += add;
}
static bool at(const World &W, ll p, const std::string &s) {   // s occupies cells p-|s|+1 .. p
    ll L = s.size(); if (p - L + 1 < 0) return false;
    for (ll i = 0; i < L; ++i) if (W.tape[p - L + 1 + i] != (unsigned char)(s[i] - '0')) return false;
    return true;
}
// returns 0 = not a K-moment, 1 = K-moment without jump, 2 = jumped
static int kmoment(World &W) {
    ll p = W.h - 1;
    std::string MS; for (auto &x : SUFS) if (at(W, p, x)) { MS = x; break; }
    if (MS.empty()) { if (KDBG > 0 && W.nj > 0 && W.h > W.r1) { --KDBG; std::string s; for (ll i = std::max(W.lo, W.h - 40); i < W.h; ++i) s += char(48 + W.tape[i]); printf("  KDBG step=%lld left40=%s\n", W.step, s.c_str()); } return 0; }
    p -= MS.size();
    ll lu = U.size(), ls = S_.size(), acc = 0;
    while (p - lu + 1 >= W.lo && at(W, p, U)) { ++acc; p -= lu; }
    if (acc < BEB || (acc - BEB) % ALB) { if (KDBG > 0 && W.nj > 0) { --KDBG; printf("  KDBG2 step=%lld suffix=%s acc=%lld (bad residue)\n", W.step, MS.c_str(), acc); } return 0; }
    std::vector<ll> tok; ll start = p + 1;
    while (true) {
        if (!(p - ls + 1 >= W.lo && at(W, p, S_))) break;
        ll pp = p - ls, m = 0;
        while (pp - lu + 1 >= W.lo && at(W, pp, U)) { ++m; pp -= lu; }
        if (m < BE || (m - BE) % AL) break;
        tok.push_back((m - BE) / AL); p = pp; start = pp + 1;
    }
    if (tok.empty()) return 0;
    bool nz = false; ll mx = 0, nnz = 0;
    for (ll x : tok) { if (x) { nz = true; ++nnz; } mx = std::max(mx, x); }
    if (!nz) return 1;
    ll k = tok.size() - 1;   // digits (tok[0] = a)
    ll R = (W.nj == 0 && R0 >= 0) ? R0 : (RKF >= 0 ? RKC + (ll)(RKF * pow((double)k, RPOW)) : RR);
    if (RMODM > 0) { ll r = ((R - RMODC) % RMODM + RMODM) % RMODM; if (r) R += RMODM - r; }   // round R up into RMODC mod RMODM
    if (RCAP >= 0 && R > RCAP) { printf("RCAP k=%lld R=%lld J%lld step=%lld\n", k, R, W.nj + 1, W.step); fflush(stdout); return 3; }
    std::string nw;
    for (ll i = 0; i < k + 1; ++i) { for (ll j = 0; j < BE; ++j) nw += U; nw += S_; }
    for (ll j = 0; j < ALB * R + BEB; ++j) nw += U;
    nw += MS;
    ll oldlen = W.h - start;
    // far region view (nearest part)
    ll fl = W.lo; while (fl < start && !W.tape[fl]) ++fl;
    std::string farw; for (ll i = std::max(fl, start - 4 * FARV); i < start; ++i) farw += char('0' + W.tape[i]);
    std::string fv = dtoks(farw); if ((ll)fv.size() > FARV) fv = "..." + fv.substr(fv.size() - FARV);
    // rewrite
    std::string right;   // --loose: cells right of the head are kept and shifted
    if (W.r1 >= W.h) for (ll i = W.h; i <= W.r1; ++i) right += char('0' + W.tape[i]);
    for (ll i = start; i <= std::max(W.h, W.r1); ++i) W.tape[i] = 0;
    while (start + (ll)(nw.size() + right.size()) + 4 >= (ll)W.tape.size()) { ll s0 = W.off; grow(W); start += W.off - s0; }
    for (size_t i = 0; i < nw.size(); ++i) W.tape[start + i] = nw[i] - '0';
    W.h = start + nw.size();
    for (size_t i = 0; i < right.size(); ++i) W.tape[W.h + i] = right[i] - '0';
    W.hi = std::max(W.hi, W.h + (ll)right.size()); W.r1 = W.hi; while (W.r1 >= W.lo && !W.tape[W.r1]) --W.r1;
    W.q = Q;
    ++W.nj; W.zeros.push_back(k);
    char buf[512];
    std::string us; for (int i = 0; i < 2 * NS; ++i) if (W.segused >> i & 1) { us += char('A' + i / 2); us += char('0' + i % 2); us += ','; }
    snprintf(buf, sizeof buf, "  J%lld step=%lld seg=%lld k=%lld R=%lld a=%lld nz=%lld max=%lld old=%lld far=%lldc used=%s | ",
             W.nj, W.step, W.seg, k, R, tok[0], nnz, mx, oldlen, start - fl, us.c_str());
    W.log += buf; W.log += fv; W.log += "\n";
    bool chg = W.zeros.size() < 2 || W.zeros[W.zeros.size() - 2] != k || (W.segused & ~W.lastused);
    W.lastused = W.segused;
    if (!QUIET && (ALLJ || chg)) { printf("%s%s\n", buf, fv.c_str()); fflush(stdout); }
    W.seg = 0; W.segused = 0;
    return 2;
}
static std::string zs(const World &W) {
    std::string s; size_t i = 0;
    while (i < W.zeros.size()) { size_t j = i; while (j < W.zeros.size() && W.zeros[j] == W.zeros[i]) ++j;
        if (!s.empty()) s += ' '; s += std::to_string(W.zeros[i]); if (j - i > 1) s += "^" + std::to_string(j - i); i = j; }
    return s;
}
static std::string um(unsigned m) {
    std::string us; for (int i = 0; i < 2 * NS; ++i) if (m >> i & 1) { if (!us.empty()) us += ','; us += char('A' + i / 2); us += char('0' + i % 2); }
    return us;
}
static int usedstates(const std::vector<Tr> &t) {
    int u = 1;
    for (int i = 0; i < 2 * NS; ++i) if (t[i].def) u = std::max({u, i / 2 + 1, t[i].nx + 1});
    return u;
}
static void run(World &W, int depth) {
    while (true) {
        if (W.h <= 1 || W.h >= (ll)W.tape.size() - 2) grow(W);
        int c = W.tape[W.h];
        if (W.q == Q && c == 0 && (LOOSE || W.h > W.r1) && W.step > 0) {
            int r = kmoment(W);
            if (r == 2 && DUMPJ == W.nj) { ll a = W.lo; while (a < W.h && !W.tape[a]) ++a; std::string w; for (ll i = a; i <= std::max(W.r1, W.h); ++i) w += char(48 + W.tape[i]); printf("DUMP %s %lld %c\n", w.c_str(), W.h - a, 65 + W.q); return; }
            if (r == 3) { ++leaves; printf("LEAF %s RCAP @J%lld zeros=[%s]\n", fmt(W.t).c_str(), W.nj, zs(W).c_str()); return; }
            if (r == 2) { if (W.nj >= JMAX) { ++leaves; printf("LEAF %s J%lld zeros=[%s] used=%s\n", fmt(W.t).c_str(), W.nj, zs(W).c_str(), um(W.used).c_str()); fflush(stdout); return; } continue; }
        }
        Tr &x = W.t[2 * W.q + c];
        if (!x.def) {
            ll ones = 0; for (ll i = W.lo; i <= W.hi; ++i) ones += W.tape[i];
            ++leaves;
            printf("LEAF %s H %c%d @J%lld seg=%lld ones=%lld zeros=[%s] used=%s\n", fmt(W.t).c_str(), 'A' + W.q, c, W.nj, W.seg, ones, zs(W).c_str(), um(W.used).c_str());
            fflush(stdout);
            if (!COMPLETE || W.nund >= MAXUND) return;
            int lim = std::min(usedstates(W.t) + 1, NS);
            int slot = 2 * W.q + c;
            for (int nx = 0; nx < lim; ++nx) for (int w = 0; w < 2; ++w) for (int d = -1; d <= 1; d += 2) {
                World V = W; V.t[slot] = {w, d, nx, true}; V.nund++;
                if (!QUIET) printf("# branch %s\n", fmt(V.t).c_str());
                run(V, depth + 1);
            }
            return;
        }
        W.segused |= 1u << (2 * W.q + c); W.used |= 1u << (2 * W.q + c);
        W.tape[W.h] = x.w;
        if (x.w && W.h > W.r1) W.r1 = W.h; else if (!x.w && W.h == W.r1) { while (W.r1 >= W.lo && !W.tape[W.r1]) --W.r1; }
        W.h += x.d; W.q = x.nx; ++W.step; ++W.seg;
        if (W.h < W.lo) W.lo = W.h; if (W.h > W.hi) W.hi = W.h;
        if (SNAP && W.step % SNAP == 0) {
            ll a = W.lo; while (a < W.hi && !W.tape[a]) ++a;
            std::string w; for (ll i = a; i <= W.r1; ++i) w += char('0' + W.tape[i]);
            std::string v = dtoks(w); if (v.size() > 700) v = v.substr(0, 350) + " ... " + v.substr(v.size() - 350);
            printf("  SNAP step=%lld state=%c head=%+lld width=%lld | %s\n    right80=%s\n", W.step, 'A' + W.q, W.h - W.r1, W.r1 - a + 1, v.c_str(),
                   w.substr(w.size() > 80 ? w.size() - 80 : 0).c_str()); fflush(stdout);
        }
        if (W.seg >= MAXS || W.step - W.step0 >= MAXT) {
            ++leaves;
            if (!QUIET) {
                ll a = W.lo; while (a < W.hi && !W.tape[a]) ++a;
                std::string w; for (ll i = a; i <= W.r1; ++i) w += char('0' + W.tape[i]);
                std::string v = dtoks(w); if (v.size() > 600) v = v.substr(0, 200) + " ... " + v.substr(v.size() - 400);
                printf("  TAPE state=%c head=%+lld (from right end) width=%lld | %s\n", 'A' + W.q, W.h - W.r1, W.r1 - a + 1, v.c_str());
            }
            printf("LEAF %s T @J%lld seg=%lld zeros=[%s] used=%s\n", fmt(W.t).c_str(), W.nj, W.seg, zs(W).c_str(), um(W.used).c_str()); fflush(stdout); return;
        }
    }
}
int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: zfg MACHINE TEMPLATE [--R0 N] [--R N] [--jumps N] [--maxs N] [--start W:H:Q] [--complete] [--maxund N] [--quiet]\n"); return 2; }
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    std::string m = argv[1], tp = argv[2], start;
    for (int i = 3; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--R0") R0 = atoll(argv[++i]); else if (a == "--R") RR = atoll(argv[++i]);
        else if (a == "--jumps") JMAX = atoll(argv[++i]); else if (a == "--maxs") MAXS = (ll)atof(argv[++i]); else if (a == "--maxtotal") MAXT = (ll)atof(argv[++i]);
        else if (a == "--start") start = argv[++i]; else if (a == "--complete") COMPLETE = true;
        else if (a == "--maxund") MAXUND = atoll(argv[++i]); else if (a == "--quiet") QUIET = true; else if (a == "--alljumps") ALLJ = true; else if (a == "--loose") LOOSE = true; else if (a == "--snap") SNAP = (ll)atof(argv[++i]); else if (a == "--dumpj") DUMPJ = atoll(argv[++i]); else if (a == "--S2") { std::stringstream q(argv[++i]); std::string y; while (std::getline(q, y, ',')) SUFS.push_back(y); } else if (a == "--kdbg") KDBG = atoll(argv[++i]);
        else if (a == "--rk") RKF = atof(argv[++i]); else if (a == "--rc") RKC = atoll(argv[++i]); else if (a == "--rpow") RPOW = atof(argv[++i]); else if (a == "--rcap") RCAP = atoll(argv[++i]); else if (a == "--rmodc") { RMODM = atoll(argv[++i]); RMODC = atoll(argv[++i]); }
        else if (a == "--far") FARV = atoll(argv[++i]);
        else { fprintf(stderr, "bad option %s\n", a.c_str()); return 2; }
    }
    // template
    { std::vector<std::string> f; std::stringstream ss(tp); std::string x; while (std::getline(ss, x, ',')) f.push_back(x);
      if (f.size() < 8 || f[0] != "R") { fprintf(stderr, "template not understood / not O=R: %s\n", tp.c_str()); return 2; }
      Q = f[1][0] - 'A'; Pp = f[2].substr(2); U = f[3].substr(2); S_ = f[4].substr(2);
      if (sscanf(f[5].c_str(), "d=%lldd+%lld", &AL, &BE) != 2 || sscanf(f[6].c_str(), "b=%lldb+%lld", &ALB, &BEB) != 2) { fprintf(stderr, "bad d/b\n"); return 2; }
      SUF = f[7].substr(2); if (SUF == "-") SUF = ""; SUFS.insert(SUFS.begin(), SUF); if (Pp == "-") Pp = ""; }
    std::vector<std::string> rows; { std::stringstream ss(m); std::string r; while (std::getline(ss, r, '_')) rows.push_back(r); }
    NS = rows.size();
    World W; W.t.assign(2 * NS, {0, 0, 0, false});
    for (int s = 0; s < NS; ++s) for (int c = 0; c < 2; ++c) { std::string x = rows[s].substr(3 * c, 3);
        if (x[2] != '-' && x[2] != 'Z') W.t[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    W.tape.assign(1 << 20, 0); W.off = 1 << 19;
    std::string w; ll head = 0; int q0 = 0;
    if (!start.empty()) { size_t a = start.find(':'), b = start.rfind(':'); w = start.substr(0, a); if (w == "-") w = "";
        head = atoll(start.substr(a + 1, b - a - 1).c_str()); q0 = start[b + 1] - 'A'; }
    while ((ll)w.size() + 8 >= (ll)W.tape.size() / 2) { W.tape.resize(W.tape.size() * 2); }
    for (size_t i = 0; i < w.size(); ++i) W.tape[W.off + i] = w[i] - '0';
    W.h = W.off + head; W.q = q0; W.lo = std::min(W.off, W.h); W.hi = std::max<ll>(W.off + (ll)w.size() - 1, W.h);
    W.r1 = W.lo - 1; for (ll i = W.lo; i <= W.hi; ++i) if (W.tape[i]) W.r1 = i;
    if (!start.empty()) W.step = 1;   // allow a K-moment at the start configuration
    printf("# zfg %s %s R0=%lld R=%lld jumps=%lld maxs=%lld%s\n", m.c_str(), tp.c_str(), R0 < 0 ? RR : R0, RR, JMAX, MAXS, COMPLETE ? " complete" : "");
    run(W, 0);
    printf("# leaves=%lld\n", leaves);
}
