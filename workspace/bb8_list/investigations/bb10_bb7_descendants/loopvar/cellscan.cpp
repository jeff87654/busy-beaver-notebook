// cellscan.cpp: fast halting screen of many machines on a few start words (head right of the word, given state).
//   cellscan MACHINES.txt STATE CELLFILE...   (each CELLFILE line 1: CAP, line 2: the word)
// Prints, per machine: machine TAB letters (H = halted within CAP, . = not) TAB halting steps.  Stops a machine's
// cells after the first cell if that one halts (the first cell is the real first exhaustion).
// Build: g++ -O2 -std=c++17 -static -o cellscan.exe cellscan.cpp
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <fstream>
struct Tr { unsigned char w; signed char d; unsigned char nx; bool def; };
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage\n"); return 2; }
    std::ifstream mf(argv[1]); int q0 = argv[2][0] - 'A';
    std::vector<std::string> words; std::vector<long long> caps;
    for (int i = 3; i < argc; ++i) { std::ifstream f(argv[i]); long long c; std::string w; f >> c >> w; caps.push_back(c); words.push_back(w); }
    std::vector<unsigned char> tape;
    std::string m;
    while (mf >> m) {
        int nst = (int)(m.size() + 1) / 7; std::vector<Tr> tr(2 * nst);
        for (int s = 0; s < nst; ++s) for (int c = 0; c < 2; ++c) {
            const char *x = m.c_str() + 7 * s + 3 * c;
            if (x[0] == '-') tr[2 * s + c] = {0, 0, 0, false};
            else tr[2 * s + c] = {(unsigned char)(x[0] - '0'), (signed char)(x[1] == 'R' ? 1 : -1), (unsigned char)(x[2] - 'A'), true};
        }
        std::string let, steps, hashes;
        for (size_t k = 0; k < words.size(); ++k) {
            const std::string &w = words[k]; long long cap = caps[k];
            size_t size = w.size() + 2 * (size_t)std::min<long long>(cap, 40000000) / 1 + 16;
            size = std::min<size_t>(size, (size_t)1 << 27);
            tape.assign(size, 0);
            size_t off = size / 2; for (size_t i = 0; i < w.size(); ++i) tape[off + i] = (unsigned char)(w[i] - '0');
            size_t pos = off + w.size(); int q = q0; long long st = 0; bool halted = false, out = false;
            while (st < cap) {
                const Tr &x = tr[2 * q + tape[pos]];
                if (!x.def) { halted = true; break; }
                tape[pos] = x.w; pos += x.d; q = x.nx; ++st;
                if (pos == 0 || pos + 1 >= size) { out = true; break; }
            }
            {   // fingerprint of the final configuration (state, head offset, nonzero tape) for de-duplication
                unsigned long long h = 1469598103934665603ULL; size_t lo = 0, hi = size;
                while (lo < size && !tape[lo]) ++lo; while (hi > lo && !tape[hi - 1]) --hi;
                for (size_t i = lo; i < hi; ++i) { h ^= tape[i]; h *= 1099511628211ULL; }
                h ^= (unsigned long long)q * 1000003ULL ^ (unsigned long long)(pos - lo) * 7919ULL; h *= 1099511628211ULL;
                char buf[32]; snprintf(buf, sizeof buf, "%s%016llx", k ? "," : "", h); hashes += buf;
            }
            let += halted ? 'H' : (out ? 'O' : '.');
            steps += (k ? "," : "") + std::to_string(halted ? st : -1);
            if (k == 0 && halted) break;
        }
        printf("%s\t%s\t%s\t%s\n", m.c_str(), let.c_str(), steps.c_str(), hashes.c_str()); fflush(stdout);
    }
    return 0;
}
