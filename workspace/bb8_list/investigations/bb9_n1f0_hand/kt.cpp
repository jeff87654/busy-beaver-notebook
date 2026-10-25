// kt.cpp: literal TM run that reports canonical Kt moments (record notation):
//   Kt ds m r t = 0^inf <far junk> D(d_n)..D(d_1) D(m) (10)^r 11 (11111100)^t 1001 B> 0^inf,  D(x) = (10)^x 1.
//   kt MACHINE WORD HEAD STATE MAXSTEPS [--all] [--ntok N] [--maxp N] [--quiet]
// At every moment with state B, head on the rightmost visited cell reading 0 and the tape left of it matching
// the tail, the tokens are parsed right-to-left (as many as possible, junk left of them reported as width).
// Prints "K step t=.. ntok=.. | d_n .. d_1 | m | r" whenever the token list other than (m, r, d_1) changes
// (--all: every K moment).  --ntok N prints only the nearest N tokens (others summarised).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
typedef long long ll;
struct Tr { int w, d, nx; bool def; };
static std::vector<unsigned char> t; static ll off, lo, hi, pos; static int q;
static void grow() { ll add = t.size(); std::vector<unsigned char> n(t.size() + 2 * add, 0); memcpy(&n[add], t.data(), t.size()); t.swap(n); off += add; lo += add; hi += add; pos += add; }
static bool at(ll p, const char *s) { ll L = strlen(s); if (p - L + 1 < lo) return false; for (ll i = 0; i < L; ++i) if (t[p - L + 1 + i] != s[i] - '0') return false; return true; }
int main(int argc, char **argv) {
    std::string m = argv[1]; int n = (m.size() + 1) / 7; std::vector<Tr> tr(2 * n);
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * s + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') tr[2 * s + c] = {0, 0, 0, false}; else tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    std::string w = argv[2]; if (w == "-") w = ""; ll head = atoll(argv[3]); q = argv[4][0] - 'A'; ll maxs = (ll)atof(argv[5]);
    bool all = false, quiet = false; int evq = -1, evc = 0; std::vector<std::string> ctxs; std::vector<ll> ctxn; ll ntok = 40, maxp = 100000000;
    for (int i = 6; i < argc; ++i) { std::string a = argv[i];
        if (a == "--all") all = true; else if (a == "--ntok") ntok = atoll(argv[++i]); else if (a == "--maxp") maxp = atoll(argv[++i]); else if (a == "--quiet") quiet = true; else if (a == "--ev") { evq = argv[++i][0] - 'A'; evc = argv[i][1] - '0'; } }
    ll sz = std::max<ll>(1 << 20, 4 * (ll)w.size()); t.assign(sz, 0); off = sz / 2;
    for (size_t i = 0; i < w.size(); ++i) t[off + i] = w[i] == '1';
    pos = off + head; lo = std::min(off, pos); hi = std::max(off + (ll)w.size() - 1, pos);
    ll step = 0, prints = 0, nk = 0; std::string last;
    while (step < maxs) {
        if (pos <= 8 || pos >= (ll)t.size() - 2) grow();
        int c = t[pos];
        if (q == 1 && c == 0 && pos == hi && at(pos - 1, "1001")) {
            ll p = pos - 5, tt = 0;
            while (at(p, "11111100")) { ++tt; p -= 8; }
            if (at(p, "11")) {
                p -= 2; ll r = 0; while (p - 1 >= lo && t[p] == 0 && t[p - 1] == 1) { ++r; p -= 2; }
                std::vector<ll> tok;
                while (p >= lo && t[p] == 1) { ll x = 0; ll pp = p - 1; while (pp - 1 >= lo && t[pp] == 0 && t[pp - 1] == 1) { ++x; pp -= 2; } tok.push_back(x); p = pp; }
                ll junk = 0; { ll a = lo; while (a <= p && !t[a]) ++a; junk = p - a + 1; if (junk < 0) junk = 0; }
                ++nk;
                // key: tokens except the nearest two (m, d1)
                std::string key = std::to_string(tt) + ":" + std::to_string(junk) + ":";
                for (size_t i = 2; i < tok.size(); ++i) key += std::to_string(tok[i]) + ",";
                if ((all || key != last) && prints < maxp) {
                    std::string s; ll N = tok.size();
                    // print far -> near; compress repeats
                    std::vector<std::string> v; for (ll i = N - 1; i >= 0; --i) v.push_back(std::to_string(tok[i]));
                    ll start = 0; if (N > ntok) { s += "[" + std::to_string(N - ntok) + " more] "; start = N - ntok; }
                    size_t k = start; while (k < v.size()) { size_t l = k; while (l < v.size() && v[l] == v[k]) ++l; s += v[k]; if (l - k > 1) s += "*" + std::to_string(l - k); s += ' '; k = l; }
                    if (!quiet) printf("K %lld t=%lld junk=%lld ntok=%lld | %s| r=%lld\n", step, tt, junk, N, s.c_str(), r);
                    fflush(stdout); last = key; ++prints;
                }
            }
        }
        if (q == evq && c == evc) { std::string cx; for (ll i = pos - 4; i <= pos + 4; ++i) { if (i == pos) cx += '['; cx += char(48 + t[i]); if (i == pos) cx += ']'; }
            size_t k = 0; while (k < ctxs.size() && ctxs[k] != cx) ++k;
            if (k == ctxs.size()) { ctxs.push_back(cx); ctxn.push_back(0); printf("EV %lld new ctx %s (left %lld of lo, %lld from hi)\n", step, cx.c_str(), pos - lo, hi - pos); fflush(stdout); }
            ctxn[k]++; }
        const Tr &x = tr[2 * q + c];
        if (!x.def) { ll ones = 0; for (ll i = lo; i <= hi; ++i) ones += t[i]; printf("HALT %c%d step %lld ones %lld Kmoments %lld\n", 'A' + q, c, step, ones, nk);
            // tail of tape around head
            std::string s; for (ll i = std::max(lo, pos - 60); i <= std::min(hi, pos + 60); ++i) { if (i == pos) s += '['; s += char(48 + t[i]); if (i == pos) s += ']'; } printf("  near head: %s\n", s.c_str()); return 0; }
        t[pos] = x.w; pos += x.d; q = x.nx; ++step;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
    }
    printf("END step %lld Kmoments %lld\n", step, nk);
    for (size_t k = 0; k < ctxs.size(); ++k) printf("  ctx %s x%lld\n", ctxs[k].c_str(), ctxn[k]);
}
