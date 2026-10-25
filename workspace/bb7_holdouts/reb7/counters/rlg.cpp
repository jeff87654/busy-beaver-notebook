// rlg: like rl but general u/s/S block language. Tape left of head (template orientation): PREFIX u^r0 s u^r1 s ... u^rn S, head in Q on blank.
//  rlg MACHINE O Q u s S MAXSTEPS MAXOUT MODE < "r0 ... rn" | "B" | "P:<prefixbits> r0 ... rn"
//  mode 0: print when r[-2]==0 ; 1: every moment ; 2: when #runs/#odd/prefix changes
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <cstdint>
#include <algorithm>
int nx[16][2], wr[16][2], dr[16][2];
static std::string rle(const std::string &w) {
    std::string o; size_t i = 0;
    while (i < w.size()) { size_t j = i; while (j < w.size() && w[j] == w[i]) ++j; o += w[i]; if (j - i > 1) o += "^" + std::to_string(j - i); o += '.'; i = j; }
    return o.empty() ? "-" : o;
}
int main(int argc, char **argv) {
    if (argc < 10) return 2;
    const char *M = argv[1]; bool mir = argv[2][0] == 'L'; int Q = argv[3][0] - 'A';
    std::string u = argv[4], s = argv[5], S = argv[6]; if (s == "-") s = ""; if (S == "-") S = "";
    long long N = atoll(argv[7]), maxout = atoll(argv[8]); int mode = atoi(argv[9]);
    int ns = 0;
    for (const char *t = M; *t; ) {
        for (int c = 0; c < 2; ++c) {
            if (t[0] == '-' || t[2] == 'H' || t[2] == '-') nx[ns][c] = -1;
            else { wr[ns][c] = t[0] - '0'; dr[ns][c] = (t[1] == 'R') ? 1 : -1; if (mir) dr[ns][c] = -dr[ns][c]; nx[ns][c] = t[2] - 'A'; }
            t += 3;
        }
        ++ns; if (*t == '_') ++t;
    }
    long long SZ = 1LL << 27;
    std::vector<uint8_t> T(SZ, 0);
    long long p = SZ / 2; int q;
    std::vector<long long> init; char buf[1 << 16]; std::string pre;
    bool blank = false;
    while (scanf("%65535s", buf) == 1) { if (buf[0] == 'B') blank = true; else if (buf[0] == 'P') pre = buf + 2; else init.push_back(atoll(buf)); }
    long long lo = p;
    if (blank) q = 0;
    else {
        q = Q; std::string w = pre;
        for (size_t i = 0; i < init.size(); ++i) { if (i) w += s; for (long long k = 0; k < init[i]; ++k) w += u; }
        w += S;
        for (size_t i = 0; i < w.size(); ++i) T[p - (long long)w.size() + (long long)i] = w[i] - '0';
        lo = p - (long long)w.size();
    }
    long long hi = p; long long nout = 0; size_t lastn = 0; long long lastodd = -1; std::string lastpre = "#";
    std::vector<long long> R;
    for (long long st = 0; st < N; ++st) {
        if (p <= 2 || p >= SZ - 2) { printf("TAPE %lld\n", st); return 0; }
        int c = T[p];
        if (nx[q][c] < 0) { long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += T[i]; printf("H %lld %lld\n", st, ones); return 0; }
        T[p] = wr[q][c]; if (T[p]) { if (p < lo) lo = p; if (p > hi) hi = p; }
        p += dr[q][c]; q = nx[q][c];
        if (q != Q || T[p]) continue;
        while (hi > lo && !T[hi]) --hi;
        if (hi > p) continue;
        while (lo < p && !T[lo]) ++lo;
        long long L = p - lo; if (L <= 0 || L > 50000000) continue;
        // match S
        long long x = p;
        bool ok = true;
        for (long long i = 0; i < (long long)S.size(); ++i) if (T[p - (long long)S.size() + i] != S[i] - '0') { ok = false; break; }
        if (!ok) continue;
        x = p - (long long)S.size();
        auto match = [&](long long end, const std::string &w) { if (end - (long long)w.size() < lo - 64) return false; for (size_t i = 0; i < w.size(); ++i) if (T[end - (long long)w.size() + (long long)i] != w[i] - '0') return false; return true; };
        R.clear();
        for (;;) {
            long long k = 0;
            while (x > lo - 1 && match(x, u)) { x -= (long long)u.size(); ++k; if (x <= lo) break; }
            R.push_back(k);
            if (x <= lo) break;
            if (s.empty() || !match(x, s)) break;
            x -= (long long)s.size();
            if (x <= lo) { R.push_back(0); break; }
        }
        std::reverse(R.begin(), R.end());
        std::string P;
        for (long long i = lo; i < x; ++i) P += char('0' + T[i]);
        if (R.size() < 2 && mode != 3) continue;
        if (R.size() < 2) R.assign(2, 1);
        long long odd = 0; for (auto v : R) odd += v & 1;
        bool pr;
        if (mode == 1) pr = true;
        else if (mode == 0 || mode == 4) pr = R[R.size() - 2] == 0;
        else pr = R.size() != lastn || odd != lastodd || P != lastpre;
        lastn = R.size(); lastodd = odd; lastpre = P;
        if (!pr) continue;
        if (mode == 3 || mode == 4) { std::string all; for (long long i = lo; i < p; ++i) all += char(48 + T[i]); printf("%lld | %s\n", st + 1, rle(all).c_str()); if (++nout >= maxout) { printf("END maxout\n"); return 0; } continue; }
        printf("%lld | %s |", st + 1, rle(P).c_str());
        for (size_t j = 0; j < R.size(); ) { size_t e = j; while (e < R.size() && R[e] == R[j]) ++e; if (e - j > 1) printf(" %lldx%zu", R[j], e - j); else printf(" %lld", R[j]); j = e; }
        printf("\n"); fflush(stdout);
        if (++nout >= maxout) { printf("END maxout\n"); return 0; }
    }
    printf("END %lld\n", N);
}
