// batt231_fast: exact FSA-trace-accelerated version of batt231.cpp.
// Since any child that has not failed prior to step s on config i has emitted the exact same (write, move) sequence
// as the base machine on config i, its tape and head position at step s are 100% identical to the base machine's.
// Recording the base's read symbol sym[i][s] alongside (w, d) eliminates all per-child tape allocations and copies.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <functional>
#include <windows.h>
typedef long long ll;
struct Tr { signed char w, d, nx; };
static void parse(const char *m, Tr *T) { int ns = (strlen(m) + 1) / 7;
    for (int q = 0; q < ns; ++q) for (int b = 0; b < 2; ++b) { const char *p = m + 7 * q + 3 * b;
        if (p[0] == 'z') T[2 * q + b] = {0, 0, -2}; else if (p[0] == '-' || p[2] - 'A' >= ns) T[2 * q + b] = {0, 0, -1};
        else T[2 * q + b] = {(signed char)(p[0] - '0'), (signed char)(p[1] == 'R' ? 1 : -1), (signed char)(p[2] - 'A')}; } }
static bool kparse(const std::vector<unsigned char> &t, ll pos, ll lo, ll hi, ll &a, ll &b, std::vector<ll> &ds) {
    if (t[pos] != 0) return false; for (ll i = lo; i < pos; ++i) if (t[i]) return false;
    ll r1 = hi; while (r1 > pos && !t[r1]) --r1; ll i = pos + 1, ones = 0; while (i <= r1 && t[i]) { ++ones; ++i; }
    if (ones % 2 == 0) return false; b = (ones - 1) / 2; if (i + 1 > r1 || t[i] || t[i + 1]) return false; i += 2;
    std::vector<ll> f;
    while (true) { ll o = 0; while (i <= r1 && t[i]) { ++o; ++i; } if (i > r1) { if (o == 1) break; return false; }
        if (o % 2 || t[i] || i + 1 > r1 || t[i + 1]) return false; f.push_back(o / 2); i += 2; }
    if (f.empty()) return false; a = f[0]; ds.assign(f.begin() + 1, f.end()); return true;
}
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    Tr base[32]; parse(argv[1], base); ll CAP = (ll)atof(argv[2]);
    bool pass_only = (argc > 5 && strcmp(argv[5], "--pass-only") == 0);
    std::vector<std::vector<unsigned char>> tr;
    { FILE *f = fopen(argv[3], "r"); char bf[4096];
      while (fgets(bf, sizeof bf, f)) { if (bf[0] == '#' || bf[0] < ' ') continue; ll a, b; char ds[4000] = ""; sscanf(bf, "%lld;%lld;%3999s", &a, &b, ds);
        std::vector<ll> d; char *x = ds; while (*x) { ll v = strtoll(x, &x, 10); ll rep = 1; if (*x == '*') { ++x; rep = strtoll(x, &x, 10); } for (ll i = 0; i < rep; ++i) d.push_back(v); if (*x == ',') ++x; else break; }
        std::vector<unsigned char> w; w.push_back(0); for (ll i = 0; i < 2 * b + 1; ++i) w.push_back(1); w.push_back(0); w.push_back(0);
        for (ll i = 0; i < 2 * a; ++i) w.push_back(1); w.push_back(0); w.push_back(0);
        for (ll v : d) { for (ll i = 0; i < 2 * v; ++i) w.push_back(1); w.push_back(0); w.push_back(0); } w.push_back(1);
        ll mz = 0; while (mz < (ll)d.size() && d[mz] == 0) ++mz;
        ll SZ = 1 << 16; while (SZ < 8 * (ll)w.size()) SZ <<= 1; std::vector<unsigned char> t(SZ, 0); ll off = SZ / 4;
        for (size_t i = 0; i < w.size(); ++i) t[off + i] = w[i]; ll pos = off, lo = off, hi = off + w.size() - 1; int q = 4;
        std::vector<unsigned char> trc;
        for (ll s = 0; s < CAP; ++s) {
            if (pos < 2 || pos >= (ll)t.size() - 2) { size_t add = t.size(); std::vector<unsigned char> n(3 * add, 0); memcpy(&n[add], t.data(), add); t.swap(n); pos += add; lo += add; hi += add; }
            if (s > 0 && q == 4) { ll A, B; std::vector<ll> D;
                if (kparse(t, pos, lo, hi, A, B, D)) {
                    if (a > 0 && A == 0) break;
                    if (a == 0) { bool z = (ll)D.size() > mz; for (ll k = 0; k <= mz && k < (ll)D.size(); ++k) if (D[k]) z = false; if (z) break; } } }
            unsigned char sym = t[pos];
            Tr &x = base[2 * q + sym]; if (x.nx < 0) break;
            trc.push_back(x.w | ((x.d > 0) << 1) | (sym << 2)); t[pos] = x.w; pos += x.d; if (pos < lo) lo = pos; if (pos > hi) hi = pos; q = x.nx; }
        tr.push_back(trc); }
      fclose(f); }
    size_t tot = 0; for (auto &x : tr) tot += x.size(); fprintf(stderr, "battery %zu configs, %zu base steps\n", tr.size(), tot);
    FILE *fin = fopen(argv[4], "r"); char line[512];
    std::function<void(Tr *, int, const std::string &)> rec = [&](Tr *T, int ns, const std::string &name) {
        const Tr &bq = base[2 * 4 + 0]; std::string qs, ff; int ncand = 0;
        for (int X = 0; X < ns; ++X) {
            const Tr &x0 = T[2 * X]; if (x0.nx < 0 || x0.w != bq.w || x0.d != bq.d) continue; ++ncand;
            bool ok = true;
            for (size_t i = 0; i < tr.size() && ok; ++i) {
                const unsigned char *trp = tr[i].data();
                size_t nsteps = tr[i].size();
                int q = X;
                for (size_t s = 0; s < nsteps; ++s) {
                    unsigned char entry = trp[s];
                    int sym = entry >> 2;
                    int bt = entry & 3;
                    Tr &x = T[2 * q + sym]; const char *kind = 0;
                    if (x.nx == -2) {
                        Tr save = x;
                        for (int nx = 0; nx < ns; ++nx) { x = {(signed char)(bt & 1), (signed char)((bt >> 1) ? 1 : -1), (signed char)nx};
                            std::string nm = name; size_t p = 7 * q + 3 * sym; nm[p] = '0' + (bt & 1); nm[p + 1] = (bt >> 1) ? 'R' : 'L'; nm[p + 2] = 'A' + nx;
                            rec(T, ns, nm); }
                        x = save; return; }
                    if (x.nx == -1) kind = "HT"; else if ((x.w | ((x.d > 0) << 1)) != bt) kind = "WD";
                    if (kind) { if (!pass_only && ff.empty()) { char b[96]; snprintf(b, sizeof b, "%zu %zu %s %c%d q0=%c", i, s, kind, 'A' + q, sym, 'A' + X); ff = b; } ok = false; break; }
                    q = x.nx; } }
            if (ok) qs += char('A' + X);
        }
        if (!qs.empty()) printf("PASS %s qset=%s\n", name.c_str(), qs.c_str());
        else if (!pass_only) {
            if (!ncand) printf("FAIL - - NOK - %s\n", name.c_str());
            else printf("FAIL %s %s\n", ff.c_str(), name.c_str());
        }
    };
    while (fscanf(fin, "%511s", line) == 1) {
        Tr T[32]; parse(line, T); rec(T, (strlen(line) + 1) / 7, std::string(line));
    }
    fflush(stdout);
    return 0;
}
