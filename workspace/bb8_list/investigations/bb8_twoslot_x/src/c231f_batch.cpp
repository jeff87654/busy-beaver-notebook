// c231f_batch.cpp: High-speed batch world follower for champ_231/232 children (with lazy H expansion).
// Tracks exact first Kc configuration (step, b0, a0, k1, ds0), exhaustion events (all ds == 0),
// rebuild rounds (k_1 -> k_2 -> k_3 ...), halting outcome, and span growth for non-Kc trajectories.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <windows.h>

typedef long long ll;
struct Tr { signed char w, d, nx; };
static ll EXCAP = 10000LL;

static ll Uf(int j, ll x);
static ll Wf(int j, ll B) {
    if (B < 0) return -1;
    ll v = B;
    for (int i = 0; i < j; ++i) { v = Uf(i, v); if (v < 0) return -1; }
    return v;
}
static ll Uf(int j, ll x) {
    if (x < 0) return -1;
    if (j == 0) { ll r = 3 * x + 9; return r >= EXCAP ? -1 : r; }
    ll n = x + 2 - (j - 1);
    ll v = Wf(j - 1, 3);
    if (v < 0) return -1;
    for (ll i = 0; i < n; ++i) { v = Uf(j - 1, v); if (v < 0) return -1; }
    return v;
}

static std::string rle_ds(const std::vector<ll> &ds, size_t max_len = 80) {
    std::string vw;
    for (size_t k = 0; k < ds.size();) {
        size_t j = k;
        while (j < ds.size() && ds[j] == ds[k]) ++j;
        char bf[48];
        if (j - k > 1) snprintf(bf, sizeof bf, "%lld*%zu", ds[k], j - k);
        else snprintf(bf, sizeof bf, "%lld", ds[k]);
        if (!vw.empty()) vw += ",";
        vw += bf;
        k = j;
        if (vw.size() > max_len) { vw += "..."; break; }
    }
    return vw;
}

static std::string rle_zs(const std::vector<ll> &zs, size_t max_len = 120) {
    std::string out;
    for (size_t k = 0; k < zs.size();) {
        size_t j = k;
        while (j < zs.size() && zs[j] == zs[k]) ++j;
        char bf[48];
        if (j - k > 1) snprintf(bf, sizeof bf, "%lldx%zu", zs[k], j - k);
        else snprintf(bf, sizeof bf, "%lld", zs[k]);
        if (!out.empty()) out += " ";
        out += bf;
        k = j;
        if (out.size() > max_len) { out += " ..."; break; }
    }
    return out;
}

struct SimBuffer {
    std::vector<unsigned char> t;
    ll off, lo, hi, pos;
    SimBuffer() : t(1 << 20, 0), off(1 << 19), lo(0), hi(0), pos(0) {}
    void reset() {
        for (ll i = lo; i <= hi; ++i) t[i] = 0;
        off = (ll)t.size() / 2;
        pos = lo = hi = off;
    }
    void grow() {
        ll add = t.size();
        std::vector<unsigned char> n(t.size() + 2 * add, 0);
        memcpy(&n[add], t.data(), t.size());
        t.swap(n);
        off += add; lo += add; hi += add; pos += add;
    }
};

static void run_one(SimBuffer &sb, const std::string &id, const std::string &m, unsigned QMASK,
                    ll MAX_START, ll MAX_SEG, ll MAXT, ll JMAX, ll RC, ll CLS, ll MOD) {
    int ns = (m.size() + 1) / 7;
    Tr T[32];
    for (int q = 0; q < ns; ++q) for (int b = 0; b < 2; ++b) {
        const char *p = m.c_str() + 7 * q + 3 * b;
        if (p[0] == '-' || p[0] == 'z' || p[2] - 'A' >= ns) T[2 * q + b] = {0, 0, -1};
        else T[2 * q + b] = {(signed char)(p[0] - '0'), (signed char)(p[1] == 'R' ? 1 : -1), (signed char)(p[2] - 'A')};
    }
    sb.reset();
    int q = 0;
    ll step = 0, seg = 0, nj = 0;
    ll span1 = 0, ones1 = 0;
    ll chk1 = MAX_START / 10;
    std::vector<ll> zs;
    std::vector<std::string> rounds;
    std::string first_kc = "NONE";
    int n_exhaust = 0, n_rebuilds = 0;
    bool after_exhaust = false;
    ll prev_mz = -1, prev_k = -1;

    auto lastone = [&]() {
        ll r = sb.hi;
        while (r > sb.pos && !sb.t[r]) --r;
        return r;
    };

    std::string outcome = "NONE";
    ll halt_ones = -1;

    while (true) {
        if (nj == 0 && step == chk1) {
            span1 = sb.hi - sb.lo + 1;
            ll o = 0; for (ll i = sb.lo; i <= sb.hi; ++i) o += sb.t[i];
            ones1 = o;
        }
        if (nj == 0 && step >= MAX_START) { outcome = "STOP_START"; break; }
        if (nj > 0 && seg >= MAX_SEG) { outcome = "STOP_SEG"; break; }
        if (step >= MAXT) { outcome = "STOP_MAXT"; break; }

        if (sb.pos < 8 || sb.pos >= (ll)sb.t.size() - 8) sb.grow();
        int c = sb.t[sb.pos];

        if ((QMASK >> q & 1) && c == 0 && step > 0) {
            bool leftblank = true;
            for (ll i = sb.lo; i < sb.pos; ++i) if (sb.t[i]) { leftblank = false; break; }
            if (leftblank && sb.t[sb.pos + 1] == 1) {
                ll i = sb.pos + 1, r1 = lastone();
                ll ones = 0;
                while (i <= r1 && sb.t[i]) { ++ones; ++i; }
                bool ok = (ones % 2 == 1);
                ll b = (ones - 1) / 2;
                ll kc_end = -1;
                std::vector<ll> fld;
                if (ok && i + 1 <= r1 && sb.t[i] == 0 && sb.t[i + 1] == 0) {
                    i += 2;
                    while (true) {
                        ll o = 0;
                        while (i <= r1 && sb.t[i]) { ++o; ++i; }
                        if (o == 1 && (i > r1 || (i + 1 < (ll)sb.t.size() && sb.t[i] == 0 && sb.t[i + 1] == 0))) {
                            kc_end = i - 1;
                            break;
                        }
                        if (i > r1 || o % 2 || sb.t[i] != 0 || i + 1 > r1 || sb.t[i + 1] != 0) { ok = false; break; }
                        fld.push_back(o / 2);
                        i += 2;
                    }
                } else ok = false;

                if (ok && !fld.empty()) {
                    ll a = fld[0];
                    std::vector<ll> ds(fld.begin() + 1, fld.end());
                    ll mz = 0;
                    while (mz < (ll)ds.size() && ds[mz] == 0) ++mz;

                    if (first_kc == "NONE") {
                        char bf[256];
                        snprintf(bf, sizeof bf, "step=%lld:b=%lld,a=%lld,k=%zu[%s]",
                                 step, b, a, ds.size(), rle_ds(ds, 40).c_str());
                        first_kc = bf;
                        char rbf[64];
                        snprintf(rbf, sizeof rbf, "R1(k=%zu,a=%lld,b=%lld)", ds.size(), a, b);
                        rounds.push_back(rbf);
                    } else if (after_exhaust && (a > 0 || mz < (ll)ds.size())) {
                        ++n_rebuilds;
                        after_exhaust = false;
                        char rbf[64];
                        snprintf(rbf, sizeof rbf, "R%d(k=%zu,a=%lld,b=%lld@+%lld)", n_rebuilds + 1, ds.size(), a, b, seg);
                        if (rounds.size() < 12) rounds.push_back(rbf);
                    }

                    if (a == 0 && mz == (ll)ds.size()) {
                        if (!after_exhaust) {
                            ++n_exhaust;
                            after_exhaust = true;
                        }
                    }

                    int kind = 0;
                    ll nb = b;
                    ll v = 0;
                    if (a > 0) {
                        kind = 1;
                        nb = b + 3 * a;
                    } else if (mz < (ll)ds.size() && mz <= b) {
                        kind = 2;
                        v = ds[mz];
                        ll x = b;
                        for (ll it = 0; it < v && x >= 0; ++it) x = Uf((int)mz, x);
                        if (x >= 0) nb = x;
                        else {
                            nb = std::max<ll>(RC + 40LL * n_exhaust, mz + 1);
                            ll rr = ((nb - CLS) % MOD + MOD) % MOD;
                            if (rr) nb += MOD - rr;
                        }
                        for (ll k = 0; k <= mz; ++k) ds[k] = 0;
                        // check if all ds are now 0 after this clear!
                        bool allz = true;
                        for (ll dv : ds) if (dv != 0) { allz = false; break; }
                        if (allz && !after_exhaust) {
                            ++n_exhaust;
                            after_exhaust = true;
                        }
                    }

                    if (kind) {
                        ++nj;
                        if (kind == 2) {
                            if (!after_exhaust && prev_k >= 0 && (mz <= prev_mz || (ll)ds.size() != prev_k)) {
                                // mid-tower rebuild (without hitting full exhaustion)
                                ++n_rebuilds;
                                char rbf[64];
                                snprintf(rbf, sizeof rbf, "M%d(k=%zu,m=%lld@+%lld)", n_rebuilds + 1, ds.size(), mz, seg);
                                if (rounds.size() < 12) rounds.push_back(rbf);
                            }
                            prev_mz = mz;
                            prev_k = (ll)ds.size();
                            zs.push_back((ll)ds.size());
                        }
                        ll new_len = 1 + (2 * nb + 1) + 2 + 2 + 1;
                        for (ll v2 : ds) new_len += 2 * v2 + 2;
                        while (kc_end - new_len + 1 < 16) {
                            ll old_off = sb.off;
                            sb.grow();
                            kc_end += sb.off - old_off;
                        }
                        ll new_pos = kc_end - new_len + 1;
                        for (ll k = std::min(sb.pos, new_pos); k <= kc_end; ++k) sb.t[k] = 0;
                        ll cc = new_pos + 1;
                        for (ll k = 0; k < 2 * nb + 1; ++k) sb.t[cc++] = 1;
                        cc += 2; cc += 2;
                        for (ll v2 : ds) {
                            for (ll k = 0; k < 2 * v2; ++k) sb.t[cc++] = 1;
                            cc += 2;
                        }
                        sb.t[cc] = 1;
                        sb.pos = new_pos;
                        if (sb.pos < sb.lo) sb.lo = sb.pos;
                        if (cc > sb.hi) sb.hi = cc;
                        seg = 0;
                        if (nj >= JMAX) { outcome = "END_JUMPS"; break; }
                        continue;
                    }
                }
            }
        }

        Tr &x = T[2 * q + c];
        if (x.nx < 0) {
            ll ones = 0;
            for (ll i = sb.lo; i <= sb.hi; ++i) ones += sb.t[i];
            halt_ones = ones;
            char bf[32];
            snprintf(bf, sizeof bf, "HALT_%c%d", 'A' + q, c);
            outcome = bf;
            break;
        }
        sb.t[sb.pos] = x.w;
        sb.pos += x.d;
        if (sb.pos < sb.lo) sb.lo = sb.pos;
        if (sb.pos > sb.hi) sb.hi = sb.pos;
        q = x.nx;
        ++step;
        ++seg;
    }

    ll span2 = sb.hi - sb.lo + 1;
    ll ones2 = halt_ones >= 0 ? halt_ones : [&]() { ll o = 0; for (ll i = sb.lo; i <= sb.hi; ++i) o += sb.t[i]; return o; }();
    std::string rstr;
    for (size_t i = 0; i < rounds.size(); ++i) {
        if (i) rstr += "->";
        rstr += rounds[i];
    }
    if (rstr.empty()) rstr = "-";

    printf("%s\t%s\t%s\t%lld\t%lld\t%lld\t%d\t%d\t%lld\t%lld\t%s\t%s\t%s\n",
           id.c_str(), m.c_str(), outcome.c_str(), nj, ones2, step,
           n_exhaust, n_rebuilds, span1, span2,
           first_kc.c_str(), rstr.c_str(), rle_zs(zs).c_str());
}

int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    if (argc < 2) { fprintf(stderr, "Usage: c231f_batch LISTFILE [--max-start S] [--max-seg S] [--maxt S] [--jumps J]\n"); return 2; }
    ll MAX_START = 5000000LL, MAX_SEG = 10000000LL, MAXT = 50000000LL, JMAX = 300, RC = 20, CLS = 39, MOD = 162;
    for (int i = 2; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--max-start") MAX_START = (ll)atof(argv[++i]);
        else if (a == "--max-seg") MAX_SEG = (ll)atof(argv[++i]);
        else if (a == "--maxt") MAXT = (ll)atof(argv[++i]);
        else if (a == "--jumps") JMAX = atoll(argv[++i]);
    }
    FILE *fin = fopen(argv[1], "r");
    SimBuffer sb;
    char id[128], m[256], qset[64];
    printf("id\tmachine\toutcome\tjumps\tones\tstep\tn_exhaust\tn_rebuilds\tspan1\tspan2\tfirst_kc\trounds\tzeros\n");
    ll cnt = 0;
    while (fscanf(fin, "%127s %255s %63s", id, m, qset) == 3) {
        unsigned QMASK = 0;
        for (const char *z = qset; *z; ++z) if (*z >= 'A' && *z <= 'H') QMASK |= 1u << (*z - 'A');
        run_one(sb, id, m, QMASK, MAX_START, MAX_SEG, MAXT, JMAX, RC, CLS, MOD);
        if (++cnt % 100 == 0) { fflush(stdout); fprintf(stderr, "%lld done\n", cnt); }
    }
    fflush(stdout);
    fclose(fin);
    return 0;
}
