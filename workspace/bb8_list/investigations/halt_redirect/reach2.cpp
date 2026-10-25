// reach.cpp: does MACHINE, started from START (word, head index, state), reach the configuration TARGET_WORD with the
// head on the blank right of it in TARGET_STATE (all other cells blank), within MAXSTEPS?
//   reach MACHINE JOBS.txt MAXSTEPS        JOBS lines: label startword head state targetword targetstate
// Prints per job: label REACHED step | HALT step state read ones | TIMEOUT
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
struct Tr { int w, d, nx; bool def; };
int main(int argc, char **argv) {
    std::string m = argv[1]; long long N = atoll(argv[3]);
    std::vector<std::string> rows; { std::stringstream ss(m); std::string r; while (std::getline(ss, r, '_')) rows.push_back(r); }
    int n = rows.size(); std::vector<Tr> t(2 * n, {0, 0, 0, false});
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) { std::string x = rows[q].substr(3 * c, 3);
        if (x[2] != '-' && x[2] != 'Z') t[2 * q + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    std::ifstream f(argv[2]); std::string line;
    while (std::getline(f, line)) {
        std::stringstream ss(line); std::string lab, w, tw, qs, tqs; long long head;
        if (!(ss >> lab >> w >> head >> qs >> tw >> tqs)) continue;
        int q = qs[0] - 'A', tq = tqs[0] - 'A';
        long long L = 8 * (long long)(w.size() + tw.size()) + (1 << 20);
        std::vector<unsigned char> tape(L, 0); long long off = L / 4;
        for (size_t i = 0; i < w.size(); ++i) tape[off + i] = w[i] - '0';
        long long h = off + head, lo = off, hi = off + w.size(); long long step = 0; bool done = false;
        std::vector<unsigned char> T(tw.size()); for (size_t i = 0; i < tw.size(); ++i) T[i] = tw[i] - '0';
        while (step <= N) {
            if (h < 1 || h >= L - 1) { printf("%s\tTAPE\t%lld\n", lab.c_str(), step); done = true; break; }
            if (h < lo) lo = h; if (h > hi) hi = h;
            if (q == tq && tape[h] == 0 && h - (long long)T.size() >= lo && tape[h - (long long)T.size()] == T[0]) {
                long long s0 = h - T.size();
                bool ok = memcmp(&tape[s0], T.data(), T.size()) == 0;
                if (ok) for (long long i = lo; i < s0 && ok; ++i) if (tape[i]) ok = false;
                if (ok) for (long long i = h; i <= hi && ok; ++i) if (tape[i]) ok = false;
                if (ok) { printf("%s\tREACHED\t%lld\n", lab.c_str(), step); done = true; break; }
            }
            int c = tape[h]; const Tr &tr = t[2 * q + c];
            if (!tr.def) { long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += tape[i];
                printf("%s\tHALT\t%lld\t%c\t%d\t%lld\n", lab.c_str(), step, 'A' + q, c, ones); done = true; break; }
            tape[h] = tr.w; h += tr.d; q = tr.nx; ++step;
        }
        if (!done) printf("%s\tTIMEOUT\t%lld\n", lab.c_str(), N);
        fflush(stdout);
    }
}
