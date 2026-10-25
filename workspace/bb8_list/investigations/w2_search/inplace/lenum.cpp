// lenum.cpp: lazy TNF enumeration of n1 + J0 + new states (literal screen).
// Start: tape bits (stdin), head at the right end, state G.  The run is literal; when an undefined free slot
// (J0 or a new state's slot) is read, branch over halt + all {0,1}x{L,R}x(A..J, used new states, next new state).
// A leaf ends at the first K-moment (state G reading 0 right of the last 1, tape ending 1 1010) AFTER the first J0
// read, or at MAXS / width.  Output per leaf: machine, kind, steps, far-ones (ones left of the parsed token list),
// ntok, token summary (nearest-first up to 12).
// usage: lenum NS MAXS MAXNODES < bits
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
struct Tr { int w, d, nx; bool def; };
static const char *BASE = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC";
static int NS; static long long LISTPOS = 0; static long long MAXS, MAXNODES, nodes = 0;
static std::string bits;
static std::vector<unsigned char> T0;
static std::string mstr(Tr *m) {
    std::string s;
    for (int q = 0; q < 10 + NS; ++q) {
        if (q) s += '_';
        for (int c = 0; c < 2; ++c) {
            const Tr &x = m[2*q+c];
            if (!x.def) s += "---";
            else { s += char('0'+x.w); s += x.d > 0 ? 'R' : 'L'; s += char('A'+x.nx); }
        }
    }
    return s;
}
static void dfs(Tr *m) {
    if (++nodes > MAXNODES) return;
    long long N = T0.size();
    std::vector<unsigned char> t(T0);
    long long off = N / 2, pos = off + bits.size(), lo = off, hi = pos, steps = 0;
    long long r1 = off + bits.size() - 1; while (r1 >= lo && !t[r1]) --r1;
    int q = 6; bool seenJ0 = false;
    while (true) {
        int s = t[pos];
        if (seenJ0 && q == 6 && s == 0 && pos > r1 && pos - 5 >= lo && t[pos-5]==1 && t[pos-4]==1 && t[pos-3]==0 && t[pos-2]==1 && t[pos-1]==0) {
            // parse tokens from the right
            long long p = pos - 5; std::vector<long long> tok;
            while (p >= lo && t[p] == 1) {
                long long mm = 0; --p;
                while (p - 1 >= lo && t[p] == 0 && t[p-1] == 1) { ++mm; p -= 2; }
                tok.push_back(mm);
            }
            long long fo = 0; for (long long i = lo; i <= p; ++i) fo += t[i];
            long long lm = lo; while (!t[lm]) ++lm;
            printf("%s	K	%lld	far=%lld	ntok=%zu	left=%lld	len=%lld	", mstr(m).c_str(), steps, fo, tok.size(), lm - (off + LISTPOS), r1 - lm + 1);
            for (size_t i = 0; i < tok.size() && i < 14; ++i) printf("%lld ", tok[i]);
            printf("\n");
            return;
        }
        Tr &x = m[2*q+s];
        if (!x.def) {
            bool freeslot = (q == 9 && s == 0) || q >= 10;
            if (!freeslot) { printf("%s\tHB\t%lld\n", mstr(m).c_str(), steps); return; }
            long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += t[i];
            printf("%s\tH%c%d\t%lld\tones=%lld\n", mstr(m).c_str(), 'A'+q, s, steps, ones);
            // branch
            int used = 0; for (int k = 0; k < NS; ++k) { bool u = false; for (int i = 0; i < 2*(10+NS); ++i) if (m[i].def && m[i].nx == 10+k) u = true; if (u) used = k+1; }
            int maxst = 10 + std::min(NS, used + 1);
            for (int w = 0; w < 2; ++w) for (int d = 0; d < 2; ++d) for (int nx = 0; nx < maxst; ++nx) {
                x = {w, d ? 1 : -1, nx, true};
                dfs(m);
            }
            x.def = false;
            return;
        }
        if (q == 9 && s == 0) seenJ0 = true;
        t[pos] = x.w;
        if (x.w && pos > r1) r1 = pos; else if (!x.w && pos == r1) { while (r1 >= lo && !t[r1]) --r1; }
        pos += x.d; q = x.nx; ++steps;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (steps >= MAXS) { printf("%s\tT\t%lld\n", mstr(m).c_str(), steps); return; }
        if (pos <= 1 || pos >= N - 2) { printf("%s\tW\t%lld\n", mstr(m).c_str(), steps); return; }
    }
}
int main(int argc, char **argv) {
    NS = atoi(argv[1]); MAXS = atoll(argv[2]); MAXNODES = atoll(argv[3]); if (argc > 4) LISTPOS = atoll(argv[4]);
    int ch; while ((ch = getchar()) != EOF) if (ch == '0' || ch == '1') bits += (char)ch;
    T0.assign(bits.size() * 2 + 400000, 0);
    long long off = T0.size() / 2; for (size_t i = 0; i < bits.size(); ++i) T0[off+i] = bits[i]-'0';
    Tr m[32];
    for (int i = 0; i < 32; ++i) m[i] = {0,0,0,false};
    for (int q = 0; q < 10; ++q) for (int c = 0; c < 2; ++c) {
        const char *x = BASE + 7*q + 3*c;
        if (x[0] != '-') m[2*q+c] = {x[0]-'0', x[1]=='R'?1:-1, x[2]-'A', true};
    }
    dfs(m);
    fprintf(stderr, "nodes %lld\n", nodes);
}
