// win MACHINE N R : histogram of windows (radius R) at moments the machine enters the halting state Q (the one with an undefined entry)
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <map>
#include <string>
int W[16][2], D[16][2], NX[16][2];
int main(int argc, char **argv) {
    const char *p = argv[1]; int ns = 0;
    while (*p) { for (int c = 0; c < 2; ++c) { if (p[0] == '-') NX[ns][c] = -1; else { W[ns][c] = p[0]-'0'; D[ns][c] = p[1]=='R'?1:-1; NX[ns][c] = p[2]-'A'; } p += 3; } ns++; if (*p == '_') ++p; }
    int HQ = -1, HC = -1; for (int s = 0; s < ns; ++s) for (int c = 0; c < 2; ++c) if (NX[s][c] < 0) { HQ = s; HC = c; }
    long long N = atoll(argv[2]); int R = atoi(argv[3]);
    const long long SZ = 1 << 22; std::vector<unsigned char> T(SZ, 0); long long h = SZ / 2; int q = 0;
    std::map<std::string, long long> hist; long long lo = h, hi = h;
    for (long long st = 0; st < N; ++st) {
        int c = T[h];
        if (NX[q][c] < 0) { printf("HALT %lld\n", st); break; }
        int prevq = q;
        T[h] = W[q][c]; h += D[q][c]; q = NX[q][c];
        if (h < lo) lo = h; if (h > hi) hi = h;
        if (q == HQ && prevq != HQ) {
            std::string s;
            for (long long i = h - R; i <= h + R; ++i) { char ch = (i < lo || i > hi) ? '.' : (T[i] ? '1' : '0'); if (i == h) { s += '['; s += ch; s += ']'; } else s += ch; }
            s += " from "; s += (char)('A' + prevq);
            hist[s]++;
        }
    }
    printf("halt state %c reading %d\n", 'A' + HQ, HC);
    for (auto &kv : hist) printf("%12lld %s\n", kv.second, kv.first.c_str());
}
