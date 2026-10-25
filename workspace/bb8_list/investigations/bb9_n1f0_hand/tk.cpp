// tk.cpp: literal TM tracer with D-token views.  D(m) = (10)^m 1 printed as m; raw cells in <..>; x*k repeats.
//   tk MACHINE WORD HEAD STATE MAXSTEPS [--edge Q] [--every N] [--left X] [--final] [--maxp N] [--big T]
//   --edge Q   at every visit of the rightmost visited cell in state Q print the token view when its shape changes
//              (shape = tokens with values >= T (--big, default 40) replaced by #)
//   --every N  token view every N steps
//   --left X   print when the head first goes left of cell X (cell 0 = first char of WORD), then each new minimum
//              that is at least 1000 cells further left
//   --final    token view at the end (also printed on halt)
// Halt: prints "HALT q c step ones" and the view.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
typedef long long ll;
struct Tr { int w, d, nx; bool def; };
static std::vector<unsigned char> t; static ll off, lo, hi, pos; static int q;
static ll BIG = 40;
static std::string view(bool shape) {
    ll a = lo; while (a < hi && !t[a]) ++a; ll b = hi; while (b > a && !t[b]) --b;
    if (pos > b) b = pos; if (pos < a) a = pos;
    std::vector<std::string> tok; std::string raw;
    auto fl = [&]() { if (!raw.empty()) { tok.push_back("<" + raw + ">"); raw.clear(); } };
    ll i = a;
    while (i <= b) {
        ll j = i, m = 0; bool hd = false;
        while (j + 1 <= b && t[j] == 1 && t[j + 1] == 0) { if (j == pos || j + 1 == pos) hd = true; j += 2; ++m; }
        if (j <= b && t[j] == 1 && !hd && j != pos) { fl(); tok.push_back(shape && m >= BIG ? "#" : std::to_string(m)); i = j + 1; }
        else { if (i == pos) { raw += "["; raw += char('A' + q); raw += "]"; } raw += char('0' + t[i]); ++i; }
    }
    fl();
    std::string out; size_t k = 0;
    while (k < tok.size()) { size_t l = k; while (l < tok.size() && tok[l] == tok[k]) ++l;
        if (!out.empty()) out += ' '; out += tok[k]; if (l - k > 1) out += "*" + std::to_string(l - k); k = l; }
    return out;
}
static std::string cutv(const std::string &v, ll c) { return (c && (ll)v.size() > 3 * c) ? v.substr(0, 3 * c) + " ..." : v; }
static void grow() { ll add = t.size(); std::vector<unsigned char> n(t.size() + 2 * add, 0); memcpy(&n[add], t.data(), t.size()); t.swap(n); off += add; lo += add; hi += add; pos += add; }
int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: tk MACHINE WORD HEAD STATE MAXSTEPS [opts]\n"); return 2; }
    std::string m = argv[1]; int n = (m.size() + 1) / 7; std::vector<Tr> tr(2 * n);
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * s + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') tr[2 * s + c] = {0, 0, 0, false}; else tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    std::string w = argv[2]; if (w == "-") w = ""; ll head = atoll(argv[3]); q = argv[4][0] - 'A'; ll maxs = (ll)atof(argv[5]);
    int eq = -1; ll every = 0, leftx = -1, maxp = 1000000, vcut = 0, dumpat = -1; bool fin = false;
    for (int i = 6; i < argc; ++i) { std::string a = argv[i];
        if (a == "--edge") eq = argv[++i][0] - 'A'; else if (a == "--every") every = (ll)atof(argv[++i]);
        else if (a == "--left") leftx = atoll(argv[++i]); else if (a == "--final") fin = true;
        else if (a == "--maxp") maxp = atoll(argv[++i]); else if (a == "--big") BIG = atoll(argv[++i]); else if (a == "--cut") vcut = atoll(argv[++i]); else if (a == "--dumpat") dumpat = (ll)atof(argv[++i]);
        else { fprintf(stderr, "bad opt %s\n", a.c_str()); return 2; } }
    ll sz = std::max<ll>(1 << 20, 4 * (ll)w.size()); t.assign(sz, 0); off = sz / 2;
    for (size_t i = 0; i < w.size(); ++i) t[off + i] = w[i] == '1';
    pos = off + head; lo = std::min(off, pos); hi = std::max(off + (ll)w.size() - 1, pos);
    ll step = 0, prints = 0, minp = leftx >= 0 ? off + leftx : -1; std::string lastshape; ll sim = 0;
    while (step < maxs) {
        if (pos <= 1 || pos >= (ll)t.size() - 2) { ll o = off; grow(); if (minp >= 0) minp += off - o; }
        if (step == dumpat) { ll a = lo; while (a < hi && !t[a]) ++a; ll b = hi; while (b > a && !t[b]) --b; if (pos > b) b = pos; if (pos < a) a = pos; std::string s; for (ll i = a; i <= b; ++i) s += char(48 + t[i]); printf("DUMP %s %lld %c\n", s.c_str(), pos - a, 65 + q); return 0; }
        int c = t[pos]; const Tr &x = tr[2 * q + c];
        if (!x.def) { ll ones = 0; for (ll i = lo; i <= hi; ++i) ones += t[i];
            printf("HALT %c%d step %lld ones %lld\n  %s\n", 'A' + q, c, step, ones, view(false).c_str()); return 0; }
        if (eq >= 0 && q == eq && pos == hi && prints < maxp) {
            std::string s = view(true); if (vcut && (ll)s.size() > vcut) s = s.substr(0, vcut);
            if (s != lastshape) { if (sim) printf("   (... %lld similar)\n", sim); sim = 0; printf("E %lld | %s\n", step, cutv(view(false), vcut).c_str()); lastshape = s; ++prints; fflush(stdout); }
            else ++sim;
        }
        if (every && step % every == 0) { printf("V %lld | %s\n", step, view(false).c_str()); fflush(stdout); }
        if (minp >= 0 && pos < minp) { printf("L %lld cell %lld | %s\n", step, pos - off, view(false).c_str()); fflush(stdout); minp = pos - 1000; }
        t[pos] = x.w; pos += x.d; q = x.nx; ++step;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
    }
    printf("END step %lld\n", step);
    if (fin) printf("  %s\n", view(false).c_str());
}
