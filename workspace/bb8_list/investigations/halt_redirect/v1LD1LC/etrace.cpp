// ktrace.cpp: print the configuration, as D-tokens (D(m) = (10)^m 1), every time the machine is in state Q with the
// head on the blank right of all 1s.  ktrace MACHINE WORD HEAD STATE Q MAXSTEPS [MAXLINES=200] [MAXTOK=60]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <sstream>
struct Tr { int w, d, nx; bool def; };
int main(int argc, char **argv) {
    std::string m = argv[1], w = argv[2]; if (w == "-") w = ""; long long head = atoll(argv[3]); int q = argv[4][0] - 'A', Q = argv[5][0] - 'A';
    long long N = atoll(argv[6]); long long ML = argc > 7 ? atoll(argv[7]) : 200; int MT = argc > 8 ? atoi(argv[8]) : 60;
    std::vector<std::string> rows; { std::stringstream ss(m); std::string r; while (std::getline(ss, r, '_')) rows.push_back(r); }
    int n = rows.size(); std::vector<Tr> t(2 * n, {0, 0, 0, false});
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { std::string x = rows[s].substr(3 * c, 3);
        if (x[2] != '-' && x[2] != 'Z') t[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    long long L = 1 << 24; std::vector<unsigned char> tape(L, 0); long long off = L / 4;
    for (size_t i = 0; i < w.size(); ++i) tape[off + i] = w[i] - '0';
    long long h = off + head, lo = off, hi = off + w.size(), step = 0, lines = 0, rmost = -1;
    for (long long i = lo; i < hi; ++i) if (tape[i]) rmost = i;
    while (step <= N && lines < ML) {
        if (h < 1 || h >= L - 1) { printf("TAPE %lld\n", step); return 0; }
        if (h < lo) lo = h; if (h > hi) hi = h;
        if ((Q < 0 || q == Q) && tape[h] == 0) {
            bool right = true; for (long long i = h; i <= hi; ++i) if (tape[i]) { right = false; break; }
            if (right) {
                long long a = lo; while (a < h && !tape[a]) ++a;
                std::string out; int nt = 0; long long i = a; std::vector<long long> toks; bool junk = false; long long jpos = 0, tailpairs = 0;
                while (i < h) {
                    long long mm = 0; while (i + 1 < h && tape[i] == 1 && tape[i + 1] == 0 && i + 2 < h + 1) { mm++; i += 2; }
                    if (i < h && tape[i] == 1) { toks.push_back(mm); ++i; }
                    else if (i >= h - 1 && mm > 0) { tailpairs = mm; i = h; }
                    else { junk = true; jpos = i; break; }
                }
                printf("%lld %c:", step, 0x41 + q);
                if (junk) { printf(" JUNK@%lld", jpos - a); }
                // run-length compress tokens
                size_t k = 0; int shown = 0;
                while (k < toks.size() && shown < MT) { size_t j = k; while (j < toks.size() && toks[j] == toks[k]) ++j;
                    if (j - k > 1) printf(" %lld*%zu", toks[k], j - k); else printf(" %lld", toks[k]); k = j; ++shown; }
                if (k < toks.size()) printf(" ...");
                if (tailpairs) printf(" |(10)^%lld", tailpairs);
                printf("\n"); ++lines;
            }
        }
        int c = tape[h]; const Tr &tr = t[2 * q + c];
        if (!tr.def) { long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += tape[i]; printf("HALT %lld %c%d ones %lld\n", step, 'A' + q, c, ones); return 0; }
        tape[h] = tr.w; h += tr.d; q = tr.nx; ++step;
    }
    printf("END %lld\n", step);
}
