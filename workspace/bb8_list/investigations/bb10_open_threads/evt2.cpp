// evt.cpp: literal TM simulator that prints a compact EVENT view of champion-core runs.
//   evt MACHINE WORDFILE HEAD STATE MAXSTEPS [-q CANON] [-r LEVEL] [-k K] [-m MAXLINES] [-s SNAP] [-e E] [-d DUMP]
// Canonical configuration: state CANON (default B), reading 0, no 1 right of the head.  Items: tape from the leftmost
// 1 to the head, greedily cut into D-tokens D(m) = (10)^m 1 (printed m, repeats m*k) and junk <..> (runs c:k, (10)^k).
// Champion phase: "locked" when two canonical configs with the same key (shape) differ in two adjacent tokens
// a: m+3 -> m, r -> 2r+6-e.  Items right of r = TAIL.  K-moments = configs ending in "tok tok TAIL".  Consecutive
// K-moments must be R1 / R2 / R3 (as in hyb10); anything else, or 64 canonical configs without a K-moment, unlocks.
// Output:  L step | items         lock (first K-moment)
//          R2/R3 step | items     with -r 2 (R2 and R3) or -r 3 (R3 only) (default -r 3; -r 9 none)
//          U step r1 r2 r3 | items   unlock; prints the last K-moment, then "  ! step | items" the config after it
//          C step | items         unlocked: canonical config whose shape differs from the previous one (first K of a
//                                 shape regime; X n = suppressed)
//          S step | items         snapshot of the whole tape every SNAP steps without output (head = [Q])
//          H step Q read ones | items    halt;  T step | items   MAXSTEPS reached
// Build: g++ -O2 -std=c++17 -static -o evt.exe evt.cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>

struct Tr { int w, d, nx; bool def; };
struct It { bool tok; long long m; std::string j;
    bool operator==(const It &o) const { return tok == o.tok && m == o.m && j == o.j; }
    bool operator!=(const It &o) const { return !(*this == o); } };
static std::vector<unsigned char> t;
static long long pos, sz, lo, hi, rmax1, lmin1;
static int q;

static std::string junkstr(const std::vector<unsigned char> &j) {
    std::string out = "<"; size_t i = 0; bool first = true;
    while (i < j.size()) {
        if (!first) out += "."; first = false;
        if (i + 3 < j.size() && j[i] != j[i + 1] && j[i + 2] == j[i] && j[i + 3] == j[i + 1]) {
            size_t k = i; while (k + 1 < j.size() && j[k] == j[i] && j[k + 1] == j[i + 1]) k += 2;
            out += "("; out += char('0' + j[i]); out += char('0' + j[i + 1]); out += ")^"; out += std::to_string((k - i) / 2);
            i = k; continue;
        }
        size_t k = i; while (k < j.size() && j[k] == j[i]) ++k;
        out += char('0' + j[i]); out += ":"; out += std::to_string(k - i); i = k;
    }
    return out + ">";
}
static std::vector<It> items(long long a, long long b, long long hp) {
    std::vector<It> v; std::vector<unsigned char> raw;
    auto flush = [&]() { if (!raw.empty()) { v.push_back(It{false, 0, junkstr(raw)}); raw.clear(); } };
    long long i = a;
    while (i < b) {
        if (i == hp) { flush(); v.push_back(It{false, 0, std::string("[") + char('A' + q) + "]"}); }
        if (t[i] == 1) {
            long long j = i, m = 0;
            while (j + 2 < b && t[j + 1] == 0 && t[j + 2] == 1 && !(hp > j && hp <= j + 2)) { j += 2; ++m; }
            bool ends = (j + 1 >= b) || t[j + 1] == 1 || hp == j + 1;
            if (ends) { flush(); v.push_back(It{true, m, ""}); i = j + 1; continue; }
            for (long long z = i; z <= j + 1 && z < b; ++z) raw.push_back(t[z]);
            i = std::min(j + 2, b); continue;
        }
        raw.push_back(t[i]); ++i;
    }
    flush();
    if (hp >= b) v.push_back(It{false, 0, std::string("[") + char('A' + q) + "]"});
    return v;
}
static std::string fmt(const std::vector<It> &v) {
    std::string out;
    for (size_t k = 0; k < v.size();) {
        size_t l = k; while (l < v.size() && v[l] == v[k]) ++l;
        out += v[k].tok ? std::to_string(v[k].m) : v[k].j;
        if (l - k > 1) out += "*" + std::to_string(l - k);
        out += " "; k = l;
    }
    return out;
}
static std::string shape(const std::vector<It> &v) {
    std::string out;
    for (size_t k = 0; k < v.size();) {
        size_t l = k; while (l < v.size() && v[l] == v[k]) ++l;
        if (v[k].tok) out += "#"; else for (char ch : v[k].j) if (!(ch >= '0' && ch <= '9')) out += ch;
        if (l - k > 1) out += "*";
        out += " "; k = l;
    }
    return out;
}
static long long E_ = 2;
// transition between consecutive K-moments x -> y with tail length tl: 0 none, 1/2/3
static int classify(const std::vector<It> &x, const std::vector<It> &y, size_t tl) {
    if (x.size() != y.size() || x.size() < tl + 2) return 0;
    size_t n = x.size(), ia = n - tl - 2, ir = n - tl - 1;
    for (size_t k = ir + 1; k < n; ++k) if (x[k] != y[k]) return 0;
    if (!x[ia].tok || !x[ir].tok || !y[ia].tok || !y[ir].tok) return 0;
    long long a0 = x[ia].m, r0 = x[ir].m, a1 = y[ia].m, r1 = y[ir].m;
    if (a0 >= 4 && a1 == a0 - 3 && r1 == 2 * r0 + 6 - E_) {
        for (long long k = (long long)ia - 1; k >= 0; --k) if (x[k] != y[k]) return 0;
        return 1;
    }
    if (a0 == 1 && r1 == E_ && ia >= 1) {
        if (a1 == 2 * r0 + 7 - 2 * E_ && x[ia - 1].tok && y[ia - 1].tok && x[ia - 1].m >= 4 && y[ia - 1].m == x[ia - 1].m - 3) {
            for (long long k = (long long)ia - 2; k >= 0; --k) if (x[k] != y[k]) return 0;
            return 2;
        }
        if (a1 == 1) {
            long long j = (long long)ia - 1;
            while (j >= 0 && x[j].tok && x[j].m == 1 && y[j].tok && y[j].m == 1) --j;
            if (j < 1) return 0;
            if (!(x[j].tok && x[j].m == 1 && y[j].tok && y[j].m == 2 * r0 + 7 - 2 * E_)) return 0;
            if (!(x[j - 1].tok && y[j - 1].tok && x[j - 1].m >= 4 && y[j - 1].m == x[j - 1].m - 3)) return 0;
            for (long long k = j - 2; k >= 0; --k) if (x[k] != y[k]) return 0;
            return 3;
        }
    }
    return 0;
}
static void dump(const char *fn) {
    if (!fn) return;
    FILE *f = fopen(fn, "w"); if (!f) return;
    long long a = std::min(lo, pos), b = std::max(hi, pos);
    fprintf(f, "%c %lld\n", 'A' + q, pos - a);
    std::string s; for (long long i = a; i <= b; ++i) s += char('0' + t[i]);
    fprintf(f, "%s\n", s.c_str()); fclose(f);
}
static std::string whole() {
    long long a = std::min(lo, pos), b = std::max(hi, pos);
    while (a < pos && t[a] == 0) ++a;
    while (b > pos && t[b] == 0) --b;
    if (b - a > 4000000) return "(too wide)";
    return fmt(items(a, b + 1, pos));
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: evt MACHINE WORDFILE HEAD STATE MAXSTEPS [opts]\n"); return 2; }
    std::string m = argv[1];
    int n = (int)(m.size() + 1) / 7;
    std::vector<Tr> tr(2 * n);
    for (int s = 0; s < n; ++s)
        for (int c = 0; c < 2; ++c) {
            const char *x = m.c_str() + 7 * s + 3 * c;
            if (x[0] == '-' || x[2] == 'Z' || x[2] - 'A' >= n) { tr[2 * s + c] = {0, 0, 0, false}; continue; }
            tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true};
        }
    std::string word; long long head = atoll(argv[3]); q = argv[4][0] - 'A';
    if (std::string(argv[2]) != "-") {
        FILE *f = fopen(argv[2], "r"); if (!f) { fprintf(stderr, "no word file\n"); return 2; }
        int ch = fgetc(f);
        if (ch >= 'A' && ch <= 'P') { q = ch - 'A'; long long h; if (fscanf(f, "%lld", &h) == 1) head = h; }
        else if (ch != EOF) ungetc(ch, f);
        while ((ch = fgetc(f)) != EOF) if (ch == '0' || ch == '1') word += (char)ch;
        fclose(f);
    }
    long long maxs = atoll(argv[5]);
    long long K = 1, MAXL = 3000, SNAP = 0, RL = 3, JSTOP = 0; const char *dumpf = nullptr; int cq = 1;
    for (int i = 6; i < argc; ++i) {
        std::string o = argv[i];
        if (o == "-q") cq = argv[++i][0] - 'A';
        else if (o == "-r") RL = atoll(argv[++i]);
        else if (o == "-k") K = atoll(argv[++i]);
        else if (o == "-m") MAXL = atoll(argv[++i]);
        else if (o == "-s") SNAP = atoll(argv[++i]);
        else if (o == "-e") E_ = atoll(argv[++i]);
        else if (o == "-d") dumpf = argv[++i];
        else if (o == "-j") JSTOP = atoll(argv[++i]);
    }
    sz = 1 << 16; while (sz < (long long)word.size() * 4 + 1024) sz *= 2;
    long long off = sz / 4;
    t.assign(sz, 0);
    for (size_t i = 0; i < word.size(); ++i) t[off + i] = word[i] == '1';
    pos = off + head; lo = off; hi = off + (long long)word.size() - 1; if (hi < lo) hi = lo;
    if (pos > hi) hi = pos;
    if (pos < lo) lo = pos;
    rmax1 = -1; lmin1 = sz;
    for (long long i = lo; i <= hi; ++i) if (t[i]) { if (rmax1 < i) rmax1 = i; if (lmin1 > i) lmin1 = i; }
    long long steps = 0, nl = 0, lastout = 0, regime = 0, supp = 0, sinceK = 0, c1 = 0, c2 = 0, c3 = 0;
    long long tl = -1;
    std::vector<It> tail, lastK; std::string lastshape;
    std::unordered_map<std::string, std::vector<It>> hist;
    auto out = [&](const std::string &s) { printf("%s\n", s.c_str()); fflush(stdout); ++nl; lastout = steps; };
    auto unlock = [&](const std::vector<It> &v) {
        out("U " + std::to_string(steps) + " " + std::to_string(c1) + " " + std::to_string(c2) + " " + std::to_string(c3) + " | " + fmt(lastK));
        out("  ! " + std::to_string(steps) + " | " + fmt(v));
        tl = -1; lastshape = shape(v); regime = 1; supp = 0; hist.clear();
    };
    while (true) {
        int c = t[pos];
        if (q == cq && c == 0 && pos > rmax1 && steps > 0) {
            long long a = lmin1 <= rmax1 ? lmin1 : pos;
            std::vector<It> v = items(a, pos, -1);
            bool handled = false;
            if (tl >= 0) {
                bool isK = (long long)v.size() >= tl + 2;
                if (isK) for (long long kk = 0; kk < tl; ++kk) if (v[v.size() - tl + kk] != tail[kk]) { isK = false; break; }
                if (isK) isK = v[v.size() - tl - 1].tok && v[v.size() - tl - 2].tok;
                if (isK) {
                    int r = classify(lastK, v, (size_t)tl);
                    if (r) {
                        if (r == 1) ++c1; else if (r == 2) ++c2; else ++c3;
                        if ((r == 3 && RL <= 3) || (r == 2 && RL <= 2))
                            out("R" + std::to_string(r) + " " + std::to_string(steps) + " | " + fmt(v));
                        lastK = v; sinceK = 0;
                        if (JSTOP > 0 && c1 + c2 + c3 >= JSTOP) { printf("J %lld e=%lld tail=%lld | %s\n", steps, E_, tl, fmt(v).c_str()); dump(dumpf); return 0; }
                    } else unlock(v);
                    handled = true;
                } else if (++sinceK > 64 + (lastK.size() > (size_t)tl && lastK[lastK.size() - tl - 1].tok ? lastK[lastK.size() - tl - 1].m * 4 : 0)) { unlock(v); handled = true; }
                else handled = true;
            }
            if (!handled) {
                std::string sh = shape(v);
                if (sh == lastshape) ++regime; else { if (supp) printf("X %lld\n", supp); regime = 0; supp = 0; lastshape = sh; }
                if (regime < K) out("C " + std::to_string(steps) + " | " + fmt(v)); else ++supp;
                std::string key = sh + "|" + std::to_string(v.size()) + (v.back().tok ? "|" + std::to_string(v.back().m) : "|" + v.back().j);
                auto itf = hist.find(key);
                if (itf != hist.end() && itf->second.size() == v.size() && v.size() >= 2) {
                    const std::vector<It> &h = itf->second;
                    long long d1 = -1, nd = 0;
                    for (long long kk = (long long)v.size() - 1; kk >= 0; --kk) if (h[kk] != v[kk]) { d1 = kk; ++nd; if (nd > 2) break; }
                    if (nd == 2) {
                        size_t p = (size_t)d1;
                        if (p + 1 < v.size() && h[p + 1] != v[p + 1] && h[p].tok && h[p + 1].tok && v[p].tok && v[p + 1].tok &&
                            h[p].m >= 4 && v[p].m == h[p].m - 3 && v[p + 1].m - 2 * h[p + 1].m >= 0 && v[p + 1].m - 2 * h[p + 1].m <= 6) {
                            E_ = 6 - (v[p + 1].m - 2 * h[p + 1].m);
                            tl = (long long)(v.size() - p - 2);
                            tail.assign(v.begin() + p + 2, v.end());
                            lastK = v; sinceK = 0; c1 = c2 = c3 = 0;
                            if (supp) { printf("X %lld\n", supp); supp = 0; }
                            out("L " + std::to_string(steps) + " e=" + std::to_string(E_) + " tail=" + std::to_string(tl) + " | " + fmt(v));
                            hist.clear();
                        }
                    }
                }
                if (tl < 0) { if (hist.size() > 4096) hist.clear(); hist[key] = v; }
            }
            if (nl >= MAXL) { printf("M %lld | %s\n", steps, whole().c_str()); dump(dumpf); return 0; }
        }
        const Tr &x = tr[2 * q + c];
        if (!x.def) {
            long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += t[i];
            if (tl >= 0) printf("U %lld %lld %lld %lld | %s\n", steps, c1, c2, c3, fmt(lastK).c_str());
            printf("H %lld %c %d %lld | %s\n", steps, 'A' + q, c, ones, whole().c_str());
            dump(dumpf); return 0;
        }
        if (steps >= maxs) {
            if (supp) printf("X %lld\n", supp);
            if (tl >= 0) printf("U %lld %lld %lld %lld | %s\n", steps, c1, c2, c3, fmt(lastK).c_str());
            printf("T %lld | %s\n", steps, whole().c_str());
            dump(dumpf); return 0;
        }
        if (SNAP > 0 && steps - lastout >= SNAP) out("S " + std::to_string(steps) + " | " + whole());
        t[pos] = (unsigned char)x.w;
        if (x.w) { if (pos > rmax1) rmax1 = pos; if (pos < lmin1) lmin1 = pos; }
        else {
            if (pos == rmax1) { long long k = pos - 1; while (k >= lo && !t[k]) --k; rmax1 = k >= lo ? k : -1; if (rmax1 < 0) lmin1 = sz; }
            if (pos == lmin1 && rmax1 >= 0) { long long k = pos + 1; while (k <= hi && !t[k]) ++k; lmin1 = k; }
        }
        pos += x.d; q = x.nx; ++steps;
        if (pos < lo) lo = pos;
        if (pos > hi) hi = pos;
        if (pos <= 1 || pos >= sz - 2) {
            std::vector<unsigned char> u(2 * sz, 0);
            memcpy(u.data() + sz / 2, t.data(), sz);
            long long d = sz / 2;
            pos += d; lo += d; hi += d; if (rmax1 >= 0) rmax1 += d; lmin1 += d; t.swap(u); sz *= 2;
        }
    }
}
