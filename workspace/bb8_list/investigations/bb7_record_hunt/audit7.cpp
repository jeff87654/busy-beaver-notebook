#include <windows.h>
#define main dlscan2_main
#include "../../../bb8_list/neighbors/dlscan2.cpp"
#undef main

#include <iostream>
#include <fstream>
#include <sstream>

static std::string dstr(const std::vector<long long> &ds) {
    if (ds.empty()) return "-";
    std::string o;
    for (size_t i = 0; i < ds.size(); ++i) {
        if (i) o += ",";
        if (i >= 12 && i + 2 < ds.size()) { o += "..."; i = ds.size() - 2; continue; }
        o += std::to_string(ds[i]);
    }
    return o;
}

static bool parse_tmpl_str(const std::string &s, bool &mir, Tmpl &t) {
    std::vector<std::string> f;
    std::stringstream ss(s);
    std::string item;
    while (std::getline(ss, item, ',')) f.push_back(item);
    if (f.size() < 7) return false;
    mir = (f[0] == "L");
    t.q = f[1][0] - 'A';
    for (size_t i = 2; i < f.size(); ++i) {
        size_t eq = f[i].find('=');
        if (eq == std::string::npos) continue;
        std::string k = f[i].substr(0, eq), v = f[i].substr(eq + 1);
        if (k == "P") t.P = (v == "-" ? "" : v);
        else if (k == "u") t.u = v;
        else if (k == "s") t.s = v;
        else if (k == "S") t.S = (v == "-" ? "" : v);
        else if (k == "d") {
            size_t pos = v.find("d+");
            t.al = std::stoll(v.substr(0, pos));
            t.be = std::stoll(v.substr(pos + 2));
        } else if (k == "b") {
            size_t pos = v.find("b+");
            t.alB = std::stoll(v.substr(0, pos));
            t.beB = std::stoll(v.substr(pos + 2));
        }
    }
    return true;
}

// Strip hidden digits from the right of t.P
static Tmpl strip_P(const Tmpl &t, std::string &strip_note) {
    Tmpl tm = t;
    std::string P = t.P;
    long long ul = (long long)t.u.size(), sl = (long long)t.s.size();
    std::vector<long long> p_digs;
    while ((long long)P.size() >= sl && P.compare(P.size() - sl, sl, t.s) == 0) {
        long long x = (long long)P.size() - sl;
        long long k = 0;
        while (x >= ul && P.compare(x - ul, ul, t.u) == 0) {
            x -= ul;
            ++k;
        }
        if (k < t.be || (k - t.be) % t.al != 0) break;
        long long d = (k - t.be) / t.al;
        if (x == 0 && d == 0) break; // leading 0 on empty P would vanish
        p_digs.push_back(d);
        P.resize(x);
    }
    if (!p_digs.empty()) {
        std::reverse(p_digs.begin(), p_digs.end());
        tm.P = P;
        strip_note = "P_rem=" + (P.empty() ? "-" : P) + ",p_digs=[" + dstr(p_digs) + "]";
    } else {
        strip_note = "-";
    }
    return tm;
}

// Prefix-agnostic right-to-left parser: peels S, b, a, and (u^v s)* from the right, returns remaining prefix P_new
static bool parse_anyP(Prober2 &pr, const Tmpl &t, long long p, long long lo, P2 &r, std::string &P_new) {
    long long len = p - lo;
    if (len < (long long)t.S.size()) return false;
    pr.buf.resize(len);
    for (long long i = 0; i < len; ++i) pr.buf[i] = char('0' + pr.tape[lo + i]);
    if (pr.buf.compare(len - t.S.size(), t.S.size(), t.S) != 0) return false;
    long long x = len - (long long)t.S.size();
    pr.runs.clear();
    long long ul = (long long)t.u.size(), sl = (long long)t.s.size();
    for (;;) {
        long long k = 0;
        while (x >= ul && pr.buf.compare(x - ul, ul, t.u) == 0) { x -= ul; ++k; }
        pr.runs.push_back(k);
        if (x == 0) break;
        if (x >= sl && pr.buf.compare(x - sl, sl, t.s) == 0) {
            // Only peel s if either x > sl or it's part of a valid digit
            x -= sl;
        } else {
            break;
        }
    }
    if (pr.runs.size() < 2) return false;
    auto dec = [](long long raw, long long al, long long be, long long &v) {
        if (raw < be || (raw - be) % al) return false;
        v = (raw - be) / al; return true;
    };
    if (!dec(pr.runs[0], t.alB, t.beB, r.b) || !dec(pr.runs[1], t.al, t.be, r.a)) return false;
    r.ds.clear();
    for (size_t i = pr.runs.size(); i-- > 2;) {
        long long v;
        if (!dec(pr.runs[i], t.al, t.be, v)) return false;
        r.ds.push_back(v);
    }
    P_new = pr.buf.substr(0, x);
    if (P_new.empty()) {
        while (!r.ds.empty() && r.ds[0] == 0) r.ds.erase(r.ds.begin());
    }
    return true;
}

struct TraceRes {
    int nk = 0, n_macro = 0, n_rebuilds = 0;
    bool halted = false;
    long long halt_step = -1, halt_ones = 0;
    long long first_step = -1, last_step = -1;
    std::vector<long long> first_ds, last_ds;
    long long first_a = 0, first_b = 0, last_a = 0, last_b = 0;
    int max_n = 0;
};

static TraceRes run_trace(Prober2 &pr, const TM &m, const Tmpl &t, long long maxs, int max_macro) {
    TraceRes res;
    const long long SZ = 1LL << 23; // 8M cells
    if ((long long)pr.tape.size() < SZ) pr.tape.assign(SZ, 0);
    long long p = SZ / 2, mn = p, mx = p - 1, vlo = p, vhi = p;
    int q = 0;
    long long work = 0;
    std::vector<long long> prev_ds;
    bool has_prev = false;
    for (long long st = 0; st < maxs; ++st) {
        if (p <= 8 || p >= SZ - 8) break;
        int c = pr.tape[p];
        if (m.nx[q][c] < 0) {
            res.halted = true;
            res.halt_step = st;
            for (long long i = mn; i <= mx; ++i) res.halt_ones += pr.tape[i];
            break;
        }
        int wr = m.w[q][c];
        pr.tape[p] = (uint8_t)wr;
        if (p < vlo) vlo = p;
        if (p > vhi) vhi = p;
        if (wr) { if (mn > mx) mn = mx = p; else { if (p < mn) mn = p; if (p > mx) mx = p; } }
        p += m.d[q][c]; q = m.nx[q][c];
        if (p < vlo) vlo = p;
        if (p > vhi) vhi = p;
        if (q != t.q || pr.tape[p] != 0) continue;
        while (mx > p && !pr.tape[mx]) --mx;
        if (mx > p) continue;
        while (mn < p && !pr.tape[mn]) ++mn;
        long long lo = mn < p ? mn : p;
        work += p - lo;
        if (work > 800000000LL) break;
        P2 got;
        if (!pr.parse(t, p, lo, got)) continue;
        if (res.nk == 0) {
            res.first_step = st + 1;
            res.first_ds = got.ds;
            res.first_a = got.a;
            res.first_b = got.b;
        }
        res.nk++;
        if (!has_prev || got.ds != prev_ds) {
            if (has_prev && got.ds.size() > prev_ds.size()) res.n_rebuilds++;
            prev_ds = got.ds;
            has_prev = true;
            res.n_macro++;
        }
        res.last_step = st + 1;
        res.last_ds = got.ds;
        res.last_a = got.a;
        res.last_b = got.b;
        if ((int)got.ds.size() > res.max_n) res.max_n = (int)got.ds.size();
        if (res.n_macro >= max_macro) break;
    }
    memset(pr.tape.data() + vlo, 0, (size_t)(vhi - vlo + 1));
    return res;
}

struct RefitRes {
    bool r3_ok = false;
    long long m3 = 0, c3 = 0, e3 = 0, tail = -1, a3 = 0, b3 = 0;
};

static RefitRes refit_r3(Prober2 &pr, const TM &m, const Tmpl &t, long long N) {
    RefitRes rf;
    std::vector<std::tuple<long long, long long, long long>> pts;
    std::set<long long> tails;
    std::set<std::pair<long long, long long>> consts;
    int bad = 0;
    for (long long k = 1; k <= 3; ++k) {
        for (long long b = 4 * k + 6; b <= 4 * k + 9; ++b) {
            std::vector<long long> ds = {1, 2};
            ds.insert(ds.end(), k, 0);
            P2 r = pr.run_next(m, t, ds, 0, b, N);
            if (r.kind != 0 || (long long)r.ds.size() != 2 + k || r.ds[0] != 1 || r.ds[1] != 1) {
                bad++;
                continue;
            }
            pts.push_back({k, b, r.ds[2]});
            for (size_t i = 3; i < r.ds.size(); ++i) tails.insert(r.ds[i]);
            consts.insert({r.a, r.b});
        }
    }
    if (bad == 0 && tails.size() <= 1 && consts.size() == 1) {
        std::map<long long, std::vector<std::pair<long long, long long>>> byk;
        for (auto &p : pts) byk[std::get<0>(p)].push_back({std::get<1>(p), std::get<2>(p)});
        long long m3_1 = 0, c_1 = 0, m3_2 = 0, c_2 = 0, m3_3 = 0, c_3 = 0;
        if (lin2(byk[1], m3_1, c_1) && lin2(byk[2], m3_2, c_2) && lin2(byk[3], m3_3, c_3)) {
            if (m3_1 == m3_2 && m3_2 == m3_3 && (c_2 - c_1) == (c_3 - c_2)) {
                rf.r3_ok = true;
                rf.m3 = m3_1;
                rf.e3 = c_2 - c_1;
                rf.c3 = c_1 - rf.e3;
                rf.tail = tails.empty() ? 1 : *tails.begin();
                rf.a3 = consts.begin()->first;
                rf.b3 = consts.begin()->second;
            }
        }
    }
    return rf;
}

// Follow an exhaustion probe: returns H, K (in t), or P (in anyP with P_new != t.P), or T
static P2 run_exhaust_probe(Prober2 &pr, const TM &m, const Tmpl &t, const std::vector<long long> &ds, long long a, long long b, long long N, std::string &P_new_out) {
    std::string w = pr.word(t, ds, a, b);
    long long need = 2 * N + 2 * (long long)w.size() + 64;
    if ((long long)pr.tape.size() < need) pr.tape.assign(need, 0);
    long long p = (long long)pr.tape.size() / 2, vlo = p - (long long)w.size(), vhi = p;
    long long mn = p, mx = p - 1;
    for (size_t i = 0; i < w.size(); ++i) {
        pr.tape[vlo + i] = (uint8_t)(w[i] - '0');
        if (w[i] == '1') { if (mn > mx) mn = mx = vlo + i; else mx = vlo + i; }
    }
    int q = t.q;
    P2 r;
    P2 first_any;
    std::string first_P;
    bool have_any = false;
    long long work = 0;
    for (long long st = 0; st < N; ++st) {
        int c = pr.tape[p];
        if (m.nx[q][c] < 0) { r.kind = 1; r.steps = st; break; }
        int wr = m.w[q][c];
        pr.tape[p] = (uint8_t)wr;
        if (wr) { if (mn > mx) mn = mx = p; else { if (p < mn) mn = p; if (p > mx) mx = p; } }
        p += m.d[q][c]; q = m.nx[q][c];
        if (p < vlo) vlo = p;
        if (p > vhi) vhi = p;
        if (q != t.q || pr.tape[p] != 0) continue;
        while (mx > p && !pr.tape[mx]) --mx;
        if (mx > p) continue;
        while (mn < p && !pr.tape[mn]) ++mn;
        long long lo = mn < p ? mn : p;
        work += p - lo;
        if (work > 400000000LL) break;
        P2 got;
        if (pr.parse(t, p, lo, got)) {
            got.kind = 0; got.steps = st + 1; r = got;
            P_new_out = t.P;
            break;
        }
        if (!have_any) {
            std::string Pn;
            if (parse_anyP(pr, t, p, lo, first_any, Pn) && (!first_any.ds.empty() || first_any.a > 0)) {
                first_any.kind = 3; // 'P' = prefix-changed K-config
                first_any.steps = st + 1;
                first_P = Pn;
                have_any = true;
            }
        }
    }
    if (r.kind == 2 && have_any) {
        r = first_any;
        P_new_out = first_P;
    }
    if (vlo < 0) vlo = 0;
    memset(pr.tape.data() + vlo, 0, (size_t)(vhi - vlo + 1));
    return r;
}

int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    if (argc < 3) {
        fprintf(stderr, "Usage: audit7 IN.tsv OUT.tsv\n");
        return 1;
    }
    std::ifstream in(argv[1]);
    std::ofstream out(argv[2]);
    out << "machine\tgrade\tsrc\ttmpl\tstrip_P\tparams\trefit_r3\tn_macro\tn_reb\tmax_n\tfirst_K\tlast_K\tpatS\tB0\tpatL\texh_detail\n";
    Prober2 pr;
    std::string line;
    int idx = 0;
    while (std::getline(in, line)) {
        if (line.empty() || line[0] == '#') continue;
        std::vector<std::string> f;
        std::stringstream ss(line);
        std::string item;
        while (std::getline(ss, item, '\t')) f.push_back(item);
        if (f.size() < 6) continue;
        std::string mstr = f[0], grade = f[3], tmpl_s = f[4], params_s = f[5];
        std::string src = f.size() > 6 ? f[6] : "-";
        TM m;
        if (!parse(mstr, m)) continue;
        bool mir = false;
        Tmpl t_orig;
        if (!parse_tmpl_str(tmpl_s, mir, t_orig)) continue;
        if (mir) m = mirrored(m);

        std::string strip_note;
        Tmpl t = strip_P(t_orig, strip_note);

        TraceRes tr = run_trace(pr, m, t, 8000000LL, 400);
        RefitRes rf = refit_r3(pr, m, t, 200000LL);

        int n_zero = tr.nk > 0 ? (int)tr.last_ds.size() : 1;
        std::vector<long long> zds;
        if (!t.P.empty()) zds.assign(n_zero, 0);

        std::string patS, patL, exh_detail;
        for (long long b = 0; b < 16; ++b) {
            std::string Pn;
            P2 r = run_exhaust_probe(pr, m, t, zds, 0, b, 200000LL, Pn);
            patS += (r.kind == 1 ? 'H' : r.kind == 0 ? 'K' : r.kind == 3 ? 'P' : 'T');
        }
        // When t.P is empty, zds is empty, so K(; 0; b) is independent of n_zero! Use B0 = 16.
        // When t.P is nonempty, zds has n_zero zeros, so use B0 = 2 * n_zero + 16.
        long long B0 = t.P.empty() ? 16 : (2 * n_zero + 16);
        for (long long b = B0; b < B0 + 12; ++b) {
            std::string Pn;
            P2 r = run_exhaust_probe(pr, m, t, zds, 0, b, 500000LL, Pn);
            patL += (r.kind == 1 ? 'H' : r.kind == 0 ? 'K' : r.kind == 3 ? 'P' : 'T');
            if (b < B0 + 4) {
                if (!exh_detail.empty()) exh_detail += " ; ";
                if (r.kind == 1) exh_detail += "b=" + std::to_string(b) + ":H(" + std::to_string(r.steps) + ")";
                else if (r.kind == 2) exh_detail += "b=" + std::to_string(b) + ":T";
                else if (r.kind == 3) exh_detail += "b=" + std::to_string(b) + ":P(" + (Pn.empty() ? "-" : Pn) + ",n=" + std::to_string(r.ds.size()) + ",ds=[" + dstr(r.ds) + "],a=" + std::to_string(r.a) + ",b=" + std::to_string(r.b) + ")";
                else exh_detail += "b=" + std::to_string(b) + ":K(n=" + std::to_string(r.ds.size()) + ",ds=[" + dstr(r.ds) + "],a=" + std::to_string(r.a) + ",b=" + std::to_string(r.b) + ")";
            }
        }

        std::string rf_s = rf.r3_ok
            ? ("R3 " + std::to_string(rf.m3) + "b" + (rf.c3 >= 0 ? "+" : "") + std::to_string(rf.c3) + (rf.e3 >= 0 ? "+" : "") + std::to_string(rf.e3) + "k tail=" + std::to_string(rf.tail) + " a=" + std::to_string(rf.a3) + " b=" + std::to_string(rf.b3))
            : "FAIL";
        std::string fk_s = tr.nk == 0 ? "-" : ("s=" + std::to_string(tr.first_step) + " n=" + std::to_string(tr.first_ds.size()) + " [" + dstr(tr.first_ds) + "] a=" + std::to_string(tr.first_a) + " b=" + std::to_string(tr.first_b));
        std::string lk_s = tr.nk == 0 ? "-" : ("s=" + std::to_string(tr.last_step) + " n=" + std::to_string(tr.last_ds.size()) + " [" + dstr(tr.last_ds) + "] a=" + std::to_string(tr.last_a) + " b=" + std::to_string(tr.last_b));
        if (tr.halted) lk_s += " HALT@" + std::to_string(tr.halt_step);

        out << mstr << "\t" << grade << "\t" << src << "\t" << tmpl_s << "\t" << strip_note << "\t" << params_s << "\t"
            << rf_s << "\t" << tr.n_macro << "\t" << tr.n_rebuilds << "\t" << tr.max_n << "\t" << fk_s << "\t" << lk_s << "\t"
            << patS << "\t" << B0 << "\t" << patL << "\t" << exh_detail << "\n";
        if (++idx % 50 == 0) {
            out.flush();
            fprintf(stderr, "Audited %d rows...\n", idx);
        }
    }
    fprintf(stderr, "Done! Audited %d rows.\n", idx);
    return 0;
}
