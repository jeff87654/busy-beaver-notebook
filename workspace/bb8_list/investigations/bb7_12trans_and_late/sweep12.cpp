// sweep12.cpp: Fast, zero-allocation 13th-Slot & 12th+13th-Slot Completion Sweep
// Compiled with: g++ -O3 -static -o sweep12.exe sweep12.cpp
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>
#include <unordered_set>
#include <thread>
#include <mutex>
#include <atomic>

struct TM {
    int w[7][2];
    int d[7][2];
    int nx[7][2];
    int halt_slot;
};

static bool parse_tm(const std::string &s, TM &m) {
    if (s.size() < 47) return false;
    m.halt_slot = -1;
    for (int q = 0; q < 7; ++q) {
        for (int c = 0; c < 2; ++c) {
            int idx = q * 7 + c * 3;
            if (s[idx] == '-') {
                m.w[q][c] = 1; m.d[q][c] = 1; m.nx[q][c] = -1;
                m.halt_slot = q * 2 + c;
            } else {
                m.w[q][c] = s[idx] - '0';
                m.d[q][c] = (s[idx + 1] == 'R') ? 1 : -1;
                m.nx[q][c] = s[idx + 2] - 'A';
            }
        }
    }
    return true;
}

static std::string format_tm(const TM &m) {
    std::string out;
    out.reserve(48);
    for (int q = 0; q < 7; ++q) {
        if (q > 0) out += '_';
        for (int c = 0; c < 2; ++c) {
            if (m.nx[q][c] < 0) {
                out += "---";
            } else {
                out += char('0' + m.w[q][c]);
                out += (m.d[q][c] > 0) ? 'R' : 'L';
                out += char('A' + m.nx[q][c]);
            }
        }
    }
    return out;
}

struct Template {
    bool valid = false;
    char side = 'R';
    int Q = 0;
    std::string P, u, s, S;
    long long d_al = 1, d_be = 0, b_al = 1, b_be = 0;
};

static Template parse_template(const std::string &ts) {
    Template T;
    if (ts.empty() || ts == "-") return T;
    std::vector<std::string> parts;
    std::stringstream ss(ts);
    std::string item;
    while (std::getline(ss, item, ',')) parts.push_back(item);
    if (parts.size() < 8) return T;
    T.side = parts[0][0];
    T.Q = parts[1][0] - 'A';
    for (size_t i = 2; i < parts.size(); ++i) {
        const std::string &p = parts[i];
        if (p.rfind("P=", 0) == 0) { T.P = p.substr(2); if (T.P == "-") T.P = ""; }
        else if (p.rfind("u=", 0) == 0) { T.u = p.substr(2); }
        else if (p.rfind("s=", 0) == 0) { T.s = p.substr(2); }
        else if (p.rfind("S=", 0) == 0) { T.S = p.substr(2); if (T.S == "-") T.S = ""; }
        else if (p.rfind("d=", 0) == 0) { sscanf(p.c_str(), "d=%lldd+%lld", &T.d_al, &T.d_be); }
        else if (p.rfind("b=", 0) == 0) { sscanf(p.c_str(), "b=%lldb+%lld", &T.b_al, &T.b_be); }
    }
    if (T.d_al <= 0) T.d_al = 1;
    if (T.b_al <= 0) T.b_al = 1;
    if (T.d_be < 0) T.d_be = 0;
    if (T.b_be < 0) T.b_be = 0;
    T.valid = !T.u.empty() && !T.s.empty() && T.Q >= 0 && T.Q < 7;
    return T;
}

static std::string rep_str(const std::string &x, long long k) {
    std::string o;
    if (k > 0) o.reserve(x.size() * k);
    for (long long i = 0; i < k; ++i) o += x;
    return o;
}

struct ParentRow {
    std::string machine;
    std::string grade;
    std::string verdict;
    std::string exhaustion;
    int n_after_5k = 13;
    int n_after_100k = 13;
    int n_engine = 13;
    std::string non_engine_slots;
    std::string tmpl_str;
    Template T;
    std::vector<int> z_slots; // 0 executions after 100k
    std::vector<int> r_slots; // rare late (1..20 executions after 5k)
    int orig_max_nd = 0;
};

struct Candidate {
    std::string machine;
    int parent_idx;
    int mut_mask; // bitmask of mutated slots (0..13)
    std::string mut_desc;
};

struct EvalResult {
    bool keep = false;
    bool halted = false;
    bool touched_blank = false;
    bool touched_exh = false;
    long long steps = 0;
    long long span = 0;
    long long ones = 0;
    int n_K = 0;
    int max_nd = 0;
    int last_nd = 0;
    int n_rebuilds = 0;
    std::string obs_O;
    std::string best_ds_str;
    std::string E0_pat;
    std::string E1_pat;
    bool has_H_in_E = false;
    bool has_K_in_E = false;
};

// Parse tape w[0..len-1] at K-moment using free-prefix right-to-left parsing
static bool parse_k_word(const std::string &w, const Template &T, std::string &O_out, std::vector<long long> &ds_out, long long &a_out, long long &b_out) {
    if (w.size() < T.S.size()) return false;
    if (w.compare(w.size() - T.S.size(), T.S.size(), T.S) != 0) return false;
    long long e = (long long)w.size() - (long long)T.S.size();
    std::vector<long long> rr;
    while (true) {
        long long k = 0;
        while (e >= (long long)T.u.size() && w.compare(e - T.u.size(), T.u.size(), T.u) == 0) {
            e -= (long long)T.u.size();
            ++k;
        }
        rr.push_back(k);
        if (e >= (long long)T.s.size() && w.compare(e - T.s.size(), T.s.size(), T.s) == 0 && rr.size() < 10000) {
            e -= (long long)T.s.size();
        } else {
            break;
        }
    }
    if (e > 32) return false; // Outer prefix O must be <= 32 bits
    if (rr.size() < 2) return false;
    long long raw_b = rr[0];
    long long raw_a = rr[1];
    if (raw_b < T.b_be || (raw_b - T.b_be) % T.b_al != 0) return false;
    if (raw_a < T.d_be || (raw_a - T.d_be) % T.d_al != 0) return false;
    b_out = (raw_b - T.b_be) / T.b_al;
    a_out = (raw_a - T.d_be) / T.d_al;
    ds_out.clear();
    for (long long i = (long long)rr.size() - 1; i >= 2; --i) {
        long long rd = rr[i];
        if (rd < T.d_be || (rd - T.d_be) % T.d_al != 0) return false;
        ds_out.push_back((rd - T.d_be) / T.d_al);
    }
    O_out = w.substr(0, e);
    return true;
}

static char probe_exhaustion_one(const TM &m, const Template &T, const std::string &O, int n_zeros, long long b_val, long long max_steps, int mut_mask, bool &touched_exh, std::vector<unsigned char> &ptape) {
    auto enc_d = [&](long long d) { return rep_str(T.u, T.d_al * d + T.d_be) + T.s; };
    std::string w = O + rep_str(enc_d(0), n_zeros) + enc_d(0) + rep_str(T.u, T.b_al * b_val + T.b_be) + T.S;
    const long long SZ = (long long)ptape.size();
    const long long OFF = SZ / 2;
    long long lo = 0, hi = (long long)w.size();
    for (size_t i = 0; i < w.size(); ++i) ptape[OFF + i] = (w[i] == '1') ? 1 : 0;
    ptape[OFF + w.size()] = 0;
    long long min_vis = 0, max_vis = (long long)w.size();

    long long pos = (long long)w.size();
    int q = T.Q;
    int dir_mult = (T.side == 'L') ? -1 : 1;
    char res = 'T';

    for (long long st = 1; st <= max_steps; ++st) {
        if (pos + OFF <= 4 || pos + OFF >= SZ - 5) { res = 'T'; break; }
        int c = ptape[OFF + pos];
        if (st > 2 && c == 0 && q == T.Q && lo <= hi) {
            while (lo <= hi && !ptape[OFF + hi]) --hi;
            while (lo <= hi && !ptape[OFF + lo]) ++lo;
            if (lo <= hi && pos > hi && hi - lo < 8000) {
                std::string cw;
                cw.reserve(pos - lo);
                for (long long i = lo; i < pos; ++i) cw += char('0' + ptape[OFF + i]);
                std::string O2;
                std::vector<long long> ds2;
                long long a2 = 0, b2 = 0;
                if (parse_k_word(cw, T, O2, ds2, a2, b2)) {
                    bool has_nz = (a2 > 0);
                    for (long long d : ds2) if (d > 0) has_nz = true;
                    if (has_nz && !ds2.empty()) { res = 'K'; break; }
                }
            }
        }
        int s = q * 2 + c;
        if (mut_mask & (1 << s)) touched_exh = true;
        if (m.nx[q][c] < 0) { res = 'H'; break; }
        int nw = m.w[q][c];
        ptape[OFF + pos] = nw;
        if (nw) {
            if (lo > hi) lo = hi = pos;
            else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; }
        }
        pos += m.d[q][c] * dir_mult;
        q = m.nx[q][c];
        if (pos < min_vis) min_vis = pos;
        if (pos > max_vis) max_vis = pos;
    }
    for (long long i = min_vis; i <= max_vis; ++i) ptape[OFF + i] = 0;
    return res;
}

static std::string format_ds(const std::vector<long long> &ds, long long a, long long b) {
    std::string s = "[";
    for (size_t i = 0; i < ds.size(); ) {
        size_t j = i;
        while (j < ds.size() && ds[j] == ds[i]) ++j;
        if (i > 0) s += ",";
        s += std::to_string(ds[i]);
        if (j - i > 1) s += "^" + std::to_string(j - i);
        i = j;
        if (s.size() > 60) { s += ",..."; break; }
    }
    s += "];a=" + std::to_string(a) + ";b=" + std::to_string(b);
    return s;
}

static EvalResult evaluate_candidate(const Candidate &cand, const ParentRow &parent, std::vector<unsigned char> &tape, std::vector<unsigned char> &ptape) {
    EvalResult R;
    TM m;
    parse_tm(cand.machine, m);
    const long long SZ = (long long)tape.size();
    const long long OFF = SZ / 2;

    long long pos = 0, lo = 0, hi = -1;
    long long min_vis = 0, max_vis = 0;
    int q = 0;
    tape[OFF] = 0;

    const long long MAX_STEPS = 500000LL;
    bool has_tmpl = parent.T.valid;
    bool is_orig = (cand.mut_mask == 0);

    int prev_stable_nd = -1;
    bool dropped_low = false;
    std::string last_key;
    int key_streak = 0;

    for (long long st = 1; st <= MAX_STEPS; ++st) {
        if (pos + OFF <= 4 || pos + OFF >= SZ - 5) {
            R.steps = st - 1;
            R.span = max_vis - min_vis + 1;
            for (long long i = min_vis; i <= max_vis; ++i) tape[OFF + i] = 0;
            return R;
        }
        if (st == 20000 && (max_vis - min_vis + 1) < 28) {
            R.steps = st;
            R.span = max_vis - min_vis + 1;
            for (long long i = min_vis; i <= max_vis; ++i) tape[OFF + i] = 0;
            return R;
        }
        if (st == 100000 && (max_vis - min_vis + 1) < 80) {
            R.steps = st;
            R.span = max_vis - min_vis + 1;
            for (long long i = min_vis; i <= max_vis; ++i) tape[OFF + i] = 0;
            return R;
        }

        int c = tape[OFF + pos];

        // Check for K-moment in parent template
        if (has_tmpl && R.n_K < 800 && c == 0 && q == parent.T.Q && lo <= hi) {
            while (lo <= hi && !tape[OFF + hi]) --hi;
            while (lo <= hi && !tape[OFF + lo]) ++lo;
            bool at_edge = (parent.T.side == 'R') ? (pos > hi) : (pos < lo);
            if (lo <= hi && at_edge && (hi - lo) < 6000) {
                std::string w;
                w.reserve(hi - lo + 1);
                if (parent.T.side == 'R') {
                    for (long long i = lo; i < pos; ++i) w += char('0' + tape[OFF + i]);
                } else {
                    for (long long i = hi; i > pos; --i) w += char('0' + tape[OFF + i]);
                }
                std::string O;
                std::vector<long long> ds;
                long long a = 0, b = 0;
                if (parse_k_word(w, parent.T, O, ds, a, b)) {
                    R.n_K++;
                    int nd = (int)ds.size();
                    R.last_nd = nd;
                    std::string key = O + "|" + std::to_string(nd);
                    if (key == last_key) key_streak++;
                    else { last_key = key; key_streak = 1; }

                    if (key_streak >= 2) {
                        if (R.obs_O.empty() || nd >= R.max_nd) R.obs_O = O;
                        if (nd > R.max_nd) {
                            R.max_nd = nd;
                            R.best_ds_str = format_ds(ds, a, b);
                        }
                        if (prev_stable_nd >= 2 && nd <= 1) dropped_low = true;
                        if (dropped_low && nd >= 3) {
                            R.n_rebuilds++;
                            dropped_low = false;
                        }
                        prev_stable_nd = nd;
                    }
                }
            }
        }

        int s = q * 2 + c;
        if (cand.mut_mask & (1 << s)) R.touched_blank = true;

        if (m.nx[q][c] < 0) {
            R.halted = true;
            R.steps = st;
            R.span = max_vis - min_vis + 1;
            if (st >= 150000 && R.touched_blank) {
                long long ones = 0;
                for (long long i = min_vis; i <= max_vis; ++i) ones += tape[OFF + i];
                R.ones = ones;
                R.keep = true; // Late literal halter (>= 150k steps)
            }
            for (long long i = min_vis; i <= max_vis; ++i) tape[OFF + i] = 0;
            return R;
        }

        int nw = m.w[q][c];
        tape[OFF + pos] = nw;
        if (nw) {
            if (lo > hi) lo = hi = pos;
            else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; }
        }
        pos += m.d[q][c];
        q = m.nx[q][c];
        if (pos < min_vis) min_vis = pos;
        if (pos > max_vis) max_vis = pos;
    }

    R.steps = MAX_STEPS;
    R.span = max_vis - min_vis + 1;
    for (long long i = min_vis; i <= max_vis; ++i) tape[OFF + i] = 0;

    if (R.span < 180) return R;

    // Probe exhaustion E0 and E1 if machine matched K-template
    if (has_tmpl && R.n_K >= 4 && R.max_nd >= 2) {
        std::string O_use = R.obs_O.empty() ? parent.T.P : R.obs_O;
        for (long long b = 16; b < 24; ++b) {
            char c0 = probe_exhaustion_one(m, parent.T, O_use, 0, b, 15000, cand.mut_mask, R.touched_exh, ptape);
            char c1 = probe_exhaustion_one(m, parent.T, O_use, 1, b, 15000, cand.mut_mask, R.touched_exh, ptape);
            R.E0_pat += c0;
            R.E1_pat += c1;
            if (c0 == 'H' || c1 == 'H') R.has_H_in_E = true;
            if (c0 == 'K' || c1 == 'K') R.has_K_in_E = true;
        }
        if (is_orig) {
            R.keep = true;
            return R;
        }
        // If neither the blank-tape run nor the exhaustion probe EVER touched a mutated transition,
        // then this variant is behaviorally identical to ORIG!
        if (!R.touched_blank && !R.touched_exh) {
            return R;
        }
        bool parent_halts = (parent.verdict.find("HALT") != std::string::npos && parent.verdict.find("NEVER") == std::string::npos) || parent.grade == "CHAMPION";
        if (R.has_H_in_E || (parent_halts && R.max_nd >= 3)) {
            R.keep = true;
        }
    } else if (is_orig || (R.touched_blank && R.span >= 1000)) {
        bool parent_halts = (parent.verdict.find("HALT") != std::string::npos && parent.verdict.find("NEVER") == std::string::npos) || parent.grade == "CHAMPION";
        if (is_orig || parent_halts) R.keep = true;
    }

    return R;
}

static std::string slot_name(int s) {
    char buf[4];
    snprintf(buf, sizeof(buf), "%c%d", 'A' + (s / 2), s % 2);
    return std::string(buf);
}

static int parse_slot_name(const std::string &sn) {
    if (sn.size() < 2) return -1;
    int q = sn[0] - 'A';
    int c = sn[1] - '0';
    if (q < 0 || q >= 7 || c < 0 || c >= 2) return -1;
    return q * 2 + c;
}

static void load_census_file(const std::string &path, std::vector<ParentRow> &parents, std::unordered_set<std::string> &seen_parents) {
    std::ifstream fin(path);
    std::string line;
    bool header = true;
    while (std::getline(fin, line)) {
        if (header) { header = false; continue; }
        if (line.empty()) continue;
        std::vector<std::string> f;
        std::stringstream ss(line);
        std::string item;
        while (std::getline(ss, item, '\t')) f.push_back(item);
        if (f.size() < 11) continue;
        std::string m = f[0];
        if (seen_parents.count(m)) continue;
        seen_parents.insert(m);

        ParentRow P;
        P.machine = m;
        P.grade = f[1];
        P.verdict = f[2];
        P.n_after_5k = std::stoi(f[5]);
        P.n_after_100k = std::stoi(f[6]);
        P.n_engine = std::stoi(f[7]);
        P.non_engine_slots = f[8];
        P.tmpl_str = f[10];
        P.exhaustion = (f.size() > 12) ? f[12] : "-";
        P.T = parse_template(P.tmpl_str);

        bool is_halts = (P.verdict.find("HALT") != std::string::npos && P.verdict.find("NEVER") == std::string::npos) || P.grade == "CHAMPION";
        if (P.n_after_100k > 12 && !is_halts) continue;

        if (P.non_engine_slots != "-") {
            std::stringstream ss2(P.non_engine_slots);
            std::string tok;
            while (std::getline(ss2, tok, ';')) {
                size_t col = tok.find(':');
                if (col == std::string::npos) continue;
                int s = parse_slot_name(tok.substr(0, col));
                if (s <= 0) continue; // skip A0
                std::string role = tok.substr(col + 1);
                if (role.rfind("STARTUP_ONLY", 0) == 0 ||
                    role.rfind("EARLY_ONLY", 0) == 0 ||
                    role.rfind("UNUSED", 0) == 0 ||
                    role.find(",vl=0,") != std::string::npos) {
                    P.z_slots.push_back(s);
                } else {
                    P.r_slots.push_back(s);
                }
            }
        }
        if (!P.z_slots.empty() || (is_halts && !P.r_slots.empty())) {
            parents.push_back(P);
        }
    }
}

int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);

    std::vector<ParentRow> parents;
    std::unordered_set<std::string> seen_parents;
    load_census_file("census12_all.tsv", parents, seen_parents);
    load_census_file("census12_pool7f.tsv", parents, seen_parents);

    fprintf(stderr, "Selected %zu parent machines for 12-transition completion sweep.\n", parents.size());

    struct Action { int w, d, q; std::string str; };
    std::vector<Action> actions;
    for (int w = 0; w < 2; ++w) {
        for (int d : {-1, 1}) {
            for (int q = 0; q < 7; ++q) {
                std::string s;
                s += char('0' + w);
                s += (d > 0) ? 'R' : 'L';
                s += char('A' + q);
                actions.push_back({w, d, q, s});
            }
        }
    }

    std::vector<Candidate> cands;
    std::unordered_set<std::string> seen_cands;

    auto add_cand = [&](const std::string &m_str, int p_idx, int mut_mask, const std::string &desc) {
        if (seen_cands.insert(m_str).second) {
            cands.push_back({m_str, p_idx, mut_mask, desc});
        }
    };

    for (size_t pi = 0; pi < parents.size(); ++pi) {
        const auto &P = parents[pi];
        TM base_m;
        parse_tm(P.machine, base_m);
        bool is_halts = (P.verdict.find("HALT") != std::string::npos && P.verdict.find("NEVER") == std::string::npos) || P.grade == "CHAMPION";
        bool has_H_class = (P.exhaustion.find(":H") != std::string::npos);

        std::vector<int> slots1 = P.z_slots;
        for (int s : P.r_slots) slots1.push_back(s);

        // 0. Include parent itself as control
        add_cand(P.machine, (int)pi, 0, "ORIG");

        // 1. 1-MUT on all slots in slots1
        for (int s : slots1) {
            int q = s / 2, c = s % 2;
            for (const auto &a : actions) {
                if (base_m.w[q][c] == a.w && base_m.d[q][c] == a.d && base_m.nx[q][c] == a.q) continue;
                TM m2 = base_m;
                m2.w[q][c] = a.w; m2.d[q][c] = a.d; m2.nx[q][c] = a.q;
                add_cand(format_tm(m2), (int)pi, (1 << s), "1MUT:" + slot_name(s) + "=" + a.str);
            }
        }

        // 2. HALT-REL: move --- to s in slots1, fill old_H with all 28 actions
        if (base_m.halt_slot >= 0) {
            int hq = base_m.halt_slot / 2, hc = base_m.halt_slot % 2;
            for (int s : slots1) {
                int sq = s / 2, sc = s % 2;
                for (const auto &a : actions) {
                    TM m2 = base_m;
                    m2.w[hq][hc] = a.w; m2.d[hq][hc] = a.d; m2.nx[hq][hc] = a.q;
                    m2.w[sq][sc] = 1; m2.d[sq][sc] = 1; m2.nx[sq][sc] = -1;
                    m2.halt_slot = s;
                    add_cand(format_tm(m2), (int)pi, (1 << base_m.halt_slot) | (1 << s),
                             "HREL:" + slot_name(base_m.halt_slot) + "=" + a.str + "," + slot_name(s) + "=---");
                }
            }
        }

        // 3. 2-MUT:
        //    - Every pair (s1, s2) in z_slots x z_slots (all <=11-transition engines!)
        //    - For HALTS / CHAMPION / has_H_class (X33-type parity-locked machines!), also z_slots x r_slots and r_slots x r_slots
        std::vector<std::pair<int, int>> pairs;
        for (size_t i = 0; i < P.z_slots.size(); ++i) {
            for (size_t j = i + 1; j < P.z_slots.size(); ++j) {
                pairs.push_back({P.z_slots[i], P.z_slots[j]});
            }
            if (is_halts || has_H_class) {
                for (size_t j = 0; j < P.r_slots.size(); ++j) {
                    pairs.push_back({P.z_slots[i], P.r_slots[j]});
                }
            }
        }
        if (is_halts) {
            for (size_t i = 0; i < P.r_slots.size(); ++i) {
                for (size_t j = i + 1; j < P.r_slots.size(); ++j) {
                    pairs.push_back({P.r_slots[i], P.r_slots[j]});
                }
            }
        }

        for (auto pr : pairs) {
            int s1 = pr.first, s2 = pr.second;
            int q1 = s1 / 2, c1 = s1 % 2;
            int q2 = s2 / 2, c2 = s2 % 2;
            for (const auto &a1 : actions) {
                if (base_m.w[q1][c1] == a1.w && base_m.d[q1][c1] == a1.d && base_m.nx[q1][c1] == a1.q) continue;
                for (const auto &a2 : actions) {
                    if (base_m.w[q2][c2] == a2.w && base_m.d[q2][c2] == a2.d && base_m.nx[q2][c2] == a2.q) continue;
                    TM m2 = base_m;
                    m2.w[q1][c1] = a1.w; m2.d[q1][c1] = a1.d; m2.nx[q1][c1] = a1.q;
                    m2.w[q2][c2] = a2.w; m2.d[q2][c2] = a2.d; m2.nx[q2][c2] = a2.q;
                    add_cand(format_tm(m2), (int)pi, (1 << s1) | (1 << s2),
                             "2MUT:" + slot_name(s1) + "=" + a1.str + "," + slot_name(s2) + "=" + a2.str);
                }
            }
        }
    }

    fprintf(stderr, "Generated %zu unique candidate machines. Evaluating on 2 threads...\n", cands.size());

    std::ofstream fout("sweep12_survivors.tsv");
    fout << "machine\tparent\tparent_grade\tparent_verdict\tmut_desc\thalted\tsteps\tones\tspan\tn_K\tmax_nd\tlast_nd\tn_rebuilds\tE0_pat\tE1_pat\tbest_cfg\tobs_O\ttemplate\n";
    std::mutex out_mtx;

    std::atomic<size_t> next_idx{0};
    std::atomic<size_t> kept_cnt{0};

    auto worker = [&]() {
        SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_IDLE);
        std::vector<unsigned char> tape(1 << 21, 0);  // 2M cells per thread
        std::vector<unsigned char> ptape(1 << 18, 0); // 256k cells per thread for E-probes
        while (true) {
            size_t idx = next_idx.fetch_add(1);
            if (idx >= cands.size()) break;
            const auto &c = cands[idx];
            const auto &p = parents[c.parent_idx];
            EvalResult r = evaluate_candidate(c, p, tape, ptape);
            if (r.keep) {
                kept_cnt.fetch_add(1);
                std::lock_guard<std::mutex> lock(out_mtx);
                fout << c.machine << "\t"
                     << p.machine << "\t"
                     << p.grade << "\t"
                     << p.verdict << "\t"
                     << c.mut_desc << "\t"
                     << (r.halted ? 1 : 0) << "\t"
                     << r.steps << "\t"
                     << r.ones << "\t"
                     << r.span << "\t"
                     << r.n_K << "\t"
                     << r.max_nd << "\t"
                     << r.last_nd << "\t"
                     << r.n_rebuilds << "\t"
                     << (r.E0_pat.empty() ? "-" : r.E0_pat) << "\t"
                     << (r.E1_pat.empty() ? "-" : r.E1_pat) << "\t"
                     << (r.best_ds_str.empty() ? "-" : r.best_ds_str) << "\t"
                     << (r.obs_O.empty() ? "-" : r.obs_O) << "\t"
                     << p.tmpl_str << "\n";
            }
            if ((idx + 1) % 10000 == 0) {
                fprintf(stderr, "  evaluated %zu / %zu (kept=%zu)\n", idx + 1, cands.size(), kept_cnt.load());
            }
        }
    };

    std::thread t1(worker);
    std::thread t2(worker);
    t1.join();
    t2.join();

    fout.close();
    fprintf(stderr, "Sweep complete! Wrote %zu survivors to sweep12_survivors.tsv\n", kept_cnt.load());
    return 0;
}
