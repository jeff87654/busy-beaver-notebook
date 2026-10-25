// c7m: literal TM simulation from a Kt/D0-type word (head in B on the blank right end).
// Prints D0 moments  FAR (10)^y 011 (100)^P 1^L 11 (11111100)^t 1001 B>  (FAR as D-tokens, tail abbreviated),
// Kt moments (optional), H0 events (C7's H reading 0, with the left cell), halt.
// usage: c7m MACHINE SPEC MAXSTEPS [flags]   SPEC = "frame|toks|m|r|t" (toks far-first, x*k, zN gaps) or "w:WORD"
// flags: kt (print Kt moments too), noh (no H0 lines), far=N (max chars of FAR view)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <windows.h>
typedef long long ll;
static std::vector<unsigned char> t; static ll pos, lo, hi, r1;
static std::string D(ll d) { std::string s; for (ll i = 0; i < d; ++i) s += "10"; return s + "1"; }
static std::string toks(ll a, ll b, size_t maxc) {   // far-first token view of cells [a,b]
    std::vector<std::string> tk; ll i = a;
    while (i <= b) {
        if (!t[i]) { ll j = i; while (j <= b && !t[j]) ++j; tk.push_back("z" + std::to_string(j - i)); i = j; continue; }
        ll j = i, x = 0; while (j + 2 <= b && t[j + 1] == 0 && t[j + 2] == 1) { j += 2; ++x; }
        tk.push_back(std::to_string(x)); i = j + 1;
    }
    std::string out; size_t k = 0;
    while (k < tk.size()) { size_t l = k; while (l < tk.size() && tk[l] == tk[k]) ++l; if (!out.empty()) out += ' ';
        out += tk[k]; if (l - k > 1) out += "*" + std::to_string(l - k); k = l; }
    if (out.size() > maxc) out = out.substr(0, maxc / 3) + " ... " + out.substr(out.size() - 2 * maxc / 3);
    return out;
}
static bool at(ll p, const char *s) { ll L = strlen(s); if (p - L + 1 < lo) return false; for (ll i = 0; i < L; ++i) if (t[p - L + 1 + i] != s[i] - '0') return false; return true; }
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    std::string m = argv[1]; int n = (m.size() + 1) / 7;
    int W[32], Dd[32], NX[32]; bool DEF[32];
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * s + 3 * c; int k = 2 * s + c;
        if (x[0] == '-') DEF[k] = false; else { DEF[k] = true; W[k] = x[0] - '0'; Dd[k] = x[1] == 'R' ? 1 : -1; NX[k] = x[2] - 'A'; } }
    std::string spec = argv[2], w;
    if (spec.rfind("w:", 0) == 0) w = spec.substr(2);
    else if (spec.rfind("f:", 0) == 0) { FILE *fp = fopen(spec.c_str() + 2, "r"); int ch; while ((ch = fgetc(fp)) != EOF) if (ch == '0' || ch == '1') w += (char)ch; fclose(fp); }
    else {
        std::vector<std::string> f; size_t p0 = 0; while (true) { size_t p1 = spec.find('|', p0); f.push_back(spec.substr(p0, p1 == std::string::npos ? std::string::npos : p1 - p0)); if (p1 == std::string::npos) break; p0 = p1 + 1; }
        w = f[0];
        size_t a = 0; std::string ts = f[1];
        while (!ts.empty()) { size_t b = ts.find(',', a); std::string it = ts.substr(a, b == std::string::npos ? std::string::npos : b - a); size_t st = it.find('*');
            ll rep = st == std::string::npos ? 1 : atoll(it.c_str() + st + 1);
            for (ll j = 0; j < rep; ++j) { if (it[0] == 'z') { ll g = atoll(it.c_str() + 1); for (ll q = 0; q < g; ++q) w += "0"; } else w += D(atoll(it.c_str())); }
            if (b == std::string::npos) break; a = b + 1; }
        ll mm = atoll(f[2].c_str()), r = atoll(f[3].c_str()), tt = atoll(f[4].c_str());
        w += D(mm); for (ll i = 0; i < r; ++i) w += "10"; w += "11"; for (ll i = 0; i < tt; ++i) w += "11111100"; w += "1001";
    }
    ll MAXS = (ll)atof(argv[3]); bool kt = false, noh = false, dump1 = false; size_t FARC = 300;
    for (int i = 4; i < argc; ++i) { std::string a = argv[i]; if (a == "kt") kt = true; else if (a == "dump1") dump1 = true; else if (a == "noh") noh = true; else if (a.rfind("far=", 0) == 0) FARC = atoi(a.c_str() + 4); }
    ll sz = std::max<ll>(1 << 20, 8 * (ll)w.size()); t.assign(sz, 0); ll off = sz / 4;
    for (size_t i = 0; i < w.size(); ++i) t[off + i] = w[i] == '1';
    pos = off + w.size(); lo = off; hi = pos; r1 = off + w.size() - 1; while (r1 >= lo && !t[r1]) --r1;
    int q = 1; ll step = 0; const int QB = 1, QH = 7;
    while (step < MAXS) {
        if (pos < 4 || pos + 4 >= (ll)t.size()) { ll add = t.size(); std::vector<unsigned char> nt(t.size() + 2 * add, 0); memcpy(&nt[add], t.data(), t.size()); t.swap(nt); pos += add; lo += add; hi += add; r1 += add; }
        int c = t[pos];
        if (q == QH && c == 0 && !noh) { printf("H0 step=%lld left=%d\n", step, t[pos - 1]); }
        int k = 2 * q + c;
        if (!DEF[k]) { ll ones = 0; for (ll i = lo; i <= hi; ++i) ones += t[i]; ll a0 = lo; while (a0 < hi && !t[a0]) ++a0;
            printf("HALT %c%d step=%lld ones=%lld | %s <%c> %s\n", 'A' + q, c, step, ones, toks(a0, pos - 1, 4 * FARC).c_str(), 'A' + q, toks(pos, r1, 2 * FARC).c_str()); return 0; }
        t[pos] = W[k]; if (W[k] && pos > r1) r1 = pos; else if (!W[k] && pos == r1) { while (r1 >= lo && !t[r1]) --r1; }
        pos += Dd[k]; q = NX[k]; ++step; if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (q == QB && pos == r1 + 1 && at(r1, "1001")) {
            ll p = r1 - 4, tt = 0; while (at(p, "11111100")) { ++tt; p -= 8; }
            // p = last cell of "1^L 11" region (or of the Kt "(10)^r 11")
            ll ones = 0, pp = p; while (pp >= lo && t[pp]) { ++ones; --pp; }
            // D0: ... (10)^y 011 (100)^P 1^L 11 : before the ones run must be "00" (from 100) or "011"'s 0? 
            bool d0 = false; ll L = ones - 2, P = 0, y = 0, farEnd = 0;
            if (ones >= 2 && pp - 1 >= lo && t[pp] == 0) {
                ll x = pp; // x points at a 0: inside "...100" pattern? we expect cells x-1,x = "00" preceded by 1
                // the (100)^P region read leftwards: "0","0","1" ; first the "1" that started 1^L?  the 1^L run includes the block's 1? No: (100)^P 1^L: last block ends with 00, then 1^L.
                ll P0 = 0; ll c2 = pp;
                while (c2 - 2 >= lo && t[c2] == 0 && t[c2 - 1] == 0 && t[c2 - 2] == 1) { ++P0; c2 -= 3; }
                // now expect "011" read leftwards from c2: cells c2-2..c2 = 0,1,1
                if (P0 >= 0 && c2 - 2 >= lo && t[c2] == 1 && t[c2 - 1] == 1 && t[c2 - 2] == 0) {
                    ll c3 = c2 - 3, yy = 0; while (c3 - 1 >= lo && t[c3] == 0 && t[c3 - 1] == 1) { ++yy; c3 -= 2; }
                    d0 = true; P = P0; y = yy; farEnd = c3;
                } else if (P0 > 0 && t[c2] == 1 && t[c2-1]==1) {
                    // the (100) run ended by the 011 whose leading 0 is the last 0 of a 100 block? handled above
                }
            }
            if (d0) { ll a0 = lo; while (a0 < farEnd && !t[a0]) ++a0;
                printf("D0 step=%lld t=%lld L=%lld P=%lld y=%lld | far: %s\n", step, tt, L, P, y, toks(a0, farEnd, FARC).c_str()); fflush(stdout);
                if (dump1) { std::string dw; for (ll i = a0; i <= r1; ++i) dw += char('0' + t[i]); printf("DUMP %s\n", dw.c_str()); return 0; } }
            else if (kt) { ll a0 = lo; while (a0 < r1 && !t[a0]) ++a0; printf("KT step=%lld t=%lld | %s\n", step, tt, toks(a0, p, FARC).c_str()); fflush(stdout); }
        }
    }
    printf("MAX step=%lld\n", step);
}
