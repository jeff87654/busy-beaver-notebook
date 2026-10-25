// peek: for machines on stdin, run MAXS steps from blank. Determine the static side (fewer frontier
// extensions after step 2^20). Print the tape near that end (first 24 cells) and, for the outermost 8 cells,
// which slots were read there after step 2^18 (counts), plus total slot counts for those slots.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <map>
#include <iostream>
int W[16][2], D[16][2], NX[16][2];
int main(int argc, char **argv) {
    long long maxs = atoll(argv[1]);
    std::string line;
    while (std::getline(std::cin, line)) {
        std::string m = line.substr(0, line.find_first_of(" \t"));
        if (m.size() < 6) continue;
        int n = (int)(m.size() + 1) / 7;
        for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * q + 3 * c;
            if (x[0] == '-') { NX[q][c] = -1; continue; } W[q][c] = x[0] - '0'; D[q][c] = x[1] == 'R' ? 1 : -1; NX[q][c] = x[2] - 'A'; }
        long long size = 1 << 24, off = size / 2; std::vector<unsigned char> t(size, 0);
        long long pos = 0, lo = 0, hi = 0; int q = 0; long long nl = 0, nr = 0;
        // per (cell offset from lo / from hi, slot) counts after 2^18
        long long cL[8][16][2] = {}, cR[8][16][2] = {}, tot[16][2] = {};
        std::string res = "END";
        for (long long st = 0; st < maxs; ++st) {
            if (pos + off < 2 || pos + off + 2 >= size) { std::vector<unsigned char> nt(size * 2, 0); memcpy(nt.data() + size / 2, t.data(), size); off += size / 2; size *= 2; t.swap(nt); }
            unsigned char *T = t.data() + off; int c = T[pos];
            if (st > (1 << 18)) { tot[q][c]++; long long dl = pos - lo, dr = hi - pos; if (dl < 8) cL[dl][q][c]++; if (dr < 8) cR[dr][q][c]++; }
            if (NX[q][c] < 0) { res = "HALT@" + std::to_string(st); break; }
            T[pos] = W[q][c]; pos += D[q][c]; q = NX[q][c];
            if (pos < lo) { lo = pos; if (st > (1 << 20)) nl++; }
            if (pos > hi) { hi = pos; if (st > (1 << 20)) nr++; }
        }
        bool left = nl <= nr; unsigned char *T = t.data() + off;
        std::string w; for (int i = 0; i < 24; ++i) { long long p = left ? lo + i : hi - i; w += char('0' + T[p]); }
        printf("%s\t%s\tstatic=%s nl=%lld nr=%lld\tend=%s\t", m.c_str(), res.c_str(), left ? "L" : "R", nl, nr, w.c_str());
        for (int d = 0; d < 8; ++d) { printf("[%d:", d); for (int qq = 0; qq < n; ++qq) for (int c = 0; c < 2; ++c) { long long k = left ? cL[d][qq][c] : cR[d][qq][c]; if (k) printf(" %c%d=%lld/%lld", 'A' + qq, c, k, tot[qq][c]); } printf("]"); }
        printf("\n"); fflush(stdout);
    }
}
