// renum.cpp: TNF-style enumeration of the completions of a machine from given configurations.
//   renum BASE NMAX STARTS.txt BUDGET [REPORT_STEPS=100000]
// BASE: machine string (padded to NMAX states with ------ automatically). STARTS: lines "label word head state"
// (e.g. the base's halting configurations). Each node is simulated from every start; at the first start that reaches
// an undefined transition, that transition is branched over every value (targets up to the first unused state, TNF)
// and the node itself is also a leaf (the transition stays undefined = halt). Leaves whose starts all halt within
// REPORT_STEPS are only counted; the others are printed: machine <TAB> per-start outcomes (H:steps:ones:state, T, W).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
struct Tr { int w, d, nx; bool def; };
static int NMAX; static long long BUD, REP; static long long nodes = 0, quiet = 0, printed = 0;
struct St { std::string lab, w; long long head; int q; };
static std::vector<St> sts;
static std::string fmt(const std::vector<Tr> &t) {
    std::string s;
    for (int q = 0; q < NMAX; ++q) { if (q) s += '_';
        for (int c = 0; c < 2; ++c) { const Tr &x = t[2 * q + c];
            if (!x.def) s += "---"; else { s += char('0' + x.w); s += x.d > 0 ? 'R' : 'L'; s += char('A' + x.nx); } } }
    return s;
}
struct Res { char kind; long long steps, ones; int q, c; };
static std::vector<unsigned char> tape;
static Res sim(const std::vector<Tr> &t, const St &s) {
    long long L = std::max<long long>(1 << 16, 4 * (long long)s.w.size());
    tape.assign(L, 0); long long off = L / 2 - (long long)s.w.size() / 2;
    for (size_t i = 0; i < s.w.size(); ++i) tape[off + i] = s.w[i] - '0';
    long long h = off + s.head; int q = s.q; long long step = 0;
    while (step < BUD) {
        if (h < 0 || h >= (long long)tape.size()) {
            long long add = tape.size(); if ((long long)tape.size() + add > 40000000) return {'W', step, 0, q, 0};
            std::vector<unsigned char> nt(tape.size() + 2 * add, 0); memcpy(&nt[add], tape.data(), tape.size()); tape.swap(nt); h += add; }
        int c = tape[h]; const Tr &tr = t[2 * q + c];
        if (!tr.def) { long long ones = 0; for (auto v : tape) ones += v; return {'H', step, ones, q, c}; }
        tape[h] = tr.w; h += tr.d; q = tr.nx; ++step;
    }
    return {'T', step, 0, q, 0};
}
static void dfs(std::vector<Tr> &t, int used) {
    ++nodes;
    std::vector<Res> rs; int bq = -1, bc = -1; bool loud = false;
    for (auto &s : sts) { Res r = sim(t, s); rs.push_back(r);
        if (r.kind == 'H' && bq < 0) { bq = r.q; bc = r.c; }
        if (r.kind != 'H' || r.steps > REP) loud = true; }
    if (loud) { ++printed; printf("%s", fmt(t).c_str());
        for (auto &r : rs) { if (r.kind == 'H') printf("\tH:%lld:%lld:%c%d", r.steps, r.ones, 'A' + r.q, r.c); else printf("\t%c:%lld", r.kind, r.steps); }
        printf("\n"); fflush(stdout); }
    else ++quiet;
    if (bq < 0) return;
    int undef = 0; for (int i = 0; i < 2 * NMAX; ++i) if (!t[i].def) ++undef;
    if (undef <= 1) return;                       // defining the last undefined transition leaves no halt
    int lim = std::min(used + 1, NMAX);
    for (int nx = 0; nx < lim; ++nx) for (int w = 0; w < 2; ++w) for (int d = -1; d <= 1; d += 2) {
        t[2 * bq + bc] = {w, d, nx, true};
        dfs(t, std::max(used, nx + 1));
        t[2 * bq + bc].def = false;
    }
}
int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: renum BASE NMAX STARTS BUDGET [REPORT_STEPS]\n"); return 2; }
    std::string base = argv[1]; NMAX = atoi(argv[2]); BUD = atoll(argv[4]); REP = argc > 5 ? atoll(argv[5]) : 100000;
    std::vector<std::string> rows; { std::stringstream ss(base); std::string r; while (std::getline(ss, r, '_')) rows.push_back(r); }
    int used = rows.size(); while ((int)rows.size() < NMAX) rows.push_back("------");
    std::vector<Tr> t(2 * NMAX, {0, 0, 0, false});
    for (int q = 0; q < NMAX; ++q) for (int c = 0; c < 2; ++c) { std::string x = rows[q].substr(3 * c, 3);
        if (x[2] != '-' && x[2] != 'Z') t[2 * q + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    { std::ifstream f(argv[3]); std::string l; while (std::getline(f, l)) { std::stringstream ss(l); St s; std::string qs; if (ss >> s.lab >> s.w >> s.head >> qs) { s.q = qs[0] - 'A'; sts.push_back(s); } } }
    printf("#starts"); for (auto &s : sts) printf("\t%s", s.lab.c_str()); printf("\n");
    dfs(t, used);
    printf("#summary nodes=%lld printed=%lld quiet=%lld\n", nodes, printed, quiet);
}
