// cover.cpp: enumerate all NS-state machines (TNF) whose run from the blank tape writes and moves exactly like REF's for N steps.
// The tape history of REF is fixed, so a candidate is a state sequence c_t with a consistent partial table.  DFS branches only
// when an undefined candidate slot is first read (next state: any existing state or the next new one).
// usage: cover REF NS N  -> one line per surviving candidate: partial table (unused slots ---) and its used slots.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
using namespace std;
int NS; long long N; vector<unsigned char> S, Wv, Dv, RQ;   // RQ: REF state after the step   // per step: read symbol, written symbol, dir (1=R)
struct Tr { signed char w, d, q; };
long long found = 0, nodes = 0;
void out(Tr T[][2], int used) {
    string s;
    bool pr[16][16] = {}; { int c = 0; for (long long t = 0; t < N; ++t) { c = T[c][S[t]].q; pr[RQ[t]][c] = true; } }
    for (int q = 0; q < NS; ++q) { if (q) s += '_'; for (int c = 0; c < 2; ++c) { Tr &t = T[q][c]; if (t.q < 0) s += "---"; else { s += char('0' + t.w); s += t.d ? 'R' : 'L'; s += char('A' + t.q); } } }
    string ps; for (int a = 0; a < 16; ++a) for (int b = 0; b < 16; ++b) if (pr[a][b]) { ps += char('A' + a); ps += char('A' + b); ps += ','; }
    printf("%s states_used=%d pairs=%s\n", s.c_str(), used, ps.c_str()); fflush(stdout); ++found;
}
void dfs(Tr T[][2], long long t, int c, int used) {
    ++nodes;
    while (t < N) {
        int s = S[t]; Tr &tr = T[c][s];
        if (tr.q < 0) {
            for (int nq = 0; nq <= used && nq < NS; ++nq) {
                Tr U[16][2]; memcpy(U, T, sizeof(Tr) * 16 * 2);
                U[c][s] = {(signed char)Wv[t], (signed char)Dv[t], (signed char)nq};
                dfs(U, t + 1, nq, nq == used ? used + 1 : used);
            }
            return;
        }
        if (tr.w != Wv[t] || tr.d != Dv[t]) return;
        c = tr.q; ++t;
    }
    out(T, used);
}
int main(int argc, char **argv) {
    const char *m = argv[1]; NS = atoi(argv[2]); N = (long long)atof(argv[3]);
    int n = (strlen(m) + 1) / 7; int W[16][2], D[16][2], Q[16][2];
    for (int i = 0; i < n; ++i) for (int c = 0; c < 2; ++c) { const char *x = m + 7 * i + 3 * c; if (x[0] == '-') Q[i][c] = -1; else { W[i][c] = x[0] - '0'; D[i][c] = x[1] == 'R'; Q[i][c] = x[2] - 'A'; } }
    const long long SZ = 1LL << 25; vector<unsigned char> tape(SZ); long long p = SZ / 2; int q = 0;
    S.resize(N); Wv.resize(N); Dv.resize(N); RQ.resize(N);
    for (long long t = 0; t < N; ++t) { int s = tape[p]; if (Q[q][s] < 0) { N = t; break; } S[t] = s; Wv[t] = W[q][s]; Dv[t] = D[q][s]; tape[p] = W[q][s]; p += D[q][s] ? 1 : -1; q = Q[q][s]; RQ[t] = q; }
    Tr T[16][2]; for (int i = 0; i < 16; ++i) for (int c = 0; c < 2; ++c) T[i][c] = {-1, -1, -1};
    dfs(T, 0, 0, 1);
    fprintf(stderr, "# candidates %lld nodes %lld N %lld\n", found, nodes, N);
}
