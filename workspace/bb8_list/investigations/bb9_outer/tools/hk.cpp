// hk.cpp: literal slot-usage tracer (find "hook" transitions used only at rare moments).
//   hk MACHINE STEPS [RARE] < "SPEC"   SPEC = symsim-style tape: tokens like 1^2 011^40 01^18 1 0 G>  (head = the cell right of
//   the token before 'Q>', i.e. the head is on the first cell after the last token, state Q), or "blank" (start A on blank tape).
// Prints per slot: count, first step, last step; and for slots with count <= RARE the first RARE uses with step, head offset from
// the leftmost nonzero cell and a run-length-compressed tape.
#include <bits/stdc++.h>
using namespace std; typedef long long ll;
static string comp(const string &x) {
    string o; size_t i = 0, n = x.size();
    while (i < n) {
        int bp = 0; size_t bc = 0;
        for (int p = 1; p <= 12 && i + 4 * p <= n; ++p) { size_t r = 1; while (i + (r + 1) * p <= n && x.compare(i + r * p, p, x, i, p) == 0) ++r; if (r >= 4 && r * p > bc) { bc = r * p; bp = p; } }
        if (bp) { o += "(" + x.substr(i, bp) + ")^" + to_string(bc / bp); i += bc; } else o += x[i++];
    }
    return o;
}
int main(int argc, char **argv) {
    string m = argv[1]; ll steps = atoll(argv[2]); int RARE = argc > 3 ? atoi(argv[3]) : 20;
    int ns = (m.size() + 1) / 7; int W[16][2], D[16][2], N[16][2];
    for (int q = 0; q < ns; ++q) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * q + 3 * c; if (x[0] == '-' || x[2] == 'Z') N[q][c] = -1; else { W[q][c] = x[0] - '0'; D[q][c] = x[1] == 'R' ? 1 : -1; N[q][c] = x[2] - 'A'; } }
    string line, all; while (getline(cin, line)) all += line + " ";
    istringstream is(all); string tok; string cells; int q = 0; ll head = 0;
    vector<string> toks; while (is >> tok) toks.push_back(tok);
    if (toks.size() == 1 && toks[0] == "blank") { cells = "0"; head = 0; q = 0; }
    else for (auto &t : toks) {
        if (t.size() >= 2 && t.back() == '>') { q = t[0] - 'A'; head = cells.size(); cells += "0"; continue; }
        size_t c = t.find('^'); string w = t.substr(0, c); ll r = c == string::npos ? 1 : atoll(t.c_str() + c + 1);
        for (ll i = 0; i < r; ++i) cells += w;
    }
    const ll SZ = 1LL << 26; vector<unsigned char> T(SZ, 0); ll off = SZ / 2; for (size_t i = 0; i < cells.size(); ++i) T[off + i] = cells[i] - '0';
    ll pos = off + head, lo = off, hi = off + (ll)cells.size() - 1;
    ll cnt[16][2] = {}, fst[16][2], lst[16][2]; for (auto &a : fst) a[0] = a[1] = -1;
    vector<string> ev[16][2];
    ll s = 0;
    for (; s < steps; ++s) {
        int c = T[pos];
        if (N[q][c] < 0) { printf("HALT step %lld state %c sym %d\n", s, 'A' + q, c); break; }
        if (cnt[q][c] < RARE) {
            ll a = lo; while (a < hi && !T[a]) ++a; ll b = hi; while (b > a && !T[b]) --b;
            string x; ll A = min(a, pos), Bb = max(b, pos);
            for (ll i = A; i <= Bb; ++i) x += (i == pos ? (T[i] ? 'I' : 'O') : char('0' + T[i]));
            char buf[200]; snprintf(buf, sizeof buf, "  step %lld off=%lld (from left 1) width=%lld : ", s, pos - a, b - a + 1);
            ev[q][c].push_back(string(buf) + comp(x).substr(0, 400));
        }
        if (fst[q][c] < 0) fst[q][c] = s; lst[q][c] = s; ++cnt[q][c];
        T[pos] = W[q][c]; pos += D[q][c]; q = N[q][c];
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (pos <= 1 || pos >= SZ - 2) { printf("TAPE OVERFLOW %lld\n", s); break; }
    }
    printf("steps %lld\n", s);
    for (int a = 0; a < ns; ++a) for (int c = 0; c < 2; ++c) {
        printf("%c%d count %lld first %lld last %lld\n", 'A' + a, c, cnt[a][c], fst[a][c], lst[a][c]);
        if (cnt[a][c] <= RARE) for (auto &e : ev[a][c]) printf("%s\n", e.c_str());
    }
}
