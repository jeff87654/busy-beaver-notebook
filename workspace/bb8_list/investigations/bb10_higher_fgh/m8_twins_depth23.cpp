// m8_twins_depth23.cpp
// Exhaustive lazy TNF search of 2-state (I, J) extensions from M8's C04-trace halting twins:
//   M8_t1: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0RC--- (and 1RD---)
//   M8_t3: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0RB--- (and 0RE---)

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
    int ntops;
    std::string last_view;
    Snapshot snap;
};

static void grow_snap(Snapshot& s) {
    ll add = s.t.size();
    std::vector<unsigned char> n(s.t.size() + 2 * add, 0);
    memcpy(&n[add], s.t.data(), s.t.size());
    s.t.swap(n);
    s.off += add; s.lo += add; s.hi += add; s.pos += add; s.r1 += add;
}

static void compact_snap(Snapshot& s) {
    ll pad = 32768;
    ll span = s.hi - s.lo + 1;
    ll new_sz = span + 2 * pad;
    std::vector<unsigned char> n(new_sz, 0);
    memcpy(&n[pad], &s.t[s.lo], span);
    ll shift = pad - s.lo;
    s.t.swap(n);
    s.off += shift;
    s.lo += shift;
    s.hi += shift;
    s.pos += shift;
    s.r1 += shift;
}

RunOut sim_from_snap(
    const Snapshot& init_snap,
    const std::vector<Tr>& tr,
    int init_q,
    ll B_val, ll CLS, ll MOD,
    ll JMAX, ll MAXS, ll MAXT, ll MAXTOPS, ll TOPK,
    bool save_snap_on_unassigned = false,
    ll EXACTCAP = 50000
) {
    Snapshot s = init_snap;
    int q = init_q;
    ll seg = 0;
    ll RMIN = 20, RMOD = 36;
    int QS = 1; // B
    bool cnt = true;
    int ntops = 0;
    ll maxk = 0;
    std::string last_v;

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
                        std::string vv = dview_buf(s.t, s.lo, rstart - 1, 200);
                        last_v = vv;
                        if (MAXTOPS > 0) {
                            size_t sp = vv.rfind(' ');
                            std::string last = sp == std::string::npos ? vv : vv.substr(sp + 1);
                            int ntok = 0;
                            for (char ch : vv) if (ch == ' ') ++ntok;
                            if (last.size() > 2 && last[0] == '1' && last[1] == '*' && atoll(last.c_str() + 2) >= TOPK && ntok <= 5) {
                                ++ntops;
                                if (ntops >= MAXTOPS) {
                                    return {"MAXTOPS", -1, s.step, seg, s.nj, 0, maxk, ntops, last_v, {}};
                                }
                            }
                        }
                        for (ll i = st0; i <= std::max(s.hi, s.pos); ++i) s.t[i] = 0;
                        while (st0 + (ll)nw.size() + 16 >= (ll)s.t.size()) {
                            ll o = s.off; grow_snap(s); st0 += s.off - o;
                        }
                        for (size_t i = 0; i < nw.size(); ++i) s.t[st0 + i] = nw[i] - '0';
                        s.pos = st0 + nw.size(); s.hi = s.pos; s.r1 = s.pos - 1; q = QS; seg = 0;
                        if (s.nj >= JMAX) {
                            return {"MAXJ", -1, s.step, seg, s.nj, 0, maxk, ntops, last_v, {}};
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
            if (save_snap_on_unassigned) {
                compact_snap(s);
                return {buf, slot, s.step, seg, s.nj, ones, maxk, ntops, last_v, s};
            } else {
                return {buf, slot, s.step, seg, s.nj, ones, maxk, ntops, last_v, {}};
            }
        }
        s.t[s.pos] = x.w;
        if (x.w && s.pos > s.r1) s.r1 = s.pos;
        else if (!x.w && s.pos == s.r1) { while (s.r1 >= s.lo && !s.t[s.r1]) --s.r1; }
        s.pos += x.d; q = x.nx; ++s.step; ++seg;
        if (s.pos < s.lo) s.lo = s.pos;
        if (s.pos > s.hi) s.hi = s.pos;
        if (seg >= MAXS || s.step >= MAXT) {
            return {"MAXS", -1, s.step, seg, s.nj, 0, maxk, ntops, last_v, {}};
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

    struct Base { const char* name; const char* tm; } bases[] = {
        {"M8_t1 (0LH/0RC)", "1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0RC---"},
        {"M8_t3 (1LH/0RB)", "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0RB---"},
    };

    for (const auto& b : bases) {
        auto tr0 = parse_tm(b.tm, 10);
        Snapshot blank;
        blank.t.assign(1 << 18, 0);
        blank.off = (1 << 17);
        blank.pos = blank.off; blank.lo = blank.off; blank.hi = blank.off; blank.r1 = blank.off - 1;
        blank.step = 0; blank.nj = 0; blank.ncl = 0;

        RunOut r0 = sim_from_snap(blank, tr0, 0, 66, 66, 150, 200, (ll)1e8, (ll)1e9, 0, 200, true, 4000000);
        printf("\n=== %s H1 snapshot: status=%s step=%lld nj=%lld ones=%lld ===\n",
               b.name, r0.status.c_str(), r0.step, r0.nj, r0.ones);
        fflush(stdout);

        ll nj0 = r0.snap.nj;
        int d2_undef = 0, d2_maxj = 0, d2_maxs = 0, d2_maxt = 0;
        int d3_nodes = 0, d3_undef = 0, d3_maxj = 0, d3_maxs = 0, d3_maxt = 0;
        int d4_nodes = 0, d4_undef = 0, d4_maxj = 0, d4_maxs = 0, d4_maxt = 0;
        ll max_dj_seen = 0;
        int max_ntops_seen = 0;

        ll MAXS_LIM = 1800000;
        ll MAXT_LIM = r0.step + 15000000LL;
        ll JMAX_LIM = nj0 + 80;

        for (int h1_w = 0; h1_w < 2; ++h1_w) {
            for (int h1_d : {-1, 1}) {
                Tr h1_tr = {h1_w, h1_d, 8, true};
                int c1 = r0.snap.t[r0.snap.pos + h1_d];
                int slot1 = 2 * 8 + c1;
                for (int i_w = 0; i_w < 2; ++i_w) {
                    for (int i_d : {-1, 1}) {
                        for (int i_nx = 0; i_nx < 10; ++i_nx) {
                            if (h1_d == 1 && i_nx < 8) continue;
                            auto tr2 = tr0;
                            tr2[2 * 7 + 1] = h1_tr;
                            tr2[slot1] = {i_w, i_d, i_nx, true};
                            bool j_unlocked = (i_nx == 9);
                            RunOut r2 = sim_from_snap(r0.snap, tr2, 7, 66, 66, 150, JMAX_LIM, MAXS_LIM, MAXT_LIM, 6, 200, true);
                            if (r2.status.rfind("UNDEF", 0) == 0) {
                                d2_undef++;
                                ll dj2 = r2.nj - nj0;
                                if (dj2 > max_dj_seen) max_dj_seen = dj2;
                                if (r2.ntops > max_ntops_seen) max_ntops_seen = r2.ntops;
                                if (dj2 >= 8 || r2.ntops >= 1) {
                                    printf("  [D2 HALT] H1=%s I=%s_%s -> %s dj=%lld ntops=%d maxk=%lld | last=%s\n",
                                           fmt_tr(tr2[15]).c_str(), fmt_tr(tr2[16]).c_str(), fmt_tr(tr2[17]).c_str(),
                                           r2.status.c_str(), dj2, r2.ntops, r2.maxk, r2.last_view.c_str());
                                }
                                int slot2 = r2.unassigned_slot;
                                int nx2_start = j_unlocked ? 0 : 9;
                                for (int s2_w = 0; s2_w < 2; ++s2_w) {
                                    for (int s2_d : {-1, 1}) {
                                        for (int s2_nx = nx2_start; s2_nx < 10; ++s2_nx) {
                                            d3_nodes++;
                                            auto tr3 = tr2;
                                            tr3[slot2] = {s2_w, s2_d, s2_nx, true};
                                            int q_resume2 = slot2 / 2;
                                            RunOut r3 = sim_from_snap(r2.snap, tr3, q_resume2, 66, 66, 150, JMAX_LIM, MAXS_LIM, MAXT_LIM, 6, 200, true);
                                            if (r3.status.rfind("UNDEF", 0) == 0) {
                                                d3_undef++;
                                                ll dj3 = r3.nj - nj0;
                                                if (dj3 > max_dj_seen) max_dj_seen = dj3;
                                                if (r3.ntops > max_ntops_seen) max_ntops_seen = r3.ntops;
                                                if (dj3 >= 10 || r3.ntops >= 1) {
                                                    printf("  [D3 HALT] H1=%s I=%s_%s J=%s_%s -> %s dj=%lld ntops=%d maxk=%lld | last=%s\n",
                                                           fmt_tr(tr3[15]).c_str(),
                                                           fmt_tr(tr3[16]).c_str(), fmt_tr(tr3[17]).c_str(),
                                                           fmt_tr(tr3[18]).c_str(), fmt_tr(tr3[19]).c_str(),
                                                           r3.status.c_str(), dj3, r3.ntops, r3.maxk, r3.last_view.c_str());
                                                    fflush(stdout);
                                                }
                                                if (dj3 == 0 && r3.step - r0.step > 15) continue;
                                                int slot3 = r3.unassigned_slot;
                                                int slot4 = -1;
                                                for (int s = 16; s < 20; ++s) {
                                                    if (s != slot1 && s != slot2 && s != slot3) { slot4 = s; break; }
                                                }
                                                int q_resume3 = slot3 / 2;
                                                for (int s3_w = 0; s3_w < 2; ++s3_w) {
                                                    for (int s3_d : {-1, 1}) {
                                                        for (int s3_nx = 0; s3_nx < 10; ++s3_nx) {
                                                            auto tr4 = tr3;
                                                            tr4[slot3] = {s3_w, s3_d, s3_nx, true};
                                                            int q_halt = slot4 / 2;
                                                            if (q_halt == 9 && tr4[16].nx != 9 && tr4[17].nx != 9) continue;
                                                            if (slot4 == 2 * 8 + (1 - c1) && h1_d == 1) {
                                                                if (tr4[2*8 + c1].nx != 8 && tr4[18].nx != 8 && tr4[19].nx != 8) continue;
                                                            }
                                                            d4_nodes++;
                                                            RunOut r4 = sim_from_snap(r3.snap, tr4, q_resume3, 66, 66, 150, JMAX_LIM, MAXS_LIM, MAXT_LIM, 6, 200, false);
                                                            if (r4.status.rfind("UNDEF", 0) == 0) {
                                                                d4_undef++;
                                                                ll dj4 = r4.nj - nj0;
                                                                if (dj4 > max_dj_seen) max_dj_seen = dj4;
                                                                if (r4.ntops > max_ntops_seen) max_ntops_seen = r4.ntops;
                                                                if (dj4 >= 12 || r4.ntops >= 2) {
                                                                    printf("  [D4 HALT] H1=%s I=%s_%s J=%s_%s -> %s dj=%lld ntops=%d maxk=%lld ones=%lld | last=%s\n",
                                                                           fmt_tr(tr4[15]).c_str(),
                                                                           fmt_tr(tr4[16]).c_str(), fmt_tr(tr4[17]).c_str(),
                                                                           fmt_tr(tr4[18]).c_str(), fmt_tr(tr4[19]).c_str(),
                                                                           r4.status.c_str(), dj4, r4.ntops, r4.maxk, r4.ones, r4.last_view.c_str());
                                                                    fflush(stdout);
                                                                }
                                                            } else if (r4.status == "MAXJ") d4_maxj++;
                                                            else if (r4.status == "MAXS") d4_maxs++;
                                                            else if (r4.status == "MAXTOPS") d4_maxt++;
                                                        }
                                                    }
                                                }
                                            } else if (r3.status == "MAXJ") d3_maxj++;
                                            else if (r3.status == "MAXS") d3_maxs++;
                                            else if (r3.status == "MAXTOPS") d3_maxt++;
                                        }
                                    }
                                }
                            } else if (r2.status == "MAXJ") d2_maxj++;
                            else if (r2.status == "MAXS") d2_maxs++;
                            else if (r2.status == "MAXTOPS") d2_maxt++;
                        }
                    }
                }
            }
        }
        printf("Summary %s D2: UNDEF=%d MAXJ=%d MAXS=%d MAXTOPS=%d\n", b.name, d2_undef, d2_maxj, d2_maxs, d2_maxt);
        printf("Summary %s D3 (%d): UNDEF=%d MAXJ=%d MAXS=%d MAXTOPS=%d\n", b.name, d3_nodes, d3_undef, d3_maxj, d3_maxs, d3_maxt);
        printf("Summary %s D4 (%d): UNDEF=%d MAXJ=%d MAXS=%d MAXTOPS=%d | max_dj=%lld max_ntops=%d\n",
               b.name, d4_nodes, d4_undef, d4_maxj, d4_maxs, d4_maxt, max_dj_seen, max_ntops_seen);
        fflush(stdout);
    }
    return 0;
}
