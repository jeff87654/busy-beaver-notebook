// hsim.cpp (bb9_h003check, 2026-10-22): own literal TM simulator for the h003 check.
// Byte tape; the ONLY non-literal step is the champion clear (CL), applied at a canonical B-moment
//    ... D(x_n) .. D(x_1) D(m) (10)^r 11 (11111100)^t 1001 [state B on 0, blank to the right],  D(x) = (10)^x 1,
// when m = 1, x_1..x_k = 1 (k >= 0) and x_(k+1) = X = 1 mod 3, X >= 4:   X 1^(k+1)  ->  1^(k+2)  with r := 3R+2, R from
// --R list (then --Rdef).  Option --lit disables all jumps (pure literal run).
// Output: one "CL" line per jump (view far->near before the clear), "I0"/"H0L0" event lines (H reads 0 with 0 on its left,
// I reads 0), counts of H0 events with left 1, HALT line with ones and the final view.
// Usage: hsim MACHINE [--kt "toks;m;r;t"] [--R a,b,..] [--Rdef N] [--maxs N] [--maxj N] [--lit] [--view N] [--ev N]
//        [--cnt] (counter skip: same (k,X) three times with C dropping by 3 -> C := 6 + C mod 3; logged)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <windows.h>
typedef long long ll;
static std::vector<unsigned char> T;
static int VIEW = 400;
static std::string view(ll a, ll b) {
    while (a <= b && !T[a]) ++a;
    std::vector<std::string> v;
    for (ll i = a; i <= b;) {
        if (!T[i]) { ll j = i; while (j <= b && !T[j]) ++j; v.push_back("z" + std::to_string(j - i)); i = j; continue; }
        ll x = 0, j = i; while (j + 2 <= b && T[j + 1] == 0 && T[j + 2] == 1) { j += 2; ++x; }
        v.push_back(std::to_string(x)); i = j + 1;
    }
    std::string o;
    for (size_t k = 0; k < v.size();) { size_t l = k; while (l < v.size() && v[l] == v[k]) ++l;
        if (!o.empty()) o += ' '; o += v[k]; if (l - k > 1) o += "*" + std::to_string(l - k); k = l; }
    if ((ll)o.size() > VIEW) o = o.substr(0, VIEW / 3) + " ... " + o.substr(o.size() - 2 * VIEW / 3);
    return o;
}
static std::vector<std::string> split(const std::string &s, char c) {
    std::vector<std::string> r; size_t p = 0;
    while (true) { size_t q = s.find(c, p); r.push_back(s.substr(p, q == std::string::npos ? std::string::npos : q - p)); if (q == std::string::npos) break; p = q + 1; }
    return r;
}
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    std::string M = argv[1]; int ns = (int)(M.size() + 1) / 7;
    int W[64], Dm[64], Nx[64]; bool def[64];
    for (int s = 0; s < ns; ++s) for (int c = 0; c < 2; ++c) {
        const char *x = M.c_str() + 7 * s + 3 * c; int i = 2 * s + c;
        def[i] = x[0] != '-'; W[i] = def[i] ? x[0] - '0' : 0; Dm[i] = x[1] == 'R' ? 1 : -1; Nx[i] = def[i] ? x[2] - 'A' : 0; }
    std::vector<ll> RL; ll RDEF = 366, MAXS = (ll)2e11, MAXJ = -1, EV = 50; bool LIT = false, CNT = false, CANON = false, STOPTOP = false; ll D0LOG = 0; ll E0LOG = 0; std::string KT;
    for (int i = 2; i < argc; ++i) { std::string a = argv[i];
        if (a == "--R") { for (auto &z : split(argv[++i], ',')) RL.push_back(atoll(z.c_str())); }
        else if (a == "--Rdef") RDEF = atoll(argv[++i]);
        else if (a == "--maxs") MAXS = (ll)atof(argv[++i]);
        else if (a == "--maxj") MAXJ = atoll(argv[++i]);
        else if (a == "--lit") LIT = true;
        else if (a == "--cnt") CNT = true;
        else if (a == "--canon") CANON = true;
        else if (a == "--stoptop") STOPTOP = true;
        else if (a == "--d0") D0LOG = atoll(argv[++i]);
        else if (a == "--e0") E0LOG = atoll(argv[++i]);
        else if (a == "--view") VIEW = atoi(argv[++i]);
        else if (a == "--ev") EV = atoll(argv[++i]);
        else if (a == "--kt") KT = argv[++i];
        else { fprintf(stderr, "bad arg %s\n", a.c_str()); return 2; } }
    std::string w0;
    int q = 0;
    if (!KT.empty()) {   // "t1,t2*rep,zN,...;m;r;t"  tokens far->near
        auto f = split(KT, ';');
        if (!f[0].empty()) for (auto &it : split(f[0], ',')) {
            size_t st = it.find('*'); ll rep = st == std::string::npos ? 1 : atoll(it.c_str() + st + 1);
            for (ll j = 0; j < rep; ++j) {
                if (it[0] == 'z') { ll g = atoll(it.c_str() + 1); w0.append(g, '0'); }
                else { ll d = atoll(it.c_str()); for (ll u = 0; u < d; ++u) w0 += "10"; w0 += "1"; } } }
        ll m = atoll(f[1].c_str()), r = atoll(f[2].c_str()), t = atoll(f[3].c_str());
        for (ll u = 0; u < m; ++u) w0 += "10"; w0 += "1";
        for (ll u = 0; u < r; ++u) w0 += "10"; w0 += "11";
        for (ll u = 0; u < t; ++u) w0 += "11111100"; w0 += "1001";
        q = 1;
    }
    ll SZ = 1 << 22; while ((ll)w0.size() * 3 + 1024 > SZ) SZ *= 2;
    T.assign(SZ, 0);
    ll pos = SZ / 3, lo = pos, hi = pos;
    for (size_t i = 0; i < w0.size(); ++i) T[pos + i] = w0[i] - '0';
    pos += w0.size(); hi = pos;
    ll r1 = pos - 1; while (r1 >= lo && !T[r1]) --r1;
    ll h0odd = 0; ll step = 0, nj = 0, h0one = 0, h0zero = 0, i0 = 0, i1 = 0, evp = 0;
    ll hk[3] = {-1, -1, -1}, hX[3] = {-1, -1, -1}, hC[3] = {-1, -1, -1}; ll lastI0 = 0;
    auto grow = [&]() { ll add = T.size(); std::vector<unsigned char> nt(T.size() + 2 * add, 0); memcpy(&nt[add], T.data(), T.size()); T.swap(nt); pos += add; lo += add; hi += add; r1 += add; };
    const int QH = 7, QI = 8;
    while (true) {
        if (pos < 64 || pos >= (ll)T.size() - 64) grow();
        int c = T[pos];
        if ((!LIT || CANON || D0LOG > 0) && q == 1 && c == 0 && pos > r1 && pos - 4 >= lo && T[pos - 1] == 1 && T[pos - 2] == 0 && T[pos - 3] == 0 && T[pos - 4] == 1) {
            ll p = pos - 5, t = 0;
            auto is = [&](ll e, const char *s) { ll L = strlen(s); if (e - L + 1 < lo) return false; for (ll i = 0; i < L; ++i) if (T[e - L + 1 + i] != s[i] - '0') return false; return true; };
            while (is(p, "11111100")) { ++t; p -= 8; }
            if (D0LOG > 0 && T[p] == 1) {   // D0f moment: l 1 (10)^s 101 (10)^y 011 (100)^P 1^L 11 (11111100)^t 1001 B>
                ll a = p, c1 = 0; while (a >= lo && T[a] == 1) { ++c1; --a; }
                ll P = 0; while (a - 2 >= lo && T[a] == 0 && T[a - 1] == 0 && T[a - 2] == 1) { ++P; a -= 3; }
                if (c1 >= 3 && P >= 1 && a - 2 >= lo && T[a] == 1 && T[a - 1] == 1 && T[a - 2] == 0) {
                    a -= 3; ll y = 0; while (a - 1 >= lo && T[a] == 0 && T[a - 1] == 1) { ++y; a -= 2; }
                    if (a - 2 >= lo && T[a] == 1 && T[a - 1] == 0 && T[a - 2] == 1) { a -= 3; ll s2 = 0; while (a - 1 >= lo && T[a] == 0 && T[a - 1] == 1) { ++s2; a -= 2; }
                        --D0LOG; printf("D0 step=%lld t=%lld L=%lld P=%lld y=%lld s=%lld | far: %s\n", step, t, c1 - 2, P, y, s2, view(a - VIEW, a).c_str()); fflush(stdout); } }
            }
            if (is(p, "11")) {
                p -= 2; ll r = 0; while (p - 1 >= lo && T[p] == 0 && T[p - 1] == 1) { ++r; p -= 2; }
                ll mEnd = p;
                // tokens near->far: m, then 1s, then X, then one more (C) for the counter skip
                std::vector<ll> tk, ts; int after = -1;
                while (p >= lo && T[p] == 1) {
                    ll x = 0, pp = p; while (pp - 2 >= lo && T[pp - 1] == 0 && T[pp - 2] == 1) { ++x; pp -= 2; }
                    tk.push_back(x); ts.push_back(pp); p = pp - 1;
                    if (after >= 0) { if (--after < 0) break; continue; }
                    if (tk.size() == 1 && x != 1) break;
                    if (tk.size() >= 2 && x != 1) after = 0;
                }
                ll k = -1; ll X = -1;
                if (tk.size() >= 2 && tk[0] == 1) { size_t i = 1; while (i < tk.size() && tk[i] == 1) ++i; if (i < tk.size()) { k = i - 1; X = tk[i]; } }
                if (CANON) { printf("CANON step=%lld t=%lld r=%lld | %s\n", step, t, r, view(lo, mEnd).c_str()); fflush(stdout); }
                if (!LIT && k >= 0 && X >= 4 && X % 3 == 1) {
                    ll st = ts[k + 1], C = (k + 2 < (ll)tk.size()) ? tk[k + 2] : -1;
                    ll R = nj < (ll)RL.size() ? RL[nj] : RDEF; ++nj;
                    printf("CL %lld step=%lld t=%lld r=%lld K=%lld X=%lld R=%lld h0one=%lld h0zero=%lld odd=%lld i0=%lld i1=%lld | %s\n", nj, step, t, r, k + 1, X, R, h0one, h0zero, h0odd, i0, i1, view(lo, mEnd).c_str());
                    fflush(stdout);
                    if (STOPTOP && nj > 1 && X == 7 && C == 0 && ts[k + 1] - lo >= 0) {   // view '0*2 7 1*K' exactly?
                        std::string v = view(lo, mEnd); if (v.rfind("0*2 7 1*", 0) == 0 && v.find(' ', 8) == std::string::npos) { printf("STOPTOP step=%lld\n", step); break; } }
                    std::string w;
                    bool acc = CNT && C >= 12 && hk[0] == k && hk[1] == k && hX[0] == X && hX[1] == X && hC[0] == C + 3 && hC[1] == C + 6 && h0zero == 0 && i0 == lastI0;
                    hk[1] = hk[0]; hX[1] = hX[0]; hC[1] = hC[0]; hk[0] = k; hX[0] = X; hC[0] = C; lastI0 = i0;
                    if (acc) { ll nc = 6 + C % 3; st = ts[k + 2]; for (ll u = 0; u < nc; ++u) w += "10"; w += "1";
                        printf("  CNT C=%lld -> %lld\n", C, nc); hk[0] = -1; }
                    for (ll u = 0; u < k + 2; ++u) w += "101";
                    for (ll u = 0; u < 3 * R + 2; ++u) w += "10"; w += "11";
                    for (ll u = 0; u < t; ++u) w += "11111100"; w += "1001";
                    for (ll i = st; i <= hi; ++i) T[i] = 0;
                    while (st + (ll)w.size() + 128 >= (ll)T.size()) { ll o = pos; grow(); st += pos - o; }
                    for (size_t i = 0; i < w.size(); ++i) T[st + i] = w[i] - '0';
                    pos = st + w.size(); hi = pos; r1 = pos - 1; q = 1;
                    h0one = h0zero = i0 = i1 = h0odd = 0; lastI0 = 0;
                    if (MAXJ >= 0 && nj >= MAXJ) { printf("MAXJ step=%lld\n", step); break; }
                    continue;
                }
            }
        }
        // H0 with left 1 and T[pos+2] = 1 (the cell right of the E cell): h003 and M8 resynchronise bit-for-bit after 6 steps.
        // Anything else is an "odd" event and is logged.
        if (q == QH && c == 0 && T[pos - 1] && !T[pos + 2]) { ++h0odd; if (evp < EV) { ++evp; printf("H0ODD step=%lld right=%d%d%d | %s [H] %s\n", step, T[pos+1], T[pos+2], T[pos+3], view(pos - VIEW, pos - 1).c_str(), view(pos + 1, pos + 40).c_str()); } }
        if (q == QH && c == 0) { if (T[pos - 1]) ++h0one; else { ++h0zero; if (evp < EV) { ++evp; printf("H0L0 step=%lld | %s\n", step, view(pos - VIEW, pos).c_str()); } } }
        if (q == QI) { if (c == 0) { ++i0; if (evp < EV) { ++evp; printf("I0 step=%lld | ...%s [I0]\n", step, view(pos - VIEW, pos - 1).c_str()); } } else ++i1; }
        if (q == 4 && c == 0 && E0LOG > 0) { --E0LOG; printf("E0 step=%lld jumps=%lld left3=%d%d%d | %s [E0]\n", step, nj, T[pos-3], T[pos-2], T[pos-1], view(pos - VIEW, pos - 1).c_str()); }
        int i = 2 * q + c;
        if (!def[i]) {
            ll ones = 0; for (ll j = lo; j <= hi; ++j) ones += T[j];
            printf("HALT %c%d step=%lld ones=%lld jumps=%lld h0one=%lld h0zero=%lld odd=%lld i0=%lld i1=%lld\n  tape: %s\n", 'A' + q, c, step, ones, nj, h0one, h0zero, h0odd, i0, i1, view(lo, hi).c_str());
            break;
        }
        T[pos] = W[i];
        if (W[i]) { if (pos > r1) r1 = pos; } else if (pos == r1) { while (r1 >= lo && !T[r1]) --r1; }
        pos += Dm[i]; q = Nx[i]; ++step;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (step >= MAXS) { printf("MAXS step=%lld jumps=%lld state=%c | %s\n", step, nj, 'A' + q, view(lo, hi).c_str()); break; }
    }
    return 0;
}
