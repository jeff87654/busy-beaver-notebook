// pkf8q_batch.cpp: Batch version of pkf8q.cpp for fast screening of a1_X / a1_X_r1t0 candidates.
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <windows.h>

typedef long long ll;
struct Tr { int w, d, nx; bool def; };

static std::vector<unsigned char> t;
static ll off, lo, hi, pos, r1;
static int q;

static void grow() {
    ll add = t.size();
    std::vector<unsigned char> n(t.size() + 2 * add, 0);
    memcpy(&n[add], t.data(), t.size());
    t.swap(n);
    off += add; lo += add; hi += add; pos += add; r1 += add;
}

static bool at(ll p, const char *s) {
    ll L = strlen(s);
    if (p - L + 1 < lo) return false;
    for (ll i = 0; i < L; ++i)
        if (t[p - L + 1 + i] != s[i] - '0') return false;
    return true;
}

static std::string dview(ll a, ll b, size_t maxc) {
    while (a <= b && !t[a]) ++a;
    std::vector<std::string> tok; ll i = a;
    while (i <= b) {
        if (t[i] == 0) {
            ll j = i; while (j <= b && !t[j]) ++j;
            if (j - i >= 2 || j > b) tok.push_back("z" + std::to_string(j - i));
            else tok.push_back("z1");
            i = j; continue;
        }
        ll j = i, m = 0;
        while (j + 2 <= b && t[j] == 1 && t[j + 1] == 0 && t[j + 2] == 1) { j += 2; ++m; }
        tok.push_back(std::to_string(m)); i = j + 1;
    }
    std::string out; size_t k = 0;
    while (k < tok.size()) {
        size_t l = k; while (l < tok.size() && tok[l] == tok[k]) ++l;
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

int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    if (argc < 2) {
        fprintf(stderr, "usage: pkf8q_batch <jobs.txt> [--maxs S] [--jumps J]\n");
        return 2;
    }
    std::string jobs_path = argv[1];
    ll JMAX = 400, MAXS = 20000000LL, MAXT = 200000000LL;
    double GROW = 2.0; ll RMIN = 20, MOD = 360360, RMOD = 36, EXACTCAP = 4000000;
    for (int i = 2; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--maxs") MAXS = atoll(argv[++i]);
        else if (a == "--maxt") MAXT = atoll(argv[++i]);
        else if (a == "--jumps") JMAX = atoll(argv[++i]);
    }

    ll init_sz = 1 << 22;
    t.assign(init_sz, 0);

    std::ifstream in(jobs_path);
    std::string line;
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        std::istringstream iss(line);
        std::string id, m, qset_str;
        if (!(iss >> id >> m >> qset_str)) continue;

        unsigned QMASK = 0;
        for (char ch : qset_str) if (ch >= 'A' && ch <= 'H') QMASK |= 1u << (ch - 'A');
        int QS = 1;

        int n = (m.size() + 1) / 7;
        std::vector<Tr> tr(2 * n);
        for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) {
            const char *x = m.c_str() + 7 * s + 3 * c;
            if (x[0] == '-' || x[2] == 'Z' || x[0] == 'z' || x[2] - 'A' >= n) tr[2 * s + c] = {0, 0, 0, false};
            else tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true};
        }

        off = t.size() / 2;
        pos = off; q = 0; lo = off; hi = off; r1 = lo - 1;
        ll step = 0, seg = 0, nj = 0, ncl = 0, maxk = 0;
        std::vector<ll> zs;
        std::string status = "UNKNOWN";
        std::string halt_slot = "-";
        ll ones = 0;
        std::string first_j = "-";

        auto pickR = [&](ll want_res, ll modulus) -> ll {
            ll wdt = r1 - lo + 1;
            ll base = std::max<ll>(RMIN, (ll)(GROW * (double)wdt));
            if (want_res >= 0) {
                ll x = base;
                ll rr = ((want_res % modulus) + modulus) % modulus;
                x += ((rr - x % modulus) % modulus + modulus) % modulus;
                return x;
            }
            return base;
        };

        while (true) {
            if (pos <= 8 || pos >= (ll)t.size() - 8) grow();
            int c = t[pos];
            if ((q == QS || (QMASK >> q & 1)) && c == 0 && pos > r1 && step > 0 && at(pos - 1, "1001")) {
                ll p = pos - 5, tt = 0;
                while (at(p, "11111100")) { ++tt; p -= 8; }
                if (at(p, "11")) {
                    p -= 2; ll r = 0;
                    while (p - 1 >= lo && t[p] == 0 && t[p - 1] == 1) { ++r; p -= 2; }
                    ll rstart = p + 1;
                    std::vector<ll> tok, tpos;
                    while (p >= lo && t[p] == 1) {
                        ll x = 0; ll pp = p - 1;
                        while (pp - 1 >= lo && t[pp] == 0 && t[pp - 1] == 1) { ++x; pp -= 2; }
                        tok.push_back(x); tpos.push_back(pp + 1); p = pp;
                    }
                    if (!tok.empty()) {
                        ll mm = tok[0]; int kind = 0; ll k = 0;
                        if (mm % 3 == 1 && r % 3 == 2) {
                            bool nz = mm > 1;
                            while (k + 1 < (ll)tok.size() && tok[k + 1] % 3 == 1) { if (tok[k + 1] > 1) nz = true; ++k; }
                            if (nz) {
                                if (k >= 1 || (double)(r + 4) * pow(2.0, (double)(mm / 3)) > (double)EXACTCAP) kind = 2;
                            }
                        }
                        if (!kind && mm >= 3) kind = 1;
                        if (kind) {
                            std::string nw; ll st0; ll newr;
                            if (kind == 2) {
                                st0 = tpos[k];
                                for (ll i = 0; i <= k; ++i) nw += "101";
                                ll R = pickR(-1, MOD);
                                newr = 3 * R + 2; ++ncl; zs.push_back(k);
                                if (k > maxk) maxk = k;
                            } else {
                                st0 = tpos[0]; ll k3 = mm / 3, m2 = mm % 3;
                                for (ll i = 0; i < m2; ++i) nw += "10"; nw += "1";
                                double approx = (double)(r + 4); bool small = true; ll ex = r + 4;
                                for (ll i = 0; i < k3; ++i) { approx *= 2; if (approx > (double)EXACTCAP) { small = false; break; } ex *= 2; }
                                if (small) newr = ex - 4;
                                else {
                                    ll res = ((__int128)powmod(2, k3, RMOD) * ((r + 4) % RMOD) % RMOD - 4 + RMOD) % RMOD;
                                    ll base = std::max<ll>(RMIN, (ll)(GROW * (double)(r1 - lo + 1)));
                                    newr = base + ((res - base % RMOD) % RMOD + RMOD) % RMOD;
                                }
                            }
                            if (nj == 0) {
                                first_j = (kind == 2 ? "CL:" : "R1:") + std::string("s=") + std::to_string(step) + ",t=" + std::to_string(tt) + ",m=" + std::to_string(mm) + ",r=" + std::to_string(r) + "|[" + dview(lo, rstart - 1, 80) + "]";
                            }
                            for (ll i = 0; i < newr; ++i) nw += "10";
                            nw += "11"; for (ll i = 0; i < tt; ++i) nw += "11111100"; nw += "1001";
                            ++nj;
                            for (ll i = st0; i <= std::max(hi, pos); ++i) t[i] = 0;
                            while (st0 + (ll)nw.size() + 16 >= (ll)t.size()) { ll o = off; grow(); st0 += off - o; }
                            for (size_t i = 0; i < nw.size(); ++i) t[st0 + i] = nw[i] - '0';
                            pos = st0 + nw.size(); hi = pos; r1 = pos - 1; seg = 0;
                            if (nj >= JMAX) { status = "JMAX"; break; }
                            continue;
                        }
                    }
                }
            }
            const Tr &x = tr[2 * q + c];
            if (!x.def) {
                for (ll i = lo; i <= hi; ++i) ones += t[i];
                status = "HALT";
                halt_slot = std::string(1, char('A' + q)) + std::to_string(c);
                break;
            }
            t[pos] = x.w;
            if (x.w && pos > r1) r1 = pos;
            else if (!x.w && pos == r1) { while (r1 >= lo && !t[r1]) --r1; }
            pos += x.d; q = x.nx; ++step; ++seg;
            if (pos < lo) lo = pos;
            if (pos > hi) hi = pos;
            if (seg >= MAXS || step >= MAXT) { status = "MAXS"; break; }
        }

        std::string zstr;
        for (size_t i = 0; i < zs.size(); ++i) {
            if (i) zstr += ",";
            zstr += std::to_string(zs[i]);
        }
        if (zstr.empty()) zstr = "-";

        printf("%s\t%s\t%s\t%s\t%s\t%lld\t%lld\t%lld\t%lld\t%lld\t%s\t%s\n",
               id.c_str(), m.c_str(), qset_str.c_str(), status.c_str(), halt_slot.c_str(),
               step, ones, nj, ncl, maxk, zstr.c_str(), first_j.c_str());
        fflush(stdout);

        ll z_lo = std::max<ll>(0, lo - 16);
        ll z_hi = std::min<ll>((ll)t.size() - 1, std::max(hi, pos) + 16);
        memset(&t[z_lo], 0, z_hi - z_lo + 1);
    }
    return 0;
}
