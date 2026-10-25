// tslit: literal lazy-branching lockstep screener for two-change neighbourhoods.
//   tslit BASE SPACE NSAME BUDDIFF OUT [--part i/n]
// BASE: machine string (n states, '---' = halt).  If SPACE == "two": new state index n (letter A+n) added with lazy slots;
//   parents = base with 1 or 2 base slots changed, at least one changed slot -> new state.
// If SPACE == "one": no new state; parents = base with exactly one slot changed (any of 32 actions or halt).
// If SPACE == "list": read parents from stdin (machine strings, 'zzz' = lazy slot), one per line.
// Each parent is run from blank in lockstep with the base's (write,move) trace (base trace computed for NSAME steps).
// Lazy slots are branched on first read over halt + 32 actions (halt-only if no other halt could remain).
// Leaf lines:  H <steps> <sigma> <divstep> <machine>       halted (divstep = first step whose (w,d) differs from base, -1 none)
//              S <machine> <usedmask>                       same as base through NSAME steps
//              D <divstep> <endstep> <span1> <ones1> <span2> <ones2> <machine>   diverged, still running at divstep+BUDDIFF
//                 (span1/ones1 at divstep+BUDDIFF/10, span2/ones2 at the end)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <windows.h>
typedef long long ll;
enum { UNDEF = -1, LAZY = -2 };
struct Tr { signed char w, d, nx; };   // nx: >=0 state, -1 halt, -2 lazy
static int NS;           // states in children
static std::vector<unsigned char> btr;  // base trace: 2 bits/step packed in bytes (w | d<<1)
static ll NSAME, BUD;
static FILE *fo;
static ll nleaf = 0;
std::string mstr(const Tr *T) {
    std::string s;
    for (int q = 0; q < NS; ++q) { if (q) s += '_';
        for (int b = 0; b < 2; ++b) { const Tr &t = T[2 * q + b];
            if (t.nx == LAZY) s += "zzz"; else if (t.nx < 0) s += "---"; else { s += char('0' + t.w); s += t.d > 0 ? 'R' : 'L'; s += char('A' + t.nx); } } }
    return s;
}
static void parse(const char *m, Tr *T, int ns) {
    for (int q = 0; q < ns; ++q) for (int b = 0; b < 2; ++b) { const char *p = m + 7 * q + 3 * b;
        if (p[0] == 'z') T[2 * q + b] = {0, 0, LAZY};
        else if (p[0] == '-' || p[2] == '-' || p[2] - 'A' >= ns) T[2 * q + b] = {0, 0, UNDEF};
        else T[2 * q + b] = {(signed char)(p[0] - '0'), (signed char)(p[1] == 'R' ? 1 : -1), (signed char)(p[2] - 'A')}; }
}
struct St { std::vector<unsigned char> tape; ll pos, lo, hi; int q; ll step, div; };
static inline int btrace(ll s) { return (btr[s >> 2] >> ((s & 3) * 2)) & 3; }
static void run(Tr *T, St st) {
    // run until halt / lazy read / end
    std::vector<unsigned char> &tp = st.tape;
    ll pos = st.pos, lo = st.lo, hi = st.hi, step = st.step, div = st.div; int q = st.q;
    if (NSAME == 0 && div < 0 && step == 0) div = 0;   // free mode: no base comparison
    ll endstep = div >= 0 ? div + BUD : NSAME;
    ll chk1 = div >= 0 ? div + BUD / 10 : -1; ll span1 = 0, ones1 = 0;
    while (true) {
        if (step >= endstep) {
            if (div < 0) { fprintf(fo, "S %s\n", mstr(T).c_str()); }
            else { ll ones = 0; for (ll i = lo; i <= hi; ++i) ones += tp[i];
                fprintf(fo, "D %lld %lld %lld %lld %lld %lld %s\n", div, step, span1, ones1, hi - lo + 1, ones, mstr(T).c_str()); }
            ++nleaf; return;
        }
        if (step == chk1) { ll ones = 0; for (ll i = lo; i <= hi; ++i) ones += tp[i]; span1 = hi - lo + 1; ones1 = ones; }
        if (pos < 2 || pos >= (ll)tp.size() - 2) { // grow
            ll add = tp.size(); std::vector<unsigned char> n(tp.size() + 2 * add, 0); memcpy(&n[add], tp.data(), tp.size()); tp.swap(n);
            pos += add; lo += add; hi += add; }
        int c = tp[pos]; Tr &t = T[2 * q + c];
        if (t.nx == UNDEF) { ll ones = 0; for (ll i = lo; i <= hi; ++i) ones += tp[i];
            fprintf(fo, "H %lld %lld %lld %s\n", step, ones, div, mstr(T).c_str()); ++nleaf; return; }
        if (t.nx == LAZY) {
            // other halts available?
            bool otherhalt = false;
            for (int i = 0; i < 2 * NS; ++i) if (i != 2 * q + c && (T[i].nx == UNDEF || T[i].nx == LAZY)) otherhalt = true;
            St s2{tp, pos, lo, hi, q, step, div};
            // halt option
            t.nx = UNDEF; run(T, s2);
            if (otherhalt) {
                for (int w = 0; w < 2; ++w) for (int d = 0; d < 2; ++d) for (int nx = 0; nx < NS; ++nx) {
                    t = {(signed char)w, (signed char)(d ? 1 : -1), (signed char)nx};
                    St s3{tp, pos, lo, hi, q, step, div}; run(T, s3); }
            }
            t = {0, 0, LAZY}; return;
        }
        int bt = div < 0 ? btrace(step) : 0;
        if (div < 0 && (bt & 1) != t.w || div < 0 && ((bt >> 1) & 1) != (t.d > 0)) { div = step; endstep = div + BUD; chk1 = div + BUD / 10;
            if (BUD == 0) { fprintf(fo, "X %lld %s\n", div, mstr(T).c_str()); ++nleaf; return; } }
        tp[pos] = t.w; pos += t.d; if (pos < lo) lo = pos; if (pos > hi) hi = pos; q = t.nx; ++step;
    }
}
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    if (argc < 6) { fprintf(stderr, "usage\n"); return 2; }
    const char *B = argv[1]; std::string space = argv[2]; NSAME = (ll)atof(argv[3]); BUD = (ll)atof(argv[4]); fo = fopen(argv[5], "w");
    int pi = 0, pn = 1;
    for (int i = 6; i < argc; ++i) if (!strcmp(argv[i], "--part")) sscanf(argv[++i], "%d/%d", &pi, &pn);
    int nb = (strlen(B) + 1) / 7;
    NS = space == "two" ? nb + 1 : nb;
    if (space == "list") NS = nb;  // list machines have NS = nb states (base given with same size)
    Tr base[32]; parse(B, base, nb);
    // base trace
    if (NSAME > 0) { btr.assign(NSAME / 4 + 2, 0); std::vector<unsigned char> tp(1 << 24, 0); ll pos = 1 << 23; int q = 0;
      for (ll s = 0; s < NSAME; ++s) { Tr &t = base[2 * q + tp[pos]]; if (t.nx < 0) { fprintf(stderr, "base halts at %lld\n", s); NSAME = s; break; }
        btr[s >> 2] |= (t.w | ((t.d > 0) << 1)) << ((s & 3) * 2); tp[pos] = t.w; pos += t.d; q = t.nx;
        if (pos < 2 || pos >= (ll)tp.size() - 2) { ll add = tp.size(); std::vector<unsigned char> n(3 * add, 0); memcpy(&n[add], tp.data(), add); tp.swap(n); pos += add; } } }
    std::vector<std::string> parents;
    if (space == "list") { char buf[512]; while (scanf("%511s", buf) == 1) parents.push_back(buf); }
    else {
        std::vector<Tr> vals; vals.push_back({0, 0, UNDEF});
        for (int w = 0; w < 2; ++w) for (int d = 0; d < 2; ++d) for (int nx = 0; nx < NS; ++nx) vals.push_back({(signed char)w, (signed char)(d ? 1 : -1), (signed char)nx});
        auto same = [](const Tr &a, const Tr &b) { return (a.nx < 0 && b.nx < 0) || (a.nx == b.nx && a.w == b.w && a.d == b.d); };
        Tr T[32];
        int nslot = 2 * nb;
        if (space == "two") {
            for (int i = 0; i < 2 * NS; ++i) T[i] = i < nslot ? base[i] : Tr{0, 0, LAZY};
            for (int a = 0; a < nslot; ++a) for (auto &va : vals) { if (same(va, base[a])) continue;
                // single change
                if (va.nx == nb) { Tr U[32]; memcpy(U, T, sizeof U); U[a] = va; parents.push_back(mstr(U)); }
                for (int b = a + 1; b < nslot; ++b) for (auto &vb : vals) { if (same(vb, base[b])) continue;
                    if (va.nx != nb && vb.nx != nb) continue;
                    Tr U[32]; memcpy(U, T, sizeof U); U[a] = va; U[b] = vb; parents.push_back(mstr(U)); } }
        } else {
            for (int a = 0; a < nslot; ++a) for (auto &va : vals) { if (same(va, base[a])) continue;
                Tr U[32]; memcpy(U, base, sizeof U); U[a] = va; parents.push_back(mstr(U)); }
        }
    }
    fprintf(stderr, "parents %zu NS %d NSAME %lld\n", parents.size(), NS, NSAME);
    ll np = 0;
    for (size_t i = 0; i < parents.size(); ++i) { if ((ll)(i % pn) != pi) continue;
        Tr T[32]; std::string m = parents[i];
        parse(m.c_str(), T, NS);   // lazy slots are written as zzz by mstr
        bool anyh = false; for (int k = 0; k < 2 * NS; ++k) if (T[k].nx < 0) anyh = true;
        if (!anyh) continue;
        St st; st.tape.assign(1 << 12, 0); st.pos = 1 << 11; st.lo = st.hi = st.pos; st.q = 0; st.step = 0; st.div = -1;
        fprintf(fo, "P %s\n", m.c_str());
        run(T, st); ++np;
        if (np % 200 == 0) { fflush(fo); fprintf(stderr, "%lld parents, %lld leaves\n", np, nleaf); }
    }
    fprintf(fo, "END %lld %lld\n", np, nleaf); fclose(fo);
    return 0;
}
