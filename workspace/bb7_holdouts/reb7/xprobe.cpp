// xprobe: start from K_T1(ds;a;b) (template T1) and run the ORIGINAL machine until the first K-moment of template
// T2 (possibly the other orientation), a halt, or N steps.
//   xprobe MACHINE  O1 Q1 P1 u1 s1 al1 be1 alB1 beB1 S1  O2 Q2 P2 u2 s2 al2 be2 alB2 beB2 S2  N  < lines "ds a b"
// Output per input line: "K ds a b steps" (T2 coordinates) | "H steps" | "T".
// Orientation: a template with O = R reads the tape left->right with the head at the right end; O = L is the mirror
// image (dlscan2 mirrors the machine). We keep one tape in original orientation and test T2 on the appropriate view.
#define main dlscan2_main
#include "../../bb8_list/neighbors/dlscan2.cpp"
#undef main
static std::string dstr(const std::vector<long long> &ds) {
    if (ds.empty()) return "-";
    std::string o;
    for (size_t i = 0; i < ds.size(); ++i) { if (i) o += ","; o += std::to_string(ds[i]); }
    return o;
}
static void rdT(char **a, Tmpl &t, bool &mir) {
    mir = a[0][0] == 'L';
    t.q = a[1][0] - 'A'; t.P = strcmp(a[2], "-") ? a[2] : ""; t.u = a[3]; t.s = a[4];
    t.al = atoll(a[5]); t.be = atoll(a[6]); t.alB = atoll(a[7]); t.beB = atoll(a[8]); t.S = strcmp(a[9], "-") ? a[9] : "";
}
int main(int argc, char **argv) {
    if (argc != 23) { fprintf(stderr, "usage\n"); return 2; }
    TM m;
    if (!parse(argv[1], m)) return 2;
    Tmpl t1, t2; bool mir1, mir2;
    rdT(argv + 2, t1, mir1);
    rdT(argv + 12, t2, mir2);
    long long N = atoll(argv[22]);
    static char ds_s[1000000]; long long aa, bb;
    Prober2 pr;
    while (scanf("%999999s %lld %lld", ds_s, &aa, &bb) == 3) {
        std::vector<long long> ds;
        if (strcmp(ds_s, "-")) { char *x = ds_s; while (*x) { ds.push_back(strtoll(x, &x, 10)); if (*x == ',') ++x; } }
        std::string w = pr.word(t1, ds, aa, bb);
        long long SZ = 2 * N + 2 * (long long)w.size() + 64;
        if (SZ > (1LL << 28)) SZ = 1LL << 28;
        std::vector<uint8_t> T(SZ, 0);
        long long c0 = SZ / 2;
        // place w so that, in T1's view, the head is right after w; original orientation: if mir1, reverse
        long long p;
        long long mn, mx;
        if (!mir1) { for (size_t i = 0; i < w.size(); ++i) T[c0 - (long long)w.size() + i] = (uint8_t)(w[i] - '0'); p = c0; mn = c0 - (long long)w.size(); mx = c0 - 1; }
        else { for (size_t i = 0; i < w.size(); ++i) T[c0 + (long long)w.size() - i] = (uint8_t)(w[i] - '0'); p = c0; mn = c0 + 1; mx = c0 + (long long)w.size(); }
        while (mn <= mx && !T[mn]) ++mn;
        while (mx >= mn && !T[mx]) --mx;
        int q = t1.q;
        long long st;
        bool done = false;
        std::vector<uint8_t> view;
        for (st = 0; st < N; ++st) {
            if (p <= 2 || p >= SZ - 3) break;
            int c = T[p];
            if (m.nx[q][c] < 0) { printf("H %lld\n", st); done = true; break; }
            int wr = m.w[q][c]; T[p] = (uint8_t)wr;
            if (wr) { if (mn > mx) mn = mx = p; else { if (p < mn) mn = p; if (p > mx) mx = p; } }
            p += m.d[q][c]; q = m.nx[q][c];
            if (q != t2.q || T[p] != 0) continue;
            if (!mir2) {
                while (mx > p && !T[mx]) --mx;
                if (mx > p) continue;
                while (mn < p && !T[mn]) ++mn;
                long long lo = mn < p ? mn : p;
                long long len = p - lo;
                if (len > 2000000) continue;
                pr.tape.assign(T.begin() + lo, T.begin() + p);
                pr.tape.push_back(0);
                P2 got;
                if (pr.parse(t2, len, 0, got)) { printf("K %s %lld %lld %lld\n", dstr(got.ds).c_str(), got.a, got.b, st + 1); done = true; break; }
            } else {
                while (mn < p && !T[mn]) ++mn;
                if (mn < p) continue;
                while (mx > p && !T[mx]) --mx;
                long long hi = mx > p ? mx : p;
                long long len = hi - p;
                if (len > 2000000) continue;
                pr.tape.resize(len + 1);
                for (long long i = 0; i < len; ++i) pr.tape[i] = T[hi - i];
                pr.tape[len] = 0;
                P2 got;
                if (pr.parse(t2, len, 0, got)) { printf("K %s %lld %lld %lld\n", dstr(got.ds).c_str(), got.a, got.b, st + 1); done = true; break; }
            }
        }
        if (!done) printf("T\n");
        fflush(stdout);
    }
    return 0;
}
