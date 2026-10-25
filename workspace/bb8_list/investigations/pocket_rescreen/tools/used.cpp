// used N < machines : run from blank tape N steps; print machine, status, used-transition mask (A0 A1 B0 ...), and the
// machine restricted to used transitions (unused slots shown as ...), so rows identical on used slots group together.
#include <cstdio>
#include <cstring>
#include <vector>
#include <string>
int main(int argc, char **argv) {
    long long N = atoll(argv[1]); char line[256];
    while (scanf("%255s", line) == 1) {
        int n = (strlen(line) + 1) / 7, w[16][2], d[16][2], nx[16][2]; bool def[16][2];
        for (int q = 0; q < n; ++q) for (int s = 0; s < 2; ++s) {
            const char *c = line + q * 7 + s * 3;
            def[q][s] = c[0] != '-' && c[2] != '-' && c[2] - 'A' < n;
            if (def[q][s]) { w[q][s] = c[0] - '0'; d[q][s] = c[1] == 'R' ? 1 : -1; nx[q][s] = c[2] - 'A'; }
        }
        std::vector<unsigned char> t(1 << 22, 0); long long p = 1 << 21; int q = 0; long long i; bool used[16][2] = {};
        const char *st = "RUN";
        for (i = 0; i < N; ++i) {
            int s = t[p]; used[q][s] = true;
            if (!def[q][s]) { st = "HALT"; break; }
            t[p] = w[q][s]; p += d[q][s]; q = nx[q][s];
            if (p < 1 || p >= (long long)t.size() - 1) { st = "WIDE"; break; }
        }
        std::string r;
        for (int a = 0; a < n; ++a) { if (a) r += '_'; for (int s = 0; s < 2; ++s) r += used[a][s] ? std::string(line + a * 7 + s * 3, 3) : std::string("..."); }
        printf("%s %s %lld %s\n", line, st, i, r.c_str()); fflush(stdout);
    }
}
