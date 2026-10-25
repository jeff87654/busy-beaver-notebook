// kt9.cpp: D-token tracer at right-edge visits in a given state (generalises tr9's dshape/dall to any state Q).
//   kt9 MACHINE TAPE HEAD STATE MAXSTEPS Q MAXPRINT [MODE=shape|all|every:K] [-u]
// At every step where the head is in state Q, reading 0, on the rightmost visited cell, the tape left of the head is
// shown as D-tokens D(m) = (10)^m 1 (numbers, equal neighbours compressed x*k; other cells raw in <...>).
// shape: print when the shape (numbers -> #) changes;  all: every visit;  every:K every K-th visit.
// -u: D-tokens are read as (01)^m ... no: -u reads U-tokens U(m) = 1 (01)^m instead (mirror encoding).
// At a halt (undefined transition) prints HALT step state symbol ones and the token view of the whole tape.
// Build: g++ -O2 -std=c++17 -static -o kt9.exe kt9.cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
struct Tr { int w, d, nx; bool def; };
static std::vector<unsigned char> t;
static long long lo, hi, pos;
static std::string dtoks(long long a, long long b) {
    std::vector<std::string> tok; std::string raw;
    auto flushraw = [&]() {
        if (raw.empty()) return;
        std::string out; size_t i = 0;
        while (i < raw.size()) {
            size_t j = i;
            if (i + 3 < raw.size() && raw[i] != raw[i + 1] && raw[i + 2] == raw[i] && raw[i + 3] == raw[i + 1]) {
                while (j + 1 < raw.size() && raw[j] == raw[i] && raw[j + 1] == raw[i + 1]) j += 2;
                out += "(" + raw.substr(i, 2) + ")^" + std::to_string((j - i) / 2) + " "; i = j; continue;
            }
            while (j < raw.size() && raw[j] == raw[i]) ++j;
            if (j - i >= 3) out += std::string(1, raw[i]) + "^" + std::to_string(j - i) + " ";
            else out += raw.substr(i, j - i) + " ";
            i = j;
        }
        if (!out.empty()) out.pop_back();
        tok.push_back("<" + out + ">"); raw.clear();
    };
    long long i = a;
    while (i < b && t[i] == 0) ++i;
    while (i < b) {
        long long j = i, m = 0;
        while (j + 1 < b && t[j] == 1 && t[j + 1] == 0) { j += 2; ++m; }
        if (j < b && t[j] == 1) { flushraw(); tok.push_back(std::to_string(m)); i = j + 1; }
        else { raw += char('0' + t[i]); ++i; }
    }
    flushraw();
    std::string out;
    for (size_t k = 0; k < tok.size();) {
        size_t l = k; while (l < tok.size() && tok[l] == tok[k]) ++l;
        out += tok[k]; if (l - k > 1) out += "*" + std::to_string(l - k); out += " "; k = l;
    }
    return out;
}
static std::string shapeof(const std::string &s) {
    std::string o; bool num = false;
    for (char c : s) { if (c >= '0' && c <= '9') { if (!num) o += '#'; num = true; } else { o += c; num = false; } }
    return o;
}
int main(int argc, char **argv) {
    if (argc < 8) { fprintf(stderr, "usage: kt9 MACHINE TAPE HEAD STATE MAXSTEPS Q MAXPRINT [shape|all|every:K]\n"); return 2; }
    std::string m = argv[1], word = argv[2];
    if (word == "-") word = "";
    long long head = atoll(argv[3]); int q = argv[4][0] - 'A'; long long maxs = atoll(argv[5]);
    int Q = argv[6][0] - 'A'; long long maxp = atoll(argv[7]);
    std::string mode = argc > 8 ? argv[8] : "shape";
    long long every = 0; if (mode.rfind("every:", 0) == 0) every = atoll(mode.c_str() + 6);
    int n = (int)(m.size() + 1) / 7;
    std::vector<Tr> tr(2 * n);
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) {
        const char *x = m.c_str() + 7 * s + 3 * c;
        if (x[0] == '-' || x[2] == 'Z' || x[2] == 'H' + 20) tr[2 * s + c].def = false;
        else tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true};
        if (x[0] == '-') tr[2 * s + c].def = false;
    }
    long long sz = 1 << 20, off = sz / 2;
    t.assign(sz, 0);
    for (size_t i = 0; i < word.size(); ++i) t[off + i] = word[i] == '1';
    pos = off + head; lo = off; hi = off + (long long)word.size() - 1; if (hi < lo) hi = lo;
    if (pos > hi) hi = pos; if (pos < lo) lo = pos;
    long long steps = 0, prints = 0, visits = 0, sim = 0; std::string lastshape, lastline;
    while (steps < maxs) {
        int c = t[pos];
        const Tr &x = tr[2 * q + c];
        if (!x.def) {
            long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += t[i];
            if (sim) printf("   ... %lld similar; last: %s\n", sim, lastline.c_str());
            printf("HALT %lld %c%d ones %lld | %s [%c] %s\n", steps, 'A' + q, c, ones, dtoks(lo, pos).c_str(), 'A' + q,
                   dtoks(pos, hi + 1).c_str());
            return 0;
        }
        if (q == Q && c == 0 && pos == hi) {
            ++visits;
            std::string v = dtoks(lo, pos);
            bool pr = false;
            if (mode == "all") pr = true;
            else if (every) pr = (visits % every == 0);
            else { std::string sh = shapeof(v); if (sh != lastshape) { pr = true; lastshape = sh; } }
            if (pr) {
                if (sim && mode == "shape") printf("   ... %lld similar; last: %s\n", sim, lastline.c_str());
                printf("S %lld | %s\n", steps, v.c_str()); fflush(stdout); sim = 0;
                if (++prints >= maxp) return 0;
            } else { ++sim; lastline = std::to_string(steps) + " | " + v; }
        }
        t[pos] = x.w; pos += x.d; q = x.nx; ++steps;
        if (pos < lo) { lo = pos; }
        if (pos > hi) { hi = pos; }
        if (pos <= 2 || pos >= sz - 3) {
            std::vector<unsigned char> nt(3 * sz, 0);
            memcpy(&nt[sz], t.data(), sz); t.swap(nt); pos += sz; lo += sz; hi += sz; sz *= 3;
        }
    }
    if (sim) printf("   ... %lld similar; last: %s\n", sim, lastline.c_str());
    printf("END %lld\n", steps);
    return 0;
}
