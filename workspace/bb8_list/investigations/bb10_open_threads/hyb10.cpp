// hyb10.cpp: literal TM simulator (up to 16 states) that reports "canonical configurations" as D-token item lists
// and stops when it has verified that the champion counter rules R1-R3 drive the run ("champion phase").
//   hyb10 MACHINE WORDFILE HEAD STATE MAXSTEPS [-k K] [-m MAXOUT] [-c NCONF] [-d DUMPFILE] [-q CANONSTATE]
//                                              [-v V] [-w W] [-x]
// WORDFILE: a file holding the initial tape as 0/1 characters; "-" = blank tape.
//   A first line "Q HEAD" (state letter, head index) overrides the HEAD/STATE arguments (the dump format).
// Canonical configuration: state CANONSTATE (default B), reading 0, no 1 to the right of the head.
// Items of a canonical configuration: the tape from the leftmost 1 to the head, greedily cut into D-tokens
// D(m) = (10)^m 1 (printed m, equal neighbours m*k) and junk (printed <..> as runs: "c:k" or "(10)^k", joined by '.').
// Champion phase detection:
//   - lock: two canonical configs (within the last W) differ exactly in two adjacent tokens (a, r) with
//     a: m+3 -> m and r -> 2r+4. The items right of r form the TAIL; configs ending in "tok tok TAIL" are K-moments.
//   - verify: consecutive K-moments must be R1 (a: m+3 -> m, r -> 2r+4), R2 (a: 1 -> 2r+3, r -> 2, the token
//     left of a: x -> x-3, x >= 4) or R3 (a = 1 stays, r -> 2, token j: x -> x-3 (x >= 4), token j+1: 1 -> 2r+3,
//     tokens j+2 .. a-1 equal 1). Anything else unlocks.
//   - after V verified transitions (default 4) print "J" and stop (unless -x: never stop on J).
// Output lines:
//   C step idx | items        canonical config (first K of each shape regime; K = 0 prints none)
//   X n                       n canonical configs of the previous regime were not printed
//   L step tail=N             lock;  V step R1|R2|R3 j  verified transition;  U step  unlock
//   J step tail=N | items     stop: champion phase verified (the K-moment)
//   N step | items            stop: NCONF canonical configs seen
//   M step | items            stop: MAXOUT C lines printed
//   H step state read ones | items      halt (whole tape, head shown as [Q] before its cell)
//   T step | items            MAXSTEPS reached (whole tape, head shown)
// -d DUMPFILE: at any stop, write "STATE HEAD\nTAPE\n" (tape = leftmost..rightmost visited cell) to DUMPFILE.
// Build: g++ -O2 -std=c++17 -static -o hyb10.exe hyb10.cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <deque>
#include <map>
#include <unordered_map>
#include <algorithm>

struct Tr { int w, d, nx; bool def; };
struct It { bool tok; long long m; std::string j; long long end = 0; bool hard = false;
    bool operator==(const It &o) const { return tok == o.tok && m == o.m && j == o.j; } };
static std::vector<unsigned char> t;
static long long pos, sz, lo, hi, rmax1, lmin1;
static int q;

static std::string junkstr(const std::vector<unsigned char> &j) {
    std::string out = "<";
    size_t i = 0; bool first = true;
    while (i < j.size()) {
        if (!first) out += ".";
        first = false;
        if (i + 3 < j.size() && j[i] != j[i + 1] && j[i + 2] == j[i] && j[i + 3] == j[i + 1]) {
            size_t k = i; while (k + 1 < j.size() && j[k] == j[i] && j[k + 1] == j[i + 1]) k += 2;
            out += "("; out += char('0' + j[i]); out += char('0' + j[i + 1]); out += ")^"; out += std::to_string((k - i) / 2);
            i = k; continue;
        }
        size_t k = i; while (k < j.size() && j[k] == j[i]) ++k;
        out += char('0' + j[i]); out += ":"; out += std::to_string(k - i);
        i = k;
    }
    return out + ">";
}

// items of cells [a, b) appended to v; the head cell hp (if a <= hp <= b) gets a marker item "[Q]" in front of it.
// Each item records its end (exclusive) and whether the end is a hard cut (a token followed by a 1): parsing that
// restarts at a hard cut gives the same items as a full parse.
static void itemsv_into(std::vector<It> &v, long long a, long long b, long long hp, long long skip = 0) {
    std::vector<unsigned char> raw; long long rawend = a;
    auto flush = [&]() { if (!raw.empty()) { It it{false, 0, junkstr(raw)}; it.end = rawend; it.hard = false; v.push_back(it); raw.clear(); } };
    long long i = a;
    while (i < b) {
        if (i == hp) { flush(); It it{false, 0, std::string("[") + char('A' + q) + "]"}; it.end = i; v.push_back(it); }
        if (t[i] == 1) {
            long long j = i, m = 0;
            if (skip > 0 && i == a) { j = i + 2 * skip; m = skip; }   // known unchanged (10) pairs of the first token
            while (j + 2 < b && t[j + 1] == 0 && t[j + 2] == 1 && !(hp > j && hp <= j + 2)) { j += 2; ++m; }
            bool ends = (j + 1 >= b) || t[j + 1] == 1 || hp == j + 1;
            if (ends) { flush(); It it{true, m, ""}; it.end = j + 1; it.hard = (j + 1 < b && t[j + 1] == 1 && hp != j + 1); v.push_back(it); i = j + 1; continue; }
            // not a token: every 1 of this (10) run fails the same way, so cells i .. j+1 are all junk
            for (long long z = i; z <= j + 1 && z < b; ++z) raw.push_back(t[z]);
            i = std::min(j + 2, b); rawend = i;
            continue;
        }
        raw.push_back(t[i]); ++i; rawend = i;
    }
    flush();
    if (hp >= b) { It it{false, 0, std::string("[") + char('A' + q) + "]"}; it.end = b; v.push_back(it); }
}
static std::vector<It> itemsv(long long a, long long b, long long hp) { std::vector<It> v; itemsv_into(v, a, b, hp); return v; }
// index of the last item that ends at a hard cut strictly left of 'dirty' (-1 if none): items 0..k are unchanged
static long long reuse_index(const std::vector<It> &v, long long dirty) {
    long long lo = 0, hi_ = (long long)v.size() - 1, k = -1;
    while (lo <= hi_) { long long mid = (lo + hi_) / 2; if (v[mid].end < dirty) { k = mid; lo = mid + 1; } else hi_ = mid - 1; }
    while (k >= 0 && !v[k].hard) --k;
    return k;
}

static std::string fmt(const std::vector<It> &v, size_t from = 0) {
    std::string out;
    for (size_t k = from; k < v.size();) {
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
        if (v[k].tok) out += "#"; else { for (char ch : v[k].j) { if (ch >= '0' && ch <= '9') { if (out.empty() || out.back() != '#') out += '#'; } else out += ch; } }
        if (l - k > 1) out += "*"; out += " "; k = l;
    }
    return out;
}

static void dump(const char *fn) {
    if (!fn) return;
    FILE *f = fopen(fn, "w"); if (!f) return;
    long long a = std::min(lo, pos), b = std::max(hi, pos);
    fprintf(f, "%c %lld\n", 'A' + q, pos - a);
    std::string s; s.reserve(b - a + 2);
    for (long long i = a; i <= b; ++i) s += char('0' + t[i]);
    fprintf(f, "%s\n", s.c_str()); fclose(f);
}

// classify the transition between two K-moments with the same tail length tl; returns 0 if none, else 1/2/3
static long long E_ = 2;   // accumulator offset: r = 3b + e; R1 r -> 2r + 6 - e, refill 2r + 7 - 2e, reset e
static int classify(const std::vector<It> &x, const std::vector<It> &y, size_t tl, long long &jpos, long long k0) {
    if (x.size() != y.size() || x.size() < tl + 2) return 0;
    size_t n = x.size(), ia = n - tl - 2, ir = n - tl - 1;
    for (size_t k = ir + 1; k < n; ++k) if (!(x[k] == y[k])) return 0;
    if (!x[ia].tok || !x[ir].tok || !y[ia].tok || !y[ir].tok) return 0;
    long long a0 = x[ia].m, r0 = x[ir].m, a1 = y[ia].m, r1 = y[ir].m;
    if (a0 >= 4 && a1 == a0 - 3 && r1 == 2 * r0 + 6 - E_) {
        for (long long k = (long long)ia - 1; k > k0; --k) if (!(x[k] == y[k])) return 0;
        jpos = (long long)ia; return 1;
    }
    if (a0 == 1 && r1 == E_ && ia >= 1) {
        if (a1 == 2 * r0 + 7 - 2 * E_ && x[ia - 1].tok && y[ia - 1].tok && x[ia - 1].m >= 4 && y[ia - 1].m == x[ia - 1].m - 3) {
            for (long long k = (long long)ia - 2; k > k0; --k) if (!(x[k] == y[k])) return 0;
            jpos = (long long)ia - 1; return 2;
        }
        if (a1 == 1) {
            // find j: the borrowed token
            long long j = (long long)ia - 1;
            while (j >= 0 && x[j].tok && x[j].m == 1 && y[j].tok && y[j].m == 1) --j;
            // now x[j] should be 1 -> y[j] = 2r+3, and x[j-1] = borrowed
            if (j < 1) return 0;
            if (!(x[j].tok && x[j].m == 1 && y[j].tok && y[j].m == 2 * r0 + 7 - 2 * E_)) return 0;
            if (!(x[j - 1].tok && y[j - 1].tok && x[j - 1].m >= 4 && y[j - 1].m == x[j - 1].m - 3)) return 0;
            for (long long k = j - 2; k > k0; --k) if (!(x[k] == y[k])) return 0;
            jpos = j - 1; return 3;
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: hyb10 MACHINE WORDFILE HEAD STATE MAXSTEPS [opts]\n"); return 2; }
    std::string m = argv[1];
    int n = (int)(m.size() + 1) / 7;
    std::vector<Tr> tr(2 * n);
    for (int s = 0; s < n; ++s)
        for (int c = 0; c < 2; ++c) {
            const char *x = m.c_str() + 7 * s + 3 * c;
            if (x[0] == '-' || x[2] == 'Z' || x[2] - 'A' >= n) { tr[2 * s + c] = {0, 0, 0, false}; continue; }
            tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true};
        }
    std::string word;
    long long head = atoll(argv[3]);
    q = argv[4][0] - 'A';
    if (std::string(argv[2]) != "-") {
        FILE *f = fopen(argv[2], "r"); if (!f) { fprintf(stderr, "no word file\n"); return 2; }
        int ch = fgetc(f);
        if (ch >= 'A' && ch <= 'P') { q = ch - 'A'; long long h; if (fscanf(f, "%lld", &h) == 1) head = h; }
        else if (ch != EOF) ungetc(ch, f);
        while ((ch = fgetc(f)) != EOF) if (ch == '0' || ch == '1') word += (char)ch;
        fclose(f);
    }
    long long maxs = atoll(argv[5]);
    unsigned long long HASH = 1469598103934665603ULL; bool hashmode = false; long long nhash = 0;
    long long K = 0, MAXOUT = 2000, NCONF = 0, V = 4, W = 4096, AMORT = 8, SUF = 48, PRELOCK = -1; const char *dumpf = nullptr; int cq = 1; bool nostop = false;
    for (int i = 6; i < argc; ++i) {
        std::string o = argv[i];
        if (o == "-k") K = atoll(argv[++i]);
        else if (o == "-m") MAXOUT = atoll(argv[++i]);
        else if (o == "-c") NCONF = atoll(argv[++i]);
        else if (o == "-d") dumpf = argv[++i];
        else if (o == "-q") cq = argv[++i][0] - 'A';
        else if (o == "-v") V = atoll(argv[++i]);
        else if (o == "-w") W = atoll(argv[++i]);
        else if (o == "-x") nostop = true;
        else if (o == "-a") AMORT = atoll(argv[++i]);
        else if (o == "-p") PRELOCK = atoll(argv[++i]);
        else if (o == "-H") hashmode = true;
        else if (o == "-e") E_ = atoll(argv[++i]);
    }
    sz = 1 << 16; while (sz < (long long)word.size() * 4 + 1024) sz *= 2;
    long long off = sz / 4;
    t.assign(sz, 0);
    for (size_t i = 0; i < word.size(); ++i) t[off + i] = word[i] == '1';
    pos = off + head; lo = off; hi = off + (long long)word.size() - 1; if (hi < lo) hi = lo;
    if (pos > hi) hi = pos; if (pos < lo) lo = pos;
    rmax1 = -1; lmin1 = sz;
    for (long long i = lo; i <= hi; ++i) if (t[i]) { if (rmax1 < i) rmax1 = i; if (lmin1 > i) lmin1 = i; }
    long long steps = 0, nout = 0, nconf = 0, regime = 0, supp = 0, verified = 0, sinceK = 0;
    long long tl = -1;           // locked tail length, -1 = not locked
    const long long INF = (long long)4e18;
    std::vector<It> tail, lastK, cur;
    long long lastK_dirty = INF, cur_a = -1, dirty = -INF;   // dirty: leftmost changed cell since the last parse
    struct HE { std::vector<It> v; long long idx; };
    std::unordered_map<std::string, HE> hist;   // last canonical config per key (suffix shape, size, last item)
    std::vector<long long> dirtyLog;            // dirty value of every parse (for prefix reuse in comparisons)
    std::string lastshape;
    long long lastparse = 0;
    while (true) {
        int c = t[pos];
        if (q == cq && c == 0 && pos > rmax1 && (steps > 0 || PRELOCK >= 0)) {
            long long a = lmin1 <= rmax1 ? lmin1 : pos;
            long long k = (a == cur_a) ? reuse_index(cur, dirty) : -1;
            long long restart = k >= 0 ? cur[k].end : a;
            // amortise: skip canonical configs whose re-parse would cost much more than the steps since the last one
            { long long cost = pos - restart;
              if (k + 1 < (long long)cur.size() && cur[k + 1].tok && a == cur_a) { long long p = std::min((dirty - restart) / 2 - 2, cur[k + 1].m); if (p > 0) cost -= 2 * p; }
              if (cost > AMORT * (steps - lastparse) + 256) goto simulate; }
            lastparse = steps;
            ++nconf;
            long long skip = 0;
            if (k + 1 < (long long)cur.size() && cur[k + 1].tok && a == cur_a) {
                long long p = (dirty - restart) / 2 - 2;
                if (p > cur[k + 1].m) p = cur[k + 1].m;
                if (p > 0) skip = p;
            }
            cur.resize(k + 1);
            itemsv_into(cur, restart, pos, -1, skip);
            cur_a = a;
            dirtyLog.push_back(dirty);
            lastK_dirty = std::min(lastK_dirty, dirty);
            dirty = INF;
            const std::vector<It> &v = cur;
            if (hashmode) {
                std::string fs = fmt(v);
                for (char ch : fs) { HASH ^= (unsigned char)ch; HASH *= 1099511628211ULL; }
                HASH ^= 0xff; HASH *= 1099511628211ULL; ++nhash;
                if (NCONF && nhash >= NCONF) { printf("HASH %016llx %lld\n", HASH, nhash); printf("N %lld | -\n", steps); return 0; }
                goto simulate;
            }
            if (PRELOCK >= 0) {
                tl = PRELOCK; tail.assign(v.end() - tl, v.end()); lastK = v; lastK_dirty = INF; verified = 0; sinceK = 0;
                PRELOCK = -1; printf("P %lld tail=%lld e=%lld | %s\n", steps, tl, E_, fmt(v).c_str()); goto simulate;
            }
            if (K > 0) {
                std::string sh = shape(v);
                if (sh == lastshape) ++regime; else {
                    if (supp) { printf("X %lld\n", supp); ++nout; }
                    regime = 0; supp = 0; lastshape = sh;
                }
                if (regime < K) { printf("C %lld %lld | %s\n", steps, regime, fmt(v).c_str()); ++nout; }
                else ++supp;
            }
            if (tl >= 0) {
                bool isK = (long long)v.size() >= tl + 2;
                if (isK) for (long long kk = 0; kk < tl; ++kk) if (!(v[v.size() - tl + kk] == tail[kk])) { isK = false; break; }
                if (isK) isK = v[v.size() - tl - 1].tok && v[v.size() - tl - 2].tok;
                if (isK) {
                    long long jp = -1;
                    long long k0 = reuse_index(v, lastK_dirty);
                    int r = classify(lastK, v, (size_t)tl, jp, k0);
                    if (r) {
                        ++verified; sinceK = 0;
                        if (K > 0 || nostop) printf("V %lld R%d %lld\n", steps, r, jp);
                        lastK = v; lastK_dirty = INF;
                        if (verified >= V) {
                            printf("J %lld tail=%lld e=%lld | %s\n", steps, tl, E_, fmt(v).c_str());
                            dump(dumpf); return 0;
                        }
                    } else {
                        if (K > 0 || nostop) printf("U %lld\n", steps);
                        tl = -1; verified = 0;
                    }
                } else if (++sinceK > 100000) { if (K > 0) printf("U %lld\n", steps); tl = -1; verified = 0; }
            }
            if (tl < 0 || verified <= 1) {
                std::string key;
                for (size_t kk = v.size() > (size_t)SUF ? v.size() - SUF : 0; kk < v.size(); ++kk) {
                    if (v[kk].tok) key += "#"; else for (char ch : v[kk].j) if (!(ch >= '0' && ch <= '9')) key += ch;
                    key += ' ';
                }
                key += std::to_string(v.size());
                key += v.back().tok ? "|" + std::to_string(v.back().m) : "|" + v.back().j;
                auto itf = hist.find(key);
                if (itf != hist.end()) {
                    const std::vector<It> &h = itf->second.v;
                    if (h.size() == v.size() && v.size() >= 2) {
                        long long ds = INF, i0 = itf->second.idx;
                        if ((long long)dirtyLog.size() - i0 > 4096) ds = -INF;
                        else for (long long ii = i0 + 1; ii < (long long)dirtyLog.size(); ++ii) ds = std::min(ds, dirtyLog[ii]);
                        long long k0 = reuse_index(v, ds);
                        long long d1 = -1, nd = 0;
                        for (long long kk = (long long)v.size() - 1; kk > k0; --kk) if (!(h[kk] == v[kk])) { d1 = kk; ++nd; if (nd > 2) break; }
                        if (nd == 2) {
                            size_t p = (size_t)d1;
                            if (p + 1 < v.size() && !(h[p + 1] == v[p + 1]) && h[p].tok && h[p + 1].tok && v[p].tok && v[p + 1].tok &&
                                h[p].m >= 4 && v[p].m == h[p].m - 3 && v[p + 1].m - 2 * h[p + 1].m >= 4 && v[p + 1].m - 2 * h[p + 1].m <= 6) {
                                E_ = 6 - (v[p + 1].m - 2 * h[p + 1].m);
                                tl = (long long)(v.size() - p - 2);
                                tail.assign(v.begin() + p + 2, v.end());
                                lastK = v; lastK_dirty = INF; verified = 1; sinceK = 0;
                                if (K > 0) printf("L %lld tail=%lld\n", steps, tl);
                            }
                        }
                    }
                }
                if ((long long)hist.size() > W || dirtyLog.size() > 2000000) { hist.clear(); dirtyLog.clear(); dirtyLog.push_back(-INF); }
                HE &e = hist[key]; e.v = v; e.idx = (long long)dirtyLog.size() - 1;
            }
            if (NCONF && nconf >= NCONF) { if (hashmode) printf("HASH %016llx %lld\n", HASH, nhash); printf("N %lld | %s\n", steps, fmt(v).c_str()); dump(dumpf); return 0; }
            if (K > 0) fflush(stdout);
            if (K > 0 && nout >= MAXOUT) { printf("M %lld | %s\n", steps, fmt(v).c_str()); dump(dumpf); return 0; }
        }
        simulate:
        const Tr &x = tr[2 * q + c];
        if (!x.def) {
            long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += t[i];
            long long a = std::min(lo, pos), b = std::max(hi, pos);
            while (a < pos && t[a] == 0) ++a;
            while (b > pos && t[b] == 0) --b;
            if (hashmode) printf("HASH %016llx %lld\n", HASH, nhash);
            printf("H %lld %c %d %lld | %s\n", steps, 'A' + q, c, ones, (b - a > 4000000) ? "" : fmt(itemsv(a, b + 1, pos)).c_str());
            dump(dumpf); return 0;
        }
        if (steps >= maxs) {
            long long a = std::min(lo, pos), b = std::max(hi, pos);
            while (a < pos && t[a] == 0) ++a;
            while (b > pos && t[b] == 0) --b;
            if (supp) printf("X %lld\n", supp);
            if (hashmode) printf("HASH %016llx %lld\n", HASH, nhash);
            printf("T %lld | %s\n", steps, (b - a > 4000000) ? "" : fmt(itemsv(a, b + 1, pos)).c_str());
            dump(dumpf); return 0;
        }
        if (t[pos] != (unsigned char)x.w && pos < dirty) dirty = pos;
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
            dirty = -INF; cur_a = -1; lastK_dirty = -INF; hist.clear(); dirtyLog.clear();
        }
    }
}
