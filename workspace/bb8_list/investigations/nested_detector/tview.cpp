// tview: literal simulator that prints run-length views of the tape at tape-end events.
//   tview MACHINE MAXSTEPS [SIDE=B] [STATES=*] [MAXLINES=200] [SKIP=0] [EVERY=1] [MAXCH=400] [TAPE HEAD STATE]
// TAPE: initial word; it may use x^n for n copies of x and (..)^n groups, e.g. "(110)^5 10 1^7" (spaces ignored);
// HEAD: head index into the word (may equal its length); STATE: start state letter.
// An end event is the head reading a blank with no 1 on its side of the tape (beyond the outermost 1).
// SIDE: R, L or B (both). STATES: letters to keep (e.g. "AF"), * = all. SKIP: ignore events before that step.
// EVERY: print only every k-th kept event. Output: step side state | runs from the far end to the head,
// "1^n" / "0^n" for runs >= 4, literal digits otherwise; a repeated group of 2-6 runs (>= 3 copies) is
// printed "(group)xk".
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <functional>
#include <cctype>

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: tview MACHINE MAXSTEPS [SIDE] [STATES] [MAXLINES] [SKIP] [EVERY] [MAXCH]\n"); return 2; }
    std::string m = argv[1];
    int n = (int)(m.size() + 1) / 7;
    int W[16][2], D[16][2], NX[16][2];
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) {
        const char *x = m.c_str() + 7 * q + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') { NX[q][c] = -1; W[q][c] = 1; D[q][c] = 1; continue; }
        W[q][c] = x[0] - '0'; D[q][c] = x[1] == 'R' ? 1 : -1; NX[q][c] = x[2] - 'A';
    }
    long long maxs = atoll(argv[2]);
    char side = argc > 3 ? argv[3][0] : 'B';
    std::string states = argc > 4 ? argv[4] : "*";
    long long maxlines = argc > 5 ? atoll(argv[5]) : 200;
    long long skip = argc > 6 ? atoll(argv[6]) : 0;
    long long every = argc > 7 ? atoll(argv[7]) : 1;
    size_t maxch = argc > 8 ? (size_t)atoll(argv[8]) : 400;
    long long size = 1 << 16, off = size / 2;
    std::vector<unsigned char> t(size, 0);
    long long pos = 0, lo = 1, hi = 0;   // lo..hi bounds of 1s (approximate, shrink lazily)
    int q = 0;
    if (argc > 11) {
        std::string spec = argv[9], word;
        // expand: tokens separated by spaces; "w^n" or "(w)^n"
        size_t i = 0;
        std::function<std::string(size_t &)> parse_seq;
        auto num = [&](size_t &k) { long long v = 0; while (k < spec.size() && isdigit((unsigned char)spec[k])) v = v * 10 + (spec[k++] - '0'); return v; };
        parse_seq = [&](size_t &k) -> std::string {
            std::string out;
            while (k < spec.size() && spec[k] != ')') {
                if (spec[k] == ' ') { ++k; continue; }
                std::string unit;
                if (spec[k] == '(') { ++k; unit = parse_seq(k); ++k; }
                else unit = std::string(1, spec[k++]);
                if (k < spec.size() && spec[k] == '^') { ++k; long long r = num(k); std::string rep; for (long long z = 0; z < r; ++z) rep += unit; unit = rep; }
                out += unit;
            }
            return out;
        };
        word = parse_seq(i);
        long long need = (long long)word.size() * 2 + 1024;
        while (size < need) size *= 2;
        t.assign(size, 0); off = size / 2;
        for (size_t z = 0; z < word.size(); ++z) t[off + z] = word[z] == '1';
        pos = argv[10][0] == 'e' ? (long long)word.size() + atoll(argv[10] + 1) : atoll(argv[10]); q = argv[11][0] - 'A';
        for (size_t z = 0; z < word.size(); ++z) if (word[z] == '1') { if (lo > hi) lo = hi = (long long)z; else hi = (long long)z; }
        fprintf(stderr, "start word length %zu\n", word.size());
    }
    long long lines = 0, kept = 0;
    std::vector<std::pair<int, long long>> runs;
    for (long long s = 0; s < maxs; ++s) {
        if (pos + off < 2 || pos + off + 2 >= size) {
            std::vector<unsigned char> nt(size * 2, 0);
            memcpy(nt.data() + size / 2, t.data(), size);
            off += size / 2; size *= 2; t.swap(nt);
        }
        unsigned char *T = t.data() + off;
        int c = T[pos];
        if (c == 0 && lo <= hi && s >= skip) {
            while (lo <= hi && !T[hi]) --hi;
            while (lo <= hi && !T[lo]) ++lo;
            char sd = 0;
            if (pos > hi) sd = 'R'; else if (pos < lo) sd = 'L';
            if (sd && (side == 'B' || side == sd) && (states == "*" || states.find(char('A' + q)) != std::string::npos)) {
                if (kept++ % every == 0) {
                    runs.clear();
                    long long a = sd == 'R' ? lo : hi, b = pos, dir = sd == 'R' ? 1 : -1;
                    for (long long i = a; i != b;) {
                        long long j = i; while (j != b && T[j] == T[i]) j += dir;
                        runs.push_back({T[i], (j - i) * dir}); i = j;
                    }
                    auto tok = [](const std::pair<int, long long> &r) {
                        if (r.second >= 4) return std::string(1, '0' + r.first) + "^" + std::to_string(r.second);
                        return std::string(r.second, '0' + r.first);
                    };
                    std::string out;
                    for (size_t i = 0; i < runs.size() && out.size() < maxch;) {
                        size_t bp = 0, bk = 1;
                        for (size_t p = 2; p <= 6; ++p) {
                            size_t k = 1;
                            while (i + (k + 1) * p <= runs.size()) {
                                bool same = true;
                                for (size_t x = 0; x < p; ++x) if (runs[i + k * p + x] != runs[i + x]) { same = false; break; }
                                if (!same) break;
                                ++k;
                            }
                            if (k >= 3 && k * p > bk * bp) { bp = p; bk = k; }
                        }
                        if (bp) {
                            out += "(";
                            for (size_t x = 0; x < bp; ++x) { if (x) out += " "; out += tok(runs[i + x]); }
                            out += ")x" + std::to_string(bk) + " ";
                            i += bp * bk;
                        } else { out += tok(runs[i]) + " "; ++i; }
                    }
                    if (out.size() >= maxch) out += "...";
                    printf("%lld %c %c w=%lld | %s\n", s, sd, 'A' + q, hi - lo + 1, out.c_str());
                    if (++lines >= maxlines) return 0;
                }
            }
        }
        if (NX[q][c] < 0) { printf("HALT at step %lld state %c\n", s, 'A' + q); return 0; }
        T[pos] = (unsigned char)W[q][c];
        if (W[q][c]) { if (lo > hi) lo = hi = pos; else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; } }
        pos += D[q][c]; q = NX[q][c];
    }
    return 0;
}
