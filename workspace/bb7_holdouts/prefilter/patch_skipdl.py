import sys
p = sys.argv[1]; s = open(p).read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a, s.count(a)); s = s.replace(a, b)
rep(r'''#define DLSCAN_NO_MAIN
#include "dlscan.cpp"
''', r'''#define DLSCAN_NO_MAIN
#include "dlscan.cpp"
#include <chrono>

// ---- --skipdl (dlscan2_skipdl.cpp): drop every template that dlscan's first pass already screened.
// dlscan's base keys are (orientation, state q, suffix) for every end shape its census saw (head on a blank, a 1 one
// or two cells inward, no 1 outward; suffix "0" if the gap is one blank, else "01" if the outermost run is a single
// 1, else "1"), probed with unit "1", separator "0". The dlscan2 template (q, P empty, u "1", s "0", d = 1d+0,
// b = 1b+0, S = that suffix) builds the same probe tapes and stops at the same first family configuration (both
// parses split the word at every 0, and the word starts at the first 1, so dlscan's leading-zero rejection never
// fires), so R1/R2 are the same tests and dlscan2's R3 (k = 1 probes for >= 3 values of b) implies dlscan's "full".
// Hence a fit on such a template means dlscan listed the machine with that full key. Conditions for the claim:
// the shape must have been seen within dlscan's census length (g_dl_steps, first pass 1,000,000) and dlscan2's
// probe budget N must not exceed dlscan's (g_dl_N, first pass 100,000). The only residual difference is the parse
// work cap per probe (dlscan 2e8 compared characters, dlscan2 4e8 scanned cells), which needs > 2e8 parse work.
static long long g_dl_steps = 1000000, g_dl_N = 100000;
static bool g_skipdl = false;
static bool g_dlsh[2][MAXQ * 4];
static double g_t[4];   // census, inference, fits, other (seconds), printed with DLSCAN2_PROF
''')
rep(r'''static long long census2(const TM &m, long long steps, End2 ends[2]) {''',
r'''static long long census2(const TM &m, long long steps, End2 ends[2]) {
    memset(g_dlsh, 0, sizeof g_dlsh);''')
rep(r'''                if (clear) { while (!T[hiB]) --hiB; end_event2(ends[0], T, q, loB, pos, 1); }''',
r'''                if (clear) {
                    if (g_skipdl && t < g_dl_steps) {       // dlscan's right-end shape, if this is one of its events
                        int gr = T[pos - 1] ? 0 : (T[pos - 2] ? 1 : -1);
                        if (gr >= 0) { long long near = pos - 1 - gr; g_dlsh[0][q * 4 + gr * 2 + (T[near - 1] == 0)] = true; }
                    }
                    while (!T[hiB]) --hiB; end_event2(ends[0], T, q, loB, pos, 1);
                }''')
rep(r'''                if (clear) { while (!T[loB]) ++loB; end_event2(ends[1], T, q, hiB, pos, -1); }''',
r'''                if (clear) {
                    if (g_skipdl && t < g_dl_steps) {       // dlscan's left-end shape
                        int gl = T[pos + 1] ? 0 : (T[pos + 2] ? 1 : -1);
                        if (gl >= 0) { long long near = pos + 1 + gl; g_dlsh[1][q * 4 + gl * 2 + (T[near + 1] == 0)] = true; }
                    }
                    while (!T[loB]) ++loB; end_event2(ends[1], T, q, hiB, pos, -1);
                }''')
rep(r'''// ---------------------------------------------------------------------------------------------- templates''',
r'''// ---------------------------------------------------------------------------------------------- templates
struct Tmpl;
static bool dl_covered(int o, const Tmpl &t);''')
rep(r'''// ------------------------------------------------------------------------------------------------- probes''',
r'''static bool dl_covered(int o, const Tmpl &t) {
    if (!t.P.empty() || t.u != "1" || t.s != "0" || t.al != 1 || t.be != 0 || t.alB != 1 || t.beB != 0) return false;
    int gap, single;
    if (t.S == "0") { gap = 1; return g_dlsh[o][t.q * 4 + 2] || g_dlsh[o][t.q * 4 + 3]; }
    else if (t.S == "01") { gap = 0; single = 1; }
    else if (t.S == "1") { gap = 0; single = 0; }
    else return false;
    return g_dlsh[o][t.q * 4 + gap * 2 + single];
}

// ------------------------------------------------------------------------------------------------- probes''')
rep(r'''    std::vector<std::string> pos; bool all = false;
    for (int i = 1; i < argc; ++i) { if (!strcmp(argv[i], "--all")) all = true; else pos.push_back(argv[i]); }''',
r'''    std::vector<std::string> pos; bool all = false;
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--all")) all = true;
        else if (!strcmp(argv[i], "--skipdl")) g_skipdl = true;
        else if (!strncmp(argv[i], "--dlsteps=", 10)) g_dl_steps = atoll(argv[i] + 10);
        else if (!strncmp(argv[i], "--dlN=", 6)) g_dl_N = atoll(argv[i] + 6);
        else pos.push_back(argv[i]);
    }''')
rep(r'''    long long N = pos.size() > 3 ? atoll(pos[3].c_str()) : 100000LL;
    std::ifstream in(pos[0]);
    if (!in) { fprintf(stderr, "cannot read %s\n", pos[0].c_str()); return 2; }
    std::ofstream out(pos[1]);''',
r'''    long long N = pos.size() > 3 ? atoll(pos[3].c_str()) : 100000LL;
    if (g_skipdl && N > g_dl_N) {
        fprintf(stderr, "--skipdl: probe budget %lld exceeds dlscan's %lld, nothing is skipped\n", N, g_dl_N);
        g_skipdl = false;
    }
    bool prof = getenv("DLSCAN2_PROF") != nullptr;
    long long nskipped = 0;
    std::ifstream in(pos[0]);
    if (!in) { fprintf(stderr, "cannot read %s\n", pos[0].c_str()); return 2; }
    std::ofstream out(pos[1]);''')
rep(r'''        End2 ends[2];
        long long halted = census2(m, steps, ends);
        ends[0].collect(); ends[1].collect();''',
r'''        End2 ends[2];
        auto t0 = std::chrono::steady_clock::now();
        long long halted = census2(m, steps, ends);
        ends[0].collect(); ends[1].collect();
        auto t1 = std::chrono::steady_clock::now();
        g_t[0] += std::chrono::duration<double>(t1 - t0).count();''')
rep(r'''            for (auto &t : infer_templates(ends[o])) {
                ++nt;''',
r'''            auto ti0 = std::chrono::steady_clock::now();
            std::vector<Tmpl> ts = infer_templates(ends[o]);
            auto ti1 = std::chrono::steady_clock::now();
            g_t[1] += std::chrono::duration<double>(ti1 - ti0).count();
            for (auto &t : ts) {
                if (g_skipdl && dl_covered(o, t)) { ++nskipped; continue; }
                ++nt;''')
rep(r'''                Fit2 f = fit2(pr, o ? mm : m, t, N);''',
r'''                auto tf0 = std::chrono::steady_clock::now();
                Fit2 f = fit2(pr, o ? mm : m, t, N);
                g_t[2] += std::chrono::duration<double>(std::chrono::steady_clock::now() - tf0).count();''')
rep(r'''    out << "\n";
    return 0;
}''', r'''    out << "\tskipped_dl_templates=" << nskipped << "\n";
    if (prof) fprintf(stderr, "prof machines=%lld census=%.3fs infer=%.3fs fits=%.3fs skipped=%lld\n", n, g_t[0], g_t[1], g_t[2], nskipped);
    return 0;
}''')
open(p, 'w').write(s)
print('patched')
