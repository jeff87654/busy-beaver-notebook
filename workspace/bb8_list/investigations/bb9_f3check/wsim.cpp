// wsim.cpp  (bb9_f3check, independent checker, 2026-10-19)
// Literal TM simulator on a byte tape, with ONE kind of jump: the record's clearing rule R0.3,
//   Kt(ctx, X, 1^k; 1; r; t)  ->  Kt(ctx, 1^(k+1); 1; 3R+2; t)      X = 1 mod 3, X >= 4, k >= 0,
// applied at a canonical moment  ... D(d_n)..D(d_1) D(m) (10)^r 11 (11111100)^t 1001 [B on 0], blank to the right,
// with m = 1, d_1..d_k = 1, d_(k+1) = X.  R is taken from --R list (in order of clears), then --Rdef.
// Everything else is simulated literally.  Logs: every jump, every read of 0 in state H with the two cells to the left
// ("H0L" lines for left cell 0 always, left cell 1 counted per segment), every non-CL canonical moment (optional),
// halt with ones count and the halting token.
//   wsim MACHINE [--R a,b,c] [--Rdef N] [--maxs N] [--canon] [--view N] [--stopj N] [--dump]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <windows.h>
typedef long long ll;
static std::vector<unsigned char> T;
static ll P0;   // offset
static int VIEW = 300;
static std::string toks(ll a, ll b) {   // D-token view of [a,b], far->near, RLE
    while (a <= b && !T[a]) ++a;
    std::vector<std::string> v; ll i = a;
    while (i <= b) {
        if (!T[i]) { ll j = i; while (j <= b && !T[j]) ++j; v.push_back("z" + std::to_string(j - i)); i = j; continue; }
        ll x = 0, j = i; while (j + 2 <= b && T[j + 1] == 0 && T[j + 2] == 1) { j += 2; ++x; }
        v.push_back(std::to_string(x)); i = j + 1;
    }
    std::string o; size_t k = 0;
    while (k < v.size()) { size_t l = k; while (l < v.size() && v[l] == v[k]) ++l; if (!o.empty()) o += ' '; o += v[k]; if (l - k > 1) o += "*" + std::to_string(l - k); k = l; }
    if ((int)o.size() > VIEW) o = o.substr(0, VIEW / 3) + " ... " + o.substr(o.size() - 2 * VIEW / 3);
    return o;
}
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    std::string M = argv[1]; int n = (M.size() + 1) / 7;
    int W[32], D[32], N[32]; bool def[32];
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { const char *x = M.c_str() + 7 * s + 3 * c; int i = 2 * s + c;
        if (x[0] == '-') { def[i] = false; W[i] = D[i] = N[i] = 0; } else { def[i] = true; W[i] = x[0] - '0'; D[i] = x[1] == 'R' ? 1 : -1; N[i] = x[2] - 'A'; } }
    std::vector<ll> RL; ll RDEF = 366; ll MAXS = (ll)4e11; std::string KT; bool canon = false; bool D0LOG = false; bool CNT = false; ll hk[2] = {-1,-1}, hX[2] = {-1,-1}, hC[2] = {-1,-1}, hz[1] = {0}; ll STOPJ = -1; int HST = 7;
    for (int i = 2; i < argc; ++i) { std::string a = argv[i];
        if (a == "--R") { std::string v = argv[++i]; size_t p = 0; while (p < v.size()) { size_t q = v.find(',', p); if (q == std::string::npos) q = v.size(); RL.push_back(atoll(v.substr(p, q - p).c_str())); p = q + 1; } }
        else if (a == "--Rdef") RDEF = atoll(argv[++i]); else if (a == "--maxs") MAXS = (ll)atof(argv[++i]);
        else if (a == "--canon") canon = true; else if (a == "--d0") D0LOG = true; else if (a == "--cnt") CNT = true; else if (a == "--view") VIEW = atoi(argv[++i]); else if (a == "--stopj") STOPJ = atoll(argv[++i]);
        else if (a == "--hstate") HST = argv[++i][0] - 'A'; else if (a == "--kt") KT = argv[++i];
        else { fprintf(stderr, "bad %s\n", a.c_str()); return 2; } }
    ll SZ = 1 << 24; T.assign(SZ, 0); ll pos = SZ / 2, lo = pos, hi = pos, r1 = pos - 1 /* rightmost 1 (or < lo) */; int q = 0;
    ll step = 0, seg = 0, nj = 0, h0one = 0, h0zero = 0, ncanon = 0, ntokparse = 0;
    const int QB = 1;
    if (!KT.empty()) {
        std::vector<std::string> f; size_t p0 = 0; while (true) { size_t p1 = KT.find(';', p0); f.push_back(KT.substr(p0, p1 == std::string::npos ? std::string::npos : p1 - p0)); if (p1 == std::string::npos) break; p0 = p1 + 1; }
        std::string w;
        size_t a0 = 0; while (!f[0].empty()) { size_t b0 = f[0].find(',', a0); std::string it = f[0].substr(a0, b0 == std::string::npos ? std::string::npos : b0 - a0);
            size_t st = it.find('*'); ll rep = st == std::string::npos ? 1 : atoll(it.c_str() + st + 1);
            if (it[0] == 'z') { ll g = atoll(it.c_str() + 1); for (ll j = 0; j < rep * g; ++j) w += "0"; }
            else { ll d = atoll(it.c_str()); for (ll j = 0; j < rep; ++j) { for (ll i = 0; i < d; ++i) w += "10"; w += "1"; } } if (b0 == std::string::npos) break; a0 = b0 + 1; }
        ll mm = atoll(f[1].c_str()), rr = atoll(f[2].c_str()), tt = atoll(f[3].c_str());
        for (ll i = 0; i < mm; ++i) w += "10"; w += "1"; for (ll i = 0; i < rr; ++i) w += "10"; w += "11"; for (ll i = 0; i < tt; ++i) w += "11111100"; w += "1001";
        while ((ll)w.size() * 2 + 64 >= (ll)T.size()) { T.assign(T.size() * 2, 0); }
        pos = T.size() / 4; lo = pos; for (size_t i = 0; i < w.size(); ++i) T[pos + i] = w[i] - '0'; pos += w.size(); hi = pos; r1 = pos - 1; q = QB;
        printf("START Kt len=%zu\n", w.size());
    }
    auto grow = [&]() { ll add = T.size(); std::vector<unsigned char> nt(T.size() + 2 * add, 0); memcpy(&nt[add], T.data(), T.size()); T.swap(nt); pos += add; lo += add; hi += add; r1 += add; };
    while (true) {
        if (pos < 16 || pos >= (ll)T.size() - 16) grow();
        int c = T[pos];
        if (q == QB && c == 0 && pos > r1 && pos - 4 >= lo && T[pos-1] == 1 && T[pos-2] == 0 && T[pos-3] == 0 && T[pos-4] == 1) {
            // parse backwards
            ll p = pos - 5, tt = 0;
            auto is = [&](ll e, const char *s) { ll L = strlen(s); if (e - L + 1 < lo) return false; for (ll i = 0; i < L; ++i) if (T[e - L + 1 + i] != s[i] - '0') return false; return true; };
            while (is(p, "11111100")) { ++tt; p -= 8; }
            if (D0LOG && T[p] == 1) {   // D0f moment: ... 1 (10)^s 101 (10)^y 011 (100)^P 1^L 11 (blocks) 1001 B>
                ll a = p, c1 = 0; while (a >= lo && T[a] == 1) { ++c1; --a; }
                ll L = c1 - 2, P = 0; while (a - 2 >= lo && T[a] == 0 && T[a - 1] == 0 && T[a - 2] == 1) { ++P; a -= 3; }
                if (L >= 1 && P >= 1 && a - 2 >= lo && T[a] == 1 && T[a - 1] == 1 && T[a - 2] == 0) {
                    a -= 3; ll y = 0; while (a - 1 >= lo && T[a] == 0 && T[a - 1] == 1) { ++y; a -= 2; }
                    if (a - 2 >= lo && T[a] == 1 && T[a - 1] == 0 && T[a - 2] == 1) { a -= 3; ll s2 = 0; while (a - 1 >= lo && T[a] == 0 && T[a - 1] == 1) { ++s2; a -= 2; }
                        printf("D0 step=%lld jumps=%lld t=%lld L=%lld P=%lld y=%lld s=%lld\n", step, nj, tt, L, P, y, s2); fflush(stdout); }
                }
            }
            if (is(p, "11")) {
                p -= 2; ll r = 0; while (p - 1 >= lo && T[p] == 0 && T[p - 1] == 1) { ++r; p -= 2; }
                // tokens: p is the last cell of D(m)
                ll mEnd = p;
                std::vector<ll> tk, ts;
                ll want = canon ? 4000000 : 1;   // lazy: tokens needed for the CL decision only
                while (p >= lo && T[p] == 1 && (ll)tk.size() < want) { ll x = 0, pp = p; while (pp - 2 >= lo && T[pp - 1] == 0 && T[pp - 2] == 1) { ++x; pp -= 2; } tk.push_back(x); ts.push_back(pp); p = pp - 1;
                    if (!canon) { if (tk.size() == 1) want = (x == 1) ? 4000000 : 1; else if (x != 1) want = tk.size() + 1; } ++ntokparse; }
                ++ncanon;
                bool cl = false; ll k = 0;
                if (tk.size() >= 2 && tk[0] == 1) { k = 0; while (k + 1 < (ll)tk.size() && tk[k + 1] == 1) ++k; // d_1..d_k = 1
                    if (k + 1 < (ll)tk.size() && tk[k + 1] % 3 == 1 && tk[k + 1] >= 4) cl = true; }
                if (canon && !cl) { printf("CANON step=%lld t=%lld r=%lld m=%lld ntok=%zu | %s\n", step, tt, r, tk.empty() ? -1 : tk[0], tk.size(), toks(lo, pos - 1).c_str()); fflush(stdout); }
                if (cl) {
                    ll X = tk[k + 1], st = ts[k + 1];
                    ll C = (k + 2 < (ll)tk.size()) ? tk[k + 2] : -1;
                    ll R = nj < (ll)RL.size() ? RL[nj] : RDEF;
                    ++nj;
                    printf("J%lld CL step=%lld seg=%lld t=%lld r_in=%lld k=%lld X=%lld C=%lld R=%lld H0one=%lld H0zero=%lld | %s\n", nj, step, seg, tt, r, k, X, C, R, h0one, h0zero, toks(lo, mEnd).c_str()); fflush(stdout);
                    std::string w;
                    // counter acceleration (R4.c): after 2 literal rounds with the same (k, X) and C dropping by 3, and no H0-left-0 event,
                    // replace C by 6 + C mod 3 (the remaining rounds are literal).  Only with --cnt.
                    bool acc = CNT && C >= 12 && hk[0] == k && hk[1] == k && hX[0] == X && hX[1] == X && hC[0] == C + 3 && hC[1] == C + 6 && h0zero == 0 && hz[0] == 0;
                    hk[1] = hk[0]; hX[1] = hX[0]; hC[1] = hC[0]; hk[0] = k; hX[0] = X; hC[0] = C; hz[0] = h0zero;
                    if (acc) { ll nc = 6 + C % 3; st = ts[k + 2]; for (ll i = 0; i < nc; ++i) w += "10"; w += "1";
                        printf("   CNT C=%lld -> %lld (%lld rounds skipped)\n", C, nc, (C - nc) / 3); hC[0] = nc; hk[0] = -1; }
                    for (ll i = 0; i <= k + 1; ++i) w += "101";   // (k+1) zero digits + m = D1
                    for (ll i = 0; i < 3 * R + 2; ++i) w += "10"; w += "11"; for (ll i = 0; i < tt; ++i) w += "11111100"; w += "1001";
                    for (ll i = st; i <= hi; ++i) T[i] = 0;
                    while (st + (ll)w.size() + 32 >= (ll)T.size()) { ll o = pos; grow(); st += pos - o; }
                    for (size_t i = 0; i < w.size(); ++i) T[st + i] = w[i] - '0';
                    pos = st + w.size(); hi = pos; r1 = pos - 1; q = QB; seg = 0; h0one = 0; h0zero = 0;
                    if (STOPJ >= 0 && nj >= STOPJ) { printf("STOPJ\n"); break; }
                    continue;
                }
            }
        }
        if (q == HST && c == 0) { if (T[pos - 1]) ++h0one; else { ++h0zero; printf("H0L0 step=%lld seg=%lld jumps=%lld left2=%d%d right=%d%d | %s\n", step, seg, nj, T[pos-2], T[pos-1], T[pos+1], T[pos+2], toks(lo, pos).c_str()); fflush(stdout); } }
        int i = 2 * q + c;
        if (!def[i]) {
            ll ones = 0; for (ll j = lo; j <= hi; ++j) ones += T[j];
            // halting token: maximal (10)^d 1 ending at pos
            ll d = 0, pp = pos; while (pp - 2 >= lo && T[pp - 1] == 0 && T[pp - 2] == 1) { ++d; pp -= 2; }
            printf("HALT %c%d step=%lld seg=%lld ones=%lld jumps=%lld H0one=%lld H0zero=%lld haltTokD=%lld leftcell=%d right=%d%d\n", 'A' + q, c, step, seg, ones, nj, h0one, h0zero, d, T[pos-1], T[pos+1], T[pos+2]);
            printf("  tape: %s\n", toks(lo, hi).c_str());
            break;
        }
        T[pos] = W[i];
        if (W[i]) { if (pos > r1) r1 = pos; } else if (pos == r1) { while (r1 >= lo && !T[r1]) --r1; }
        pos += D[i]; q = N[i]; ++step; ++seg;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (step >= MAXS) { printf("MAXS step=%lld jumps=%lld state=%c | %s\n", step, nj, 'A' + q, toks(lo, hi).c_str()); break; }
    }
    return 0;
}
