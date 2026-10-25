// rtwin.cpp: right-end survival twin simulator (n1right, 2026-10-09).
// Server: job lines "MACHINE STATE HEAD MAXS RCAP GAP PATTERN" then a line of tape bits (the base word; head offset
// HEAD relative to the word start).  PATTERN is a bit string ('-' = none) placed at word_end + GAP (word_end = len(bits)).
// Runs base and patterned tapes in lockstep.
// Output line: "B <base outcome> bmax=<max head pos - word_end over the base run> | D <div> | P <pat outcome>"
//   outcome: "K steps | toks nearest-first | far | rem=<bits right of the K head, from head pos> @<offset of head - word_end>"
//            "H steps state sym" / "T steps" / "W steps"
//   K-moment (both runs): state Q='G' reading 0, cells pos-5..pos-1 = 1 1010, cells pos..pos+3 = 0, and the token
//   champion process does not stay small (small_process false, as in gstage).  For the base this equals gstage's rule
//   when nothing lies right.
//   div: first step where the patterned run reads a cell >= word_end+GAP ("first pattern-region read"): step state sym rel
//        and first step where (state,sym) differ from the base run.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
struct Tr { signed char w, d, nx; bool def; };
static bool parsem(const char *s, Tr *m) {
    int n = (int)((strlen(s) + 1) / 7);
    if (n < 1 || n > 16 || (int)strlen(s) != 7 * n - 1) return false;
    for (int i = 0; i < 32; ++i) m[i] = {0, 0, 0, false};
    for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) {
        const char *x = s + 7 * q + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') m[2 * q + c] = {0, 0, 0, false};
        else m[2 * q + c] = {(signed char)(x[0] - '0'), (signed char)(x[1] == 'R' ? 1 : -1), (signed char)(x[2] - 'A'), true};
    }
    return true;
}
static bool small_process(std::vector<long long> tok, long long cap) {
    if (tok.size() < 2) return true;
    long long r = tok[0], a = tok[1];
    std::vector<long long> d(tok.begin() + 2, tok.end());
    for (int it = 0; it < 100000; ++it) {
        if (r > cap || a > cap) return false;
        if (a >= 4) { a -= 3; r = 2 * r + 5; continue; }
        if (a != 1) return true;
        size_t j = 0;
        while (j < d.size() && d[j] == 1) ++j;
        if (j == d.size()) return true;
        if (d[j] == 0 || d[j] == 2) return true;
        d[j] -= 3;
        if (j == 0) { a = 2 * r + 5; r = 1; }
        else { d[j - 1] = 2 * r + 5; r = 1; }
    }
    return false;
}
struct Run {
    std::vector<unsigned char> t; long long pos, lo, hi, steps; int q; bool done; std::string out; long long maxp;
    long long kpos;
};
static const long long OFF = 1 << 22;
static Tr M[32]; static long long RCAP; static long long WEND;
// try K-moment at current config; returns true and fills out
static long long MARGIN = 12;
static bool kcheck(Run &r, int mode) {
    long long p0 = r.pos;
    if (RCAP < 0 || r.q != 6 || r.t[p0] != 0 || r.steps == 0) return false;
    static const int suf[5] = {1, 1, 0, 1, 0};
    for (int i = 0; i < 5; ++i) if (r.t[p0 - 5 + i] != suf[i]) return false;
    if (mode == 0) { for (long long i = p0 + 1; i <= r.hi; ++i) if (r.t[i]) return false; }
    else if (mode == 1) { for (long long i = 1; i <= MARGIN; ++i) if (r.t[p0 + i]) return false; }
    std::vector<long long> tok;
    long long p = p0 - 5;
    while (p >= r.lo && r.t[p] == 1) {
        long long mm = 0; --p;
        while (p - 1 >= r.lo && r.t[p] == 0 && r.t[p - 1] == 1) { ++mm; p -= 2; }
        tok.push_back(mm);
    }
    if (tok.size() < 2 || small_process(tok, RCAP)) return false;
    long long l1 = r.lo; while (l1 <= p && !r.t[l1]) ++l1;
    std::string s = "K " + std::to_string(r.steps) + " |";
    for (long long x : tok) s += " " + std::to_string(x);
    s += " | ";
    for (long long i = l1; i <= p; ++i) s += char('0' + r.t[i]);
    long long rr = r.hi; while (rr > p0 && !r.t[rr]) --rr;
    s += " | rem=";
    if (rr > p0) { for (long long i = p0 + 1; i <= rr; ++i) s += char('0' + r.t[i]); }
    else s += "-";
    s += " @" + std::to_string(p0 - WEND);
    r.out = s; r.kpos = p0; return true;
}
static void step(Run &r, long long MAXS, int mode) {
    if (r.done) return;
    if (kcheck(r, mode)) { r.done = true; return; }
    int s = r.t[r.pos];
    const Tr &x = M[2 * r.q + s];
    if (!x.def) { r.out = "H " + std::to_string(r.steps) + " " + char('A' + r.q) + " " + std::to_string(s); r.done = true; return; }
    r.t[r.pos] = x.w; r.pos += x.d; r.q = x.nx; ++r.steps;
    if (r.pos < r.lo) r.lo = r.pos; if (r.pos > r.hi) r.hi = r.pos;
    if (r.pos > r.maxp) r.maxp = r.pos;
    if (r.pos < 8 || r.pos > (long long)r.t.size() - 8) { r.out = "W " + std::to_string(r.steps); r.done = true; return; }
    if (r.steps >= MAXS) { r.out = "T " + std::to_string(r.steps); r.done = true; }
}
int main() {
    static char ms[256], st[8], pat[4096];
    long long head, MAXS, GAP;
    std::vector<unsigned char> blank(2 * OFF, 0);
    while (scanf("%255s %7s %lld %lld %lld %lld %4095s", ms, st, &head, &MAXS, &RCAP, &GAP, pat) == 7) {
        std::string bits; int ch;
        while ((ch = getchar()) != EOF && ch != '\n') {}
        while ((ch = getchar()) != EOF && ch != '\n') if (ch == '0' || ch == '1') bits += (char)ch;
        if (!parsem(ms, M)) { printf("X bad machine\n"); fflush(stdout); continue; }
        std::string P = pat[0] == '-' ? std::string() : std::string(pat);
        Run a, b;
        for (Run *r : {&a, &b}) {
            r->t = blank; for (size_t i = 0; i < bits.size(); ++i) r->t[OFF + i] = bits[i] - '0';
            r->pos = OFF + head; r->lo = OFF; r->hi = OFF + bits.size(); r->steps = 0; r->q = st[0] - 'A'; r->done = false;
            r->maxp = r->pos; r->kpos = 0;
        }
        WEND = OFF + bits.size();
        long long PS = WEND + GAP;
        for (size_t i = 0; i < P.size(); ++i) b.t[PS + i] = P[i] - '0';
        if (!P.empty()) b.hi = std::max(b.hi, PS + (long long)P.size());
        std::string firstread = "-", firstdiv = "-";
        while (!a.done || !b.done) {
            if (!b.done) {
                if (firstread == "-" && b.pos >= PS)
                    firstread = std::to_string(b.steps) + " " + char('A' + b.q) + std::to_string((int)b.t[b.pos]) + " rel=" + std::to_string(b.pos - WEND);
                if (firstdiv == "-" && (a.done || a.q != b.q || a.t[a.pos] != b.t[b.pos] || a.pos != b.pos))
                    firstdiv = std::to_string(b.steps) + " " + char('A' + b.q) + std::to_string((int)b.t[b.pos]) + " rel=" + std::to_string(b.pos - WEND);
            }
            bool diverged = firstdiv != "-";
            step(a, MAXS, 0);
            if (a.done && !diverged && !b.done) { if (!kcheck(b, 2)) b.out = "N " + std::to_string(b.steps); b.done = true; }
            step(b, MAXS, 1);
        }
        printf("B %s bmax=%lld | R %s | V %s | P %s\n", a.out.c_str(), a.maxp - WEND, firstread.c_str(), firstdiv.c_str(), b.out.c_str());
        fflush(stdout);
    }
    return 0;
}
