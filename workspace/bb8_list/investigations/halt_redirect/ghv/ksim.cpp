// ksim.cpp: drop-in replacement for kst3.exe (same protocol and output), using a block-2 macro tape with the chain rule.
// Tape = left stack of runs (block, count), current block, right stack of runs. A block holds 2 cells (bit0 = left cell).
// K-moment (G frame): state G, head on a blank cell, every cell right of the head blank, the 8 cells left of the head
// are 10101010; the word from the leftmost 1 to the cell before the tail decomposes into tokens D(m) = (10)^m 1 and gaps
// 0^k (k >= 2), printed as -k.  stdin lines "word head state maxsteps"; output "K steps n items" | "H steps st read ones" | "T steps".
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
#include <sstream>
struct Tr { int w, d, nx; bool def; };
struct Run { int b; long long n; };
static std::vector<Tr> T;
static int QG = 6;
struct Mac { bool ok; int b2, q2, side2; long long steps; bool halt; int hq, hread; };
// side: 0 = head on left cell (entered from left / moving right), 1 = head on right cell
static Mac mac[16][2][4];
static bool macdone[16][2][4];
static Mac getmac(int q, int side, int b) {
    if (macdone[q][side][b]) return mac[q][side][b];
    Mac m{}; int p = side, cur = b, qq = q; long long s = 0;
    while (true) {
        int c = (cur >> p) & 1; const Tr &tr = T[2 * qq + c];
        if (!tr.def) { m.halt = true; m.hq = qq; m.hread = c; m.ok = false; break; }
        cur = (cur & ~(1 << p)) | (tr.w << p); p += tr.d; qq = tr.nx; ++s;
        if (p < 0 || p > 1) { m.ok = true; m.b2 = cur; m.q2 = qq; m.side2 = p < 0 ? 0 : 1; m.steps = s; break; }
        if (s > 64) { m.ok = false; m.halt = false; break; }
    }
    mac[q][side][b] = m; macdone[q][side][b] = true;
    return m;
}
static void push(std::vector<Run> &st, int b, long long n) {
    if (n <= 0) return;
    if (st.empty() && b == 0) return;            // blanks at the far end are implicit
    if (!st.empty() && st.back().b == b) st.back().n += n; else st.push_back({b, n});
}
static int pop(std::vector<Run> &st) {
    if (st.empty()) return 0;
    int b = st.back().b; if (--st.back().n == 0) st.pop_back();
    return b;
}
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
        // align: cell i of the word at absolute position i + pad, pad chosen so the head's block index is integral
        long long pad = 2;  // leave room
        std::vector<int> cells(w.size() + 8, 0);
        long long len = w.size() + pad + 4; if (len % 2) ++len;
        std::vector<int> abs(len, 0);
        for (size_t i = 0; i < w.size(); ++i) abs[pad + i] = w[i] - '0';
        long long hpos = pad + head;
        while ((long long)abs.size() <= hpos + 2) abs.push_back(0);
        if (abs.size() % 2) abs.push_back(0);
        long long hb = hpos / 2; int p = hpos % 2;
        std::vector<Run> L, R;
        for (long long bi = 0; bi < hb; ++bi) push(L, abs[2 * bi] | (abs[2 * bi + 1] << 1), 1);
        int cur = abs[2 * hb] | (abs[2 * hb + 1] << 1);
        for (long long bi = (long long)abs.size() / 2 - 1; bi > hb; --bi) push(R, abs[2 * bi] | (abs[2 * bi + 1] << 1), 1);
        long long step = 0; bool done = false; long long lastK = -1; long long hbk = hb, minabs = hpos;
        auto rightblank = [&]() -> bool {
            if (!R.empty()) return false;
            for (int i = p + 1; i <= 1; ++i) if ((cur >> i) & 1) return false;
            return true;
        };
        auto leftcells = [&](int k, std::vector<int> &out) {  // k cells left of the head, nearest first
            out.clear(); int pp = p - 1; int cb = cur; long long ri = (long long)L.size() - 1; long long used = 0;
            while ((int)out.size() < k) {
                if (pp >= 0) { out.push_back((cb >> pp) & 1); --pp; continue; }
                if (ri < 0) { out.push_back(0); continue; }
                cb = L[ri].b; ++used; if (used >= L[ri].n) { --ri; used = 0; }
                pp = 1;
            }
        };
        std::vector<int> lc;
        bool dbg = getenv("KSIM_DBG") != nullptr;
        while (step < N) {
            if (dbg && step < 0) {
                std::string t; for (auto &r : L) for (long long j = 0; j < r.n; ++j) { t += char('0' + (r.b & 1)); t += char('0' + ((r.b >> 1) & 1)); }
                long long hh = t.size() + p; t += char('0' + (cur & 1)); t += char('0' + ((cur >> 1) & 1));
                for (long long ri = (long long)R.size() - 1; ri >= 0; --ri) for (long long j = 0; j < R[ri].n; ++j) { t += char('0' + (R[ri].b & 1)); t += char('0' + ((R[ri].b >> 1) & 1)); }
                fprintf(stderr, "%lld %c %lld %s\n", step, 'A' + q, hh, t.c_str());
            }
            // K-moment check at cell level
            if (step > 0 && q == QG && ((cur >> p) & 1) == 0 && step != lastK && rightblank()) {
                leftcells(8, lc);
                bool tl = true; static const int TLr[8] = {0,1,0,1,0,1,0,1};
                for (int i = 0; i < 8; ++i) if (lc[i] != TLr[i]) { tl = false; break; }
                if (tl) {
                    // expand whole tape
                    std::vector<char> tape;
                    for (auto &r : L) for (long long j = 0; j < r.n; ++j) { tape.push_back(r.b & 1); tape.push_back((r.b >> 1) & 1); }
                    long long h = tape.size() + p;
                    tape.push_back(cur & 1); tape.push_back((cur >> 1) & 1);
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
                lastK = step;
            }
            // chain rule: at a block edge, entering a run of identical blocks
            if (p == 0 || p == 1) {
                int c = (cur >> p) & 1; const Tr &tr = T[2 * q + c];
                if (!tr.def) {
                    long long ones = 0;
                    for (auto &r : L) ones += r.n * (((r.b) & 1) + ((r.b >> 1) & 1));
                    for (auto &r : R) ones += r.n * (((r.b) & 1) + ((r.b >> 1) & 1));
                    ones += (cur & 1) + ((cur >> 1) & 1);
                    printf("H %lld %c %d %lld\n", step, 'A' + q, c, ones); done = true; break;
                }
            }
            // try whole-block macro step with chain when the head is at the entry cell of the block
            bool chained = false;
            {  // K-moments cannot lie strictly inside a chained run (cells to the right are nonblank)
                Mac mm = getmac(q, p, cur);
                std::vector<Run> &ah0 = (p == 0) ? R : L;
                // the last block before the implicit blank end is never chained (a K-moment may sit inside it)
                bool farok = !ah0.empty() && !(ah0.size() == 1 && ah0.back().b == cur && ah0.back().n == 1);
                if (farok && mm.ok && mm.q2 == q && ((p == 0 && mm.side2 == 1) || (p == 1 && mm.side2 == 0))) {
                    // passes through to the other side in the same state: apply to cur and to the run ahead
                    std::vector<Run> &ahead = (p == 0) ? R : L;
                    std::vector<Run> &behind = (p == 0) ? L : R;
                    long long k = 0;
                    if (!ahead.empty() && ahead.back().b == cur) {
                        k = ahead.back().n;
                        if (ahead.size() == 1) { k -= 1; ahead.back().n = 1; } else ahead.pop_back();
                    }
                    long long tot = k + 1;
                    push(behind, mm.b2, tot);
                    step += tot * mm.steps;
                    cur = pop(ahead); p = (p == 0) ? 0 : 1;
                    if (p == 0) hbk += tot; else hbk -= tot;
                    if (2 * hbk + p < minabs) minabs = 2 * hbk + p;
                    chained = true;
                }
            }
            if (chained) continue;
            // single micro step
            int c = (cur >> p) & 1; const Tr &tr = T[2 * q + c];
            cur = (cur & ~(1 << p)) | (tr.w << p); p += tr.d; q = tr.nx; ++step;
            if (p > 1) { push(L, cur, 1); cur = pop(R); p = 0; ++hbk; }
            else if (p < 0) { push(R, cur, 1); cur = pop(L); p = 1; --hbk; }
            if (2 * hbk + p < minabs) minabs = 2 * hbk + p;
        }
        if (!done) printf("T %lld\n", N);
        fflush(stdout);
    }
}
