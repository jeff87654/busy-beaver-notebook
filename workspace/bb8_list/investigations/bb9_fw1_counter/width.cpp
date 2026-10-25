// width: run machine from blank, print tape span (max-min visited) at steps 2^k; also halts.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
int W[16][2], D[16][2], NX[16][2];
int main(int argc, char **argv) {
    std::string m = argv[1]; long long maxs = atoll(argv[2]);
    int n = (int)(m.size() + 1) / 7;
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * q + 3 * c;
        if (x[0] == '-') { NX[q][c] = -1; continue; } W[q][c] = x[0] - '0'; D[q][c] = x[1] == 'R' ? 1 : -1; NX[q][c] = x[2] - 'A'; }
    long long size = 1 << 22, off = size / 2; std::vector<unsigned char> t(size, 0);
    long long pos = 0, lo = 0, hi = 0; int q = 0; long long nextp = 1024;
    for (long long st = 0; st < maxs; ++st) {
        if (pos + off < 2 || pos + off + 2 >= size) { std::vector<unsigned char> nt(size * 2, 0); memcpy(nt.data() + size / 2, t.data(), size); off += size / 2; size *= 2; t.swap(nt); }
        unsigned char *T = t.data() + off; int c = T[pos];
        if (NX[q][c] < 0) { long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += T[i]; printf("HALT %lld state %c read %d ones %lld\n", st, 'A' + q, c, ones); return 0; }
        T[pos] = W[q][c]; pos += D[q][c]; q = NX[q][c];
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (st + 1 == nextp) { long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += T[i]; printf("%lld span %lld (L %lld R %lld) ones %lld\n", st + 1, hi - lo + 1, -lo, hi, ones); fflush(stdout); nextp *= 2; }
    }
    printf("END\n");
}
