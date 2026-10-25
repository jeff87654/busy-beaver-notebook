// sim.cpp: literal TM simulator from exact configurations, with event reports.
//   sim MACHINE JOBS.txt MAXSTEPS EVENTS MAXREP
// JOBS lines: label word head state      (tape = 0^inf word 0^inf, head at word index `head`, may be -1 or len)
// EVENTS: comma list of StateSymbol pairs (e.g. E0,I1,J0; suffix r/l = only with no 1 right/left of the head) or '-'.  Each time the machine is about to
// execute one of these transitions a line is printed:
//   EV label n step state sym headrel word        (word = tape from leftmost 1..rightmost 1 extended to the head)
// After MAXREP reports the job stops (STOP label step).  Undefined transition: HALT label step state sym ones headrel word
// (word only if its length <= 2e6).  TIMEOUT label step.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>
struct Tr { int w, d, nx; bool def; };
static std::vector<unsigned char> tape;
static long long L, lo, hi;

static void dumpword(long long h, std::string &out, long long &rel) {
    long long a = lo, b = hi;
    while (a <= b && !tape[a]) ++a;
    while (b >= a && !tape[b]) --b;
    if (a > b) { a = b = h; }
    if (h < a) a = h;
    if (h > b) b = h;
    out.resize(b - a + 1);
    for (long long i = a; i <= b; ++i) out[i - a] = '0' + tape[i];
    rel = h - a;
}

// B-form test: head on a 0 with no 1 to its right; tape = list tokens, D0, D(A), head right after.
static bool relaxed = false;   // 'Bg<state>': allow a far region (anything up to a 00 run) left of the list
static bool isB(long long h) {
    long long p = h - 1; if (p < lo || !tape[p]) return false;
    long long q = p - 1; while (q - 1 >= lo && tape[q] == 0 && tape[q - 1] == 1) q -= 2;
    if (q < lo || tape[q] != 1) return false;           // q = the D0 separator
    long long s = q - 1;                                  // last cell of the list (or blank)
    long long a = lo; while (a <= s && !tape[a]) ++a;     // leftmost 1
    if (a > s) return true;                               // empty list
    if (relaxed) {
        if (tape[s]) return true;                         // list ends with a 1; far part = up to the last 00 run
        return s - 1 >= lo && !tape[s - 1];               // empty list right after a 00 run
    }
    if (!tape[s]) return false;
    for (long long i = a; i < s; ++i) if (!tape[i] && !tape[i + 1]) return false;
    return true;
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage\n"); return 1; }
    std::string m = argv[1]; long long N = atoll(argv[3]); std::string evs = argv[4]; long long maxrep = atoll(argv[5]);
    std::vector<std::string> rows; { std::stringstream ss(m); std::string r; while (std::getline(ss, r, '_')) rows.push_back(r); }
    int n = rows.size(); std::vector<Tr> t(2 * n, {0, 0, 0, false});
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) { std::string x = rows[q].substr(3 * c, 3);
        if (x[2] != '-' && x[2] != 'Z') t[2 * q + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    std::vector<char> ev(2 * n, 0); bool bstop = false; int bq = 6;
    if (evs != "-") { std::stringstream ss(evs); std::string e; while (std::getline(ss, e, ',')) { if (e == "Bf") { bstop = true; continue; } if (e.size() == 3 && e[0] == 'B' && (e[1] == 'f' || e[1] == 'g')) { bstop = true; bq = e[2] - 'A'; relaxed = (e[1] == 'g'); continue; }
        ev[2 * (e[0] - 'A') + (e[1] - '0')] = e.size() > 2 ? (e[2] == 'r' ? 2 : 3) : 1; } }
    std::string jf = argv[2]; std::ifstream fin; if (jf != "-") fin.open(jf);
    std::istream &f = (jf == "-") ? std::cin : fin; std::string line; long long N0 = N;
    while (std::getline(f, line)) {
        std::stringstream ss(line); std::string lab, w, qs; long long head;
        if (!(ss >> lab >> w >> head >> qs)) continue;
        { long long nn; N = (ss >> nn) ? nn : N0; }
        int q = qs[0] - 'A';
        L = 4 * (long long)w.size() + (1 << 16);
        tape.assign(L, 0); long long off = L / 2 - w.size() / 2;
        for (size_t i = 0; i < w.size(); ++i) tape[off + i] = w[i] - '0';
        long long h = off + head; lo = off; hi = off + (long long)w.size() - 1; if (h < lo) lo = h; if (h > hi) hi = h;
        long long step = 0, nrep = 0; bool done = false; std::string out; long long rel;
        long long Rc = 0, Lc = 0;  // ones strictly right / left of the head
        for (long long i = lo; i <= hi; ++i) { if (i > h) Rc += tape[i]; if (i < h) Lc += tape[i]; }
        while (step <= N) {
            if (h < 2 || h >= L - 2) {
                // grow tape: double and recenter
                long long nL = 2 * L; std::vector<unsigned char> nt(nL, 0); long long sh = nL / 2 - (lo + hi) / 2;
                memcpy(&nt[lo + sh], &tape[lo], hi - lo + 1); tape.swap(nt); h += sh; lo += sh; hi += sh; L = nL;
            }
            if (h < lo) lo = h; if (h > hi) hi = h;
            int c = tape[h]; int k = 2 * q + c;
            if (ev[k] && (ev[k] == 1 || (ev[k] == 2 && Rc == 0) || (ev[k] == 3 && Lc == 0))) {
                ++nrep; dumpword(h, out, rel);
                printf("EV %s %lld %lld %c %d %lld %s\n", lab.c_str(), nrep, step, 'A' + q, c, rel, out.c_str());
                fflush(stdout);
                if (nrep >= maxrep) { printf("STOP %s %lld\n", lab.c_str(), step); done = true; break; }
            }
            if (bstop && q == bq && c == 0 && Rc == 0 && step > 0 && isB(h)) {
                dumpword(h, out, rel);
                printf("BF %s %lld %lld %s\n", lab.c_str(), step, rel, out.c_str()); fflush(stdout); done = true; break;
            }
            const Tr &tr = t[k];
            if (!tr.def) {
                long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += tape[i];
                dumpword(h, out, rel);
                if (out.size() > 2000000) out = "BIG";
                printf("HALT %s %lld %c %d %lld %lld %s\n", lab.c_str(), step, 'A' + q, c, ones, rel, out.c_str());
                done = true; break;
            }
            tape[h] = tr.w;
            if (tr.d > 0) { Lc += tr.w; ++h; Rc -= tape[h]; } else { Rc += tr.w; --h; Lc -= tape[h]; }
            q = tr.nx; ++step;
        }
        if (!done) { dumpword(h, out, rel); if (out.size() > 2000000) out = "BIG";
            printf("TIMEOUT %s %lld %c %d %lld %s\n", lab.c_str(), N, 'A' + q, (int)tape[h], rel, out.c_str()); }
        printf("END %s\n", lab.c_str());
        fflush(stdout);
    }
}
