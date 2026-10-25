// ksnap: literal simulator printing the tape (pair-run RLE) at "end events": head at the left (L) or right (R)
// frontier of the visited region in a given state (or any state: '*').
//   ksnap MACHINE TAPE HEAD STATE MAXSTEPS SIDE ESTATE [MAXLINES=400] [RLE_CHARS=400] [MODE=shape]
// MODE shape: print an event when the RLE's number of tokens differs from the last printed one, or the event count
//   is a power of two; MODE all: every event (up to MAXLINES).  Also reports a halt (undefined slot).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
struct Tr { int w, d, nx; bool def; };
static std::string rle(const std::vector<unsigned char> &t, long long lo, long long hi, size_t maxc, int &ntok) {
    std::string out; ntok = 0;
    long long i = lo;
    while (i <= hi) {
        if (i + 3 <= hi && t[i] != t[i + 1] && t[i + 2] == t[i] && t[i + 3] == t[i + 1]) {
            long long j = i;
            while (j + 1 <= hi && t[j] == t[i] && t[j + 1] == t[i + 1]) j += 2;
            if (out.size() < maxc) out += "(" + std::to_string(t[i]) + std::to_string(t[i + 1]) + ")^" + std::to_string((j - i) / 2) + " ";
            i = j; ++ntok; continue;
        }
        long long j = i;
        while (j <= hi && t[j] == t[i]) ++j;
        if (out.size() < maxc) {
            if (j - i >= 4) out += std::to_string(t[i]) + "^" + std::to_string(j - i) + " ";
            else { for (long long k = i; k < j; ++k) out += char('0' + t[k]); out += " "; }
        }
        ++ntok; i = j;
    }
    if (out.size() >= maxc) out += "...";
    return out;
}
int main(int argc, char **argv) {
    if (argc < 8) { fprintf(stderr, "usage\n"); return 2; }
    std::string m = argv[1];
    int n = (int)(m.size() + 1) / 7;
    std::vector<Tr> tr(2 * n);
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) {
        const char *x = m.c_str() + 7 * q + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') { tr[2 * q + c] = {0, 0, 0, false}; continue; }
        tr[2 * q + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true};
    }
    std::string word = argv[2]; if (word == "-") word = "";
    long long head = atoll(argv[3]); int q = argv[4][0] - 'A';
    long long maxs = (long long)atof(argv[5]);
    char side = argv[6][0]; int est = argv[7][0] == '*' ? -1 : argv[7][0] - 'A';
    long long maxl = argc > 8 ? atoll(argv[8]) : 400; size_t maxc = argc > 9 ? atoll(argv[9]) : 400;
    bool all = argc > 10 && std::string(argv[10]) == "all";
    long long size = 1 << 20, off = size / 2;
    std::vector<unsigned char> t(size, 0);
    for (size_t i = 0; i < word.size(); ++i) t[off + i] = word[i] == '1';
    long long pos = off + head, lo = off, hi = off + (long long)word.size() - 1;
    if (hi < lo) hi = lo;
    long long steps = 0, ev = 0, lines = 0; int lastn = -1;
    while (steps < maxs) {
        const Tr &x = tr[2 * q + t[pos]];
        if (!x.def) {
            int nt; long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += t[i];
            printf("HALT step %lld state %c read %d ones %lld\n  %s\n", steps, 'A' + q, t[pos], ones, rle(t, lo, hi, maxc, nt).c_str());
            return 0;
        }
        t[pos] = (unsigned char)x.w; pos += x.d; q = x.nx; ++steps;
        if (pos < lo) lo = pos;
        if (pos > hi) hi = pos;
        if (pos <= 0 || pos >= size - 1) {
            std::vector<unsigned char> u(2 * size, 0);
            memcpy(u.data() + size / 2, t.data(), size);
            pos += size / 2; lo += size / 2; hi += size / 2; off += size / 2; t.swap(u); size *= 2;
        }
        if ((side == 'R' ? pos == hi : pos == lo) && (est < 0 || q == est)) {
            ++ev;
            // trim blanks for display
            long long a = lo, b = hi; while (a < b && !t[a]) ++a; while (b > a && !t[b]) --b;
            int nt; std::string r;
            bool pw = (ev & (ev - 1)) == 0;
            if (all || pw || lastn < 0) { r = rle(t, a, b, maxc, nt); }
            else { r = rle(t, a, b, 0, nt); }
            if (all || pw || nt != lastn) {
                if (!all && !pw) r = rle(t, a, b, maxc, nt);
                printf("ev %lld step %lld st %c ntok %d: %s\n", ev, steps, 'A' + q, nt, r.c_str());
                fflush(stdout);
                lastn = nt;
                if (++lines >= maxl) { printf("maxlines\n"); return 0; }
            }
        }
    }
    printf("no halt within %lld steps (events %lld)\n", maxs, ev);
    return 0;
}
