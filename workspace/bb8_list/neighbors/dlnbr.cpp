// dlnbr: directed search for digit-list machines among the neighbours of a known one.
//
//   dlnbr PARENT RADIUS OUTPUT PART NPARTS [STEPS=300000] [N=20000]
//
// Enumerates every machine that differs from PARENT in 1..RADIUS transitions (each slot may take any of the 32
// defined values or be undefined) and keeps at least one undefined (halting) transition. Machine number i is
// handled by the run with PART == i % NPARTS, so NPARTS runs cover the neighbourhood exactly once.
// Each machine gets the census of dlscan.cpp (both tape ends) and its probes. For every key whose R1, R2 and R3
// rules fit (the criterion of kfit.py for a digit-list counter) the halting boundary is fitted too and graded
// as dlscan.py does:
//   SAFE (the non-halting argument of the parent applies), NOBOUNDARY (no halting boundary found),
//   CHECK (the rules fit but the argument does not carry over), HALT? (the boundary is within reach).
// The grade of a machine is the safest grade among its keys. Machines that halt within STEPS are skipped.
//
// OUTPUT (TSV): machine, grade, key (O,state,suffix,unit,sep), params m1,c1|m2,c2,b2|m3,c3,a3,b3|mh,ch of that
// key, edits (number of changed transitions); one row per digit-list machine; last line "#summary ...".
#define DLSCAN_NO_MAIN
#include "dlscan.cpp"
#include <chrono>

// Set DLNBR_PROFILE=1 to print where the time went (census, key inference, probes) on stderr.
static double T_CEN = 0, T_KEY = 0, T_FIT = 0;
static double now() {
    return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
}

static long long floordiv(long long a, long long b) {
    long long q = a / b;
    if (a % b != 0 && ((a < 0) != (b < 0))) --q;
    return q;
}

// kfit.lin_fit: fit m b + c on the two smallest b and verify the rest.
static bool lin_fit(const std::vector<std::pair<long long, long long>> &v, long long &m, long long &c) {
    if (v.size() < 2) return false;
    m = floordiv(v[1].second - v[0].second, v[1].first - v[0].first);
    c = v[0].second - m * v[0].first;
    for (auto &x : v) if (x.second != m * x.first + c) return false;
    return true;
}

struct Fit {
    bool r123 = false, h = false;
    long long m1 = 0, c1 = 0, m2 = 0, c2 = 0, b2 = 0, m3 = 0, c3 = 0, a3 = 0, b3 = 0, mh = 0, ch = 0;
    int grade = -1;   // 0 SAFE, 1 NOBOUNDARY, 2 CHECK, 3 HALT?
};
static const char *GRADE[] = {"SAFE", "NOBOUNDARY", "CHECK", "HALT?"};

// kfit.fit (R1, R2, R3, H) and kfit.safety for one key.
static Fit fit(Prober &pr, const TM &m, const Key &key, long long N) {
    Fit f;
    std::vector<std::pair<long long, long long>> v;
    for (int b = 1; b <= 5; ++b) {
        Probe r = pr.run_next(m, key, {2}, 2, b, N);
        if (r.kind != 0 || r.ds.size() != 1 || r.ds[0] != 2 || r.a != 1) return f;
        v.push_back({b, r.b});
    }
    if (!lin_fit(v, f.m1, f.c1)) return f;
    v.clear();
    for (int b = 1; b <= 5; ++b) {
        Probe r = pr.run_next(m, key, {2}, 0, b, N);
        if (r.kind != 0 || r.ds.size() != 1 || r.ds[0] != 1) return f;
        if (b == 1) f.b2 = r.b; else if (r.b != f.b2) return f;
        v.push_back({b, r.a});
    }
    if (!lin_fit(v, f.m2, f.c2)) return f;
    // R3 and the halting boundary
    std::vector<std::pair<long long, long long>> kh, refill;
    bool first = true, consts_ok = true;
    for (int b = 1; b <= 4; ++b) {
        bool have = false, one = true; long long val = 0;
        for (int k = 1; k < 8 * b + 8; ++k) {
            std::vector<int> ds = {1, 2};
            ds.insert(ds.end(), k, 0);
            Probe r = pr.run_next(m, key, ds, 0, b, N);
            if (r.kind == 1) { kh.push_back({b, k}); break; }
            if (r.kind != 0) break;
            if ((long long)r.ds.size() != 2 + k || r.ds[0] != 1 || r.ds[1] != 1) break;
            bool tail = true;
            for (size_t i = 3; i < r.ds.size(); ++i) if (r.ds[i] != 1) tail = false;
            if (!tail) break;
            if (first) { f.a3 = r.a; f.b3 = r.b; first = false; }
            else if (r.a != f.a3 || r.b != f.b3) consts_ok = false;
            long long x = r.ds[2] + k;
            if (!have) { have = true; val = x; } else if (x != val) one = false;
        }
        if (have) { if (!one) consts_ok = false; refill.push_back({b, val}); }
    }
    if (!(consts_ok && refill.size() >= 3 && lin_fit(refill, f.m3, f.c3))) return f;
    f.r123 = true;
    f.h = kh.size() >= 3 && lin_fit(kh, f.mh, f.ch);
    if (!f.h) { f.grade = 1; return f; }
    bool s1 = true, s2 = true, s3 = true, s4 = true;
    for (long long b = 1; b < 200; ++b) {
        if (!(f.m1 * b + f.c1 >= b + 1)) s1 = false;
        if (!(f.m2 * b + f.c2 >= b)) s2 = false;
        if (!(f.m3 * b + f.c3 - (b - 1) >= 2)) s3 = false;
        if (!(f.mh * b + f.ch > b - 1)) s4 = false;
    }
    bool s5 = f.a3 == 1 && f.b3 == 1 && f.b2 == 1;
    f.grade = !s4 ? 3 : (!(s1 && s2 && s3 && s5) ? 2 : 0);
    return f;
}

static const char LET[] = "ABCDEFGH";

static std::string slot_str(int v) {
    if (v == 32) return "---";
    std::string s;
    s += char('0' + v / 16); s += (v / 8 % 2) ? 'R' : 'L'; s += LET[v % 8];
    return s;
}

static std::string machine_str(const int *sl) {
    std::string s;
    for (int q = 0; q < 8; ++q) { if (q) s += '_'; s += slot_str(sl[2 * q]); s += slot_str(sl[2 * q + 1]); }
    return s;
}

struct Search {
    Prober pr; std::ofstream out; long long steps = 0, N = 0, part = 0, nparts = 1;
    long long idx = 0, n = 0, nhalt = 0, ndl = 0, ngrade[4] = {0, 0, 0, 0};

    void handle(const int *sl, int edits) {
        bool undefined = false;
        for (int i = 0; i < 16; ++i) if (sl[i] == 32) undefined = true;
        if (!undefined) return;
        if (idx++ % nparts != part) return;
        std::string s = machine_str(sl);
        TM m; parse(s, m);
        ++n;
        End ends[2];
        double t0 = now();
        long long hs = census(m, steps, ends);
        T_CEN += now() - t0;
        if (hs >= 0) { ++nhalt; return; }
        TM mm = mirrored(m);
        Fit best; std::string bestkey;
        for (int o = 0; o < 2 && best.grade != 0; ++o) {
            t0 = now();
            std::vector<Key> ks = base_keys(ends[o]);
            if (!getenv("DLNBR_NOGENERAL")) for (auto &k : general_keys(ends[o])) ks.push_back(k);
            T_KEY += now() - t0;
            for (auto &k : ks) {
                t0 = now();
                Fit f = fit(pr, o ? mm : m, k, N);
                T_FIT += now() - t0;
                if (!f.r123) continue;
                if (best.grade < 0 || f.grade < best.grade) { best = f; bestkey = key_str(o ? 'L' : 'R', k); }
                if (best.grade == 0) break;
            }
        }
        if (best.grade < 0) return;
        ++ndl; ++ngrade[best.grade];
        out << s << "\t" << GRADE[best.grade] << "\t" << bestkey << "\t" << best.m1 << "," << best.c1 << "|"
            << best.m2 << "," << best.c2 << "," << best.b2 << "|" << best.m3 << "," << best.c3 << "," << best.a3
            << "," << best.b3 << "|";
        if (best.h) out << best.mh << "," << best.ch; else out << "-";
        out << "\t" << edits << "\n";
        if (ndl % 50 == 0) out.flush();
    }

    // all subsets of up to `left` further slots (in increasing slot order), every non-base value on each
    void go(const int *base, int *sl, int start, int left, int edits) {
        if (edits > 0) handle(sl, edits);
        if (left == 0) return;
        for (int i = start; i < 16; ++i) {
            for (int v = 0; v <= 32; ++v) {
                if (v == base[i]) continue;
                sl[i] = v;
                go(base, sl, i + 1, left - 1, edits + 1);
            }
            sl[i] = base[i];
        }
    }
};

// dlnbr --reach ROWS OUTPUT [STEPS=3000000]: for each row "machine<TAB>grade<TAB>key..." of a search output,
// run the machine (mirrored for an L key) from the blank tape and report how often it is in a family
// configuration of that key: machine, grade, key, halted_step, n_configs, n_with_digits, max_digits.
// A machine that never shows a configuration with digits is not a digit-list counter from the blank tape,
// whatever its rules do on constructed lists.
static int reach_mode(const char *rows, const char *outp, long long steps) {
    std::ifstream in(rows); std::ofstream out(outp);
    out << "machine\tgrade\tkey\thalted_step\tn_configs\tn_with_digits\tmax_digits\n";
    Prober pr; std::string line;
    while (std::getline(in, line)) {
        if (line.empty() || line[0] == '#' || line.compare(0, 7, "machine") == 0) continue;
        std::vector<std::string> f; size_t i = 0;
        while (i <= line.size()) { size_t j = line.find('\t', i); if (j == std::string::npos) j = line.size(); f.push_back(line.substr(i, j - i)); i = j + 1; }
        if (f.size() < 3) continue;
        TM m; if (!parse(f[0], m)) continue;
        std::vector<std::string> k; i = 0;
        while (i <= f[2].size()) { size_t j = f[2].find(',', i); if (j == std::string::npos) j = f[2].size(); k.push_back(f[2].substr(i, j - i)); i = j + 1; }
        if (k.size() != 5) continue;
        Key key{k[1][0] - 'A', k[2], k[3], k[4]};
        long long nK, nDig, maxDig;
        long long h = pr.trace(k[0] == "L" ? mirrored(m) : m, key, steps, nK, nDig, maxDig);
        out << f[0] << "\t" << f[1] << "\t" << f[2] << "\t" << h << "\t" << nK << "\t" << nDig << "\t" << maxDig << "\n";
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc >= 4 && !strcmp(argv[1], "--reach")) return reach_mode(argv[2], argv[3], argc > 4 ? atoll(argv[4]) : 3000000LL);
    if (argc < 6) { fprintf(stderr, "usage: dlnbr PARENT RADIUS OUTPUT PART NPARTS [STEPS] [N]\n"); return 2; }
    std::string parent = argv[1];
    int radius = atoi(argv[2]);
    g_snap_backoff = true;
    Search S;
    S.out.open(argv[3]);
    S.part = atoll(argv[4]); S.nparts = atoll(argv[5]);
    S.steps = argc > 6 ? atoll(argv[6]) : 300000LL;
    S.N = argc > 7 ? atoll(argv[7]) : 20000LL;
    if ((int)parent.size() != 55 || radius < 0 || radius > 4) { fprintf(stderr, "bad parent or radius\n"); return 2; }
    int base[16], sl[16];
    for (int q = 0; q < 8; ++q) for (int c = 0; c < 2; ++c) {
        const char *t = parent.c_str() + 7 * q + 3 * c;
        base[2 * q + c] = t[0] == '-' ? 32 : (t[0] - '0') * 16 + (t[1] == 'R' ? 8 : 0) + (t[2] - 'A');
    }
    memcpy(sl, base, sizeof sl);
    S.out << "machine\tgrade\tkey\tparams\tedits\n";
    if (radius == 0) S.handle(sl, 0);
    S.go(base, sl, 0, radius, 0);
    S.out << "#summary\tmachines=" << S.n << "\thalted=" << S.nhalt << "\tdigit_list=" << S.ndl;
    for (int g = 0; g < 4; ++g) S.out << "\t" << GRADE[g] << "=" << S.ngrade[g];
    S.out << "\n";
    if (getenv("DLNBR_PROFILE")) fprintf(stderr, "census %.2fs, keys %.2fs, probes %.2fs\n", T_CEN, T_KEY, T_FIT);
    return 0;
}
