// perturb8_scan.cpp: Fast C++ perturbation & 9-state extension scanner for 8-state K-machines.
// Always runs at IDLE_PRIORITY_CLASS (0x00000040).
#ifdef _WIN32
#include <windows.h>
#endif
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>
#include <set>

struct Tr { int w, d, nx; bool def; };

struct Tmpl {
    bool mirror;
    int TQ;
    std::string P, u, s, S;
    long long al, be, alB, beB;
    long long req_B0; // -1 if b is free accumulator
    int nE;
    std::string mode; // "a_acc" or "b_acc"
};

struct KCfg {
    std::vector<long long> ds;
    long long a, b;
};

static std::string make_word(const Tmpl &t, const std::vector<long long> &ds, long long a, long long b) {
    std::string res = t.P;
    for (size_t i = 0; i < ds.size(); ++i) {
        long long cnt = t.al * ds[i] + t.be;
        for (long long k = 0; k < cnt; ++k) res += t.u;
        res += t.s;
    }
    long long acnt = t.al * a + t.be;
    for (long long k = 0; k < acnt; ++k) res += t.u;
    res += t.s;
    long long bcnt = t.alB * b + t.beB;
    for (long long k = 0; k < bcnt; ++k) res += t.u;
    res += t.S;
    return res;
}

static bool kparse(const Tmpl &t, const std::string &w, KCfg &out) {
    if (w.size() < t.P.size() + t.S.size()) return false;
    if (w.compare(0, t.P.size(), t.P) != 0) return false;
    if (w.compare(w.size() - t.S.size(), t.S.size(), t.S) != 0) return false;
    std::vector<long long> runs;
    size_t i = t.P.size(), e = w.size() - t.S.size();
    while (true) {
        long long k = 0;
        size_t i0 = i;
        while (i + t.u.size() <= e && w.compare(i, t.u.size(), t.u) == 0) {
            i += t.u.size();
            ++k;
        }
        if (i == e) {
            runs.push_back(k);
            break;
        }
        bool fs = false;
        for (long long kk = k; kk >= 0; --kk) {
            size_t j = i0 + kk * t.u.size();
            if (j + t.s.size() <= e && w.compare(j, t.s.size(), t.s) == 0) {
                runs.push_back(kk);
                i = j + t.s.size();
                fs = true;
                break;
            }
        }
        if (!fs) return false;
    }
    if (runs.size() < 2) return false;
    long long bl = runs.back();
    if (bl < t.beB || (bl - t.beB) % t.alB != 0) return false;
    long long bval = (bl - t.beB) / t.alB;
    if (t.req_B0 >= 0 && bval != t.req_B0) return false;
    out.ds.clear();
    for (size_t j = 0; j + 1 < runs.size(); ++j) {
        if (runs[j] < t.be || (runs[j] - t.be) % t.al != 0) return false;
        long long v = (runs[j] - t.be) / t.al;
        if (j + 2 < runs.size()) out.ds.push_back(v);
        else out.a = v;
    }
    out.b = bval;
    return true;
}

struct SimRes {
    char kind; // 'K', 'H', 'U' (hit need_branch slot), 'T', 'W'
    long long steps;
    int hslot;
    KCfg k;
};

static std::vector<unsigned char> tp;

static SimRes sim_k(const std::vector<Tr> &tr, const bool *need_branch, const Tmpl &t,
                    const std::vector<long long> &ds, long long a, long long b, long long bud) {
    std::string w = make_word(t, ds, a, b);
    long long size = 32768;
    while (size < 4 * (long long)w.size() + 2048) size *= 2;
    tp.assign(size, 0);
    long long off = size / 2;
    long long lo = 1, hi = 0;
    for (size_t z = 0; z < w.size(); ++z) {
        if (w[z] == '1') {
            tp[off + z] = 1;
            if (lo > hi) lo = hi = z;
            else hi = z;
        }
    }
    long long pos = (long long)w.size();
    int q = t.TQ;
    for (long long st = 0; st < bud; ++st) {
        if (pos + off < 4 || pos + off + 4 >= size) {
            if (size >= (1LL << 20)) return {'W', st, -1, {}};
            std::vector<unsigned char> nt(size * 2, 0);
            memcpy(nt.data() + size / 2, tp.data(), size);
            off += size / 2;
            size *= 2;
            tp.swap(nt);
        }
        unsigned char *T = tp.data() + off;
        int c = T[pos];
        if (st > 0 && c == 0 && q == t.TQ && lo <= hi) {
            while (lo <= hi && !T[hi]) --hi;
            while (lo <= hi && !T[lo]) ++lo;
            if (pos > hi && lo <= hi && pos - lo < 12000) {
                std::string ww;
                ww.reserve(pos - lo);
                for (long long i = lo; i < pos; ++i) ww += char('0' + T[i]);
                KCfg kc;
                if (kparse(t, ww, kc)) return {'K', st, -1, kc};
            }
        }
        int sl = 2 * q + c;
        const Tr &x = tr[sl];
        if (!x.def) {
            if (need_branch && need_branch[sl]) return {'U', st, sl, {}};
            return {'H', st, sl, {}};
        }
        T[pos] = x.w;
        if (x.w) {
            if (lo > hi) lo = hi = pos;
            else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; }
        }
        pos += x.d;
        q = x.nx;
    }
    return {'T', bud, -1, {}};
}

struct BlankRes {
    char kind; // 'H', 'U', 'T', 'X', 'C', 'W'
    long long steps;
    int hslot;
    int nK;
    int nE;
    int max_len;
    std::string trace_summary;
};

static BlankRes sim_blank(const std::vector<Tr> &tr, const bool *need_branch, const Tmpl &t, long long bud) {
    long long size = 65536;
    tp.assign(size, 0);
    long long off = size / 2;
    long long lo = 1, hi = 0;
    long long pos = 0;
    int q = 0;
    long long mn = 0, mx = 0, ckp = 2048, lastsp = -1;
    int nK = 0, nE = 0, max_len = 0;
    bool prev_was_E = false;
    std::string sum;
    for (long long st = 0; st < bud; ++st) {
        if (pos + off < 4 || pos + off + 4 >= size) {
            if (size >= (1LL << 22)) return {'W', st, -1, nK, nE, max_len, sum};
            std::vector<unsigned char> nt(size * 2, 0);
            memcpy(nt.data() + size / 2, tp.data(), size);
            off += size / 2;
            size *= 2;
            tp.swap(nt);
        }
        unsigned char *T = tp.data() + off;
        int c = T[pos];
        if (st > 0 && c == 0 && q == t.TQ && lo <= hi) {
            while (lo <= hi && !T[hi]) --hi;
            while (lo <= hi && !T[lo]) ++lo;
            if (pos > hi && lo <= hi && pos - lo < 12000) {
                std::string ww;
                ww.reserve(pos - lo);
                for (long long i = lo; i < pos; ++i) ww += char('0' + T[i]);
                KCfg kc;
                if (kparse(t, ww, kc)) {
                    ++nK;
                    if ((int)kc.ds.size() > max_len) max_len = (int)kc.ds.size();
                    if (prev_was_E) {
                        if (sum.size() < 100) sum += "->" + std::to_string(kc.ds.size());
                        prev_was_E = false;
                    }
                    bool is_E = false;
                    long long eval = 0;
                    if (t.mode == "a_acc") {
                        if ((int)kc.ds.size() == t.nE) {
                            bool allz = true;
                            for (auto v : kc.ds) if (v != 0) allz = false;
                            if (allz) { is_E = true; eval = kc.a; }
                        }
                    } else {
                        if ((int)kc.ds.size() == t.nE && kc.a == 0) {
                            bool allz = true;
                            for (auto v : kc.ds) if (v != 0) allz = false;
                            if (allz) { is_E = true; eval = kc.b; }
                        }
                    }
                    if (is_E) {
                        ++nE;
                        prev_was_E = true;
                        if (sum.size() < 100) {
                            if (!sum.empty()) sum += " ";
                            sum += "E" + std::to_string(eval);
                        }
                    }
                }
            }
        }
        int sl = 2 * q + c;
        const Tr &x = tr[sl];
        if (!x.def) {
            if (need_branch && need_branch[sl]) return {'U', st, sl, nK, nE, max_len, sum};
            return {'H', st, sl, nK, nE, max_len, sum};
        }
        T[pos] = x.w;
        if (x.w) {
            if (lo > hi) lo = hi = pos;
            else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; }
        }
        pos += x.d;
        q = x.nx;
        if (pos < mn) mn = pos;
        if (pos > mx) mx = pos;
        if (st == ckp) {
            long long sp = mx - mn;
            double lim = 10.0 * std::sqrt((double)st) + 300;
            if (st >= 32768 && sp > lim && nK == 0) return {'X', st, -1, nK, nE, max_len, sum};
            if (st >= 131072 && sp == lastsp && nK == 0) return {'C', st, -1, nK, nE, max_len, sum};
            lastsp = sp;
            ckp *= 2;
        }
    }
    return {'T', bud, -1, nK, nE, max_len, sum};
}

static std::string fmt_machine(const std::vector<Tr> &t, int NS, bool mirror) {
    std::string s;
    for (int q = 0; q < NS; ++q) {
        if (q) s += '_';
        for (int c = 0; c < 2; ++c) {
            const Tr &x = t[2 * q + c];
            if (!x.def) s += "---";
            else {
                s += char('0' + x.w);
                int d = mirror ? -x.d : x.d;
                s += d > 0 ? 'R' : 'L';
                s += char('A' + x.nx);
            }
        }
    }
    return s;
}

static std::string fmt_k(const KCfg &k) {
    std::string s = "[";
    for (size_t i = 0; i < k.ds.size();) {
        long long v = k.ds[i];
        size_t r = i;
        while (r < k.ds.size() && k.ds[r] == v) ++r;
        s += std::to_string(v);
        if (r - i > 1) s += "^" + std::to_string(r - i);
        if (r < k.ds.size()) s += ",";
        i = r;
    }
    s += "];" + std::to_string(k.a) + ";" + std::to_string(k.b);
    return s;
}

static Tmpl parse_tmpl_str(const std::string &ts, long long B0, int nE, const std::string &mode) {
    Tmpl t;
    t.mode = mode;
    t.nE = nE;
    t.req_B0 = (mode == "a_acc") ? B0 : -1;
    std::stringstream ss(ts);
    std::string tok;
    std::vector<std::string> parts;
    while (std::getline(ss, tok, ',')) parts.push_back(tok);
    t.mirror = (parts[0][0] == 'L');
    t.TQ = parts[1][0] - 'A';
    for (size_t i = 2; i < parts.size(); ++i) {
        size_t eq = parts[i].find('=');
        std::string k = parts[i].substr(0, eq);
        std::string v = parts[i].substr(eq + 1);
        if (k == "P") t.P = (v == "-") ? "" : v;
        else if (k == "u") t.u = v;
        else if (k == "s") t.s = v;
        else if (k == "S") t.S = (v == "-") ? "" : v;
        else if (k == "d") {
            size_t dp = v.find("d+");
            t.al = std::stoll(v.substr(0, dp));
            t.be = std::stoll(v.substr(dp + 2));
        } else if (k == "b") {
            size_t bp = v.find("b+");
            t.alB = std::stoll(v.substr(0, bp));
            t.beB = std::stoll(v.substr(bp + 2));
        }
    }
    return t;
}

static std::vector<int> parse_slots(const std::string &s) {
    std::vector<int> res;
    if (s == "-" || s.empty()) return res;
    std::stringstream ss(s);
    std::string tok;
    while (std::getline(ss, tok, ',')) {
        if (tok.size() >= 2) {
            int q = tok[0] - 'A';
            int c = tok[1] - '0';
            res.push_back(2 * q + c);
        }
    }
    return res;
}

static std::string sl_name(int sl) {
    std::string r;
    r += char('A' + sl / 2);
    r += char('0' + sl % 2);
    return r;
}

struct ScanCtx {
    std::string pid, group, tag_info;
    Tmpl t;
    int NS;
    std::vector<Tr> tr;
    bool need_branch[18];
    std::set<std::string> *seen_machines;
    long long nodes = 0, survivors = 0;
};

static void evaluate_and_branch(ScanCtx &ctx) {
    ++ctx.nodes;
    const Tmpl &t = ctx.t;
    long long B0 = (t.req_B0 >= 0) ? t.req_B0 : 0;

    // 1. Test D / R2
    SimRes d0, d1;
    if (t.mode == "a_acc") {
        d0 = sim_k(ctx.tr, ctx.need_branch, t, {3}, 4, B0, 5000);
        if (d0.kind == 'U') goto do_branch_d0;
        if (d0.kind != 'K' || d0.k.ds.size() != 1 || d0.k.ds[0] != 2 || d0.k.a < 8) return;
        d1 = sim_k(ctx.tr, ctx.need_branch, t, {3}, 5, B0, 5000);
        if (d1.kind == 'U') { d0 = d1; goto do_branch_d0; }
        if (d1.kind != 'K' || d1.k.ds.size() != 1 || d1.k.ds[0] != 2 || d1.k.a <= d0.k.a) return;
    } else {
        d0 = sim_k(ctx.tr, ctx.need_branch, t, {3}, 2, 10, 5000);
        if (d0.kind == 'U') goto do_branch_d0;
        if (d0.kind != 'K' || d0.k.ds.size() != 1 || d0.k.ds[0] != 3 || d0.k.a >= 2 || d0.k.b <= 10) return;
        d1 = sim_k(ctx.tr, ctx.need_branch, t, {3}, 0, 10, 8000);
        if (d1.kind == 'U') { d0 = d1; goto do_branch_d0; }
        if (d1.kind != 'K' || d1.k.ds.size() != 1 || d1.k.ds[0] != 2 || (d1.k.a + d1.k.b) < 10) return;
    }

    // 2. Test B1, B2, B3
    {
        SimRes b1e, b1o, b2e, b2o, b3e;
        if (t.mode == "a_acc") {
            b1e = sim_k(ctx.tr, ctx.need_branch, t, {2, 0}, 4, B0, 8000);
            if (b1e.kind == 'U') { d0 = b1e; goto do_branch_d0; }
            if (b1e.kind != 'K' || b1e.k.ds.empty() || b1e.k.ds[0] != 1) return;

            b1o = sim_k(ctx.tr, ctx.need_branch, t, {2, 0}, 5, B0, 8000);
            if (b1o.kind == 'U') { d0 = b1o; goto do_branch_d0; }
            if (b1o.kind != 'K' || b1o.k.ds.empty() || b1o.k.ds[0] != 1) return;

            b2e = sim_k(ctx.tr, ctx.need_branch, t, {2, 0, 0}, 6, B0, 10000);
            if (b2e.kind == 'U') { d0 = b2e; goto do_branch_d0; }
            if (b2e.kind != 'K' || b2e.k.ds.empty() || b2e.k.ds[0] != 1) return;

            b2o = sim_k(ctx.tr, ctx.need_branch, t, {2, 0, 0}, 7, B0, 10000);
            if (b2o.kind == 'U') { d0 = b2o; goto do_branch_d0; }
            if (b2o.kind != 'K' || b2o.k.ds.empty() || b2o.k.ds[0] != 1) return;

            b3e = sim_k(ctx.tr, ctx.need_branch, t, {2, 0, 0, 0}, 8, B0, 12000);
            if (b3e.kind == 'U') { d0 = b3e; goto do_branch_d0; }
            if (b3e.kind != 'K' || b3e.k.ds.empty() || b3e.k.ds[0] != 1) return;
            // Require at least B2 or B3 to maintain or grow list length (>= 2)
            if (b1e.k.ds.size() < 2 && b2e.k.ds.size() < 2 && b3e.k.ds.size() < 3) return;
        } else {
            b1e = sim_k(ctx.tr, ctx.need_branch, t, {2, 0}, 0, 10, 8000);
            if (b1e.kind == 'U') { d0 = b1e; goto do_branch_d0; }
            if (b1e.kind != 'K' || b1e.k.ds.empty() || b1e.k.ds[0] != 1) return;

            b1o = sim_k(ctx.tr, ctx.need_branch, t, {2, 0}, 0, 11, 8000);
            if (b1o.kind == 'U') { d0 = b1o; goto do_branch_d0; }
            if (b1o.kind != 'K' || b1o.k.ds.empty() || b1o.k.ds[0] != 1) return;

            b2e = sim_k(ctx.tr, ctx.need_branch, t, {2, 0, 0}, 0, 10, 10000);
            if (b2e.kind == 'U') { d0 = b2e; goto do_branch_d0; }
            if (b2e.kind != 'K' || b2e.k.ds.empty() || b2e.k.ds[0] != 1) return;

            b2o = sim_k(ctx.tr, ctx.need_branch, t, {2, 0, 0}, 0, 11, 10000);
            if (b2o.kind == 'U') { d0 = b2o; goto do_branch_d0; }
            if (b2o.kind != 'K' || b2o.k.ds.empty() || b2o.k.ds[0] != 1) return;

            b3e = sim_k(ctx.tr, ctx.need_branch, t, {2, 0, 0, 0}, 0, 10, 12000);
            if (b3e.kind == 'U') { d0 = b3e; goto do_branch_d0; }
            if (b3e.kind != 'K' || b3e.k.ds.empty() || b3e.k.ds[0] != 1) return;
        }

        // 3. Test E across 8 values
        std::vector<long long> e_ds(t.nE, 0);
        std::vector<SimRes> eres;
        int nH = 0, nK_e = 0, min_klen = 999999, max_klen = 0;
        std::string epat;
        for (int i = 0; i < 8; ++i) {
            long long val = (t.mode == "a_acc") ? (6 + i) : (12 + i);
            SimRes er = (t.mode == "a_acc")
                ? sim_k(ctx.tr, ctx.need_branch, t, e_ds, val, B0, 16000)
                : sim_k(ctx.tr, ctx.need_branch, t, e_ds, 0, val, 16000);
            if (er.kind == 'U') { d0 = er; goto do_branch_d0; }
            eres.push_back(er);
            epat += er.kind;
            if (er.kind == 'H') ++nH;
            else if (er.kind == 'K') {
                ++nK_e;
                int l = (int)er.k.ds.size();
                if (l < min_klen) min_klen = l;
                if (l > max_klen) max_klen = l;
            }
        }
        // Require BOTH H and K in E, and growing rebuild list length (max_klen >= 4 and max_klen > min_klen)
        if (nH == 0 || nK_e == 0 || max_klen < 4 || max_klen <= min_klen) return;

        // Check if any need_branch slot is still set; if blank hits it, branch it!
        BlankRes br = sim_blank(ctx.tr, ctx.need_branch, t, 400000);
        if (br.kind == 'U') {
            d0.hslot = br.hslot;
            goto do_branch_d0;
        }
        // Filter blank: must either still be running ('T'/'W') with nK >= 2, or halt after >= 100000 steps
        if (br.kind == 'X' || br.kind == 'C') return;
        if (br.kind == 'H' && br.steps < 100000) return;
        if (br.nK < 2 && br.steps < 100000) return;

        std::string mstr = fmt_machine(ctx.tr, ctx.NS, t.mirror);
        if (ctx.seen_machines->count(mstr)) return;
        ctx.seen_machines->insert(mstr);
        ++ctx.survivors;

        // Check parity locking status for a_acc
        std::string pstat = "OPEN";
        if (t.mode == "a_acc") {
            bool d_preserves_a_par = ((d0.k.a % 2) == 0 && (d1.k.a % 2) == 1);
            bool e_halts_even_only = true, e_halts_odd_only = true;
            for (int i = 0; i < 8; ++i) {
                int par = (6 + i) % 2;
                if (eres[i].kind == 'H' && par == 1) e_halts_even_only = false;
                if (eres[i].kind == 'K' && par == 0) e_halts_even_only = false;
                if (eres[i].kind == 'H' && par == 0) e_halts_odd_only = false;
                if (eres[i].kind == 'K' && par == 1) e_halts_odd_only = false;
            }
            if (d_preserves_a_par && (e_halts_even_only || e_halts_odd_only)) {
                int hpar = e_halts_even_only ? 0 : 1;
                bool any_b_hits_hpar = ((b1e.k.a % 2) == hpar || (b1o.k.a % 2) == hpar ||
                                        (b2e.k.a % 2) == hpar || (b2o.k.a % 2) == hpar ||
                                        (b3e.k.a % 2) == hpar);
                bool b1_dep_a = ((b1e.k.a % 2) != (b1o.k.a % 2));
                bool b2_dep_a = ((b2e.k.a % 2) != (b2o.k.a % 2));
                if (!any_b_hits_hpar) pstat = "LOCKED_A_PAR";
                else if (b1_dep_a || b2_dep_a) pstat = "B_DEP_A_PAR!";
                else pstat = "B_HITS_HPAR";
            } else if (!e_halts_even_only && !e_halts_odd_only) {
                pstat = "NON_MOD2_E!";
            }
        } else {
            pstat = "B_ACC_OPEN";
        }

        printf("%s\t%s\t%s\t%s\t%s\t%s\t%c:%lld:nK=%d:nE=%d:maxL=%d\t%s\t",
               ctx.pid.c_str(), ctx.group.c_str(), ctx.tag_info.c_str(),
               mstr.c_str(), epat.c_str(), pstat.c_str(),
               br.kind, br.steps, br.nK, br.nE, br.max_len,
               br.trace_summary.empty() ? "-" : br.trace_summary.c_str());
        printf("D=%lld/%lld B1=%s/%s B2=%s/%s B3=%s | E:",
               d0.k.a, d1.k.a,
               fmt_k(b1e.k).c_str(), fmt_k(b1o.k).c_str(),
               fmt_k(b2e.k).c_str(), fmt_k(b2o.k).c_str(),
               fmt_k(b3e.k).c_str());
        for (int i = 0; i < 8; ++i) {
            long long val = (t.mode == "a_acc") ? (6 + i) : (12 + i);
            if (eres[i].kind == 'H') printf(" %lld:H", val);
            else if (eres[i].kind == 'K') printf(" %lld:K(L%d,a%lld,b%lld)", val, (int)eres[i].k.ds.size(), eres[i].k.a, eres[i].k.b);
            else printf(" %lld:%c", val, eres[i].kind);
        }
        printf("\n");
        fflush(stdout);
        return;
    }

do_branch_d0:
    int bs = d0.hslot;
    ctx.need_branch[bs] = false;
    for (int nx = 0; nx < ctx.NS; ++nx) {
        for (int w = 0; w < 2; ++w) {
            for (int d = -1; d <= 1; d += 2) {
                ctx.tr[bs] = {w, d, nx, true};
                evaluate_and_branch(ctx);
            }
        }
    }
    ctx.tr[bs].def = false;
    ctx.need_branch[bs] = true;
}

static void run_free_set(ScanCtx &ctx, const std::vector<int> &F, const std::string &base_tag) {
    // Save original transitions of F
    std::vector<Tr> saved;
    for (int s : F) saved.push_back(ctx.tr[s]);
    // For each choice of designated halting slot u_halt in F:
    for (size_t hi = 0; hi < F.size(); ++hi) {
        for (int i = 0; i < 18; ++i) ctx.need_branch[i] = false;
        for (size_t j = 0; j < F.size(); ++j) {
            ctx.tr[F[j]].def = false;
            if (j != hi) ctx.need_branch[F[j]] = true;
        }
        ctx.tag_info = base_tag + ":H=" + sl_name(F[hi]);
        evaluate_and_branch(ctx);
    }
    for (size_t j = 0; j < F.size(); ++j) ctx.tr[F[j]] = saved[j];
}

int main(int argc, char **argv) {
#ifdef _WIN32
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
#endif
    if (argc < 3) {
        fprintf(stderr, "Usage: perturb8_scan <parents_scan.tsv> <mode: mut8|ext9> [filter_source]\n");
        return 1;
    }
    std::string tsv_path = argv[1];
    std::string scan_mode = argv[2];
    std::string filter_src = (argc > 3) ? argv[3] : "";

    std::ifstream f(tsv_path);
    std::string line;
    std::set<std::string> seen_machines;
    long long total_nodes = 0, total_surv = 0;

    while (std::getline(f, line)) {
        if (line.empty() || line[0] == '#') continue;
        std::stringstream ss(line);
        std::vector<std::string> cols;
        std::string tok;
        while (std::getline(ss, tok, '\t')) cols.push_back(tok);
        if (cols.size() < 14) continue;

        std::string pid = cols[0];
        std::string src = cols[1];
        std::string grp = cols[2];
        std::string mstr = cols[3];
        std::string tmpl_str = cols[4];
        long long B0 = std::stoll(cols[5]);
        int nE = std::stoi(cols[6]);
        std::string acc_mode = cols[7];

        if (!filter_src.empty() && src != filter_src && pid.find(filter_src) == std::string::npos) continue;

        std::vector<int> undef_slots = parse_slots(cols[8]);
        std::vector<int> D_used = parse_slots(cols[9]);
        std::vector<int> B_only = parse_slots(cols[10]);
        std::vector<int> E_only = parse_slots(cols[11]);
        std::vector<int> start_only = parse_slots(cols[12]);
        std::vector<int> unused_all = parse_slots(cols[13]);

        std::set<int> D_set(D_used.begin(), D_used.end());
        int u0 = undef_slots.empty() ? 14 : undef_slots[0];

        ScanCtx ctx;
        ctx.pid = pid;
        ctx.group = grp;
        ctx.t = parse_tmpl_str(tmpl_str, B0, nE, acc_mode);
        ctx.seen_machines = &seen_machines;
        ctx.tr.assign(18, {0, 0, 0, false});
        for (int q = 0; q < 8; ++q) {
            for (int c = 0; c < 2; ++c) {
                const char *x = mstr.c_str() + 7 * q + 3 * c;
                if (x[0] == '-') ctx.tr[2 * q + c].def = false;
                else {
                    int d = (x[1] == 'R') ? 1 : -1;
                    if (ctx.t.mirror) d = -d;
                    ctx.tr[2 * q + c] = {x[0] - '0', d, x[2] - 'A', true};
                }
            }
        }

        // Collect all defined slots outside D_set
        std::vector<int> non_D;
        for (int s = 0; s < 16; ++s) {
            if (s != u0 && !D_set.count(s)) non_D.push_back(s);
        }

        if (scan_mode == "mut8") {
            ctx.NS = 8;
            // 1. All 1-slot mutations + halt relocations across all 15 defined slots
            for (int s = 0; s < 16; ++s) {
                if (s == u0) continue;
                run_free_set(ctx, {s, u0}, "1slot_" + sl_name(s));
            }
            // 2. All 2-slot mutations + halt relocations for pairs of non-D slots
            for (size_t i = 0; i < non_D.size(); ++i) {
                for (size_t j = i + 1; j < non_D.size(); ++j) {
                    run_free_set(ctx, {non_D[i], non_D[j], u0},
                                 "2slot_" + sl_name(non_D[i]) + "_" + sl_name(non_D[j]));
                }
            }
        } else if (scan_mode == "ext9") {
            ctx.NS = 9;
            int I_state = 8;
            // 9A: Route u0 -> (w, d, I), free set = {I0, I1}
            for (int w = 0; w < 2; ++w) {
                for (int d = -1; d <= 1; d += 2) {
                    ctx.tr[u0] = {w, d, I_state, true};
                    int d_out = ctx.t.mirror ? -d : d;
                    std::string wd = std::string(1, char('0' + w)) + (d_out > 0 ? "R" : "L");
                    run_free_set(ctx, {16, 17}, "9A_u0_" + sl_name(u0) + wd + "I");
                    ctx.tr[u0].def = false;
                }
            }
            // 9B: Route each non_D slot s -> (w, d, I), free set = {u0, I0, I1}
            for (int s : non_D) {
                Tr save_s = ctx.tr[s];
                for (int w = 0; w < 2; ++w) {
                    for (int d = -1; d <= 1; d += 2) {
                        ctx.tr[s] = {w, d, I_state, true};
                        int d_out = ctx.t.mirror ? -d : d;
                        std::string wd = std::string(1, char('0' + w)) + (d_out > 0 ? "R" : "L");
                        run_free_set(ctx, {u0, 16, 17}, "9B_" + sl_name(s) + wd + "I");
                    }
                }
                ctx.tr[s] = save_s;
            }
        }
        total_nodes += ctx.nodes;
        total_surv += ctx.survivors;
        fprintf(stderr, "[%s] %s (%s): nodes=%lld surv=%lld\n",
                scan_mode.c_str(), pid.c_str(), grp.c_str(), ctx.nodes, ctx.survivors);
    }
    fprintf(stderr, "DONE %s: total_nodes=%lld total_survivors=%lld\n",
            scan_mode.c_str(), total_nodes, total_surv);
    return 0;
}
