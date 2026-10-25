// test_h1_extensions.cpp
// Exhaustively tests all 160 halting 1-state (J) extensions of h003 and C7:
// - If H1 steps onto 1, J1 is visited first (40 choices) and J0 = ---.
// - If H1 steps onto 0, J0 is visited first (40 choices) and J1 = ---.
// Runs each with --cnt --B 66 --cls 66 --mod 150 up to +150 jumps and MAXS = 1.5e8 per segment,
// recording all top views (0*2 7 1*K) and the exact halting jump/step/ones!

#include <cstdio>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <windows.h>

typedef long long ll;
struct Tr { int w, d, nx; bool def; };

struct Snapshot {
    std::vector<unsigned char> t;
    ll off, lo, hi, pos, r1, step, nj, ncl;
};

static bool at_buf(const std::vector<unsigned char>& t, ll lo, ll p, const char *s) {
    ll L = strlen(s);
    if (p - L + 1 < lo) return false;
    for (ll i = 0; i < L; ++i) if (t[p - L + 1 + i] != s[i] - '0') return false;
    return true;
}

static std::string dview_buf(const std::vector<unsigned char>& t, ll a, ll b, size_t maxc) {
    while (a <= b && !t[a]) ++a;
    std::vector<std::string> tok;
    ll i = a;
    while (i <= b) {
        if (t[i] == 0) {
            ll j = i;
            while (j <= b && !t[j]) ++j;
            if (j - i >= 2 || j > b) tok.push_back("z" + std::to_string(j - i));
            else tok.push_back("z1");
            i = j;
            continue;
        }
        ll j = i, m = 0;
        while (j + 2 <= b && t[j] == 1 && t[j + 1] == 0 && t[j + 2] == 1) { j += 2; ++m; }
        tok.push_back(std::to_string(m));
        i = j + 1;
    }
    std::string out;
    size_t k = 0;
    while (k < tok.size()) {
        size_t l = k;
        while (l < tok.size() && tok[l] == tok[k]) ++l;
        if (!out.empty()) out += ' ';
        out += tok[k];
        if (l - k > 1) out += "*" + std::to_string(l - k);
        k = l;
    }
    if (out.size() > maxc) out = out.substr(0, maxc / 3) + " ... " + out.substr(out.size() - 2 * maxc / 3);
    return out;
}

static ll powmod(ll b, ll e, ll m) {
    ll r = 1 % m; b %= m;
    while (e > 0) {
        if (e & 1) r = (__int128)r * b % m;
        b = (__int128)b * b % m;
        e >>= 1;
    }
    return r;
}

struct RunOut {
    std::string status;
    int unassigned_slot;
    ll step, seg, nj, ones, maxk;
    std::vector<std::string> tops;
    std::string last_view;
    std::string halt_view;
    Snapshot snap;
};

static void grow_snap(Snapshot& s) {
    ll add = s.t.size();
    std::vector<unsigned char> n(s.t.size() + 2 * add, 0);
    memcpy(&n[add], s.t.data(), s.t.size());
    s.t.swap(n);
    s.off += add; s.lo += add; s.hi += add; s.pos += add; s.r1 += add;
}

RunOut sim_from_snap(
    const Snapshot& init_snap,
    const std::vector<Tr>& tr,
    int init_q,
    ll B_val, ll CLS, ll MOD,
    ll JMAX, ll MAXS, ll MAXT, ll TOPK,
    bool save_snap_on_unassigned = false
) {
    Snapshot s = init_snap;
    int q = init_q;
    ll seg = 0;
    ll RMIN = 20, RMOD = 36, EXACTCAP = 4000000;
    int QS = 1; // B
    bool cnt = true;
    ll maxk = 0;
    std::string last_v;
    std::vector<std::string> tops;

    auto pickR = [&](ll want_res, ll modulus) -> ll {
        ll base = 2;
        if (want_res >= 0) {
            ll x = base;
            ll rr = ((want_res % modulus) + modulus) % modulus;
            x += ((rr - x % modulus) % modulus + modulus) % modulus;
            return x;
        }
        return base;
    };

    while (true) {
        if (s.pos <= 8 || s.pos >= (ll)s.t.size() - 8) grow_snap(s);
        int c = s.t[s.pos];
        if (q == QS && c == 0 && s.pos > s.r1 && s.step > 0 && at_buf(s.t, s.lo, s.pos - 1, "1001")) {
            ll p = s.pos - 5, tt = 0;
            while (at_buf(s.t, s.lo, p, "11111100")) { ++tt; p -= 8; }
            if (at_buf(s.t, s.lo, p, "11")) {
                p -= 2; ll r = 0;
                while (p - 1 >= s.lo && s.t[p] == 0 && s.t[p - 1] == 1) { ++r; p -= 2; }
                ll rstart = p + 1;
                std::vector<ll> tok, tpos;
                while (p >= s.lo && s.t[p] == 1) {
                    ll x = 0; ll pp = p - 1;
                    while (pp - 1 >= s.lo && s.t[pp] == 0 && s.t[pp - 1] == 1) { ++x; pp -= 2; }
                    tok.push_back(x); tpos.push_back(pp + 1); p = pp;
                }
                if (!tok.empty()) {
                    ll mm = tok[0]; int kind = 0; ll k = 0;
                    if (mm % 3 == 1 && r % 3 == 2) {
                        bool nz = mm > 1;
                        while (k + 1 < (ll)tok.size() && tok[k + 1] % 3 == 1) {
                            if (tok[k + 1] > 1) nz = true;
                            ++k;
                        }
                        if (nz) {
                            bool is_cnt = (cnt && k == 0 && k + 1 < (ll)tok.size() && tok[0] > 1 && tok[1] >= 6);
                            if (k >= 1 || is_cnt || (double)(r + 4) * pow(2.0, (double)(mm / 3)) > (double)EXACTCAP) kind = 2;
                        }
                    }
                    if (!kind && mm >= 3) kind = 1;
                    if (kind) {
                        std::string nw; ll st0; ll newr;
                        bool jc = false;
                        if (kind == 2 && cnt && k + 1 < (ll)tok.size() && tok[k] > 1 && tok[k + 1] >= 6) {
                            bool one = true;
                            for (ll i = 1; i < k; ++i) if (tok[i] != 1) one = false;
                            if (one) jc = true;
                        }
                        if (jc) {
                            ll C = tok[k + 1], j = (C - 3) / 3; st0 = tpos[k + 1];
                            ll R = pickR(CLS, MOD);
                            ++s.ncl;
                            for (ll i = 0; i < C - 3 * j; ++i) nw += "10"; nw += "1";
                            for (ll i = 0; i < 6 * R + 7; ++i) nw += "10"; nw += "1";
                            for (ll i = 0; i < k; ++i) nw += "101";
                            newr = 2;
                        } else if (kind == 2) {
                            st0 = tpos[k];
                            for (ll i = 0; i <= k; ++i) nw += "101";
                            ll R = (s.ncl == 0 && B_val >= 0) ? B_val : pickR(CLS, MOD);
                            newr = 3 * R + 2;
                            ++s.ncl;
                            if (k > maxk) maxk = k;
                        } else {
                            st0 = tpos[0]; ll k3 = mm / 3, m2 = mm % 3;
                            for (ll i = 0; i < m2; ++i) nw += "10"; nw += "1";
                            double approx = (double)(r + 4); bool small = true; ll ex = r + 4;
                            for (ll i = 0; i < k3; ++i) {
                                approx *= 2;
                                if (approx > (double)EXACTCAP) { small = false; break; }
                                ex *= 2;
                            }
                            if (small) newr = ex - 4;
                            else {
                                ll res = ((__int128)powmod(2, k3, RMOD) * ((r + 4) % RMOD) % RMOD - 4 + RMOD) % RMOD;
                                newr = RMIN + ((res - RMIN % RMOD) % RMOD + RMOD) % RMOD;
                            }
                        }
                        for (ll i = 0; i < newr; ++i) nw += "10";
                        nw += "11";
                        for (ll i = 0; i < tt; ++i) nw += "11111100";
                        nw += "1001";
                        ++s.nj;
                        std::string vv = dview_buf(s.t, s.lo, rstart - 1, 240);
                        last_v = vv;
                        {
                            size_t sp = vv.rfind(' ');
                            std::string last = sp == std::string::npos ? vv : vv.substr(sp + 1);
                            std::string pref = sp == std::string::npos ? "" : vv.substr(0, sp);
                            int ntok = 0;
                            for (char ch : vv) if (ch == ' ') ++ntok;
                            if (last.size() > 2 && last[0] == '1' && last[1] == '*' && atoll(last.c_str() + 2) >= TOPK && ntok <= 5) {
                                tops.push_back(pref + ":" + last.substr(2) + "(t=" + std::to_string(tt) + ")");
                            }
                        }
                        for (ll i = st0; i <= std::max(s.hi, s.pos); ++i) s.t[i] = 0;
                        while (st0 + (ll)nw.size() + 16 >= (ll)s.t.size()) {
                            ll o = s.off; grow_snap(s); st0 += s.off - o;
                        }
                        for (size_t i = 0; i < nw.size(); ++i) s.t[st0 + i] = nw[i] - '0';
                        s.pos = st0 + nw.size(); s.hi = s.pos; s.r1 = s.pos - 1; q = QS; seg = 0;
                        if (s.nj >= JMAX) {
                            return {"MAXJ", -1, s.step, seg, s.nj, 0, maxk, tops, last_v, "", {}};
                        }
                        continue;
                    }
                }
            }
        }
        int slot = 2 * q + c;
        const Tr &x = tr[slot];
        if (!x.def) {
            ll ones = 0;
            for (ll i = s.lo; i <= s.hi; ++i) ones += s.t[i];
            char buf[32];
            snprintf(buf, sizeof buf, "UNDEF_%c%d", 'A' + q, c);
            std::string hv = dview_buf(s.t, s.lo, std::max(s.hi, s.pos), 240);
            if (save_snap_on_unassigned) {
                return {buf, slot, s.step, seg, s.nj, ones, maxk, tops, last_v, hv, s};
            } else {
                return {buf, slot, s.step, seg, s.nj, ones, maxk, tops, last_v, hv, {}};
            }
        }
        s.t[s.pos] = x.w;
        if (x.w && s.pos > s.r1) s.r1 = s.pos;
        else if (!x.w && s.pos == s.r1) { while (s.r1 >= s.lo && !s.t[s.r1]) --s.r1; }
        s.pos += x.d; q = x.nx; ++s.step; ++seg;
        if (s.pos < s.lo) s.lo = s.pos;
        if (s.pos > s.hi) s.hi = s.pos;
        if (seg >= MAXS || s.step >= MAXT) {
            return {"MAXS", -1, s.step, seg, s.nj, 0, maxk, tops, last_v, "", {}};
        }
    }
}

std::vector<Tr> parse_tm(const std::string& m, int n_states = 10) {
    std::vector<Tr> tr(2 * n_states, {0, 0, 0, false});
    int n = (m.size() + 1) / 7;
    for (int s = 0; s < n; ++s) {
        for (int c = 0; c < 2; ++c) {
            const char *x = m.c_str() + 7 * s + 3 * c;
            if (x[0] == '-' || x[2] == 'Z') tr[2 * s + c] = {0, 0, 0, false};
            else tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true};
        }
    }
    return tr;
}

std::string fmt_tr(const Tr& x) {
    if (!x.def) return "---";
    char buf[8];
    snprintf(buf, sizeof buf, "%d%c%c", x.w, x.d == 1 ? 'R' : 'L', 'A' + x.nx);
    return buf;
}

int main() {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);

    struct BaseInfo {
        const char* name;
        const char* tm;
    } bases[] = {
        {"h003", "1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0LI---_1RI1RC"},
        {"C7",   "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_1LC0RA"},
    };

    Snapshot blank;
    blank.t.assign(1 << 22, 0);
    blank.off = (1 << 21);
    blank.pos = blank.off;
    blank.lo = blank.off;
    blank.hi = blank.off;
    blank.r1 = blank.off - 1;
    blank.step = 0; blank.nj = 0; blank.ncl = 0;

    for (const auto& b : bases) {
        auto tr = parse_tm(b.tm, 10);
        RunOut r0 = sim_from_snap(blank, tr, 0, 66, 66, 150, 200, (ll)1e8, (ll)1e9, 200, true);
        printf("=== Base %s: status=%s step=%lld nj=%lld ones=%lld ===\n",
               b.name, r0.status.c_str(), r0.step, r0.nj, r0.ones);
        fflush(stdout);

        int h_cnt = 0, maxj_cnt = 0, maxs_cnt = 0;
        for (int h1_w = 0; h1_w < 2; ++h1_w) {
            for (int h1_d : {-1, 1}) {
                Tr h1_tr = {h1_w, h1_d, 9, true}; // -> J (state 9)
                int next_c = r0.snap.t[r0.snap.pos + h1_d]; // symbol seen by J on step 1!
                for (int j_w = 0; j_w < 2; ++j_w) {
                    for (int j_d : {-1, 1}) {
                        for (int j_nx = 0; j_nx < 10; ++j_nx) {
                            auto tr2 = tr;
                            tr2[2 * 7 + 1] = h1_tr; // H1
                            tr2[2 * 9 + next_c] = {j_w, j_d, j_nx, true}; // defined slot
                            tr2[2 * 9 + (1 - next_c)] = {0, 0, 0, false}; // halting slot = ---
                            ll nj0 = r0.snap.nj;
                            RunOut r1 = sim_from_snap(r0.snap, tr2, 7, 66, 66, 150, nj0 + 150, (ll)1.5e8, r0.step + (ll)2e9, 200, false);
                            ll dj = r1.nj - nj0;
                            if (r1.status.rfind("UNDEF", 0) == 0) h_cnt++;
                            else if (r1.status == "MAXJ") maxj_cnt++;
                            else if (r1.status == "MAXS") maxs_cnt++;

                            if (dj >= 1 || !r1.tops.empty() || r1.status == "MAXS" || r1.status == "MAXJ") {
                                std::string tstr;
                                for (size_t i = 0; i < r1.tops.size() && i < 12; ++i) {
                                    if (i) tstr += ",";
                                    tstr += r1.tops[i];
                                }
                                printf("  [%s+J] H1=%s J=%s_%s -> %s dj=%lld dstep=%lld ones=%lld maxk=%lld ntops=%d tops=[%s] | last=%s\n",
                                       b.name, fmt_tr(h1_tr).c_str(),
                                       fmt_tr(tr2[18]).c_str(), fmt_tr(tr2[19]).c_str(),
                                       r1.status.c_str(), dj, r1.step - r0.step, r1.ones, r1.maxk, (int)r1.tops.size(),
                                       tstr.c_str(), r1.last_view.c_str());
                                fflush(stdout);
                            }
                        }
                    }
                }
            }
        }
        printf("  Summary for %s + J (160 halting TMs): HALT=%d MAXJ=%d MAXS=%d\n\n",
               b.name, h_cnt, maxj_cnt, maxs_cnt);
        fflush(stdout);
    }
    return 0;
}
