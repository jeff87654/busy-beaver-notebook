// hp: host probe. Literal run from a constructed word; at each K-moment (state Q reading 0 right of all 1s, template
// side R after mirroring) parse from the right: S, b-run (u^*), then (s u^*)* digits; the unparsed left part = outer
// prefix O. Print when (O, digit count) changes:  step lo vis | O=[rl] n=<digits> a=<raw a run> b=<raw b run> d=<raw runs, first 12>
// lo = leftmost 1, vis = leftmost cell the head visited so far (positions: word at 0..len-1).
//  hp MACHINE SIDE Q u s S WORD HEADPOS STATE MAXSTEPS MAXLINES
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
int W[16][2], D[16][2], NX[16][2];
static std::string rl(const std::string &w, size_t maxch = 300) {
    std::string o; size_t i = 0;
    while (i < w.size() && o.size() < maxch) { size_t j = i; while (j < w.size() && w[j] == w[i]) ++j;
        size_t n = j - i; if (n >= 4) o += std::string(1, w[i]) + "^" + std::to_string(n) + " "; else o += w.substr(i, n) + " "; i = j; }
    if (i < w.size()) o += "...";
    if (!o.empty() && o.back() == ' ') o.pop_back();
    return o;
}
int main(int argc, char **argv) {
    if (argc < 12) { fprintf(stderr, "usage\n"); return 1; }
    std::string m = argv[1]; char side = argv[2][0]; int Q = argv[3][0] - 'A';
    std::string u = argv[4], s = argv[5], S = argv[6]; if (S == "-") S = "";
    std::string w0 = argv[7]; if (w0 == "-") w0 = "";
    long long pos = atoll(argv[8]); int q = argv[9][0] - 'A'; long long maxs = atoll(argv[10]); long long maxl = atoll(argv[11]);
    int n = (int)(m.size() + 1) / 7;
    for (int qq = 0; qq < n; ++qq) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * qq + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') { NX[qq][c] = -1; continue; } W[qq][c] = x[0] - '0'; D[qq][c] = x[1] == 'R' ? 1 : -1; NX[qq][c] = x[2] - 'A'; }
    if (side == 'L') for (int qq = 0; qq < n; ++qq) for (int c = 0; c < 2; ++c) D[qq][c] = -D[qq][c];
    long long size = 1 << 20; while (size < 4 * (long long)w0.size() + 4096) size *= 2; long long off = size / 2;
    std::vector<unsigned char> t(size, 0);
    long long lo = 1, hi = 0;
    for (size_t z = 0; z < w0.size(); ++z) { t[off + z] = w0[z] == '1'; if (w0[z] == '1') { if (lo > hi) lo = hi = (long long)z; else hi = (long long)z; } }
    long long vis = pos, lines = 0; std::string lastkey = "#";
    for (long long st = 0; st < maxs; ++st) {
        if (pos + off < 2 || pos + off + 2 >= size) { std::vector<unsigned char> nt(size * 2, 0); memcpy(nt.data() + size / 2, t.data(), size); off += size / 2; size *= 2; t.swap(nt); }
        unsigned char *T = t.data() + off; int c = T[pos];
        if (c == 0 && q == Q && lo <= hi) {
            while (lo <= hi && !T[hi]) --hi; while (lo <= hi && !T[lo]) ++lo;
            if (pos > hi) {
                std::string w; for (long long i = lo; i < pos; ++i) w += char('0' + T[i]);
                if (w.size() >= S.size() && w.compare(w.size() - S.size(), S.size(), S) == 0) {
                    long long e = (long long)w.size() - (long long)S.size(); std::vector<long long> rr;
                    while (true) { long long k = 0; while (e - (long long)u.size() >= 0 && w.compare(e - u.size(), u.size(), u) == 0) { e -= u.size(); ++k; }
                        rr.push_back(k); if (e - (long long)s.size() >= 0 && w.compare(e - s.size(), s.size(), s) == 0 && rr.size() < 1000000) e -= s.size(); else break; }
                    std::string O = w.substr(0, e);
                    long long nd = (long long)rr.size() - 2;
                    std::string key = rl(O, 120) + "|" + std::to_string(nd);
                    if (key != lastkey) {
                        std::string ds; long long shown = 0;
                        for (long long j = (long long)rr.size() - 1; j >= 2 && shown < 12; ) { long long v = rr[j]; long long r = j; while (r >= 2 && rr[r] == v) --r;
                            ds += std::to_string(v); if (j - r > 1) ds += "^" + std::to_string(j - r); ds += ","; j = r; ++shown; }
                        printf("%lld %lld %lld | O=[%s] n=%lld a=%lld b=%lld d=%s\n", st, lo, vis, rl(O, 200).c_str(), nd, rr.size() > 1 ? rr[1] : -1, rr[0], ds.c_str());
                        lastkey = key; if (++lines >= maxl) { printf("MAXL\n"); return 0; }
                    }
                }
            }
        }
        if (NX[q][c] < 0) { printf("HALT %lld state %c read %d lo %lld vis %lld\n", st, 'A' + q, c, lo, vis); return 0; }
        T[pos] = W[q][c]; if (W[q][c]) { if (lo > hi) lo = hi = pos; else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; } }
        pos += D[q][c]; q = NX[q][c]; if (pos < vis) vis = pos;
    }
    printf("END\n");
}
