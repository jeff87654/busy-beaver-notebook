// ev: edge viewer. ev MACHINE N MAXOUT SIDE(L/R/B) [EVERY]
// prints "step side state | RLE(tape)" whenever the head extends the visited region on the given side (every EVERY-th extension)
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <cstdint>
int nx[16][2], wr[16][2], dr[16][2];
int main(int argc, char **argv) {
    const char *M = argv[1]; long long N = atoll(argv[2]), maxout = atoll(argv[3]); char side = argv[4][0];
    long long every = argc > 5 ? atoll(argv[5]) : 1;
    int ns = 0;
    for (const char *t = M; *t; ) { for (int c = 0; c < 2; ++c) { if (t[0] == '-') nx[ns][c] = -1; else { wr[ns][c] = t[0]-'0'; dr[ns][c] = t[1]=='R'?1:-1; nx[ns][c] = t[2]-'A'; } t += 3; } ++ns; if (*t == '_') ++t; }
    long long SZ = 1LL << 27; std::vector<uint8_t> T(SZ, 0); long long p = SZ/2, lo = p, hi = p; int q = 0; long long nout = 0, cnt = 0;
    if (argc > 6) { std::string init = argv[6]; FILE *fi = fopen(argv[6], "r");
      if (fi) { std::string all; int ch; while ((ch = fgetc(fi)) != EOF) if (ch != 10 && ch != 13) all.push_back((char)ch); fclose(fi); init = all; }
      q = init[0]-'A'; std::string b = init.substr(2);
      if (init[1]=='<') { for (size_t i=0;i<b.size();++i) T[p+1+i]=b[i]-'0'; hi = p + b.size(); }
      else { for (size_t i=0;i<b.size();++i) T[p-(long long)b.size()+i]=b[i]-'0'; lo = p-(long long)b.size(); } }
    for (long long st = 0; st < N; ++st) {
        int c = T[p]; if (nx[q][c] < 0) { printf("H %lld\n", st); return 0; }
        T[p] = wr[q][c]; p += dr[q][c]; q = nx[q][c];
        if (p <= 1 || p >= SZ-2) { printf("TAPE\n"); return 0; }
        bool ext = false; char sd = 0;
        if (p > hi) { hi = p; if (side == 'R' || side == 'B') { ext = true; sd = 'R'; } }
        if (p < lo) { lo = p; if (side == 'L' || side == 'B') { ext = true; sd = 'L'; } }
        if (!ext) continue;
        if (++cnt % every) continue;
        std::string o; long long i = lo;
        while (i <= hi) { long long j = i; while (j <= hi && T[j] == T[i]) ++j; o += char('0'+T[i]); if (j-i>1) o += "^" + std::to_string(j-i); o += '.'; i = j; }
        printf("%lld %c %c | %s\n", st+1, sd, 'A'+q, o.c_str());
        if (++nout >= maxout) return 0;
    }
    printf("END\n");
}
