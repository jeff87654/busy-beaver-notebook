#include <windows.h>
#define main dlscan2_main
#include "../../../bb8_list/neighbors/dlscan2.cpp"
#undef main

#include <iostream>
#include <fstream>
#include <sstream>
#include <set>

static Tmpl make_tmpl(int q, const std::string &P, const std::string &u, const std::string &s,
                      long long al, long long be, long long alB, long long beB, const std::string &S) {
    Tmpl t;
    t.q = q; t.P = P; t.u = u; t.s = s;
    t.al = al; t.be = be; t.alB = alB; t.beB = beB; t.S = S;
    return t;
}

static std::string dstr(const std::vector<long long> &ds) {
    if (ds.empty()) return "-";
    std::string o;
    for (size_t i = 0; i < ds.size(); ++i) {
        if (i) o += ",";
        if (i >= 10 && i + 2 < ds.size()) { o += "..."; i = ds.size() - 2; continue; }
        o += std::to_string(ds[i]);
    }
    return o;
}

static std::string tm_to_str(const TM &m) {
    std::string s;
    for (int q = 0; q < m.n; ++q) {
        if (q) s += "_";
        for (int c = 0; c < 2; ++c) {
            if (m.nx[q][c] < 0) s += "---";
            else {
                s += char('0' + m.w[q][c]);
                s += (m.d[q][c] > 0 ? 'R' : 'L');
                s += char('A' + m.nx[q][c]);
            }
        }
    }
    return s;
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
            x -= sl;
        } else {
            break;
        }
    }
    if (pr.runs.size() < 2) return false;
    if (x > 12) return false; // prefix P_new should be short cap, not unparsed garbage
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

struct SeedSpec {
    std::string name;
    std::string mstr;
    bool mir;
    Tmpl t;
};

struct FastTrace {
    int nk = 0, n_macro = 0, n_rebuilds = 0, max_n = 0;
    bool halted = false;
    long long halt_step = -1;
    long long first_step = -1, last_step = -1;
    std::vector<long long> first_ds, last_ds;
    long long first_a = 0, first_b = 0, last_a = 0, last_b = 0;
    std::string last_P;
};

static FastTrace trace_fast(Prober2 &pr, const TM &m, const Tmpl &t, long long maxs, int max_macro) {
    FastTrace res;
    const long long SZ = 1LL << 21; // 2M cells
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
        if (st == 35000 && res.nk == 0) break;
        if (q != t.q || pr.tape[p] != 0) continue;
        while (mx > p && !pr.tape[mx]) --mx;
        if (mx > p) continue;
        while (mn < p && !pr.tape[mn]) ++mn;
        long long lo = mn < p ? mn : p;
        work += p - lo;
        if (work > 100000000LL) break;
        P2 got;
        std::string Pn;
        if (!parse_anyP(pr, t, p, lo, got, Pn)) continue;
        if (got.ds.empty() && got.a == 0 && got.b <= 1) continue;
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
        res.last_P = Pn;
        int eff_n = (int)got.ds.size();
        // If Pn is nonempty and ends with zeros of s, strip leading zeros in ds for max_n comparison if needed
        if (eff_n > res.max_n) res.max_n = eff_n;
        if (res.n_macro >= max_macro) break;
    }
    memset(pr.tape.data() + vlo, 0, (size_t)(vhi - vlo + 1));
    return res;
}

int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    std::ofstream out(argc > 1 ? argv[1] : "neighbors_out.tsv");
    out << "seed\tdist\tmachine\tnk\tn_macro\tn_reb\tmax_n\tlast_P\tfirst_K\tlast_K\tr1_check\tr2_check\tb1_check\tb2_check\tpatE\n";

    std::vector<SeedSpec> seeds = {
        {"champ_231", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB", true,
            make_tmpl(4, "100", "11", "00", 1, 0, 1, 0, "1")},
        {"r4_2_rrFFr", "1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA0LE", false,
            make_tmpl(1, "", "1", "10", 1, 0, 3, 1, "")},
        {"X33", "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE", false,
            make_tmpl(0, "", "1", "0", 1, 0, 1, 0, "")},
        {"G1_2_base5", "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG", true,
            make_tmpl(0, "", "1", "0", 1, 0, 1, 0, "0")}
    };

    Prober2 pr;
    for (auto &sd : seeds) {
        TM base_m;
        parse(sd.mstr, base_m);
        int halt_slot = -1;
        std::vector<int> def_slots;
        for (int s = 1; s < 14; ++s) {
            int q = s / 2, c = s % 2;
            if (base_m.nx[q][c] < 0) halt_slot = s;
            else def_slots.push_back(s);
        }

        long long n_cand = 0, n_pass_r1 = 0, n_pass_tr = 0;

        auto evaluate_cand = [&](const TM &cand, int dist) {
            n_cand++;
            TM m = sd.mir ? mirrored(cand) : cand;
            // Fast probe 1: K([2,1]; 2; 3) -> must return K([2,1]; 1; b') in <= 800 steps
            P2 r1 = pr.run_next(m, sd.t, {2, 1}, 2, 3, 800);
            if (r1.kind != 0 || r1.ds != std::vector<long long>{2, 1} || r1.a != 1 || r1.b < 3) return;
            // Fast probe 2: K([2,1]; 0; 4) -> must return K([2,0]; a'; b') in <= 1200 steps
            P2 r2 = pr.run_next(m, sd.t, {2, 1}, 0, 4, 1200);
            if (r2.kind != 0 || r2.ds != std::vector<long long>{2, 0}) return;
            n_pass_r1++;

            // Blank-tape trace up to 1,500,000 steps, max_macro = 80
            FastTrace tr = trace_fast(pr, m, sd.t, 1500000LL, 80);
            if (tr.halted || tr.nk < 3 || tr.max_n < 1) return;
            n_pass_tr++;

            Tmpl t_eff = sd.t;
            t_eff.P = tr.last_P;

            // Probe B1: K([1,2,0]; 0; 16) and B2: K([1,2,0,0]; 0; 16)
            P2 b1 = pr.run_next(m, t_eff, {1, 2, 0}, 0, 16, 20000);
            P2 b2 = pr.run_next(m, t_eff, {1, 2, 0, 0}, 0, 16, 20000);

            // Probe E: b = B0..B0+7 (with zds = 0^last_n if P nonempty, else empty)
            int nz = (int)tr.last_ds.size();
            std::vector<long long> zds;
            if (!t_eff.P.empty()) zds.assign(nz, 0);
            long long B0 = t_eff.P.empty() ? 16 : (2 * nz + 16);
            std::string patE;
            for (long long b = B0; b < B0 + 8; ++b) {
                P2 re = pr.run_next(m, t_eff, zds, 0, b, 100000);
                patE += (re.kind == 1 ? 'H' : re.kind == 0 ? 'K' : 'T');
            }

            std::string fk_s = "s=" + std::to_string(tr.first_step) + " n=" + std::to_string(tr.first_ds.size()) + " [" + dstr(tr.first_ds) + "] a=" + std::to_string(tr.first_a) + " b=" + std::to_string(tr.first_b);
            std::string lk_s = "s=" + std::to_string(tr.last_step) + " n=" + std::to_string(tr.last_ds.size()) + " [" + dstr(tr.last_ds) + "] a=" + std::to_string(tr.last_a) + " b=" + std::to_string(tr.last_b);
            std::string r1_s = "b=3->" + std::to_string(r1.b);
            std::string r2_s = "b=4->a=" + std::to_string(r2.a) + ",b=" + std::to_string(r2.b);
            std::string b1_s = b1.kind == 0 ? ("[" + dstr(b1.ds) + "] a=" + std::to_string(b1.a) + " b=" + std::to_string(b1.b)) : (b1.kind == 1 ? "H" : "T");
            std::string b2_s = b2.kind == 0 ? ("[" + dstr(b2.ds) + "] a=" + std::to_string(b2.a) + " b=" + std::to_string(b2.b)) : (b2.kind == 1 ? "H" : "T");

            out << sd.name << "\t" << dist << "\t" << tm_to_str(cand) << "\t"
                << tr.nk << "\t" << tr.n_macro << "\t" << tr.n_rebuilds << "\t" << tr.max_n << "\t"
                << (tr.last_P.empty() ? "-" : tr.last_P) << "\t"
                << fk_s << "\t" << lk_s << "\t" << r1_s << "\t" << r2_s << "\t" << b1_s << "\t" << b2_s << "\t" << patE << "\n";
        };

        auto set_tr = [](TM &m, int slot, int tr_idx) {
            int q = slot / 2, c = slot % 2;
            if (tr_idx < 0) {
                m.nx[q][c] = -1; m.w[q][c] = 0; m.d[q][c] = 1;
            } else {
                m.w[q][c] = (tr_idx / 14) % 2;
                m.d[q][c] = ((tr_idx / 7) % 2) ? 1 : -1;
                m.nx[q][c] = tr_idx % 7;
            }
        };
        auto get_tr = [](const TM &m, int slot) {
            int q = slot / 2, c = slot % 2;
            if (m.nx[q][c] < 0) return -1;
            return m.w[q][c] * 14 + (m.d[q][c] > 0 ? 1 : 0) * 7 + m.nx[q][c];
        };

        // Dist 0 (seed itself)
        evaluate_cand(base_m, 0);

        // Dist 1: change 1 defined slot
        for (size_t i = 0; i < def_slots.size(); ++i) {
            int s1 = def_slots[i], orig1 = get_tr(base_m, s1);
            for (int t1 = 0; t1 < 28; ++t1) {
                if (t1 == orig1) continue;
                TM cand = base_m;
                set_tr(cand, s1, t1);
                evaluate_cand(cand, 1);
            }
        }

        // Dist 2a: change 2 defined slots
        for (size_t i = 0; i < def_slots.size(); ++i) {
            int s1 = def_slots[i], orig1 = get_tr(base_m, s1);
            for (size_t j = i + 1; j < def_slots.size(); ++j) {
                int s2 = def_slots[j], orig2 = get_tr(base_m, s2);
                for (int t1 = 0; t1 < 28; ++t1) {
                    if (t1 == orig1) continue;
                    for (int t2 = 0; t2 < 28; ++t2) {
                        if (t2 == orig2) continue;
                        TM cand = base_m;
                        set_tr(cand, s1, t1);
                        set_tr(cand, s2, t2);
                        evaluate_cand(cand, 2);
                    }
                }
            }
        }

        // Dist 2b: fill halt_slot with t_h (0..27), set s1 to halt (-1)
        for (size_t i = 0; i < def_slots.size(); ++i) {
            int s1 = def_slots[i];
            for (int th = 0; th < 28; ++th) {
                TM cand = base_m;
                set_tr(cand, halt_slot, th);
                set_tr(cand, s1, -1);
                evaluate_cand(cand, 2);
            }
        }

        // Dist 3 (move halt + 1 change): fill halt_slot with th, set s1 to halt (-1), modify s2 to t2
        for (size_t i = 0; i < def_slots.size(); ++i) {
            int s1 = def_slots[i];
            for (size_t j = 0; j < def_slots.size(); ++j) {
                if (i == j) continue;
                int s2 = def_slots[j], orig2 = get_tr(base_m, s2);
                for (int th = 0; th < 28; ++th) {
                    for (int t2 = 0; t2 < 28; ++t2) {
                        if (t2 == orig2) continue;
                        TM cand = base_m;
                        set_tr(cand, halt_slot, th);
                        set_tr(cand, s1, -1);
                        set_tr(cand, s2, t2);
                        evaluate_cand(cand, 3);
                    }
                }
            }
        }

        out.flush();
        fprintf(stderr, "Seed %s: tested %lld, pass_r1=%lld, pass_tr=%lld\n", sd.name.c_str(), n_cand, n_pass_r1, n_pass_tr);
    }
    return 0;
}
