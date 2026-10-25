// ms: macro (block-k) run-length simulator with self-loop run acceleration.
// usage: ms MACHINE K MAXMACRO PRINTEVERY [maxsteps_log10]
// prints tape snapshots (run-length, block symbols as k-bit strings) every PRINTEVERY macro steps,
// and "H steps ones" at halt.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <cmath>
#include <map>
typedef unsigned long long u64;
typedef long double LD;
int NS; int W[16][2], D[16][2], NX[16][2];
int K;
struct Run { u64 b; u64 n; };
std::vector<Run> L, R; // L top=back is adjacent to head on left; R top=back adjacent on right
// macro transition cache: key (state, side(0=head at left end of block,1=right end), block)
struct MT { u64 nb; int ns; int dir; u64 steps; int halt; int ok; };
std::map<u64, MT> cache;
MT macro(int q, int side, u64 b) {
    u64 key = ((u64)q << 40) | ((u64)side << 39) | b;
    auto it = cache.find(key); if (it != cache.end()) return it->second;
    MT r; r.ok = 1; r.halt = 0; r.steps = 0;
    int pos = side ? K - 1 : 0; u64 bl = b;
    long lim = 100000;
    while (true) {
        int c = (bl >> (K - 1 - pos)) & 1;
        if (NX[q][c] < 0) { r.halt = 1; break; }
        if (W[q][c]) bl |= (1ULL << (K - 1 - pos)); else bl &= ~(1ULL << (K - 1 - pos));
        pos += D[q][c]; q = NX[q][c]; r.steps++;
        if (pos < 0) { r.dir = -1; break; }
        if (pos >= K) { r.dir = 1; break; }
        if (--lim == 0) { r.ok = 0; break; }
    }
    r.nb = bl; r.ns = q;
    if (r.halt) { r.dir = pos; } // store pos in dir for halt
    cache[key] = r; return r;
}
void push(std::vector<Run> &S, u64 b, u64 n) {
    if (S.empty() && b == 0) return;
    if (!S.empty() && S.back().b == b) S.back().n += n; else S.push_back({b, n});
}
u64 pop(std::vector<Run> &S) { // returns block, removes one
    if (S.empty()) return 0;
    u64 b = S.back().b; if (--S.back().n == 0) S.pop_back(); return b;
}
std::string bs(u64 b) { std::string s; for (int i = K - 1; i >= 0; --i) s += ((b >> i) & 1) ? '1' : '0'; return s; }
int main(int argc, char **argv) {
    const char *m = argv[1]; K = atoi(argv[2]); u64 MAXM = strtoull(argv[3], 0, 10); char mode = argv[4][0]; u64 PE = strtoull(argv[4] + 1, 0, 10);
    bool init = argc > 5 && argv[5][0] == 'i'; u64 EXTRA = argc > 6 ? strtoull(argv[6],0,10) : 0; u64 trig = 0; bool tr = false; u64 trigsteps_it = 0; LD trigsteps = 0;
    // parse
    NS = 0; const char *p = m;
    while (*p) {
        for (int c = 0; c < 2; ++c) {
            if (p[0] == '-' ) { NX[NS][c] = -1; W[NS][c] = 1; D[NS][c] = 1; }
            else { W[NS][c] = p[0] - '0'; D[NS][c] = p[1] == 'R' ? 1 : -1; NX[NS][c] = p[2] - 'A'; }
            p += 3;
        }
        NS++; if (*p == '_') ++p;
    }
    int q = 0, side = 0; u64 cur = 0; LD steps = 0;
    if (init) { // format: Q side | b^n ... [cur] b^n ...   (left to right)
        char qs[8]; int sd; scanf("%s %d", qs, &sd); q = qs[0] - 'A'; side = sd;
        char tok[200]; bool right = false; std::vector<Run> rr;
        auto pb = [](const char *t) { u64 b = 0; while (*t == '0' || *t == '1') { b = b * 2 + (*t - '0'); ++t; } return b; };
        while (scanf("%199s", tok) == 1) {
            if (tok[0] == '|') continue;
            if (tok[0] == '[') { cur = pb(tok + 1); right = true; continue; }
            char *c = strchr(tok, '^'); u64 n = c ? strtoull(c + 1, 0, 10) : 1; u64 b = pb(tok);
            if (!right) push(L, b, n); else rr.push_back({b, n});
        }
        for (size_t i = rr.size(); i-- > 0;) push(R, rr[i].b, rr[i].n);
    }
    bool was = false;
    for (u64 it = 0; it < MAXM; ++it) {
        if (mode == 's') { if (!tr && L.size() + R.size() >= PE) { tr = true; trig = it; trigsteps = steps; } if (tr && it >= trig + EXTRA) { printf("R %llu %.6Le E %llu %.6Le %c %d |", trig, trigsteps, it, steps, 'A'+q, side); for (size_t i = 0; i < L.size(); ++i) printf(" %s^%llu", bs(L[i].b).c_str(), L[i].n); printf(" [%s]", bs(cur).c_str()); for (size_t i = R.size(); i-- > 0;) printf(" %s^%llu", bs(R[i].b).c_str(), R[i].n); printf("\n"); return 0; } }
        bool cond = mode == 'p' ? (PE && it % PE == 0) : mode == 'r' ? R.size() <= PE : L.size() <= PE;
        bool pr = mode == 's' ? false : mode == 'p' ? cond : (cond && !was);
        was = cond;
        if (pr) {
            printf("T %llu %.6Le %c %d |", it, steps, 'A' + q, side);
            for (size_t i = 0; i < L.size(); ++i) printf(" %s^%llu", bs(L[i].b).c_str(), L[i].n);
            printf(" [%s]", bs(cur).c_str());
            for (size_t i = R.size(); i-- > 0;) printf(" %s^%llu", bs(R[i].b).c_str(), R[i].n);
            printf("\n");
        }
        MT t = macro(q, side, cur);
        if (!t.ok) { printf("INBLOCK-LOOP %.6Le\n", steps); return 0; }
        if (t.halt) {
            steps += t.steps + 1;
            u64 ones = __builtin_popcountll(t.nb) + 1 - ((t.nb >> (K - 1 - t.dir)) & 1);
            LD o = ones;
            for (auto &r : L) o += (LD)__builtin_popcountll(r.b) * r.n;
            for (auto &r : R) o += (LD)__builtin_popcountll(r.b) * r.n;
            printf("H macro=%llu steps=%.10Le ones=%.10Le\n", it, steps, o); return 0;
        }
        // acceleration: same state continuing in same direction over a run of identical blocks
        std::vector<Run> &Ahead = t.dir > 0 ? R : L; std::vector<Run> &Behind = t.dir > 0 ? L : R;
        int nside = t.dir > 0 ? 0 : 1;
        if (t.ns == q && nside == side && !Ahead.empty() && Ahead.back().b == cur) {
            u64 n = Ahead.back().n; Ahead.pop_back();
            push(Behind, t.nb, n + 1);
            steps += (LD)t.steps * (n + 1);
            cur = pop(Ahead);
            q = t.ns; side = nside; continue;
        }
        steps += t.steps;
        push(Behind, t.nb, 1);
        cur = pop(Ahead); q = t.ns; side = nside;
    }
    printf("END %.6Le\n", steps);
}
