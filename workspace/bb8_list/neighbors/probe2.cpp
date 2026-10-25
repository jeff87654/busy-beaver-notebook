// probe2.cpp: run arbitrary family probes with a dlscan2 template (complements dlscan2 --tmpl, whose probe set is fixed).
// Build (PATH must include C:\msys64\ucrt64\bin):
//   g++ -O2 -std=c++17 -static -I . -o probe2.exe probe2.cpp      (it includes dlscan2.cpp with main renamed; see below)
// Usage: probe2 MACHINE O Q P u s alpha beta alphaB betaB S N probe...   probe = "ds;a;b", ds comma-separated farthest-first ("" = empty list)
// Example (BB(7) champion template): probe2 <tm> R B 11 10 1 3 1 3 2 111001 300000 ";0;1" "0,0,0;0;2"
// 2026-10-03: used on the champion m=12 TNF subtree (estimate_20260926/champion_neighborhood/holdouts_12_dlscan2.tsv).
#include "dlscan2_nomain.inc"
#include <sstream>
int main(int argc, char **argv) {
    if (argc < 14) { fprintf(stderr, "usage: probe2 MACHINE O Q P u s alpha beta alphaB betaB S N probe...\n"); return 2; }
    TM m; if (!parse(argv[1], m)) { fprintf(stderr, "bad machine\n"); return 2; }
    if (argv[2][0] == 'L') m = mirrored(m);
    Tmpl t; t.q = argv[3][0] - 'A'; t.P = strcmp(argv[4], "-") ? argv[4] : ""; t.u = argv[5]; t.s = argv[6];
    t.al = atoll(argv[7]); t.be = atoll(argv[8]); t.alB = atoll(argv[9]); t.beB = atoll(argv[10]); t.S = strcmp(argv[11], "-") ? argv[11] : "";
    long long N = atoll(argv[12]);
    Prober2 pr;
    for (int i = 13; i < argc; ++i) {
        std::vector<std::string> parts; { std::stringstream ss(argv[i]); std::string it; while (std::getline(ss, it, ';')) parts.push_back(it); }
        while (parts.size() < 3) parts.push_back("0");
        std::vector<long long> ds;
        if (!parts[0].empty()) { std::stringstream ss(parts[0]); std::string d; while (std::getline(ss, d, ',')) ds.push_back(atoll(d.c_str())); }
        long long aa = atoll(parts[1].c_str()), bb = atoll(parts[2].c_str());
        P2 r = pr.run_next(m, t, ds, aa, bb, N);
        printf("K("); for (size_t j = 0; j < ds.size(); ++j) printf("%s%lld", j ? "," : "", ds[j]); printf("; %lld; %lld) -> ", aa, bb);
        if (r.kind == 1) printf("HALT after %lld\n", r.steps);
        else if (r.kind == 2) printf("TIMEOUT\n");
        else { printf("K("); for (size_t j = 0; j < r.ds.size(); ++j) printf("%s%lld", j ? "," : "", r.ds[j]); printf("; %lld; %lld) in %lld\n", r.a, r.b, r.steps); }
    }
    return 0;
}
