// nbrstart.cpp: enumerate radius-R neighbours of a TM (changing transitions among SLOTS) and print those whose run from
// the blank tape reaches a target configuration: head in state Q on a blank right of all 1s, tape (leftmost 1 .. head)
// equal to TARGET, within MAXSTEPS.
//   nbrstart MACHINE RADIUS SLOTS TARGETFILE Q MAXSTEPS
// SLOTS: comma-separated transition names (A0,B1,...) or "all".  Values: '---' or write x move x state.
// Build: g++ -O2 -std=c++17 -static -o nbrstart.exe nbrstart.cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <set>

struct Tr { int w, d, nx; bool def; };
static int nst;
static std::vector<Tr> parse(const std::string &m) {
    std::vector<Tr> tr(2 * nst);
    for (int s = 0; s < nst; ++s)
        for (int c = 0; c < 2; ++c) {
            const char *x = m.c_str() + 7 * s + 3 * c;
            if (x[0] == '-' || x[2] - 'A' >= nst) { tr[2 * s + c] = {0, 0, 0, false}; continue; }
            tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true};
        }
    return tr;
}
static std::string target; static int tq; static long long maxs;
static std::vector<unsigned char> tape;
static bool reaches(const std::vector<Tr> &tr) {
    long long size = 1 << 16; tape.assign(size, 0);
    long long pos = size / 2, lo = pos, hi = pos, steps = 0; int q = 0;
    long long rmax1 = -1, lmin1 = size;
    while (steps < maxs) {
        int c = tape[pos];
        if (q == tq && c == 0 && pos > rmax1 && rmax1 >= 0 && rmax1 - lmin1 + 1 == (long long)target.size() && pos == rmax1 + 1) {
            bool ok = true;
            for (size_t i = 0; i < target.size() && ok; ++i) ok = tape[lmin1 + i] == (unsigned char)(target[i] - '0');
            if (ok) return true;
        }
        const Tr &x = tr[2 * q + c];
        if (!x.def) return false;
        tape[pos] = (unsigned char)x.w;
        if (x.w) { if (pos > rmax1) rmax1 = pos; if (pos < lmin1) lmin1 = pos; }
        else {
            if (pos == rmax1) { long long k = pos - 1; while (k >= lo && !tape[k]) --k; rmax1 = k >= lo ? k : -1; if (rmax1 < 0) lmin1 = size; }
            if (pos == lmin1 && rmax1 >= 0) { long long k = pos + 1; while (k <= hi && !tape[k]) ++k; lmin1 = k; }
        }
        pos += x.d; q = x.nx; ++steps;
        if (pos < lo) lo = pos;
        if (pos > hi) hi = pos;
        if (pos <= 1 || pos >= size - 2) return false;   // the start-up is short: a long excursion is not the champion
    }
    return false;
}
int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage\n"); return 2; }
    std::string m = argv[1]; int rad = atoi(argv[2]); std::string slots = argv[3];
    nst = (int)(m.size() + 1) / 7;
    FILE *f = fopen(argv[4], "r"); int ch; while ((ch = fgetc(f)) != EOF) if (ch == '0' || ch == '1') target += (char)ch; fclose(f);
    tq = argv[5][0] - 'A'; maxs = atoll(argv[6]);
    std::vector<int> sl;
    for (int i = 0; i < 2 * nst; ++i) {
        std::string nm = std::string(1, char('A' + i / 2)) + char('0' + i % 2);
        if (slots == "all" || ("," + slots + ",").find("," + nm + ",") != std::string::npos) sl.push_back(i);
    }
    std::vector<std::string> vals = {"---"};
    for (int w = 0; w < 2; ++w) for (int d = 0; d < 2; ++d) for (int q = 0; q < nst; ++q)
        vals.push_back(std::string(1, char('0' + w)) + (d ? 'R' : 'L') + char('A' + q));
    std::set<std::string> seen; long long tested = 0, hits = 0;
    auto setv = [&](std::string &s, int idx, const std::string &v) { s.replace(7 * (idx / 2) + 3 * (idx % 2), 3, v); };
    auto test = [&](const std::string &s) {
        if (!seen.insert(s).second) return;
        ++tested;
        if (reaches(parse(s))) { printf("%s\n", s.c_str()); ++hits; fflush(stdout); }
    };
    if (rad == 1) {
        for (int a : sl) for (auto &v : vals) { std::string s = m; if (s.substr(7 * (a / 2) + 3 * (a % 2), 3) == v) continue; setv(s, a, v); test(s); }
    } else if (rad == 3) {
        // REQ (env): comma-separated slots; each triple must contain at least one of them
        const char *rq = getenv("REQ"); std::string req = rq ? std::string(",") + rq + "," : "";
        auto nm = [&](int i) { return std::string(1, char('A' + i / 2)) + char('0' + i % 2); };
        auto isreq = [&](int i) { return req.empty() || req.find("," + nm(i) + ",") != std::string::npos; };
        auto cur = [&](int i) { return m.substr(7 * (i / 2) + 3 * (i % 2), 3); };
        for (size_t i = 0; i < sl.size(); ++i) for (size_t j = i + 1; j < sl.size(); ++j) for (size_t k = j + 1; k < sl.size(); ++k) {
            if (!isreq(sl[i]) && !isreq(sl[j]) && !isreq(sl[k])) continue;
            for (auto &v : vals) { if (cur(sl[i]) == v) continue;
            for (auto &u : vals) { if (cur(sl[j]) == u) continue;
            for (auto &x : vals) { if (cur(sl[k]) == x) continue;
                std::string s = m; setv(s, sl[i], v); setv(s, sl[j], u); setv(s, sl[k], x); test(s); } } }
        }
    } else {
        for (size_t i = 0; i < sl.size(); ++i) for (size_t j = i + 1; j < sl.size(); ++j)
            for (auto &v : vals) for (auto &u : vals) {
                std::string s = m;
                if (s.substr(7 * (sl[i] / 2) + 3 * (sl[i] % 2), 3) == v || s.substr(7 * (sl[j] / 2) + 3 * (sl[j] % 2), 3) == u) continue;
                setv(s, sl[i], v); setv(s, sl[j], u); test(s);
            }
    }
    fprintf(stderr, "tested %lld, reach target %lld\n", tested, hits);
    return 0;
}
