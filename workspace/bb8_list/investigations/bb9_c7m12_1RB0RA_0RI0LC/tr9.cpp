// tr9.cpp: literal TM tracer (up to 16 states), tape grows as needed.
//   tr9 MACHINE TAPE HEAD STATE MAXSTEPS MODE [ARGS...]
// MODE geo F      : print at steps ~ F^k (F a float > 1), starting at 1000
// MODE trans QS N : print every time transition QS (e.g. E0) is about to be taken, at most N prints
// MODE every K    : print every K steps
// MODE usage W    : print transition usage counts per window of W steps
// Tape print: run-length view with the head shown as [Q] before the scanned cell.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <string>
#include <vector>

struct Tr { int w, d, nx; bool def; };
static std::vector<unsigned char> t;
static long long lo, hi, pos, off, sz;
static int q;

static std::string rle(long long a, long long b) {
    std::string out;
    long long i = a;
    auto cell = [&](long long k) { return std::string(k == pos ? std::string("[") + char('A' + q) + "]" : "") + char('0' + t[k]); };
    while (i <= b) {
        if (i + 3 <= b && t[i] != t[i + 1] && t[i + 2] == t[i] && t[i + 3] == t[i + 1] &&
            !(pos >= i && pos <= i + 3)) {
            long long j = i;
            while (j + 1 <= b && t[j] == t[i] && t[j + 1] == t[i + 1] && !(pos == j || pos == j + 1)) j += 2;
            if ((j - i) / 2 >= 2) {
                out += "(" + std::to_string(t[i]) + std::to_string(t[i + 1]) + ")^" + std::to_string((j - i) / 2) + " ";
                i = j;
                continue;
            }
        }
        long long j = i;
        while (j <= b && t[j] == t[i] && j != pos) ++j;
        if (j == i) { out += cell(i) + " "; ++i; continue; }
        if (j - i >= 4) out += std::to_string(t[i]) + "^" + std::to_string(j - i) + " ";
        else { for (long long k = i; k < j; ++k) out += char('0' + t[k]); out += " "; }
        i = j;
    }
    return out;
}


// D-token view of cells [a, b): D(m) = (10)^m 1 tokens as numbers, other cells as raw text in <...>,
// equal consecutive tokens compressed to x*k.
static std::string dtoks(long long a, long long b) {
    std::vector<std::string> tok;
    std::string raw;
    auto flushraw = [&]() {
        if (raw.empty()) return;
        // compress raw: runs of 10/01 pairs and of equal cells
        std::string out; size_t i = 0;
        while (i < raw.size()) {
            size_t j = i;
            if (i + 3 < raw.size() && raw[i] != raw[i + 1] && raw[i + 2] == raw[i] && raw[i + 3] == raw[i + 1]) {
                while (j + 1 < raw.size() && raw[j] == raw[i] && raw[j + 1] == raw[i + 1]) j += 2;
                out += "(" + raw.substr(i, 2) + ")^" + std::to_string((j - i) / 2) + " "; i = j; continue;
            }
            while (j < raw.size() && raw[j] == raw[i]) ++j;
            if (j - i >= 3) out += std::string(1, raw[i]) + "^" + std::to_string(j - i) + " ";
            else out += raw.substr(i, j - i) + " ";
            i = j;
        }
        if (!out.empty()) out.pop_back();
        tok.push_back("<" + out + ">"); raw.clear();
    };
    long long i = a;
    while (i < b && t[i] == 0) ++i;
    while (i < b) {
        long long j = i, m = 0;
        while (j + 1 < b && t[j] == 1 && t[j + 1] == 0) { j += 2; ++m; }
        if (j < b && t[j] == 1) { flushraw(); tok.push_back(std::to_string(m)); i = j + 1; }
        else { raw += char('0' + t[i]); ++i; }
    }
    flushraw();
    std::string out;
    for (size_t k = 0; k < tok.size();) {
        size_t l = k; while (l < tok.size() && tok[l] == tok[k]) ++l;
        out += tok[k]; if (l - k > 1) out += "*" + std::to_string(l - k); out += " "; k = l;
    }
    return out;
}
static std::string shapeof(const std::string &s) {
    std::string o; bool num = false;
    for (char c : s) { if (c >= '0' && c <= '9') { if (!num) o += '#'; num = true; } else { o += c; num = false; } }
    return o;
}

int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage: tr9 MACHINE TAPE HEAD STATE MAXSTEPS MODE [ARGS]\n"); return 2; }
    std::string m = argv[1];
    int n = (int)(m.size() + 1) / 7;
    std::vector<Tr> tr(2 * n);
    for (int s = 0; s < n; ++s)
        for (int c = 0; c < 2; ++c) {
            const char *x = m.c_str() + 7 * s + 3 * c;
            if (x[0] == '-' || x[2] == 'Z') { tr[2 * s + c] = {0, 0, 0, false}; continue; }
            tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true};
        }
    std::string word = argv[2];
    if (word == "-") word = "";
    long long head = atoll(argv[3]);
    q = argv[4][0] - 'A';
    long long maxs = atoll(argv[5]);
    std::string mode = argv[6];
    double F = 2; long long every = 0, window = 0; int tq = -1, tc = -1; long long tN = 0, tcount = 0;
    if (mode == "geo") F = atof(argv[7]);
    if (mode == "every") every = atoll(argv[7]);
    if (mode == "usage") window = atoll(argv[7]);
    if (mode == "trans") { tq = argv[7][0] - 'A'; tc = argv[7][1] - '0'; tN = atoll(argv[8]); }
    // MODE redge GAP N : print when the head stands on the rightmost visited cell, at most N prints,
    //                    and only if GAP steps passed since the last such print
    long long gap = 0, lastp = -1000000000000LL, eN = 0, ecount = 0;
    if (mode == "redge" || mode == "ledge") { gap = atoll(argv[7]); eN = atoll(argv[8]); }
    // MODE match WORDFILE : stop with "MATCH step" the first time the head is in state B on the rightmost visited
    //                       cell and the visited tape left of it (leading blanks dropped) equals the word in WORDFILE
    // MODE dshape MAXPRINT : at every right-edge visit in state B reading 0, print the D-token view when its
    //                       shape (numbers -> #) changes; repeated shapes are counted
    std::string target, lastshape, lastline; long long dsim = 0, dprints = 0, dmax = 0;
    if (mode == "dshape" || mode == "deadend" || mode == "aevents" || mode == "kcanon" || mode == "dall") dmax = atoll(argv[7]);
    if (mode == "match") { FILE *f = fopen(argv[7], "r"); char buf[1 << 16]; std::string w; size_t k;
        while ((k = fread(buf, 1, sizeof buf, f)) > 0) w.append(buf, k); fclose(f);
        for (char ch : w) if (ch == '0' || ch == '1') target += ch; }
    sz = 1 << 16; off = sz / 2;
    t.assign(sz, 0);
    for (size_t i = 0; i < word.size(); ++i) t[off + i] = word[i] == '1';
    pos = off + head; lo = off; hi = off + (long long)word.size() - 1; if (hi < lo) hi = lo;
    if (pos > hi) hi = pos; if (pos < lo) lo = pos;
    double nextg = 1000; long long steps = 0; int prevq = -1;
    std::vector<long long> use(2 * n, 0);
    auto show = [&](const char *tag) {
        long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += t[i];
        printf("%s step %lld: state %c, ones %lld, width %lld, head %lld\n  %s\n", tag, steps, 'A' + q, ones,
               hi - lo + 1, pos - lo, rle(lo, hi).c_str());
        fflush(stdout);
    };
    while (steps < maxs) {
        int c = t[pos];
        const Tr &x = tr[2 * q + c];
        if (!x.def) { if (mode == "dshape") printf("HALT tokens | %s\n", dtoks(lo, hi + 1).c_str()); show("HALT"); return 0; }
        if (mode == "trans" && q == tq && c == tc) { show("T"); if (++tcount >= tN) return 0; }
        if (mode == "match" && q == 1 && pos == hi && pos - lo >= (long long)target.size()) {
            long long f = lo; while (f < pos && t[f] == 0) ++f;
            if (pos - f == (long long)target.size()) {
                bool ok = true;
                for (size_t i = 0; i < target.size() && ok; ++i) ok = (t[f + i] == (unsigned char)(target[i] - '0'));
                if (ok) { printf("MATCH step %lld\n", steps); return 0; }
            }
        }
        if (((mode == "redge" && pos == hi) || (mode == "ledge" && pos == lo)) && steps - lastp >= gap) {
            show("R"); lastp = steps; if (++ecount >= eN) return 0;
        }
        // MODE dall N : D-token view at every right-edge visit in state B reading 0 (no shape filter)
        if (mode == "dall" && q == 1 && c == 0 && pos == hi) {
            printf("S %lld | %s\n", steps, dtoks(lo, pos).c_str());
            if (++dprints >= dmax) return 0;
        }
        if (mode == "dshape" && q == 1 && c == 0 && pos == hi) {
            std::string v = dtoks(lo, pos), sh = shapeof(v);
            if (sh != lastshape) {
                if (dsim) printf("   ... %lld similar; last: %s\n", dsim, lastline.c_str());
                printf("S %lld | %s\n", steps, v.c_str()); fflush(stdout);
                lastshape = sh; dsim = 0; if (++dprints >= dmax) return 0;
            } else { ++dsim; lastline = std::to_string(steps) + " | " + v; }
        }
        if (mode == "deadend" && q == 4 && c == 0 && (prevq == 3 || !(t[pos - 1] == 0 && t[pos + 1] == 1))) {
            printf("DE %lld %s ctx %d%d | %s [E] %s\n", steps, prevq == 3 ? "A" : "B", t[pos - 1], t[pos + 1],
                   dtoks(lo, pos).c_str(), dtoks(pos, hi + 1).c_str());
            fflush(stdout); if (++dprints >= dmax) return 0;
        }
        // MODE kcanon N : print the D-token view of every canonical K configuration (head in B on the right edge,
        // reading 0, the six cells to its left are 111001); the suffix is not shown
        if (mode == "kcanon" && q == 1 && c == 0 && pos == hi && pos - lo >= 6 && t[pos - 6] == 1 && t[pos - 5] == 1 &&
            t[pos - 4] == 1 && t[pos - 3] == 0 && t[pos - 2] == 0 && t[pos - 1] == 1) {
            printf("K %lld | %s\n", steps, dtoks(lo, pos - 6).c_str());
            fflush(stdout); if (++dprints >= dmax) return 0;
        }
        // MODE aevents N : compact log of A-events (E entered from D1 reading 0 = the champion's halting move):
        // WHOLE if nothing but blanks is left of the head, the context, and the last/first tokens around the head
        if (mode == "aevents" && q == 4 && c == 0 && prevq == 3) {
            bool whole = true; for (long long i = lo; i < pos; ++i) if (t[i]) { whole = false; break; }
            std::string L = dtoks(lo, pos), R = dtoks(pos, hi + 1);
            if (L.size() > 120) L = "..." + L.substr(L.size() - 120);
            if (R.size() > 160) R = R.substr(0, 160) + "...";
            printf("AE %lld %s ctx %d%d width %lld | %s [E] %s\n", steps, whole ? "WHOLE" : "inner", t[pos - 1],
                   t[pos + 1], hi - lo + 1, L.c_str(), R.c_str());
            fflush(stdout); if (++dprints >= dmax) return 0;
        }
        use[2 * q + c]++;
        prevq = q;
        t[pos] = (unsigned char)x.w; pos += x.d; q = x.nx; ++steps;
        if (pos < lo) lo = pos;
        if (pos > hi) hi = pos;
        if (pos <= 0 || pos >= sz - 1) {
            std::vector<unsigned char> u(2 * sz, 0);
            memcpy(u.data() + sz / 2, t.data(), sz);
            pos += sz / 2; lo += sz / 2; hi += sz / 2; off += sz / 2;
            t.swap(u); sz *= 2;
        }
        if (mode == "geo" && (double)steps >= nextg) { show("G"); nextg *= F; }
        if (mode == "every" && steps % every == 0) show("E");
        if (mode == "usage" && steps % window == 0) {
            printf("W %lld:", steps);
            for (int i = 0; i < 2 * n; ++i) printf(" %c%d=%lld", 'A' + i / 2, i % 2, use[i]);
            printf("\n"); fflush(stdout);
            std::fill(use.begin(), use.end(), 0);
        }
    }
    if (mode == "dshape" && dsim) printf("   ... %lld similar; last: %s\n", dsim, lastline.c_str());
    show("END");
    return 0;
}
