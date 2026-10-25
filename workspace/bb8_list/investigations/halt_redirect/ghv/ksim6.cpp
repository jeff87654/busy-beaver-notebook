// ksim6.cpp: drop-in replacement for kst3.exe / ksim.exe (same protocol, output "K steps n items... @ minpos"),
// macro tape with blocks of KB cells (KB = 6 handles both (10)^n runs and D1 = 101 lists) and the chain rule.
// Tape = left stack of runs (block, count), current block, right stack of runs. Block bit i = cell i of the block.
// Whole-block macro steps are taken only when nonblank cells exist right of the current block (so no K-moment can occur
// inside); otherwise single cell steps with the K-moment test.
// K-moment (G frame): state G, head on a blank cell, every cell right of the head blank, the 8 cells left of the head
// are 10101010; the word from the leftmost 1 to the cell before the tail decomposes into tokens D(m) = (10)^m 1 and
// gaps 0^k (k >= 2), printed as -k.  stdin "word head state maxsteps"; out "K steps n items @ minpos" | "H steps st read ones" | "T steps".
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
#include <sstream>
static const int KB = 6;
static const int NB = 1 << KB;
struct Tr { int w, d, nx; bool def; };
struct Run { int b; long long n; };
static std::vector<Tr> T;
static const int QG = 6;
struct Mac { bool ok; int b2, q2, exitR; long long steps; };
static Mac mac[16][KB][NB];
static bool macdone[16][KB][NB];
static Mac getmac(int q, int p0, int b) {
    if (macdone[q][p0][b]) return mac[q][p0][b];
    Mac m{}; int p = p0, cur = b, qq = q; long long s = 0;
    while (true) {
        int c = (cur >> p) & 1; const Tr &tr = T[2 * qq + c];
        if (!tr.def) { m.ok = false; break; }
        cur = (cur & ~(1 << p)) | (tr.w << p); p += tr.d; qq = tr.nx; ++s;
        if (p < 0 || p >= KB) { m.ok = true; m.b2 = cur; m.q2 = qq; m.exitR = p >= KB; m.steps = s; break; }
        if (s > 4096) { m.ok = false; break; }
    }
    mac[q][p0][b] = m; macdone[q][p0][b] = true;
    return m;
}
static void push(std::vector<Run> &st, int b, long long n) {
    if (n <= 0) return;
    if (st.empty() && b == 0) return;
    if (!st.empty() && st.back().b == b) st.back().n += n; else st.push_back({b, n});
}
static int pop(std::vector<Run> &st) {
    if (st.empty()) return 0;
    int b = st.back().b; if (--st.back().n == 0) st.pop_back();
    return b;
}
static int popc(int b) { return __builtin_popcount(b); }
int main(int argc, char **argv) {
    std::string m = argv[1];
    std::vector<std::string> rows; { std::stringstream ss(m); std::string r; while (std::getline(ss, r, '_')) rows.push_back(r); }
    int n = rows.size(); T.assign(2 * n, {0, 0, 0, false});
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) { std::string x = rows[q].substr(3 * c, 3);
        if (x[2] >= 'A' && x[2] <= 'Z' && x[0] != '-') T[2 * q + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    std::string line;
    while (std::getline(std::cin, line)) {
        std::stringstream ss(line); std::string w, qs; long long head, N;
        if (!(ss >> w >> head >> qs >> N)) { if (line.size()) { printf("BADINPUT\n"); fflush(stdout); } continue; }
        int q = qs[0] - 'A';
        long long pad = KB;
        std::vector<int> abs(w.size() + 2 * KB + 8, 0);
        for (size_t i = 0; i < w.size(); ++i) abs[pad + i] = w[i] - '0';
        long long hpos = pad + head;
        while ((long long)abs.size() <= hpos + KB) abs.push_back(0);
        while (abs.size() % KB) abs.push_back(0);
        auto blk = [&](long long bi) { int b = 0; for (int i = 0; i < KB; ++i) b |= abs[KB * bi + i] << i; return b; };
        long long hb = hpos / KB; int p = hpos % KB;
        std::vector<Run> L, R;
        for (long long bi = 0; bi < hb; ++bi) push(L, blk(bi), 1);
        int cur = blk(hb);
        for (long long bi = (long long)abs.size() / KB - 1; bi > hb; --bi) push(R, blk(bi), 1);
        long long step = 0; bool done = false; long long hbk = hb, minabs = hpos;
        std::vector<int> lc;
        auto leftcells = [&](int k) {
            lc.clear(); int pp = p - 1; int cb = cur; long long ri = (long long)L.size() - 1; long long used = 0;
            while ((int)lc.size() < k) {
                if (pp >= 0) { lc.push_back((cb >> pp) & 1); --pp; continue; }
                if (ri < 0) { lc.push_back(0); continue; }
                cb = L[ri].b; ++used; if (used >= L[ri].n) { --ri; used = 0; }
                pp = KB - 1;
            }
        };
        while (step < N) {
            if (R.empty()) {
                bool rb = true;
                for (int i = p + 1; i < KB; ++i) if ((cur >> i) & 1) { rb = false; break; }
                if (rb && step > 0 && q == QG && ((cur >> p) & 1) == 0) {
                    leftcells(9);
                    static const int TLr[8] = {0,1,0,1,0,1,0,1};
                    bool tl = lc[8] == 1; for (int i = 0; i < 8 && tl; ++i) if (lc[i] != TLr[i]) { tl = false; break; }
                    if (tl) {
                        std::vector<char> tape;
                        for (auto &r : L) for (long long j = 0; j < r.n; ++j) for (int i = 0; i < KB; ++i) tape.push_back((r.b >> i) & 1);
                        long long h = tape.size() + p;
                        for (int i = 0; i < KB; ++i) tape.push_back((cur >> i) & 1);
                        long long s = 0; while (s < h && !tape[s]) ++s;
                        long long e = h - 9; std::vector<long long> items; bool ok = (s <= e && tape[e] == 1);
                        long long pp2 = s;
                        while (ok && pp2 <= e) {
                            if (tape[pp2] == 1) {
                                long long mm = 0;
                                while (pp2 + 2 <= e && tape[pp2 + 1] == 0 && tape[pp2 + 2] == 1) { ++mm; pp2 += 2; }
                                items.push_back(mm); ++pp2;
                            } else {
                                long long k = 0; while (pp2 <= e && tape[pp2] == 0) { ++k; ++pp2; }
                                if (k < 2) { ok = false; break; }
                                items.push_back(-k);
                            }
                        }
                        if (ok) {
                            std::string out = "K " + std::to_string(step) + " " + std::to_string(items.size());
                            for (auto v : items) { out += ' '; out += std::to_string(v); }
                            out += " @ " + std::to_string(minabs - pad); printf("%s\n", out.c_str()); done = true; break;
                        }
                    }
                }
            }
            {
                int c = (cur >> p) & 1; const Tr &tr = T[2 * q + c];
                if (!tr.def) {
                    long long ones = 0;
                    for (auto &r : L) ones += r.n * popc(r.b);
                    for (auto &r : R) ones += r.n * popc(r.b);
                    ones += popc(cur);
                    printf("H %lld %c %d %lld\n", step, 'A' + q, c, ones); done = true; break;
                }
            }
            if (!R.empty()) {
                Mac mm = getmac(q, p, cur);
                if (mm.ok) {
                    if (KB * hbk < minabs) minabs = KB * hbk;   // conservative: the whole current block may be visited
                    bool chainable = (mm.q2 == q) && ((p == 0 && mm.exitR) || (p == KB - 1 && !mm.exitR));
                    std::vector<Run> &ahead = mm.exitR ? R : L;
                    std::vector<Run> &behind = mm.exitR ? L : R;
                    long long tot = 1;
                    if (chainable && !ahead.empty() && ahead.back().b == cur) {
                        long long k = ahead.back().n;
                        if (ahead.size() == 1) { k -= 1; ahead.back().n = 1; } else ahead.pop_back();
                        tot += k;
                    }
                    push(behind, mm.b2, tot);
                    step += tot * mm.steps;
                    q = mm.q2;
                    cur = pop(ahead);
                    if (mm.exitR) { hbk += tot; p = 0; } else { hbk -= tot; p = KB - 1; }
                    // the cells passed while inside the block(s): leftmost visited is the left edge when exiting left
                    if (KB * hbk + p < minabs) minabs = KB * hbk + p;
                    continue;
                }
            }
            int c = (cur >> p) & 1; const Tr &tr = T[2 * q + c];
            cur = (cur & ~(1 << p)) | (tr.w << p); p += tr.d; q = tr.nx; ++step;
            if (p >= KB) { push(L, cur, 1); cur = pop(R); p = 0; ++hbk; }
            else if (p < 0) { push(R, cur, 1); cur = pop(L); p = KB - 1; --hbk; }
            if (KB * hbk + p < minabs) minabs = KB * hbk + p;
        }
        if (!done) printf("T %lld\n", N);
        fflush(stdout);
    }
}
