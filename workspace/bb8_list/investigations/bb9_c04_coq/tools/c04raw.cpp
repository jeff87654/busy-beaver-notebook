// c04raw: literal simulator for C04 with raw RLE tape dumps at chosen events.
//   c04raw "<kt spec>" [--steps N] [--from S] [--e0] [--kmom] [--every N] [--qr Q] [--max K] [--width W] [--machine M]
// kt spec "tok,tok,...;m;r;t" (far-first; x*k = k copies, zN = N zeros; the far 0^inf is blank; no 11 prefix added)
// or raw word: "@<bits>:<state>" (head on the blank cell right of the word).
// --e0: dump when state E reads 0.  --kmom: dump at K-moments (state B on the blank right end, 1001 to the left).
// --qr Q: dump whenever the head turns from moving left to moving right while in state Q (letter) -- marks sweep ends.
// Output: tag step state | RLE of the tape (far..near) with [Q> before the head cell.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <windows.h>
typedef long long ll;
struct Tr { int w, d, nx; bool def; };
static std::vector<unsigned char> t; static ll pos, lo, hi;
static void grow() { ll add = t.size(); std::vector<unsigned char> n(t.size() + 2 * add, 0); memcpy(&n[add], t.data(), t.size()); t.swap(n); pos += add; lo += add; hi += add; }
static std::string rle(ll a, ll b) {   // cells [a,b)
    std::string s; for (ll i = a; i < b; ++i) s += char('0' + t[i]);
    std::string out; size_t i = 0, n = s.size();
    while (i < n) {
        int bk = 0, bp = 0;
        for (int p = 1; p <= 12 && i + p <= n; ++p) { int k = 1; while (i + (k + 1) * p <= n && s.compare(i + k * p, p, s, i, p) == 0) ++k;
            if (k >= 3 && k * p >= 6 && (ll)k * p > (ll)bk * bp) { bk = k; bp = p; } }
        if (bk) { if (!out.empty()) out += ' '; out += "(" + s.substr(i, bp) + ")^" + std::to_string(bk) + " "; i += (size_t)bk * bp; }
        else { out += s[i]; ++i; }
    }
    // tidy double spaces
    std::string r; for (size_t k = 0; k < out.size(); ++k) { if (out[k] == ' ' && (r.empty() || r.back() == ' ')) continue; r += out[k]; }
    while (!r.empty() && r.back() == ' ') r.pop_back();
    return r;
}
static std::string dview(ll a, ll b) {   // D-token view of cells [a,b): tokens (10)^m 1 as m, gaps of zeros as zN; RLE of equal tokens
    std::vector<std::string> tok; ll i = a;
    while (i < b) {
        if (t[i] == 0) { ll j = i; while (j < b && !t[j]) ++j; tok.push_back("z" + std::to_string(j - i)); i = j; continue; }
        ll j = i, m = 0; while (j + 2 < b && t[j] == 1 && t[j + 1] == 0 && t[j + 2] == 1) { j += 2; ++m; }
        tok.push_back(std::to_string(m)); i = j + 1;
    }
    std::string out; size_t k = 0;
    while (k < tok.size()) { size_t l = k; while (l < tok.size() && tok[l] == tok[k]) ++l;
        if (!out.empty()) out += ' '; out += tok[k]; if (l - k > 1) out += "^" + std::to_string(l - k); k = l; }
    return out;
}
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    std::string M = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF";
    std::string spec = argv[1]; ll STEPS = (ll)1e9, FROM = 0, EVERY = 0, MAXD = 1000000; bool E0 = false, KM = false, DV = false; int QR = -1; size_t WIDTH = 4000;
    for (int i = 2; i < argc; ++i) { std::string a = argv[i];
        if (a == "--steps") STEPS = (ll)atof(argv[++i]); else if (a == "--from") FROM = (ll)atof(argv[++i]);
        else if (a == "--e0") E0 = true; else if (a == "--dv") DV = true; else if (a == "--kmom") KM = true; else if (a == "--every") EVERY = (ll)atof(argv[++i]);
        else if (a == "--qr") QR = argv[++i][0] - 'A'; else if (a == "--max") MAXD = atoll(argv[++i]); else if (a == "--width") WIDTH = atoll(argv[++i]);
        else if (a == "--machine") M = argv[++i]; else if (a == "--target") ++i; else { fprintf(stderr, "bad arg %s\n", a.c_str()); return 2; } }
    int n = (M.size() + 1) / 7; std::vector<Tr> tr(2 * n);
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { const char *x = M.c_str() + 7 * s + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') tr[2 * s + c] = {0, 0, 0, false}; else tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    std::vector<unsigned char> w; int q = 1;
    std::string TGT; 
    for (int i = 2; i < argc; ++i) if (std::string(argv[i]) == "--target" && i + 1 < argc) { FILE *f = fopen(argv[i + 1], "rb"); int ch; while ((ch = fgetc(f)) != EOF) if (ch == '0' || ch == '1') TGT += char(ch); fclose(f); size_t z = TGT.find('1'); TGT = TGT.substr(z); }
    if (spec.rfind("@file:", 0) == 0) { size_t c = spec.rfind(':'); std::string fn = spec.substr(6, c - 6); FILE *f = fopen(fn.c_str(), "rb"); int ch; while ((ch = fgetc(f)) != EOF) if (ch == '0' || ch == '1') w.push_back(ch - '0'); fclose(f); q = spec[c + 1] - 'A'; }
    else if (spec[0] == '@') { size_t c = spec.find(':'); for (size_t i = 1; i < c; ++i) w.push_back(spec[i] - '0'); q = spec[c + 1] - 'A'; }
    else {
        std::vector<std::string> f; size_t p0 = 0; while (true) { size_t p1 = spec.find(';', p0); f.push_back(spec.substr(p0, p1 - p0)); if (p1 == std::string::npos) break; p0 = p1 + 1; }
        if (!f[0].empty()) { size_t a = 0; while (a <= f[0].size()) { size_t b = f[0].find(',', a); if (b == std::string::npos) b = f[0].size(); std::string it = f[0].substr(a, b - a); a = b + 1;
            ll rep = 1; size_t st = it.find('*'); if (st != std::string::npos) { rep = atoll(it.substr(st + 1).c_str()); it = it.substr(0, st); }
            for (ll k = 0; k < rep; ++k) { if (it[0] == 'z') { int z = atoi(it.c_str() + 1); for (int u = 0; u < z; ++u) w.push_back(0); }
                else { int d = atoi(it.c_str()); for (int u = 0; u < d; ++u) { w.push_back(1); w.push_back(0); } w.push_back(1); } }
            if (b == f[0].size()) break; } }
        int m = atoi(f[1].c_str()), r = atoi(f[2].c_str()), tt = atoi(f[3].c_str());
        for (int u = 0; u < m; ++u) { w.push_back(1); w.push_back(0); } w.push_back(1);
        for (int u = 0; u < r; ++u) { w.push_back(1); w.push_back(0); } w.push_back(1); w.push_back(1);
        for (int u = 0; u < tt; ++u) { const char *b = "11111100"; for (int k = 0; k < 8; ++k) w.push_back(b[k] - '0'); }
        const char *e = "1001"; for (int k = 0; k < 4; ++k) w.push_back(e[k] - '0');
    }
    ll pad = 1 << 16; t.assign(w.size() + 2 * pad, 0); memcpy(&t[pad], w.data(), w.size()); pos = pad + w.size(); lo = pad; hi = pos;
    ll st = 0, nd = 0; int lastd = 0;
    auto dump = [&](const char *tag) {
        ll a = lo, b = hi + 1; while (a < pos && !t[a]) ++a; ll bb = b; while (bb > pos + 1 && !t[bb - 1]) --bb;
        std::string s;
        if (DV && pos > a) {   // K-moment style: strip the 1001 end and tail blocks 11111100 when the head is at the right end
            ll e = pos; int tb = -1; std::string end;
            if (e - 4 >= a && t[e-4]==1 && t[e-3]==0 && t[e-2]==0 && t[e-1]==1) { e -= 4; tb = 0;
                while (e - 8 >= a) { static const int B8[8] = {1,1,1,1,1,1,0,0}; bool ok = true; for (int k = 0; k < 8; ++k) if (t[e-8+k] != B8[k]) { ok = false; break; } if (!ok) break; e -= 8; ++tb; }
                if (e - 2 >= a && t[e-1] == 1 && t[e-2] == 1) { e -= 2; end = " | 11 T" + std::to_string(tb) + " 1001"; } else { end = " | T" + std::to_string(tb) + " 1001"; } }
            else { end = ""; }
            s = dview(a, e) + end + " [" + char('A' + q) + "> " + rle(pos, bb);
        } else {
        std::string L = rle(a, pos), R = rle(pos, bb);
        s = L + " [" + char('A' + q) + "> " + R; }
        if (s.size() > WIDTH) s = s.substr(0, WIDTH / 2) + " ..... " + s.substr(s.size() - WIDTH / 2);
        printf("%s %lld %s\n", tag, st, s.c_str()); fflush(stdout); ++nd;
    };
    while (st < STEPS && nd < MAXD) {
        if (pos < 4 || pos + 4 >= (ll)t.size()) grow();
        int c = t[pos]; const Tr &x = tr[2 * q + c];
        if (st >= FROM) {
            if (E0 && q == 4 && c == 0) dump("E0");
            if (!TGT.empty() && q == 1 && c == 0 && pos >= 4 && t[pos - 1] == 1 && t[pos - 2] == 0 && t[pos - 3] == 0 && t[pos - 4] == 1) {
                bool blank = true; for (ll i = pos; i <= hi; ++i) if (t[i]) { blank = false; break; }
                if (blank) { ll a = lo; while (a < pos && !t[a]) ++a; if ((ll)TGT.size() == pos - a) { bool eq = true; for (ll i = 0; i < pos - a; ++i) if (t[a + i] != TGT[i] - '0') { eq = false; break; } if (eq) { printf("MATCH %lld\n", st); return 0; } } }
            }
            if (KM && q == 1 && c == 0 && pos >= 4 && t[pos - 1] == 1 && t[pos - 2] == 0 && t[pos - 3] == 0 && t[pos - 4] == 1) { bool blank = true; for (ll i = pos; i <= hi; ++i) if (t[i]) { blank = false; break; } if (blank) dump("K"); }
            if (EVERY && st % EVERY == 0) dump("S");
        }
        if (!x.def) { dump(c ? "HALT1" : "HALT0"); return 0; }
        if (st >= FROM && QR >= 0 && q == QR && lastd < 0 && x.d > 0) dump("T");
        t[pos] = x.w; pos += x.d; lastd = x.d; q = x.nx; ++st;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
    }
    dump("STOP");
    return 0;
}
