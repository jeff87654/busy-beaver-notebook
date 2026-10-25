// ffree: literal run from K_T(ds;a;b) (template T incl. prefix P) reporting K-moments with a FREE prefix:
// at each end event (head in state Q on the blank right of all 1s, template orientation), parse from the right:
// S, accumulator run, then as many "u^k s" runs as possible; the unparsed left part is the prefix P'. Prints
// "K step P'(RLE) n ds(first 10) a b" whenever (P', n) changes, "H step ones" at a halt.
//   ffree MACHINE O Q P u s al be alB beB S N MAXOUT  < "ds a b"
#define main dlscan2_main
#include "../../bb8_list/neighbors/dlscan2.cpp"
#undef main
static std::string rle(const std::string &w) {
    std::string o;
    size_t i = 0;
    while (i < w.size()) { size_t j = i; while (j < w.size() && w[j] == w[i]) ++j; o += w[i]; if (j - i > 1) o += "^" + std::to_string(j - i); o += '.'; i = j; }
    return o.empty() ? "-" : o;
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
    long long SZ = 1LL << 27;
    std::vector<uint8_t> T(SZ, 0);
    long long p = SZ / 2, mn = p, mx = p - 1;
    for (size_t i = 0; i < w.size(); ++i) { long long z = p - (long long)w.size() + (long long)i; T[z] = (uint8_t)(w[i] - '0'); if (w[i] == '1') { if (mn > mx) mn = mx = z; else mx = z; } }
    int q = t.q; long long nout = 0;
    std::string lastkey;
    const std::string &u = t.u, &s = t.s, &S = t.S;
    for (long long st = 0; st < N; ++st) {
        if (p <= 1 || p >= SZ - 2) { printf("TAPE %lld\n", st); return 0; }
        int c = T[p];
        if (m.nx[q][c] < 0) { long long ones = 0; for (long long i = mn; i <= mx; ++i) ones += T[i]; printf("H %lld %lld\n", st, ones); return 0; }
        int wr = m.w[q][c]; T[p] = (uint8_t)wr;
        if (wr) { if (mn > mx) mn = mx = p; else { if (p < mn) mn = p; if (p > mx) mx = p; } }
        p += m.d[q][c]; q = m.nx[q][c];
        if (q != t.q || T[p] != 0) continue;
        while (mx > p && !T[mx]) --mx;
        if (mx > p) continue;
        while (mn < p && !T[mn]) ++mn;
        long long lo = mn < p ? mn : p, len = p - lo;
        if (len > 3000000) continue;
        std::string buf(len, '0');
        for (long long i = 0; i < len; ++i) buf[i] = char('0' + T[lo + i]);
        if (buf.size() < S.size() || buf.compare(buf.size() - S.size(), S.size(), S) != 0) continue;
        long long x = (long long)buf.size() - (long long)S.size();
        std::vector<long long> runs;
        long long ul = u.size(), sl = s.size();
        long long lastgood = x;
        for (;;) {
            long long k = 0;
            while (x - ul >= 0 && buf.compare(x - ul, ul, u) == 0) { x -= ul; ++k; }
            runs.push_back(k);
            lastgood = x;
            if (x - sl < 0 || buf.compare(x - sl, sl, s) != 0) break;
            x -= sl;
            if (runs.size() > 100000) break;
        }
        if (runs.size() < 2) continue;
        // decode: runs[0] = accumulator (alB,beB), runs[1] = a, rest digits; stop at first undecodable digit
        auto dec = [](long long raw, long long al, long long be, long long &v) { if (raw < be || (raw - be) % al) return false; v = (raw - be) / al; return true; };
        long long bv, av;
        if (!dec(runs[0], t.alB, t.beB, bv) || !dec(runs[1], t.al, t.be, av)) continue;
        std::vector<long long> dsv;
        size_t i = 2;
        for (; i < runs.size(); ++i) { long long v; if (!dec(runs[i], t.al, t.be, v)) break; dsv.push_back(v); }
        // prefix = everything left of the last decoded digit (approximate: recompute position)
        long long consumed = (long long)S.size() + runs[0] * ul + sl + runs[1] * ul;
        for (size_t j = 2; j < i; ++j) consumed += sl + runs[j] * ul;
        long long plen = (long long)buf.size() - consumed;
        if (plen < 0) plen = 0;
        std::string pref = buf.substr(0, plen);
        std::reverse(dsv.begin(), dsv.end());
        std::string key = pref + "|" + std::to_string(dsv.size());
        if (key != lastkey) {
            std::string d;
            for (size_t j = 0; j < dsv.size() && j < 10; ++j) { if (j) d += ","; d += std::to_string(dsv[j]); }
            printf("K %lld P=%s n=%zu [%s%s] a=%lld b=%lld\n", st + 1, rle(pref.substr(0, 400)).c_str(), dsv.size(), d.c_str(), dsv.size() > 10 ? ",.." : "", av, bv);
            fflush(stdout);
            lastkey = key;
            if (++nout >= maxout) return 0;
        }
    }
    printf("END %lld\n", N);
    return 0;
}
