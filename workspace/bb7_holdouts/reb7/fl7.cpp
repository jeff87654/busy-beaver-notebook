// fl7: literal run from a constructed K(ds;a;b) (dlscan2 template semantics, as rk7), reporting K-configurations.
//   fl7 MACHINE O Q P u s al be alB beB S MAXSTEPS MAXOUT  < "ds a b"
// prints "K step n ds(first 12) a b" whenever the list length n changes (and the first K), "H step ones" at a halt,
// "END step" / "TAPE step" otherwise. Tape is a growable deque-like buffer (both directions).
#define main dlscan2_main
#include "../../bb8_list/neighbors/dlscan2.cpp"
#undef main
#include <deque>
static std::string dstr(const std::vector<long long> &ds, size_t mx) {
    if (ds.empty()) return "-";
    std::string o;
    for (size_t i = 0; i < ds.size() && i < mx; ++i) { if (i) o += ","; o += std::to_string(ds[i]); }
    if (ds.size() > mx) o += ",..";
    return o;
}
int main(int argc, char **argv) {
    if (argc != 14) { fprintf(stderr, "usage\n"); return 2; }
    char **a = argv + 1;
    TM m; Tmpl t;
    if (!parse(a[0], m)) return 2;
    if (a[1][0] == 'L') m = mirrored(m);
    t.q = a[2][0] - 'A'; t.P = strcmp(a[3], "-") ? a[3] : ""; t.u = a[4]; t.s = a[5];
    t.al = atoll(a[6]); t.be = atoll(a[7]); t.alB = atoll(a[8]); t.beB = atoll(a[9]); t.S = strcmp(a[10], "-") ? a[10] : "";
    long long N = atoll(a[11]), maxout = atoll(a[12]);
    static char ds_s[1000000]; long long aa, bb;
    if (scanf("%999999s %lld %lld", ds_s, &aa, &bb) != 3) return 2;
    std::vector<long long> ds;
    if (strcmp(ds_s, "-")) { char *x = ds_s; while (*x) { ds.push_back(strtoll(x, &x, 10)); if (*x == ',') ++x; } }
    Prober2 pr;
    std::string w = pr.word(t, ds, aa, bb);
    long long SZ = (1LL << 27);
    pr.tape.assign(SZ, 0);
    long long p = SZ / 2, mn = p, mx = p - 1;
    for (size_t i = 0; i < w.size(); ++i) { long long z = p - (long long)w.size() + (long long)i; pr.tape[z] = (uint8_t)(w[i] - '0'); if (w[i] == '1') { if (mn > mx) mn = mx = z; else mx = z; } }
    int q = t.q; long long nout = 0, lastn = -1, work = 0;
    for (long long st = 0; st < N; ++st) {
        if (p <= 1 || p >= SZ - 2) { printf("TAPE %lld\n", st); return 0; }
        int c = pr.tape[p];
        if (m.nx[q][c] < 0) { long long ones = 0; for (long long i = mn; i <= mx; ++i) ones += pr.tape[i]; printf("H %lld %lld\n", st, ones); return 0; }
        int wr = m.w[q][c]; pr.tape[p] = (uint8_t)wr;
        if (wr) { if (mn > mx) mn = mx = p; else { if (p < mn) mn = p; if (p > mx) mx = p; } }
        p += m.d[q][c]; q = m.nx[q][c];
        if (q != t.q || pr.tape[p] != 0) continue;
        while (mx > p && !pr.tape[mx]) --mx;
        if (mx > p) continue;
        while (mn < p && !pr.tape[mn]) ++mn;
        long long lo = mn < p ? mn : p;
        work += p - lo;
        if (work > 20000000000LL) { printf("END %lld work\n", st + 1); return 0; }
        P2 got;
        if (!pr.parse(t, p, lo, got)) continue;
        if ((long long)got.ds.size() != lastn) {
            printf("K %lld %zu %s %lld %lld\n", st + 1, got.ds.size(), dstr(got.ds, 12).c_str(), got.a, got.b);
            fflush(stdout);
            lastn = got.ds.size();
            if (++nout >= maxout) { printf("END %lld maxout\n", st + 1); return 0; }
        }
    }
    printf("END %lld steps\n", N);
    return 0;
}
