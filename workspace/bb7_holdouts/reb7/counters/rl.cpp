// rl: literal run from a constructed RUN LIST (runs of 1s separated by single 0s, then S='0', head in state Q on blank),
// machine mirrored if O=L. Prints run lists at moments (state Q, head on blank, tape right of head blank, cell left = 0):
//  mode 0: only when run[-2]==0 (end of D phase); mode 1: every moment; mode 2: only when #runs or number of odd runs changes
//  rl MACHINE O Q MAXSTEPS MAXOUT MODE  < "r0 r1 ... rn"   ("B" = start from blank tape in state A)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <cstdint>
int nx[16][2], wr[16][2], dr[16][2];
int main(int argc, char **argv) {
    if (argc < 7) return 2;
    const char *M = argv[1]; bool mir = argv[2][0] == 'L'; int Q = argv[3][0] - 'A';
    long long N = atoll(argv[4]), maxout = atoll(argv[5]); int mode = atoi(argv[6]);
    int ns = 0;
    for (const char *s = M; *s; ) {
        for (int c = 0; c < 2; ++c) {
            if (s[0] == '-' || s[2] == 'H' || s[2] == '-') nx[ns][c] = -1;
            else { wr[ns][c] = s[0] - '0'; dr[ns][c] = (s[1] == 'R') ? 1 : -1; if (mir) dr[ns][c] = -dr[ns][c]; nx[ns][c] = s[2] - 'A'; }
            s += 3;
        }
        ++ns; if (*s == '_') ++s;
    }
    long long SZ = 1LL << 28;
    std::vector<uint8_t> T(SZ, 0);
    long long p = SZ / 2; int q;
    std::vector<long long> init; char buf[64];
    bool blank = false;
    while (scanf("%63s", buf) == 1) { if (buf[0] == 'B') blank = true; else init.push_back(atoll(buf)); }
    long long lo;
    if (blank) { q = 0; lo = p; }
    else {
        q = Q; long long z = p - 1; T[z] = 0; --z; // S
        for (int i = (int)init.size() - 1; i >= 0; --i) { for (long long k = 0; k < init[i]; ++k) T[z--] = 1; if (i) T[z--] = 0; }
        lo = z + 1;
    }
    long long hi = p; long long nout = 0; size_t lastn = 0; long long lastodd = -1;
    std::vector<long long> R;
    for (long long st = 0; st < N; ++st) {
        if (p <= 2 || p >= SZ - 2) { printf("TAPE %lld\n", st); return 0; }
        int c = T[p];
        if (nx[q][c] < 0) { long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += T[i]; printf("H %lld %lld\n", st, ones); return 0; }
        T[p] = wr[q][c]; if (T[p]) { if (p < lo) lo = p; if (p > hi) hi = p; }
        p += dr[q][c]; q = nx[q][c];
        if (q != Q || T[p] || T[p - 1]) continue;
        while (hi > lo && !T[hi]) --hi;
        if (hi > p) continue;
        while (lo < p && !T[lo]) ++lo;
        if (lo >= p - 1) continue;
        // runs from lo to p-2 (p-1 is S)
        R.clear(); long long k = 0; bool bad = false; long long i = lo;
        for (; i <= p - 2; ++i) {
            if (T[i]) ++k; else { R.push_back(k); k = 0; }
        }
        R.push_back(k);
        long long odd = 0; for (auto v : R) odd += v & 1;
        bool pr = false;
        if (mode == 1) pr = true;
        else if (mode == 0) pr = R.size() >= 2 && R[R.size() - 2] == 0;
        else pr = R.size() != lastn || odd != lastodd;
        lastn = R.size(); lastodd = odd;
        if (!pr) continue;
        printf("%lld |", st + 1);
        for (size_t j = 0; j < R.size(); ) { size_t e = j; while (e < R.size() && R[e] == R[j]) ++e; if (e - j > 1) printf(" %lldx%zu", R[j], e - j); else printf(" %lld", R[j]); j = e; }
        printf("\n"); fflush(stdout);
        if (++nout >= maxout) { printf("END maxout\n"); return 0; }
    }
    printf("END %lld\n", N);
}
