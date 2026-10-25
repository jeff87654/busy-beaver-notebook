// cfollow.cpp (collapse_search, 2026-10-23): parent-vs-candidate follower for state-collapse search.
// Modes
//   lit   PARENT CANDFILE STARTFILE N [--skip S] [--keep F]
//         For every start (STARTFILE line: "q head rle": parent state index, head coordinate, RLE tape from coord 0;
//         'blank' = blank tape state 0) the parent runs N literal steps and records its EDGE MOMENTS (head on a 0 just
//         right of the rightmost 1 or just left of the leftmost 1; full-tape hash, consecutive duplicates removed).
//         Each candidate (CANDFILE line: MACHINE TAG MAP) runs from the same start (state mapped by MAP) for <= 3N steps;
//         its moment list must match the parent's as a sequence with <= S skipped moments per side per mismatch
//         (relay tolerance).  A candidate stops at its 2nd failed start.  The parent's halt must be matched by a halt.
//   world PARENT CANDFILE [--kt K | --start q:head:rle] [--Rdef R] [--maxs N] [--maxj J] [--qb B]
//         Jump world (hsim's champion CL jump at B-moments; R := Rdef for every clear).  Per candidate: number of CL
//         events equal to the parent's (full-tape hash at the CL moment), number with equal (t,K,X), total CLs, halt.
//   dump  MACHINE [--kt K] [--Rdef R] [--maxs N] [--maxj J] [--every E] [--qb B]  > STARTFILE
//         Jump-world run; writes the configuration right after every jump and every E-th B-moment as a start line.
//   prof  MACHINE [--kt K] [--Rdef R] [--maxs N] [--maxj J] [--qb B] [--lit]
//         Slot usage counts and, per state, the most frequent entry contexts (cells head-3..head+3) and entry slots.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <windows.h>
typedef long long ll; typedef unsigned long long u64;
struct Mach { int n; int W[64], D[64], N[64]; bool def[64]; std::string s; };
static Mach parse(const std::string &m) {
    Mach M; M.s = m; M.n = (int)(m.size() + 1) / 7;
    for (int s = 0; s < M.n; ++s) for (int c = 0; c < 2; ++c) {
        const char *x = m.c_str() + 7 * s + 3 * c; int i = 2 * s + c;
        M.def[i] = !(x[0] == '-' || x[2] == 'Z' || x[2] - 'A' >= M.n);
        M.W[i] = M.def[i] ? x[0] - '0' : 0; M.D[i] = x[1] == 'R' ? 1 : -1; M.N[i] = M.def[i] ? x[2] - 'A' : 0; }
    return M;
}
static inline u64 hx(ll x) { u64 z = (u64)x + 0x9E3779B97F4A7C15ULL; z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; return z ^ (z >> 31); }
struct Tape {
    std::vector<unsigned char> t; ll org; u64 H = 0;
    void init(ll size) { t.assign(size, 0); org = size / 2; H = 0; }
    void grow() { ll add = t.size(); std::vector<unsigned char> n(t.size() + 2 * add, 0); memcpy(&n[add], t.data(), t.size()); t.swap(n); org += add; }
    inline int get(ll x) { return t[x + org]; }
    inline void set(ll x, int v) { unsigned char &c = t[x + org]; if (c != v) { H ^= hx(x); c = (unsigned char)v; } }
};
struct Start { int q; ll head; std::string rle; bool blank; };
static std::vector<Start> loadStarts(const char *fn) {
    std::vector<Start> v; FILE *f = fopen(fn, "r"); if (!f) { fprintf(stderr, "no startfile\n"); exit(2); }
    static char buf[1 << 24];
    while (fgets(buf, sizeof buf, f)) { std::string l = buf; while (!l.empty() && (l.back() == '\n' || l.back() == '\r')) l.pop_back();
        if (l.empty() || l[0] == '#') continue; Start s; s.blank = (l.rfind("blank", 0) == 0);
        if (s.blank) { s.q = 0; s.head = 0; } else { char *p = (char *)l.c_str(); s.q = strtol(p, &p, 10); s.head = strtoll(p, &p, 10); while (*p == ' ') ++p; s.rle = p; }
        v.push_back(s); }
    fclose(f); return v;
}
// rle: "b r1 r2 r3 ..." first symbol b, then run lengths of alternating symbols, cells from coordinate 0
static void loadTape(Tape &T, const Start &s) {
    ll len = 0; std::vector<ll> runs; int b = 0;
    if (!s.blank) { const char *p = s.rle.c_str(); char *e; b = strtol(p, &e, 10); p = e; while (true) { ll r = strtoll(p, &e, 10); if (e == p) break; runs.push_back(r); len += r; p = e; } }
    ll size = 1 << 16; while (size < 3 * len + 4096) size *= 2;
    T.init(size); ll x = 0; int v = b;
    for (ll r : runs) { if (v) for (ll i = 0; i < r; ++i) T.set(x + i, 1); x += r; v ^= 1; }
}
static std::string rleOf(Tape &T, ll a, ll b) {
    std::string o = std::to_string(T.get(a)); ll run = 0; int cur = T.get(a);
    for (ll x = a; x <= b; ++x) { int c = T.get(x); if (c == cur) ++run; else { o += " " + std::to_string(run); cur = c; run = 1; } }
    o += " " + std::to_string(run); return o;
}
static FILE *LDUMP = nullptr; static ll LDEVERY = 0;
struct LitRes { std::vector<u64> mom; ll steps; int halt; ll maxgap = 0; };
struct Online { const std::vector<u64> *P = nullptr; size_t i = 0, j = 0; int S = 3; bool failed = false; ll gapcap = 0;
    // advance over Q (candidate moments so far); final=true means no more Q moments will come
    void adv(const std::vector<u64> &Q, bool final) {
        if (!P) return;
        while (!failed && i < P->size() && j < Q.size()) {
            if ((*P)[i] == Q[j]) { ++i; ++j; continue; }
            if (!final && j + S >= Q.size()) return;      // need lookahead
            bool ok = false;
            for (int a = 0; a <= S && !ok; ++a) for (int b = 0; b <= S && !ok; ++b) { if (a + b == 0) continue;
                if (i + a < P->size() && j + b < Q.size() && (*P)[i + a] == Q[j + b]) { i += a; j += b; ok = true; } }
            if (!ok) failed = true;
        }
    } };
static LitRes runLit(const Mach &M, const Start &s, int q0, ll maxs, size_t maxmom, Online *on = nullptr) {
    Tape T; loadTape(T, s); LitRes R; R.halt = -1; ll pos = s.head; int q = q0;
    // lazy bounds: every 1 lies in [L1, R1] (R1 upper bound, L1 lower bound); tightened only when a moment is tested
    ll L1 = 1LL << 60, R1 = -(1LL << 60);
    for (ll i = 0; i < (ll)T.t.size(); ++i) if (T.t[i]) { ll x = i - T.org; if (x < L1) L1 = x; if (x > R1) R1 = x; }
    u64 last = 0; bool haveLast = false; ll st = 0, lastst = 0; ll gapcap = on && on->gapcap > 0 ? on->gapcap : (1LL << 62);
    for (; st < maxs; ++st) {
        if (pos + T.org < 64 || pos + T.org >= (ll)T.t.size() - 64) { if (T.t.size() > ((size_t)1 << 27)) break; T.grow(); }
        int c = T.get(pos);
        if (st - lastst > gapcap) { on->failed = true; break; }
        if (c == 0) {
            int side = 0;
            if (T.get(pos - 1) == 1) { while (R1 > pos && !T.get(R1)) --R1; if (R1 <= pos) { R1 = pos - 1; side = 1; } }
            if (!side && T.get(pos + 1) == 1) { while (L1 < pos && !T.get(L1)) ++L1; if (L1 >= pos) { L1 = pos + 1; side = 2; } }
            if (side) { u64 h = T.H ^ (side == 1 ? 0x51ULL : 0x77ULL); if (!haveLast || h != last) { if (LDUMP && LDEVERY > 0 && (R.mom.size() + 1) % LDEVERY == 0) { ll a = pos, b = pos; for (ll x = pos - 1; x + T.org >= 0 && x >= pos - (ll)T.t.size(); --x) { if (x + T.org < 0) break; if (T.get(x)) a = x; } for (ll x = pos + 1; x + T.org < (ll)T.t.size(); ++x) if (T.get(x)) b = x; fprintf(LDUMP, "%d %lld %s\n", q, pos - a, rleOf(T, a, b).c_str()); }
                R.mom.push_back(h); if (st - lastst > R.maxgap) R.maxgap = st - lastst; lastst = st; last = h; haveLast = true; if (R.mom.size() >= maxmom) break;
                if (on) { on->adv(R.mom, false); if (on->failed) break; } } }
        }
        int i = 2 * q + c;
        if (!M.def[i]) { R.halt = i; break; }
        int w = M.W[i];
        if (w != c) { T.set(pos, w); if (w) { if (pos > R1) R1 = pos; if (pos < L1) L1 = pos; } }
        pos += M.D[i]; q = M.N[i];
    }
    if (st - lastst > R.maxgap) R.maxgap = st - lastst;
    R.steps = st; return R;
}
static size_t cmpMom(const std::vector<u64> &P, const std::vector<u64> &Q, int S, bool &full) {
    size_t i = 0, j = 0, matched = 0;
    while (i < P.size() && j < Q.size()) {
        if (P[i] == Q[j]) { ++i; ++j; ++matched; continue; }
        bool ok = false;
        for (int a = 0; a <= S && !ok; ++a) for (int b = 0; b <= S && !ok; ++b) { if (a + b == 0) continue;
            if (i + a < P.size() && j + b < Q.size() && P[i + a] == Q[j + b]) { i += a; j += b; ok = true; } }
        if (!ok) break;
    }
    full = (i >= P.size()); return matched;
}
struct CL { ll step, t, r, K, X; u64 h; };
struct JRes { std::vector<CL> cl; ll steps; int halt; ll ones; ll maxK; std::string fin; };
static std::string tview(Tape &T, ll a, ll b, size_t VIEW = 300) {
    while (a <= b && !T.get(a)) ++a;
    std::vector<std::string> v;
    for (ll i = a; i <= b;) {
        if (!T.get(i)) { ll j = i; while (j <= b && !T.get(j)) ++j; v.push_back("z" + std::to_string(j - i)); i = j; continue; }
        ll x = 0, j = i; while (j + 2 <= b && T.get(j + 1) == 0 && T.get(j + 2) == 1) { j += 2; ++x; }
        v.push_back(std::to_string(x)); i = j + 1; }
    std::string o;
    for (size_t k = 0; k < v.size();) { size_t l = k; while (l < v.size() && v[l] == v[k]) ++l;
        if (!o.empty()) o += ' '; o += v[k]; if (l - k > 1) o += "*" + std::to_string(l - k); k = l; }
    if (o.size() > VIEW) o = o.substr(0, VIEW / 3) + " ... " + o.substr(o.size() - 2 * VIEW / 3);
    return o;
}
static std::vector<std::string> split(const std::string &s, char c) { std::vector<std::string> r; size_t p = 0; while (true) { size_t q = s.find(c, p); r.push_back(s.substr(p, q == std::string::npos ? std::string::npos : q - p)); if (q == std::string::npos) break; p = q + 1; } return r; }
static std::string ktToRle(const std::string &KT, ll &head) {
    std::string w0; auto f = split(KT, ';');
    if (!f[0].empty()) for (auto &it : split(f[0], ',')) { size_t st = it.find('*'); ll rep = st == std::string::npos ? 1 : atoll(it.c_str() + st + 1);
        for (ll j = 0; j < rep; ++j) { if (it[0] == 'z') w0.append(atoll(it.c_str() + 1), '0'); else { ll d = atoll(it.c_str()); for (ll u = 0; u < d; ++u) w0 += "10"; w0 += "1"; } } }
    ll m = atoll(f[1].c_str()), r = atoll(f[2].c_str()), t = atoll(f[3].c_str());
    for (ll u = 0; u < m; ++u) w0 += "10"; w0 += "1"; for (ll u = 0; u < r; ++u) w0 += "10"; w0 += "11";
    for (ll u = 0; u < t; ++u) w0 += "11111100"; w0 += "1001";
    head = w0.size();
    std::string o = std::string(1, w0[0]); ll run = 0; char cur = w0[0];
    for (char ch : w0) { if (ch == cur) ++run; else { o += " " + std::to_string(run); cur = ch; run = 1; } }
    o += " " + std::to_string(run); return o;
}
struct Prof { std::vector<ll> use; std::vector<std::map<std::string, ll>> ctx; std::vector<std::map<int, ll>> ent; };
static FILE *DUMP = nullptr; static ll DUMPEVERY = 0; static const size_t MAXW = (size_t)1 << 27;
static JRes runJump(const Mach &M, const Start &s, int q0, int QB, ll RDEF, ll maxs, ll maxj, Prof *pf, bool LIT) {
    Tape T; loadTape(T, s); JRes R; R.halt = -1; R.maxK = 0; ll pos = s.head; int q = q0;
    ll lo = pos, hi = pos; for (ll i = 0; i < (ll)T.t.size(); ++i) if (T.t[i]) { ll x = i - T.org; if (x < lo) lo = x; if (x > hi) hi = x; }
    ll r1 = hi; while (r1 >= lo && !T.get(r1)) --r1;
    ll step = 0, nj = 0, bm = 0; int prevslot = -1;
    while (true) {
        if (pos + T.org < 64 || pos + T.org >= (ll)T.t.size() - 64) { if (T.t.size() > MAXW) { R.fin = "WIDE"; break; } T.grow(); }
        int c = T.get(pos);
        if (q == QB && c == 0 && pos > r1 && T.get(pos - 1) == 1 && T.get(pos - 2) == 0 && T.get(pos - 3) == 0 && T.get(pos - 4) == 1) {
            ll p = pos - 5, t = 0;
            auto is = [&](ll e, const char *z) { ll L = strlen(z); if (e - L + 1 < lo) return false; for (ll i = 0; i < L; ++i) if (T.get(e - L + 1 + i) != z[i] - '0') return false; return true; };
            while (is(p, "11111100")) { ++t; p -= 8; }
            ++bm;
            if (DUMP && DUMPEVERY > 0 && bm % DUMPEVERY == 0) fprintf(DUMP, "%d %lld %s\n", q, pos - lo, rleOf(T, lo, hi).c_str());
            if (!LIT && is(p, "11")) {
                p -= 2; ll r = 0; while (p - 1 >= lo && T.get(p) == 0 && T.get(p - 1) == 1) { ++r; p -= 2; }
                std::vector<ll> tk, ts; int after = -1;
                while (p >= lo && T.get(p) == 1) {
                    ll x = 0, pp = p; while (pp - 2 >= lo && T.get(pp - 1) == 0 && T.get(pp - 2) == 1) { ++x; pp -= 2; }
                    tk.push_back(x); ts.push_back(pp); p = pp - 1;
                    if (after >= 0) { if (--after < 0) break; continue; }
                    if (tk.size() == 1 && x != 1) break;
                    if (tk.size() >= 2 && x != 1) after = 0; }
                ll k = -1, X = -1;
                if (tk.size() >= 2 && tk[0] == 1) { size_t i = 1; while (i < tk.size() && tk[i] == 1) ++i; if (i < tk.size()) { k = i - 1; X = tk[i]; } }
                if (k >= 0 && X >= 4 && X % 3 == 1) {
                    CL e; e.step = step; e.t = t; e.r = r; e.K = k + 1; e.X = X; e.h = T.H ^ hx(pos - lo + 7777777); R.cl.push_back(e); if (k + 1 > R.maxK) R.maxK = k + 1;
                    ll st = ts[k + 1]; std::string w;
                    for (ll u = 0; u < k + 2; ++u) w += "101";
                    for (ll u = 0; u < 3 * RDEF + 2; ++u) w += "10"; w += "11";
                    for (ll u = 0; u < t; ++u) w += "11111100"; w += "1001";
                    for (ll i = st; i <= hi; ++i) T.set(i, 0);
                    while (st + (ll)w.size() + 128 + T.org >= (ll)T.t.size()) T.grow();
                    for (size_t i = 0; i < w.size(); ++i) T.set(st + i, w[i] - '0');
                    pos = st + w.size(); hi = pos; r1 = pos - 1; q = QB; ++nj;
                    if (DUMP) fprintf(DUMP, "%d %lld %s\n", q, pos - lo, rleOf(T, lo, hi).c_str());
                    if (maxj >= 0 && nj >= maxj) { R.fin = "MAXJ"; break; }
                    continue;
                }
            }
        }
        int i = 2 * q + c;
        if (pf) { pf->use[i]++; if (prevslot >= 0 && (prevslot >> 1) != q) { std::string cx; for (ll d = -3; d <= 3; ++d) cx += (char)('0' + T.get(pos + d)); pf->ctx[q][cx]++; pf->ent[q][prevslot]++; } prevslot = i; }
        if (!M.def[i]) { R.halt = i; break; }
        T.set(pos, M.W[i]);
        if (M.W[i]) { if (pos > r1) r1 = pos; } else if (pos == r1) { while (r1 >= lo && !T.get(r1)) --r1; }
        pos += M.D[i]; q = M.N[i]; ++step;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (step >= maxs) { R.fin = "MAXS"; break; }
    }
    ll ones = 0; for (ll x = lo; x <= hi; ++x) ones += T.get(x);
    R.ones = ones; R.steps = step; if (R.halt >= 0) R.fin = std::string("HALT ") + (char)('A' + R.halt / 2) + (char)('0' + R.halt % 2);
    R.fin += " | " + tview(T, lo, hi, 240);
    return R;
}
static int mapState(const std::string &mp, int q) { if (mp.empty()) return q; if (q >= (int)mp.size() || mp[q] == '.') return -1; return mp[q] - '0'; }
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    if (argc < 3) { fprintf(stderr, "see header\n"); return 2; }
    std::string mode = argv[1];
    std::string KT, STARTS; ll RDEF = 6, MAXS = (ll)2e8, MAXJ = -1, EVERY = 0; int QB = 1, SKIP = 3; double KEEP = 0.5; bool LIT = false;
    int a0 = (mode == "lit") ? 6 : (mode == "world" ? 4 : 3);
    for (int i = a0; i < argc; ++i) { std::string a = argv[i];
        if (a == "--kt") KT = argv[++i]; else if (a == "--start") STARTS = argv[++i]; else if (a == "--Rdef") RDEF = atoll(argv[++i]);
        else if (a == "--maxs") MAXS = (ll)atof(argv[++i]); else if (a == "--maxj") MAXJ = atoll(argv[++i]); else if (a == "--every") EVERY = atoll(argv[++i]);
        else if (a == "--qb") QB = atoi(argv[++i]); else if (a == "--skip") SKIP = atoi(argv[++i]); else if (a == "--keep") KEEP = atof(argv[++i]);
        else if (a == "--lit") LIT = true; else { fprintf(stderr, "bad arg %s\n", a.c_str()); return 2; } }
    Start s0; s0.blank = true; s0.q = 0; s0.head = 0;
    if (!KT.empty()) { s0.blank = false; s0.q = QB; s0.rle = ktToRle(KT, s0.head); }
    if (!STARTS.empty()) { s0.blank = false; char *p = (char *)STARTS.c_str(); s0.q = strtol(p, &p, 10); ++p; s0.head = strtoll(p, &p, 10); ++p; s0.rle = p; }
    if (mode == "ldump") {   // ldump MACHINE N EVERY : literal run from blank (or --kt/--start), dump every EVERY-th edge moment
        Mach M = parse(argv[2]); LDUMP = stdout; LDEVERY = EVERY;
        LitRes r = runLit(M, s0, s0.q, MAXS, 1u << 30);
        fprintf(stderr, "# %s steps=%lld moments=%zu halt=%d\n", M.s.c_str(), r.steps, r.mom.size(), r.halt);
        return 0;
    }
    if (mode == "dump" || mode == "prof") {
        Mach M = parse(argv[2]); Prof pf; pf.use.assign(2 * M.n, 0); pf.ctx.resize(M.n); pf.ent.resize(M.n);
        if (mode == "dump") { DUMP = stdout; DUMPEVERY = EVERY; }
        JRes R = runJump(M, s0, s0.q, QB, RDEF, MAXS, MAXJ, mode == "prof" ? &pf : nullptr, LIT);
        FILE *o = mode == "dump" ? stderr : stdout;
        fprintf(o, "# %s steps=%lld cl=%zu maxK=%lld ones=%lld %s\n", M.s.c_str(), R.steps, R.cl.size(), R.maxK, R.ones, R.fin.c_str());
        if (mode == "prof") {
            for (int i = 0; i < 2 * M.n; ++i) printf("USE %c%d %lld\n", 'A' + i / 2, i % 2, pf.use[i]);
            for (int q = 0; q < M.n; ++q) { std::vector<std::pair<ll, std::string>> v; for (auto &kv : pf.ctx[q]) v.push_back({kv.second, kv.first}); std::sort(v.rbegin(), v.rend());
                printf("CTX %c n=%zu :", 'A' + q, v.size()); for (size_t k = 0; k < v.size() && k < 12; ++k) printf(" %s:%lld", v[k].second.c_str(), v[k].first); printf("\n");
                printf("ENT %c :", 'A' + q); for (auto &kv : pf.ent[q]) printf(" %c%d:%lld", 'A' + kv.first / 2, kv.first % 2, kv.second); printf("\n"); }
        }
        return 0;
    }
    Mach P = parse(argv[2]);
    FILE *cf = fopen(argv[3], "r"); if (!cf) { fprintf(stderr, "no candfile\n"); return 2; }
    std::vector<std::string> cm, ctag, cmap; { char b1[512], b2[256], b3[64]; char line[1024];
        while (fgets(line, sizeof line, cf)) { b2[0] = b3[0] = 0; int k = sscanf(line, "%511s %255s %63s", b1, b2, b3); if (k < 1 || b1[0] == '#') continue; cm.push_back(b1); ctag.push_back(k > 1 ? b2 : "-"); cmap.push_back(k > 2 ? b3 : ""); } fclose(cf); }
    if (mode == "lit") {
        auto st = loadStarts(argv[4]); ll N = (ll)atof(argv[5]);
        std::vector<LitRes> ref;
        for (size_t k = 0; k < st.size(); ++k) { ref.push_back(runLit(P, st[k], st[k].q, N, 1u << 22));
            fprintf(stderr, "start %zu: parent moments=%zu steps=%lld halt=%d\n", k, ref[k].mom.size(), ref[k].steps, ref[k].halt); }
        std::vector<ll> hist(st.size() + 1, 0);
        for (size_t c = 0; c < cm.size(); ++c) {
            Mach Q = parse(cm[c]); int npass = 0, nfail = 0; std::string prof; double firstfrac = -1;
            for (size_t k = 0; k < st.size(); ++k) {
                int q0 = mapState(cmap[c], st[k].q); if (q0 < 0) { prof += " -"; continue; }
                Online on; on.P = &ref[k].mom; on.S = SKIP; on.gapcap = 2 * std::max(ref[k].maxgap, ref[k].steps - 0) / 1 + 1000; if (ref[k].maxgap > 0) on.gapcap = 2 * ref[k].maxgap + 1000;
                LitRes r = runLit(Q, st[k], q0, 3 * N / 2 + 1000, ref[k].mom.size() + 4, &on);
                bool full; size_t m = cmpMom(ref[k].mom, r.mom, SKIP, full);
                bool hok;
                if (ref[k].halt >= 0) hok = full && r.halt >= 0;
                else hok = full && !(r.halt >= 0 && r.mom.size() <= ref[k].mom.size());
                if (hok) { ++npass; prof += " P"; }
                else { ++nfail; char b[64]; snprintf(b, sizeof b, " %zu/%zu%s", m, ref[k].mom.size(), r.halt >= 0 ? "h" : "");
                    prof += b; if (firstfrac < 0) firstfrac = ref[k].mom.empty() ? 0 : (double)m / ref[k].mom.size();
                    if (nfail >= 2) break; }
            }
            hist[npass]++;
            bool keep = (nfail <= 1 && npass >= 1) || firstfrac >= KEEP;
            if (keep) printf("%s %s %s npass=%d nfail=%d |%s\n", cm[c].c_str(), ctag[c].c_str(), cmap[c].c_str(), npass, nfail, prof.c_str());
            if (c % 50000 == 0) { fprintf(stderr, "%zu/%zu\n", c, cm.size()); fflush(stdout); }
        }
        fprintf(stderr, "hist npass:"); for (size_t k = 0; k < hist.size(); ++k) fprintf(stderr, " %zu:%lld", k, hist[k]); fprintf(stderr, "\n");
        return 0;
    }
    if (mode == "world") {
        JRes ref = runJump(P, s0, s0.q, QB, RDEF, MAXS, MAXJ, nullptr, false);
        printf("PARENT %s steps=%lld cl=%zu maxK=%lld ones=%lld %s\n", P.s.c_str(), ref.steps, ref.cl.size(), ref.maxK, ref.ones, ref.fin.c_str());
        for (size_t k = 0; k < ref.cl.size() && k < 40; ++k) printf("  CL %zu step=%lld t=%lld r=%lld K=%lld X=%lld\n", k + 1, ref.cl[k].step, ref.cl[k].t, ref.cl[k].r, ref.cl[k].K, ref.cl[k].X);
        fflush(stdout);
        for (size_t c = 0; c < cm.size(); ++c) {
            Mach Q = parse(cm[c]); int qb = mapState(cmap[c], QB); int q0 = s0.blank ? 0 : mapState(cmap[c], s0.q);
            if (qb < 0 || q0 < 0) { printf("CAND %s %s SKIP (B or start state deleted)\n", cm[c].c_str(), ctag[c].c_str()); continue; }
            JRes r = runJump(Q, s0, q0, qb, RDEF, MAXS, MAXJ, nullptr, false);
            size_t eh = 0, em = 0; while (eh < r.cl.size() && eh < ref.cl.size() && r.cl[eh].h == ref.cl[eh].h) ++eh;
            while (em < r.cl.size() && em < ref.cl.size() && r.cl[em].t == ref.cl[em].t && r.cl[em].K == ref.cl[em].K && r.cl[em].X == ref.cl[em].X) ++em;
            std::string ks; ll mx = 0; int esc = 0; for (size_t k = 0; k < r.cl.size(); ++k) if (r.cl[k].K > mx) { mx = r.cl[k].K; ++esc; if (esc <= 12) ks += (esc > 1 ? "," : "") + std::to_string(mx); }
            ks = std::to_string(esc) + ":" + ks;
            printf("CAND %s %s eqhash=%zu eqTKX=%zu cl=%zu maxK=%lld ones=%lld steps=%lld Ks=%s %s\n", cm[c].c_str(), ctag[c].c_str(), eh, em, r.cl.size(), r.maxK, r.ones, r.steps, ks.c_str(), r.fin.c_str());
            fflush(stdout);
        }
        return 0;
    }
    fprintf(stderr, "unknown mode\n"); return 2;
}
