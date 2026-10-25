// geo: geometry screen. For each machine (stdin lines, first token), run from blank MAXS steps; report
// lo/hi at 2^16,2^20,2^24,2^28, number of left/right frontier extensions after 2^20 steps, and rare slots
// (read count <= 200) with their read counts and last read step.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
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
        long long size = 1 << 22, off = size / 2; std::vector<unsigned char> t(size, 0);
        long long pos = 0, lo = 0, hi = 0; int q = 0; long long cnt[16][2] = {}, last[16][2] = {};
        long long nl = 0, nr = 0; std::string cp; long long nextp = 1 << 16; std::string res = "END";
        for (long long st = 0; st < maxs; ++st) {
            if (pos + off < 2 || pos + off + 2 >= size) { std::vector<unsigned char> nt(size * 2, 0); memcpy(nt.data() + size / 2, t.data(), size); off += size / 2; size *= 2; t.swap(nt); }
            unsigned char *T = t.data() + off; int c = T[pos];
            cnt[q][c]++; last[q][c] = st;
            if (NX[q][c] < 0) { res = "HALT@" + std::to_string(st); break; }
            T[pos] = W[q][c]; pos += D[q][c]; q = NX[q][c];
            if (pos < lo) { lo = pos; if (st > (1 << 20)) nl++; }
            if (pos > hi) { hi = pos; if (st > (1 << 20)) nr++; }
            if (st + 1 == nextp) { cp += std::to_string(-lo) + "/" + std::to_string(hi) + " "; nextp *= 16; }
        }
        std::string rare;
        for (int qq = 0; qq < n; ++qq) for (int c = 0; c < 2; ++c) if (NX[qq][c] >= 0 && cnt[qq][c] <= 200) {
            char b[64]; snprintf(b, 64, "%c%d:%lld@%lld ", 'A' + qq, c, cnt[qq][c], last[qq][c]); rare += b; }
        printf("%s\t%s\t%s\tnl=%lld nr=%lld\t%s\n", m.c_str(), res.c_str(), cp.c_str(), nl, nr, rare.c_str()); fflush(stdout);
    }
}
