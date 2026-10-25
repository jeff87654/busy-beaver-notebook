// rk7: helper for rank7.py. Uses dlscan2's own template parser, so its K-configurations are exactly dlscan2's.
//
//   rk7 trace MACHINE O Q P u s al be alB beB S MAXSTEPS MAXK
//       literal run of MACHINE (mirrored if O == L) from the blank tape; prints every K-configuration
//       "K step ds a b" (ds comma-separated, '-' if empty), at most MAXK of them, then "HALT step ones" or
//       "END step" (step budget or MAXK reached) or "TAPE step" (tape budget exceeded).
//   rk7 probe MACHINE O Q P u s al be alB beB S N
//       reads configurations "ds a b" from stdin (ds comma-separated or '-'); for each prints
//       "K ds a b steps" (next K-configuration), "H steps" (halts) or "T" (no K-configuration within N steps).
// P/S '-' = empty. Q = the template's state letter.
#define main dlscan2_main
#include "../../bb8_list/neighbors/dlscan2.cpp"
#undef main

static std::string dstr(const std::vector<long long> &ds) {
    if (ds.empty()) return "-";
    std::string o;
    for (size_t i = 0; i < ds.size(); ++i) { if (i) o += ","; o += std::to_string(ds[i]); }
    return o;
}

static bool read_tmpl(char **a, TM &m, Tmpl &t) {
    if (!parse(a[0], m)) return false;
    if (a[1][0] == 'L') m = mirrored(m);
    t.q = a[2][0] - 'A'; t.P = strcmp(a[3], "-") ? a[3] : ""; t.u = a[4]; t.s = a[5];
    t.al = atoll(a[6]); t.be = atoll(a[7]); t.alB = atoll(a[8]); t.beB = atoll(a[9]); t.S = strcmp(a[10], "-") ? a[10] : "";
    return true;
}

static int trace_mode(char **a) {
    TM m; Tmpl t;
    if (!read_tmpl(a, m, t)) return 2;
    long long maxs = atoll(a[11]), maxk = atoll(a[12]);
    Prober2 pr;
    const long long SZ = 1LL << 26;                       // 64M cells
    pr.tape.assign(SZ, 0);
    long long p = SZ / 2, mn = p, mx = p - 1, lo_lim = 8, hi_lim = SZ - 8;
    int q = 0; long long nk = 0, work = 0;
    for (long long st = 0; st < maxs; ++st) {
        if (p <= lo_lim || p >= hi_lim) { printf("TAPE %lld\n", st); return 0; }
        int c = pr.tape[p];
        if (m.nx[q][c] < 0) {
            long long ones = 0;
            for (long long i = mn; i <= mx; ++i) ones += pr.tape[i];
            printf("HALT %lld %lld\n", st, ones); return 0;
        }
        int wr = m.w[q][c];
        pr.tape[p] = (uint8_t)wr;
        if (wr) { if (mn > mx) mn = mx = p; else { if (p < mn) mn = p; if (p > mx) mx = p; } }
        p += m.d[q][c]; q = m.nx[q][c];
        if (q != t.q || pr.tape[p] != 0) continue;
        while (mx > p && !pr.tape[mx]) --mx;
        if (mx > p) continue;
        while (mn < p && !pr.tape[mn]) ++mn;
        long long lo = mn < p ? mn : p;
        work += p - lo;
        if (work > 4000000000LL) { printf("END %lld work\n", st + 1); return 0; }
        P2 got;
        if (!pr.parse(t, p, lo, got)) continue;
        printf("K %lld %s %lld %lld\n", st + 1, dstr(got.ds).c_str(), got.a, got.b);
        if (++nk >= maxk) { printf("END %lld maxk\n", st + 1); return 0; }
    }
    printf("END %lld steps\n", maxs);
    return 0;
}

static int probe_mode(char **a) {
    TM m; Tmpl t;
    if (!read_tmpl(a, m, t)) return 2;
    long long N = atoll(a[11]);
    Prober2 pr;
    char ds_s[100000]; long long aa, bb;
    while (scanf("%99999s %lld %lld", ds_s, &aa, &bb) == 3) {
        std::vector<long long> ds;
        if (strcmp(ds_s, "-")) {
            char *x = ds_s;
            while (*x) { ds.push_back(strtoll(x, &x, 10)); if (*x == ',') ++x; }
        }
        P2 r = pr.run_next(m, t, ds, aa, bb, N);
        if (r.kind == 1) printf("H %lld\n", r.steps);
        else if (r.kind == 2) printf("T\n");
        else printf("K %s %lld %lld %lld\n", dstr(r.ds).c_str(), r.a, r.b, r.steps);
        fflush(stdout);
    }
    return 0;
}


// rk7 haltones MACHINE O Q P u s al be alB beB S N  + stdin "ds a b": run from K(ds;a;b) until halt (N steps);
// prints "H steps ones" or "T".
static int haltones_mode(char **a) {
    TM m; Tmpl t;
    if (!read_tmpl(a, m, t)) return 2;
    long long N = atoll(a[11]);
    Prober2 pr;
    char ds_s[100000]; long long aa, bb;
    while (scanf("%99999s %lld %lld", ds_s, &aa, &bb) == 3) {
        std::vector<long long> ds;
        if (strcmp(ds_s, "-")) { char *x = ds_s; while (*x) { ds.push_back(strtoll(x, &x, 10)); if (*x == ',') ++x; } }
        std::string w = pr.word(t, ds, aa, bb);
        long long SZ = 2 * N + 2 * (long long)w.size() + 64;
        if (SZ > (1LL << 28)) SZ = 1LL << 28;
        std::vector<uint8_t> T(SZ, 0);
        long long p = SZ / 2, lo = p - (long long)w.size();
        for (size_t i = 0; i < w.size(); ++i) T[lo + i] = (uint8_t)(w[i] - '0');
        int q = t.q; long long st = 0; bool h = false;
        for (; st < N; ++st) {
            if (p <= 0 || p >= SZ - 1) break;
            int c = T[p];
            if (m.nx[q][c] < 0) { h = true; break; }
            T[p] = (uint8_t)m.w[q][c]; p += m.d[q][c]; q = m.nx[q][c];
        }
        if (h) { long long ones = 0; for (long long i = 0; i < SZ; ++i) ones += T[i]; printf("H %lld %lld\n", st, ones); }
        else printf("T\n");
        fflush(stdout);
    }
    return 0;
}

// rk7 follow MACHINE O Q P u s al be alB beB S N MAXP  + stdin "ds a b": literal run from K(ds;a;b); at each event "head in
// state Q on a blank right of every 1" prints "E step parsed|raw RLE-of-tape" (MAXP events), or "H step ones".
static int follow_mode(char **a) {
    TM m; Tmpl t;
    if (!read_tmpl(a, m, t)) return 2;
    long long N = atoll(a[11]), maxp = atoll(a[12]);
    Prober2 pr;
    char ds_s[100000]; long long aa, bb;
    if (scanf("%99999s %lld %lld", ds_s, &aa, &bb) != 3) return 2;
    std::vector<long long> ds;
    if (strcmp(ds_s, "-")) { char *x = ds_s; while (*x) { ds.push_back(strtoll(x, &x, 10)); if (*x == ',') ++x; } }
    std::string w = pr.word(t, ds, aa, bb);
    long long SZ = 2 * N + 2 * (long long)w.size() + 64;
    if (SZ > (1LL << 28)) SZ = 1LL << 28;
    pr.tape.assign(SZ, 0);
    long long p = SZ / 2, mn = p, mx = p - 1;
    for (size_t i = 0; i < w.size(); ++i) { long long z = p - (long long)w.size() + (long long)i; pr.tape[z] = (uint8_t)(w[i] - '0'); if (w[i] == '1') { if (mn > mx) mn = mx = z; else mx = z; } }
    int q = t.q; long long np = 0;
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
        P2 got;
        std::string o;
        if (pr.parse(t, p, mn < p ? mn : p, got)) o = "K " + dstr(got.ds) + " " + std::to_string(got.a) + " " + std::to_string(got.b);
        else {
            long long i = mn;
            while (i < p && o.size() < 400) { long long j = i; while (j < p && pr.tape[j] == pr.tape[i]) ++j;
                long long n = j - i; o += char('0' + pr.tape[i]); if (n > 1) o += "^" + std::to_string(n); o += ' '; i = j; }
            if (i < p) o += "...";
        }
        printf("E %lld %s\n", st + 1, o.c_str());
        if (++np >= maxp) return 0;
    }
    printf("T\n");
    return 0;
}

int main(int argc, char **argv) {
    if (argc == 15 && !strcmp(argv[1], "follow")) return follow_mode(argv + 2);
    if (argc == 14 && !strcmp(argv[1], "haltones")) return haltones_mode(argv + 2);
    if (argc == 15 && !strcmp(argv[1], "trace")) return trace_mode(argv + 2);
    if (argc == 14 && !strcmp(argv[1], "probe")) return probe_mode(argv + 2);
    fprintf(stderr, "usage: rk7 trace M O Q P u s al be alB beB S MAXSTEPS MAXK | rk7 probe M O Q P u s al be alB beB S N\n");
    return 2;
}
