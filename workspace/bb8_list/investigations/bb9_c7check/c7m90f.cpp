// c7macro.cpp (bb9_c7check, 2026-10-21): exact TM simulation with an 18-cell block macro machine + chain steps
// (Marxen-Buntrock), RLE stacks of identical blocks.  No jumps of any kind: every TM step is executed, or exactly
// multiplied by a chain step over a run of identical blocks that the head crosses in one state.
// Start: --kt "tok,tok*cnt,zN,...;m;r;t" (far -> near, same format as wsim/c7sim; numbers may be huge), head after the
// final 1001 in state B (as wsim).  Stops at the first CL moment in wsim's exact sense (state B reading 0 with only
// zeros to the right, preceded by 1001 (11111100)^t 11 (10)^r D(m); m = 1, then k >= 0 tokens D1, then X = 1 mod 3,
// X >= 4), skipping the first --nocl N of them, or at a halt.  Prints J line, CTX (tokens left of X), VIEW (tokens up to
// the end of D(m)); or HALT (step, ones, full token view).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <unordered_map>
#include <cstdint>
#include <utility>
#include <windows.h>
typedef long long ll; typedef unsigned long long ull;
static const int K = 90; typedef unsigned __int128 BW;
static inline int pc(BW w){ return __builtin_popcountll((unsigned long long)w) + __builtin_popcountll((unsigned long long)(w>>64)); }
static int Wt[32], Dm[32], Nx[32]; static bool def[32];
static const int QB = 1;
struct Ent { BW w; ull c; };
static std::vector<Ent> Ls, Rs;     // back() = block adjacent to the head boundary
struct Res { BW w; uint32_t steps; int8_t side; int8_t q; int8_t pos; };   // side 0 exit left, 1 exit right, 2 halt, 3 candidate
struct KH { size_t operator()(const std::pair<BW,int>&k) const { unsigned long long a=(unsigned long long)k.first, b=(unsigned long long)(k.first>>64); return (size_t)((a*0x9E3779B97F4A7C15ULL) ^ (b*0xC2B2AE3D27D4EB4FULL) ^ (unsigned long long)k.second*0x165667B19E3779F9ULL); } };
static std::unordered_map<std::pair<BW,int>, Res, KH> cache;
static ull nmacro = 0, nchain = 0;
static Res simb(BW w, int pos, int q, bool cand, bool skipfirst) {
    uint32_t steps = 0; bool first = true;
    while (true) {
        if (pos < 0) return {w, steps, 0, (int8_t)q, -1};
        if (pos >= K) return {w, steps, 1, (int8_t)q, K};
        int c = (w >> pos) & 1;
        if (cand && q == QB && c == 0 && !(first && skipfirst) && (w >> pos) == 0) return {w, steps, 3, (int8_t)q, (int8_t)pos};
        first = false;
        int i = 2 * q + c;
        if (!def[i]) return {w, steps, 2, (int8_t)q, (int8_t)pos};
        if (Wt[i]) w |= ((BW)1 << pos); else w &= ~(((BW)1 << pos));
        pos += Dm[i]; q = Nx[i]; ++steps;
        if (steps > 50000000u) { fprintf(stderr, "block loop\n"); exit(3); }
    }
}
static Res macro(BW w, int side, int q, bool cand) {
    std::pair<BW,int> key(w, (q << 2) | (side << 1) | (cand ? 1 : 0));
    auto it = cache.find(key); if (it != cache.end()) return it->second;
    Res r = simb(w, side ? K - 1 : 0, q, cand, false); cache[key] = r; return r;
}
static void pushS(std::vector<Ent> &S, BW w, ull c) {
    if (c == 0) return;
    if (S.empty() && w == 0) return;
    if (!S.empty() && S.back().w == w) S.back().c += c; else S.push_back({w, c});
}

// ---------------- front chains: a head that crawls through a run of identical blocks with bounces into the block behind it
struct FRes { bool ok; BW a2, b2; int q; uint32_t steps; };
struct FK { BW a, b; int q; bool operator==(const FK &o) const { return a == o.a && b == o.b && q == o.q; } };
struct FKH { size_t operator()(const FK &k) const { KH h; return h(std::pair<BW,int>(k.a, k.q)) * 31 + h(std::pair<BW,int>(k.b, 7)); } };
static std::unordered_map<FK, FRes, FKH> fcacheR, fcacheL;
static ull nfront = 0;
static FRes fsim(BW a, BW b, int q, int pos, bool wantRight) {   // window a (cells 0..K-1) b (cells K..2K-1)
    unsigned char t[2 * K]; for (int j = 0; j < K; ++j) { t[j] = (a >> j) & 1; t[K + j] = (b >> j) & 1; }
    uint32_t steps = 0;
    while (true) {
        if (pos < 0 || pos >= 2 * K) break;
        int i = 2 * q + t[pos];
        if (!def[i]) return {false, 0, 0, q, steps};
        t[pos] = Wt[i]; pos += Dm[i]; q = Nx[i]; ++steps;
        if (steps > 20000000u) return {false, 0, 0, q, steps};
    }
    bool ok = wantRight ? (pos >= 2 * K) : (pos < 0);
    BW a2 = 0, b2 = 0; for (int j = 0; j < K; ++j) { if (t[j]) a2 |= (BW)1 << j; if (t[K + j]) b2 |= (BW)1 << j; }
    return {ok, a2, b2, q, steps};
}
static FRes frontR(BW u, BW w, int q) { FK k{u, w, q}; auto it = fcacheR.find(k); if (it != fcacheR.end()) return it->second; FRes r = fsim(u, w, q, K, true); fcacheR[k] = r; return r; }
static FRes frontL(BW w, BW u, int q) { FK k{w, u, q}; auto it = fcacheL.find(k); if (it != fcacheL.end()) return it->second; FRes r = fsim(w, u, q, K - 1, false); fcacheL[k] = r; return r; }
static void popOne(std::vector<Ent> &S) { if (--S.back().c == 0) S.pop_back(); }
// ---------------- writer (initial tape) ----------------
static BW wcur = 0; static int wf = 0;
static void wbit(int b) { if (b) wcur |= ((BW)1 << wf); ++wf; if (wf == K) { pushS(Ls, wcur, 1); wcur = 0; wf = 0; } }
static void wrun(const std::vector<int> &p, ull n) {
    ull L = p.size(); ull total = L * n, done = 0; size_t ph = 0;
    while (done < total && wf != 0) { wbit(p[ph]); ph = (ph + 1) % L; ++done; }
    if (K % L == 0 && total - done >= (ull)K) {
        BW b = 0; for (int j = 0; j < K; ++j) if (p[(ph + j) % L]) b |= ((BW)1 << j);
        ull nb = (total - done) / K; pushS(Ls, b, nb); done += nb * K;
    } else if (total - done > 200000000ULL) { fprintf(stderr, "run too long for non-dividing period %llu\n", L); exit(2); }
    while (done < total) { wbit(p[ph]); ph = (ph + 1) % L; ++done; }
}
static void wtok(ull x, ull cnt) {   // D(x)^cnt
    if (cnt == 0) return;
    if (2 * x + 1 <= 64 && cnt > 1) { std::vector<int> p; for (ull i = 0; i < x; ++i) { p.push_back(1); p.push_back(0); } p.push_back(1); wrun(p, cnt); return; }
    for (ull c = 0; c < cnt; ++c) { wrun({1, 0}, x); wbit(1); }
}
// ---------------- forward tokenizer with copy skipping ----------------
struct Tok { std::string s; ull c; };
struct TZ { int st; ull v; };   // st 0: Z(v) zeros, 1: T(x) after a 1, 2: T'(x) after "1 0"
static std::vector<Tok> out; static bool lead = true;
static void emit(const std::string &s, ull c = 1) { if (!out.empty() && out.back().s == s) out.back().c += c; else out.push_back({s, c}); }
static void feed(TZ &z, int b, std::vector<Tok> *rec) {
    auto em = [&](const std::string &s) { if (rec) { if (!rec->empty() && rec->back().s == s) rec->back().c++; else rec->push_back({s, 1}); } else emit(s); };
    if (z.st == 0) { if (!b) { if (!lead) ++z.v; return; } if (z.v > 0) em("z" + std::to_string(z.v)); lead = false; z = {1, 0}; return; }
    if (z.st == 1) { if (!b) { z.st = 2; return; } em(std::to_string(z.v)); z = {1, 0}; return; }
    if (b) { z = {1, z.v + 1}; return; }
    em(std::to_string(z.v)); z = {0, 2};
}
static void flush(TZ &z, bool tz = false) { if (z.st >= 1) emit(std::to_string(z.v)); else if (tz && !lead && z.v > 0) emit("z" + std::to_string(z.v)); z = {0, 0}; }
static std::string tokenize(const std::vector<Ent> &seq, ull lim, bool tz = false) {
    out.clear(); lead = true; TZ z = {0, 0}; ull pos = 0;
    for (size_t e = 0; e < seq.size() && pos < lim; ++e) {
        BW w = seq[e].w; ull c = seq[e].c; ull i = 0;
        while (i < c && pos < lim) {
            if (c - i >= 3 && pos + K <= lim) {
                TZ s0 = z; bool lead0 = lead; std::vector<Tok> rec;
                for (int j = 0; j < K; ++j) feed(z, (w >> j) & 1, &rec);
                for (auto &t : rec) emit(t.s, t.c);
                ++i; pos += K;
                ull rem = c - i - 1; ull fit = (lim - pos) / K; if (rem > fit) rem = fit;
                if (rem > 0 && !lead0 && !lead) {
                    if (s0.st == z.st && s0.v == z.v) {
                        if (rec.size() == 1) emit(rec[0].s, rec[0].c * rem);
                        else if (!rec.empty()) {
                            if (rem * rec.size() > 100000) { std::string g = "("; for (auto &t : rec) { if (g.size() > 1) g += ' '; g += t.s; if (t.c > 1) g += "*" + std::to_string(t.c); } g += ")^" + std::to_string(rem); emit(g); }
                            else for (ull r = 0; r < rem; ++r) for (auto &t : rec) emit(t.s, t.c);
                        }
                        i += rem; pos += rem * K;
                    } else if (rec.empty() && s0.st == z.st && z.v >= s0.v) { z.v += (z.v - s0.v) * rem; i += rem; pos += rem * K; }
                }
                continue;
            }
            for (int j = 0; j < K && pos < lim; ++j, ++pos) feed(z, (w >> j) & 1, nullptr);
            ++i;
        }
    }
    flush(z, tz);
    std::string s;
    for (auto &t : out) { if (!s.empty()) s += ' '; s += t.s; if (t.c > 1) s += "*" + std::to_string(t.c); }
    return s;
}
// ---------------- backward reader ----------------
struct BR {
    int e; ull rem; int j; BW w; ull dist;   // e: -1 current block, >=0 index in Ls, -2 blank
    int bit() const { return e == -2 ? 0 : (int)((w >> j) & 1); }
    void adv() {
        ++dist;
        if (e == -2) return;
        if (--j >= 0) return;
        if (rem > 0) { --rem; j = K - 1; return; }
        int ne = (e == -1) ? (int)Ls.size() - 1 : e - 1;
        if (ne < 0) { e = -2; return; }
        e = ne; w = Ls[ne].w; rem = Ls[ne].c - 1; j = K - 1;
    }
    int peek(int k) const { BR b = *this; for (int i = 0; i < k; ++i) b.adv(); return b.bit(); }
};
static BW altA(){ BW x=0; for(int j=0;j<K;j+=2) x|=(BW)1<<j; return x; }
static const BW ALT0 = altA(), ALT1 = ALT0 << 1;
static bool isAlt(BW w) { return w == ALT0 || w == ALT1; }
static bool is3(BW w) { for (int j = 3; j < K; ++j) if (((w >> j) & 1) != ((w >> (j - 3)) & 1)) return false; return true; }
static bool isS(BR bb, const char *s) { int L = strlen(s); for (int i = L - 1; i >= 0; --i) { if (bb.bit() != s[i] - '0') return false; bb.adv(); } return true; }
static void tok(BR &bb, ull &x) {
    x = 0;
    while (bb.peek(1) == 0 && bb.peek(2) == 1) {
        if (bb.rem > 0 && bb.e >= 0 && isAlt(bb.w)) { x += (K / 2) * bb.rem; bb.dist += (ull)K * bb.rem; bb.rem = 0; continue; }
        bb.adv(); bb.adv(); ++x;
    }
    bb.adv();
}
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    std::string M = argv[1]; int n = (M.size() + 1) / 7;
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { const char *x = M.c_str() + 7 * s + 3 * c; int i = 2 * s + c;
        if (x[0] == '-') def[i] = false; else { def[i] = true; Wt[i] = x[0] - '0'; Dm[i] = x[1] == 'R' ? 1 : -1; Nx[i] = x[2] - 'A'; } }
    std::string KT; ull MAXS = ~0ULL; ull NOCL = 0;
    for (int i = 2; i < argc; ++i) { std::string a = argv[i];
        if (a == "--kt") KT = argv[++i]; else if (a == "--maxs") MAXS = (ull)atof(argv[++i]); else if (a == "--nocl") NOCL = atoll(argv[++i]);
        else { fprintf(stderr, "bad %s\n", a.c_str()); return 2; } }
    std::vector<std::string> f; { size_t p0 = 0; while (true) { size_t p1 = KT.find(';', p0); f.push_back(KT.substr(p0, p1 == std::string::npos ? std::string::npos : p1 - p0)); if (p1 == std::string::npos) break; p0 = p1 + 1; } }
    if (f.size() != 4) { fprintf(stderr, "kt needs 4 fields\n"); return 2; }
    { size_t a0 = 0; std::string s = f[0]; while (!s.empty()) { size_t b0 = s.find(',', a0); std::string it = s.substr(a0, b0 == std::string::npos ? std::string::npos : b0 - a0);
        size_t st = it.find('*'); ull rep = st == std::string::npos ? 1 : strtoull(it.c_str() + st + 1, 0, 10);
        if (it[0] == 'z') { ull g = strtoull(it.c_str() + 1, 0, 10); wrun({0}, g * rep); } else wtok(strtoull(it.c_str(), 0, 10), rep);
        if (b0 == std::string::npos) break; a0 = b0 + 1; } }
    ull mm = strtoull(f[1].c_str(), 0, 10), rr = strtoull(f[2].c_str(), 0, 10), tt = strtoull(f[3].c_str(), 0, 10);
    wtok(mm, 1); wrun({1, 0}, rr); wbit(1); wbit(1); wrun({1, 1, 1, 1, 1, 1, 0, 0}, tt); wbit(1); wbit(0); wbit(0); wbit(1);
    int q = QB; ull steps = 0; ull ncand = 0, nclseen = 0;
    Res r = simb(wcur, wf, q, Rs.empty(), false);
    while (true) {
        steps += r.steps;
        if (r.side == 2 || r.side == 3) {
            BW w = r.w; int pos = r.pos; q = r.q;
            if (r.side == 2) {
                ull ones = 0; for (auto &e : Ls) ones += (ull)pc(e.w) * e.c; for (auto &e : Rs) ones += (ull)pc(e.w) * e.c; ones += pc(w);
                std::vector<Ent> seq(Ls.begin(), Ls.end()); seq.push_back({w, 1}); for (int i = (int)Rs.size() - 1; i >= 0; --i) seq.push_back(Rs[i]);
                int lc = pos > 0 ? (int)((w >> (pos - 1)) & 1) : (Ls.empty() ? 0 : (int)((Ls.back().w >> (K - 1)) & 1));
                printf("HALT %c%d step=%llu ones=%llu leftcell=%d macro=%llu chain=%llu cache=%zu\n", 'A' + q, (int)((w >> pos) & 1), steps, ones, lc, nmacro, nchain, cache.size());
                std::string v = tokenize(seq, ~0ULL); if (v.size() > 4000) v = v.substr(0, 1500) + " ... " + v.substr(v.size() - 2500);
                printf("  tape: %s\n", v.c_str());
                return 0;
            }
            ++ncand;
            BR b; b.e = -1; b.rem = 0; b.w = w; b.dist = 0; b.j = pos - 1;
            if (b.j < 0) { b.j = 0; b.dist = (ull)-1; b.adv(); }
            bool cl = false; ull kk = 0, X = 0, C = 0, mEndDist = 0, stDist = 0, tcount = 0, rcount = 0;
            if (isS(b, "1001")) {
                for (int i = 0; i < 4; ++i) b.adv();
                while (isS(b, "11111100")) { ++tcount; for (int i = 0; i < 8; ++i) b.adv(); }
                if (isS(b, "11")) { b.adv(); b.adv();
                    while (b.bit() == 0 && b.peek(1) == 1) {
                        if (b.rem > 0 && b.e >= 0 && isAlt(b.w)) { rcount += (K / 2) * b.rem; b.dist += (ull)K * b.rem; b.rem = 0; }
                        ++rcount; b.adv(); b.adv(); }
                    if (b.bit() == 1) { mEndDist = b.dist; ull m; tok(b, m);
                        if (m == 1) {
                            while (b.bit() == 1) {
                                if (b.rem > 0 && b.e >= 0 && is3(b.w) && b.peek(1) == 0 && b.peek(2) == 1 && b.peek(3) == 1) { kk += (K / 3) * b.rem; b.dist += (ull)K * b.rem; b.rem = 0; continue; }
                                ull x; tok(b, x);
                                if (x != 1) { X = x; stDist = b.dist - 1;
                                    if (b.bit() == 1) { BR c2 = b; tok(c2, C); } else C = (ull)-1;
                                    break; }
                                ++kk;
                            }
                            if (X % 3 == 1 && X >= 4 && rcount % 3 == 2) cl = true;
                        }
                    }
                }
            }
            if (cl) {
                ++nclseen;
                if (nclseen > NOCL) {
                    std::vector<Ent> seq(Ls.begin(), Ls.end()); seq.push_back({w, 1});
                    ull total = 0; for (auto &e : seq) total += e.c * K; total -= (ull)(K - pos);
                    std::string view = tokenize(seq, total - mEndDist);
                    std::string ctx = tokenize(seq, total - stDist - 1, true);
                    printf("J CL step=%llu t=%llu r_in=%llu k=%llu X=%llu C=%lld macro=%llu chain=%llu front=%llu cache=%zu cand=%llu\n", steps, tcount, rcount, kk, X, (ll)C, nmacro, nchain, nfront, cache.size(), ncand);
                    printf("CTX %s\n", ctx.c_str());
                    if (view.size() > 4000) view = view.substr(0, 1500) + " ... " + view.substr(view.size() - 2500);
                    printf("VIEW %s\n", view.c_str());
                    return 0;
                }
            }
            r = simb(w, pos, q, Rs.empty(), true);
            continue;
        }
        if (r.side == 1) {
            pushS(Ls, r.w, 1); q = r.q;
            while (true) {
                if (steps > MAXS) { printf("MAXS step=%llu\n", steps); return 0; }
                if (!Rs.empty() && Rs.back().c >= 2) {
                    Ent &e = Rs.back(); Res cr = macro(e.w, 0, q, false); ++nmacro;
                    if (cr.side == 1 && cr.q == q) { ull k = e.c - 1; steps += k * cr.steps; e.c -= k; pushS(Ls, cr.w, k); ++nchain; continue; }
                    if (!Ls.empty()) {
                        BW u = Ls.back().w; FRes f = frontR(u, e.w, q);
                        if (f.ok && f.q == q && f.b2 == u) { ull k = e.c - 1; steps += k * f.steps; e.c -= k; popOne(Ls); pushS(Ls, f.a2, k); pushS(Ls, u, 1); ++nfront; continue; }
                    }
                }
                break;
            }
            BW w; bool cand; if (Rs.empty()) { w = 0; cand = true; } else { w = Rs.back().w; if (--Rs.back().c == 0) Rs.pop_back(); cand = Rs.empty(); }
            r = macro(w, 0, q, cand); ++nmacro; continue;
        }
        if (r.side == 0) {
            pushS(Rs, r.w, 1); q = r.q;
            while (true) {
                if (steps > MAXS) { printf("MAXS step=%llu\n", steps); return 0; }
                if (!Ls.empty() && Ls.back().c >= 2) {
                    Ent &e = Ls.back(); Res cr = macro(e.w, 1, q, Rs.empty()); ++nmacro;
                    if (cr.side == 0 && cr.q == q) { ull k = e.c - 1; steps += k * cr.steps; e.c -= k; pushS(Rs, cr.w, k); ++nchain; continue; }
                    if (!Rs.empty()) {
                        BW u = Rs.back().w; FRes f = frontL(e.w, u, q);
                        if (f.ok && f.q == q && f.a2 == u) { ull k = e.c - 1; steps += k * f.steps; e.c -= k; popOne(Rs); pushS(Rs, f.b2, k); pushS(Rs, u, 1); ++nfront; continue; }
                    }
                }
                break;
            }
            BW w; if (Ls.empty()) w = 0; else { w = Ls.back().w; if (--Ls.back().c == 0) Ls.pop_back(); }
            r = macro(w, 1, q, Rs.empty()); ++nmacro; continue;
        }
    }
}
