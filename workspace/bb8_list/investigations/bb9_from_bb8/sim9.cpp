// sim9.cpp: plain literal Turing machine simulator for any number of states (up to 16), no tape limit.
//   sim9 MACHINE TAPE HEAD STATE MAXSTEPS [RLE_CHARS=240]
// TAPE is the initial word (0/1), HEAD the head index into it (it may equal the word length = the blank right of it),
// STATE a letter.  Prints a line at every 10^k steps (k >= 6) and at a halt: steps, state, ones, width and a
// run-length view of the tape (runs of 10 / 01 pairs compressed), truncated to RLE_CHARS characters.
// Build: g++ -O2 -std=c++17 -static -o sim9.exe sim9.cpp   (PATH must include C:\msys64\ucrt64\bin)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

struct Tr { int w, d, nx; bool def; };

static std::string rle(const std::vector<unsigned char> &t, long long lo, long long hi, size_t maxc) {
    std::string out;
    long long i = lo;
    while (i <= hi && out.size() < maxc) {
        // pair runs
        if (i + 3 <= hi && t[i] != t[i + 1] && t[i + 2] == t[i] && t[i + 3] == t[i + 1]) {
            long long j = i;
            while (j + 1 <= hi && t[j] == t[i] && t[j + 1] == t[i + 1]) j += 2;
            out += "(" + std::to_string(t[i]) + std::to_string(t[i + 1]) + ")^" + std::to_string((j - i) / 2) + " ";
            i = j;
            continue;
        }
        long long j = i;
        while (j <= hi && t[j] == t[i]) ++j;
        if (j - i >= 4) out += std::to_string(t[i]) + "^" + std::to_string(j - i) + " ";
        else { for (long long k = i; k < j; ++k) out += char('0' + t[k]); out += " "; }
        i = j;
    }
    if (i <= hi) out += "...";
    return out;
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: sim9 MACHINE TAPE HEAD STATE MAXSTEPS [RLE_CHARS]\n"); return 2; }
    std::string m = argv[1];
    int n = (int)(m.size() + 1) / 7;
    std::vector<Tr> tr(2 * n);
    for (int q = 0; q < n; ++q)
        for (int c = 0; c < 2; ++c) {
            const char *x = m.c_str() + 7 * q + 3 * c;
            if (x[0] == '-' || x[2] == 'Z') { tr[2 * q + c] = {0, 0, 0, false}; continue; }
            tr[2 * q + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true};
        }
    std::string word = argv[2];
    if (word == "-") word = "";
    long long head = atoll(argv[3]);
    int q = argv[4][0] - 'A';
    long long maxs = atoll(argv[5]);
    size_t maxc = argc > 6 ? (size_t)atoll(argv[6]) : 240;
    long long size = 1 << 20, off = size / 2;
    std::vector<unsigned char> t(size, 0);
    for (size_t i = 0; i < word.size(); ++i) t[off + i] = word[i] == '1';
    long long pos = off + head, lo = off, hi = off + (long long)word.size() - 1;
    long long next = 1000000, steps = 0;
    while (steps < maxs) {
        const Tr &x = tr[2 * q + t[pos]];
        if (!x.def) {
            long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += t[i];
            printf("HALT at step %lld in state %c reading %d: ones %lld (+1 for the final write), width %lld\n  %s\n",
                   steps, 'A' + q, t[pos], ones, hi - lo + 1, rle(t, lo, hi, maxc).c_str());
            return 0;
        }
        t[pos] = (unsigned char)x.w; pos += x.d; q = x.nx; ++steps;
        if (pos < lo) lo = pos;
        if (pos > hi) hi = pos;
        if (pos <= 0 || pos >= size - 1) {           // grow the tape, keep it centred
            std::vector<unsigned char> u(2 * size, 0);
            memcpy(u.data() + size / 2, t.data(), size);
            pos += size / 2; lo += size / 2; hi += size / 2; off += size / 2;
            t.swap(u); size *= 2;
        }
        if (steps == next) {
            long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += t[i];
            printf("step %lld: state %c, ones %lld, width %lld\n  %s\n", steps, 'A' + q, ones, hi - lo + 1,
                   rle(t, lo, hi, maxc).c_str());
            fflush(stdout);
            next *= 10;
        }
    }
    printf("no halt within %lld steps\n", maxs);
    return 0;
}
