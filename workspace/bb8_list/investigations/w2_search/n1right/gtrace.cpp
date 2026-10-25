// gtrace.cpp: literal tracer for n-state machines (n <= 16).
// usage: gtrace MACHINE STATE HEAD MAXS SLOTS WIN [KSTOP] < bits
//   prints "step state sym pos | window" for every read of a slot in SLOTS (e.g. "E0,I0,I1,J0,J1,K0" or "-")
//   stops at an undefined slot (HALT), at MAXS, or (KSTOP=1) at a K-moment: state G reading 0 right of the last 1
//   with the tape ending ...1 1010 (prints the final word and the head offset).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
struct Tr { int w, d, nx; bool def; };
int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage\n"); return 1; }
    const char *ms = argv[1]; int n = (strlen(ms) + 1) / 7;
    Tr m[32];
    for (int q = 0; q < 16; ++q) for (int c = 0; c < 2; ++c) m[2*q+c] = {0,0,0,false};
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) {
        const char *x = ms + 7 * q + 3 * c;
        if (x[0] != '-' && x[2] != 'Z') m[2*q+c] = {x[0]-'0', x[1]=='R'?1:-1, x[2]-'A', true};
    }
    int q = argv[2][0] - 'A'; long long head = atoll(argv[3]); long long MAXS = atoll(argv[4]);
    bool want[32] = {false};
    if (argv[5][0] != '-') {
        std::string s = argv[5]; size_t i = 0;
        while (i < s.size()) { want[2*(s[i]-'A') + (s[i+1]-'0')] = true; i += 3; }
    }
    int WIN = atoi(argv[6]); bool kstop = argc > 7 && atoi(argv[7]);
    std::string bits; int ch; while ((ch = getchar()) != EOF) if (ch == '0' || ch == '1') bits += (char)ch;
    long long N = bits.size() * 4 + (1 << 20);
    std::vector<unsigned char> t(N, 0); long long off = N / 2;
    for (size_t i = 0; i < bits.size(); ++i) t[off + i] = bits[i] - '0';
    long long pos = off + head, lo = off, hi = off + bits.size() - 1, steps = 0;
    long long r1 = hi; while (r1 >= lo && !t[r1]) --r1;
    auto win = [&](long long p) {
        std::string s;
        for (long long i = p - WIN; i <= p + WIN; ++i) { if (i == p) s += '['; s += (i>=0 && i<N) ? char('0'+t[i]) : '?'; if (i == p) s += ']'; }
        return s;
    };
    while (steps < MAXS) {
        int s = t[pos];
        if (kstop && q == 6 && s == 0 && pos > r1 && steps > 0 && pos - 5 >= lo && t[pos-5]==1 && t[pos-4]==1 && t[pos-3]==0 && t[pos-2]==1 && t[pos-1]==0) {
            long long a = lo; while (!t[a]) ++a;
            printf("K %lld head=%lld word=", steps, pos - a);
            for (long long i = a; i <= r1; ++i) putchar('0' + t[i]);
            printf("\n"); return 0;
        }
        if (want[2*q+s]) printf("%lld %c%d pos=%lld | %s\n", steps, 'A'+q, s, pos - off, win(pos).c_str());
        const Tr &x = m[2*q+s];
        if (!x.def) {
            long long a = lo; while (a <= hi && !t[a]) ++a; long long b = hi; while (b >= lo && !t[b]) --b;
            long long ones = 0; for (long long i = a; i <= b; ++i) ones += t[i];
            printf("HALT %lld %c%d pos=%lld ones=%lld word=", steps, 'A'+q, s, pos - off, ones);
            for (long long i = std::min(a, pos); i <= std::max(b, pos); ++i) { if (i == pos) putchar('['); putchar('0' + t[i]); if (i == pos) putchar(']'); }
            printf(" off=%lld\n", std::min(a,pos) - off);
            return 0;
        }
        t[pos] = x.w;
        if (x.w && pos > r1) r1 = pos;
        else if (!x.w && pos == r1) { while (r1 >= lo && !t[r1]) --r1; }
        pos += x.d; q = x.nx; ++steps;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (pos <= 1 || pos >= N - 2) { printf("WIDTH %lld\n", steps); return 0; }
    }
    printf("MAXS %lld\n", steps);
    return 0;
}
