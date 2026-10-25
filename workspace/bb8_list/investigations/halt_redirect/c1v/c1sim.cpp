// c1sim.cpp (c1 verifier, own tool).  Server: reads jobs from stdin, one per line:
//   MODE MACHINE MAXSTEPS STARTSPEC TARGETSPEC
// STARTSPEC  = BITS:HEAD:STATE   (BITS = tape word from its leftmost cell, HEAD = index into BITS (may be = len), STATE letter)
// TARGETSPEC = tokens farthest-first incl. a and r, comma separated, with x^k repetition, or '-' (none)
// The canonical K-moment: state G reading 0, all cells right of the head blank, tape (from its leftmost 1) =
//   D(t1) ... D(tn) 1010, D(m) = (10)^m 1.
// MODE reach : run until the configuration equals the target K-moment exactly (all other cells blank) -> "REACHED step minpos"
//              or the machine halts -> "HALT step STATE SYM ones" or step limit -> "TIMEOUT".
//   minpos = leftmost head position relative to BITS[0] (negative = left of the word).
// MODE trace : print every K-moment (parsed tokens RLE) until halt / limit / 400 lines.
// Every result line also prints the slots read (as letters+symbol) as "slots=...".
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <sstream>
#include <iostream>
#include <algorithm>
using namespace std;
struct Tr { int w, d, nx; bool def; };
static vector<long long> parse_tokens(const string &s) {
    vector<long long> v; stringstream ss(s); string t;
    while (getline(ss, t, ',')) { if (t.empty()) continue; size_t p = t.find('^');
        if (p == string::npos) v.push_back(atoll(t.c_str()));
        else { long long x = atoll(t.substr(0, p).c_str()), k = atoll(t.substr(p + 1).c_str()); for (long long i = 0; i < k; ++i) v.push_back(x); } }
    return v;
}
static string word_of(const vector<long long> &tk) { string w; for (long long m : tk) { for (long long i = 0; i < m; ++i) w += "10"; w += "1"; } w += "1010"; return w; }

// abstract champion process on tokens nearest-first [r, a, d1, d2, ...]; returns true if it reaches its event with all
// values <= cap (then the literal machine simply continues).  Events: a in {0,2,3} at a-bottom, borrow source d in {0,2,3}
// or the left end.  R1: a>=4: a-=3, r=2r+5.  R2/R3: a==1, first non-1 digit d>=4: d-=3, (a or zero next to d)=2r+5, r=1.
static bool small_proc(vector<long long> tk, long long cap) {
    long long r = tk[0], a = tk[1]; vector<long long> d(tk.begin() + 2, tk.end());
    for (long long it = 0; it < 10000000; ++it) {
        if (r > cap || a > cap) return false;
        if (a >= 4) { a -= 3; r = 2 * r + 5; continue; }
        if (a != 1) return true;
        size_t j = 0; while (j < d.size() && d[j] == 1) ++j;
        if (j == d.size()) return true;
        if (d[j] <= 3) return true;
        d[j] -= 3; if (j == 0) { a = 2 * r + 5; r = 1; } else { d[j - 1] = 2 * r + 5; r = 1; }
    }
    return false;
}
int main() {
    string line;
    while (getline(cin, line)) {
        stringstream ls(line); string mode, ms, sspec, tspec; long long N, CAP = 3000;
        if (!(ls >> mode >> ms >> N >> sspec >> tspec)) { printf("BADJOB\n"); fflush(stdout); continue; }
        vector<string> rows; { stringstream ss(ms); string r; while (getline(ss, r, '_')) rows.push_back(r); }
        int ns = rows.size(); vector<Tr> T(2 * ns, {0, 0, 0, false});
        for (int q = 0; q < ns; ++q) for (int c = 0; c < 2; ++c) { string x = rows[q].substr(3 * c, 3);
            if (x[2] != '-' && x[2] != 'Z' && x[2] != 'H' + 100) T[2 * q + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
        size_t c1 = sspec.find(':'), c2 = sspec.rfind(':');
        string bits = sspec.substr(0, c1); long long head = atoll(sspec.substr(c1 + 1, c2 - c1 - 1).c_str()); int q = sspec[c2 + 1] - 'A';
        string tw; bool hast = tspec != "-"; if (hast) tw = word_of(parse_tokens(tspec));
        long long L = 4 * (long long)(bits.size() + tw.size()) + (1 << 22);
        vector<unsigned char> tape(L, 0); long long off = L / 2;
        for (size_t i = 0; i < bits.size(); ++i) tape[off + i] = bits[i] - '0';
        long long h = off + head, lo = off, hi = off + (long long)bits.size(), minh = h, step = 0;
        long long ones = 0; for (char ch : bits) ones += ch == '1';
        long long rmost = -1; for (long long i = lo; i < hi; ++i) if (tape[i]) rmost = i;
        long long lmost = rmost < 0 ? -1 : lo; while (lmost >= 0 && lmost <= rmost && !tape[lmost]) ++lmost;
        unsigned used = 0; int gq = 'G' - 'A'; long long lines = 0; bool done = false;
        auto slots = [&]() { string s; for (int i = 0; i < 2 * ns; ++i) if (used >> i & 1) { s += char('A' + i / 2); s += char('0' + i % 2); s += ','; } return s; };
        while (step <= N) {
            if (h < 2 || h >= L - 2) { printf("EDGE %lld slots=%s\n", step, slots().c_str()); done = true; break; }
            if (h < minh) minh = h; if (h < lo) lo = h; if (h > hi) hi = h;
            int c = tape[h];
            if (q == gq && c == 0 && h > rmost && rmost >= 0) {
                // K-moment candidate: tape from lmost .. rmost must parse into tokens + 1010 suffix with rmost = h-2
                if (hast) {
                    long long n = tw.size();
                    if (rmost == h - 2 && ones == (long long)count(tw.begin(), tw.end(), '1') && h - n >= 0 && lmost == h - n) {
                        bool ok = true; for (long long i = 0; i < n && ok; ++i) if (tape[h - n + i] != tw[i] - 48) ok = false;
                        if (ok) { printf("REACHED %lld %lld slots=%s\n", step, minh - off, slots().c_str()); done = true; break; }
                    }
                }
                if ((mode == "trace" || mode == "stage") && step > 0 && rmost == h - 2 && tape[h - 1] == 0 && tape[h - 2] == 1 && tape[h - 3] == 0 && tape[h - 4] == 1) {
                    // parse tokens backwards from h-5
                    vector<long long> tk; long long p = h - 5; bool junk = false;
                    while (p >= lmost) { if (tape[p] != 1) { junk = true; break; } long long m = 0; --p;
                        while (p - 1 >= lmost && tape[p] == 0 && tape[p - 1] == 1) { ++m; p -= 2; }
                        if (p >= lmost && tape[p] == 0) { /* gap */ }
                        tk.push_back(m); }
                    if (!junk && p < lmost && mode == "stage" && tk.size() >= 2 && !small_proc(tk, CAP)) {
                        printf("J %lld %lld |", step, minh - off); for (long long i = (long long)tk.size() - 1; i >= 0; --i) printf(" %lld", tk[i]);
                        printf(" | slots=%s\n", slots().c_str()); done = true; break;
                    }
                    if (!junk && p < lmost && mode == "trace") {
                        printf("K %lld:", step); size_t k = tk.size();
                        // farthest first, RLE
                        long long i = (long long)tk.size() - 1;
                        while (i >= 0) { long long j = i; while (j >= 0 && tk[j] == tk[i]) --j; if (i - j > 1) printf(" %lld^%lld", tk[i], i - j); else printf(" %lld", tk[i]); i = j; }
                        printf("\n"); if (++lines >= 400) { printf("LINES\n"); done = true; break; }
                    }
                }
            }
            const Tr &tr = T[2 * q + c];
            used |= 1u << (2 * q + c);
            if (!tr.def) { printf("HALT %lld %c %d %lld %lld slots=%s\n", step, 'A' + q, c, ones, minh - off, slots().c_str()); done = true; break; }
            if (tr.w != c) { ones += tr.w ? 1 : -1; tape[h] = tr.w;
                if (tr.w) { if (h > rmost) rmost = h; if (lmost < 0 || h < lmost) lmost = h; }
                else { if (h == rmost) { while (rmost >= lmost && !tape[rmost]) --rmost; if (rmost < lmost) { rmost = lmost = -1; } }
                       else if (h == lmost) { while (lmost <= rmost && !tape[lmost]) ++lmost; } } }
            h += tr.d; q = tr.nx; ++step;
        }
        if (!done) printf("TIMEOUT %lld slots=%s\n", N, slots().c_str());
        fflush(stdout);
    }
}
