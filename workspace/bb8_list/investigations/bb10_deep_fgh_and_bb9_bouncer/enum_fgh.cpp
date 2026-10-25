// enum_fgh.cpp: Ultra-fast C++ lazy-branching DFS over the 5-slot (F1=1LD) and 6-slot (F0,F1,G0,G1,H0,H1)
// space around the 9-transition core A:1RB0RA, B:1LC1LF, C:1RD0LB, D:1RA1LE, E1:0LC.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdarg>
#include <string>
#include <vector>
#include <algorithm>
#include <chrono>

static FILE *g_out = nullptr;
static void logp(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    vprintf(fmt, ap);
    va_end(ap);
    fflush(stdout);
    if (g_out) {
        va_start(ap, fmt);
        vfprintf(g_out, fmt, ap);
        va_end(ap);
        fflush(g_out);
    }
}

struct Tr {
    signed char w, d, q; // q = -1 if undefined
};

struct Machine {
    Tr t[10][2];
    Machine() {
        for (int s = 0; s < 10; ++s)
            for (int b = 0; b < 2; ++b)
                t[s][b] = {0, 0, -1};
        // Core 9 transitions: A:1RB0RA, B:1LC1LF, C:1RD0LB, D:1RA1LE, E1:0LC
        t[0][0] = {1, +1, 1}; // A0 = 1RB
        t[0][1] = {0, +1, 0}; // A1 = 0RA
        t[1][0] = {1, -1, 2}; // B0 = 1LC
        t[1][1] = {1, -1, 5}; // B1 = 1LF
        t[2][0] = {1, +1, 3}; // C0 = 1RD
        t[2][1] = {0, -1, 1}; // C1 = 0LB
        t[3][0] = {1, +1, 0}; // D0 = 1RA
        t[3][1] = {1, -1, 4}; // D1 = 1LE
        t[4][1] = {0, -1, 2}; // E1 = 0LC
    }
};

std::string fmt_machine(const Machine &m, int nstates = 8) {
    std::string s;
    for (int q = 0; q < nstates; ++q) {
        if (q > 0) s += '_';
        for (int b = 0; b < 2; ++b) {
            if (m.t[q][b].q < 0) {
                s += "---";
            } else {
                s += char('0' + m.t[q][b].w);
                s += (m.t[q][b].d > 0 ? 'R' : 'L');
                s += char('A' + m.t[q][b].q);
            }
        }
    }
    return s;
}

static void append_D(std::vector<unsigned char> &w, int m) {
    for (int i = 0; i < m; ++i) {
        w.push_back(1);
        w.push_back(0);
    }
    w.push_back(1);
}

enum RunStatus {
    ST_BRANCH,
    ST_HALT,
    ST_TIME,
    ST_BFORM
};

struct RunResult {
    RunStatus status;
    int br_q, br_b;
    int steps;
    std::vector<int> L;
    int A;
};

static bool parse_bform(const unsigned char *t, int lo, int hi, int head, int form_type, std::vector<int> &L_out, int &A_out) {
    if (head <= lo || t[head] != 0) return false;
    for (int i = head; i <= hi; ++i)
        if (t[i] != 0) return false;
    int l1 = lo;
    while (l1 < head && t[l1] == 0) ++l1;
    if (l1 >= head) return false;

    if (form_type == 0) {
        if (t[head - 1] != 1) return false;
        std::vector<int> rev_toks;
        int p = head - 1;
        while (p >= l1) {
            if (t[p] != 1) return false;
            int m = 0;
            --p;
            while (p - 1 >= l1 && t[p] == 0 && t[p - 1] == 1) {
                ++m;
                p -= 2;
            }
            rev_toks.push_back(m);
        }
        if (rev_toks.size() < 3 || rev_toks[1] != 0) return false;
        A_out = rev_toks[0];
        L_out.clear();
        for (int i = (int)rev_toks.size() - 1; i >= 2; --i)
            L_out.push_back(rev_toks[i]);
        return true;
    } else {
        static const unsigned char suf[9] = {1, 1, 0, 1, 0, 1, 0, 1, 0};
        if (head - 9 < l1) return false;
        for (int i = 0; i < 9; ++i)
            if (t[head - 9 + i] != suf[i]) return false;
        std::vector<int> rev_toks;
        int p = head - 9;
        while (p >= l1) {
            if (t[p] != 1) return false;
            int m = 0;
            --p;
            while (p - 1 >= l1 && t[p] == 0 && t[p - 1] == 1) {
                ++m;
                p -= 2;
            }
            rev_toks.push_back(m);
        }
        if (rev_toks.size() < 2) return false;
        A_out = rev_toks[0];
        L_out.clear();
        for (int i = (int)rev_toks.size() - 1; i >= 1; --i)
            L_out.push_back(rev_toks[i]);
        return true;
    }
}

static std::vector<unsigned char> make_word(const std::vector<int> &L, int A, int form_type) {
    std::vector<unsigned char> w;
    for (int x : L) append_D(w, x);
    if (form_type == 0) {
        append_D(w, 0);
        append_D(w, A);
    } else {
        append_D(w, A);
        for (int i = 0; i < 4; ++i) {
            w.push_back(1);
            w.push_back(0);
        }
    }
    return w;
}

static RunResult run_sim(const Machine &m, const std::vector<unsigned char> &word, int start_q, int canon_q, int form_type, int max_steps, int left_margin = 2, int right_margin = 32) {
    static unsigned char tape[4096];
    const int OFF = 512;
    int len = (int)word.size();
    std::memset(tape + OFF - left_margin - 4, 0, len + left_margin + right_margin + 16);
    for (int i = 0; i < len; ++i) tape[OFF + i] = word[i];
    int h = OFF + len;
    int lo = OFF, hi = OFF + len;
    int min_h = OFF - left_margin;
    int max_h = OFF + len + right_margin;
    int q = start_q;
    RunResult res;
    res.steps = 0;
    while (res.steps < max_steps) {
        int b = tape[h];
        const Tr &tr = m.t[q][b];
        if (tr.q < 0) {
            res.status = ST_BRANCH;
            res.br_q = q;
            res.br_b = b;
            return res;
        }
        tape[h] = tr.w;
        h += tr.d;
        q = tr.q;
        ++res.steps;
        if (h < lo) {
            if (h < min_h) { res.status = ST_TIME; return res; }
            lo = h;
        }
        if (h > hi) {
            if (h > max_h) { res.status = ST_TIME; return res; }
            hi = h;
        }
        if (q == canon_q && tape[h] == 0) {
            int check_bit = (form_type == 0) ? tape[h - 1] : tape[h - 2];
            if (check_bit == 1) {
                if (parse_bform(tape, lo, hi, h, form_type, res.L, res.A)) {
                    res.status = ST_BFORM;
                    return res;
                }
            }
        }
    }
    res.status = ST_TIME;
    return res;
}

struct StartupInfo {
    bool found_list;
    int steps_at_list;
    int d0;
    int n_ones;
    int A0;
    int max_ones_run;
    int e0_steps;
};

static StartupInfo check_blank_startup(const Machine &m, int canon_q, int form_type, int max_steps = 25000) {
    static unsigned char tape[16384];
    const int OFF = 8192;
    std::memset(tape + OFF - 2048, 0, 4096);
    int h = OFF, lo = OFF, hi = OFF, q = 0;
    StartupInfo info = {false, 0, 0, 0, 0, 0, -1};
    std::vector<int> L;
    int A;
    for (int s = 1; s <= max_steps; ++s) {
        int b = tape[h];
        const Tr &tr = m.t[q][b];
        if (tr.q < 0) {
            if (q == 4 && b == 0) info.e0_steps = s;
            break;
        }
        tape[h] = tr.w;
        h += tr.d;
        q = tr.q;
        if (h < lo) {
            lo = h;
            if (lo < OFF - 2000) break;
        }
        if (h > hi) {
            hi = h;
            if (hi > OFF + 2000) break;
        }
        if (q == canon_q && tape[h] == 0) {
            int check_bit = (form_type == 0) ? tape[h - 1] : tape[h - 2];
            if (check_bit == 1 && parse_bform(tape, lo, hi, h, form_type, L, A)) {
                if (form_type == 0 && L.size() >= 6) {
                    bool all1 = true;
                    for (size_t i = 1; i < L.size(); ++i)
                        if (L[i] != 1) { all1 = false; break; }
                    if (all1) {
                        int n1 = (int)L.size() - 1;
                        if (n1 > info.max_ones_run) info.max_ones_run = n1;
                        if (!info.found_list && n1 >= 6) {
                            info.found_list = true;
                            info.steps_at_list = s;
                            info.d0 = L[0];
                            info.n_ones = n1;
                            info.A0 = A;
                            if (n1 >= 20) return info;
                        }
                    }
                } else if (form_type == 1 && L.size() >= 7) {
                    bool all1 = true;
                    for (size_t i = 1; i + 1 < L.size(); ++i)
                        if (L[i] != 1) { all1 = false; break; }
                    if (all1) {
                        int n1 = (int)L.size() - 1;
                        if (L.back() != 1) n1 = (int)L.size() - 2;
                        if (n1 > info.max_ones_run) info.max_ones_run = n1;
                        if (!info.found_list && n1 >= 6) {
                            info.found_list = true;
                            info.steps_at_list = s;
                            info.d0 = L[0];
                            info.n_ones = n1;
                            info.A0 = A;
                            if (n1 >= 20) return info;
                        }
                    }
                }
            }
        }
    }
    return info;
}

long long g_r1_pass = 0;
long long g_r2_pass = 0;
long long g_full_r12_pass = 0;

struct Hit {
    std::string mstr;
    char cs;
    int form_type;
    int r1_A1, r1_A2;
    StartupInfo st;
};
std::vector<Hit> g_hits;

static void branch_startup_dfs(Machine &mc, int canon_q, int form_type, int max_state_allowed, int r1_A1, int r1_A2) {
    unsigned char tape[4096];
    const int OFF = 2048;
    std::memset(tape, 0, sizeof(tape));
    int h = OFF, lo = OFF, hi = OFF, q = 0;
    int hit_q = -1, hit_b = -1;
    for (int s = 1; s <= 12000; ++s) {
        int b = tape[h];
        const Tr &tr = mc.t[q][b];
        if (tr.q < 0) {
            if (q >= 5 && q <= max_state_allowed) {
                hit_q = q; hit_b = b;
            }
            break;
        }
        tape[h] = tr.w;
        h += tr.d;
        q = tr.q;
        if (h < lo) { lo = h; if (lo < 16) break; }
        if (h > hi) { hi = h; if (hi >= 4080) break; }
    }
    if (hit_q >= 5) {
        int max_used = std::max(5, canon_q);
        for (int qq = 5; qq <= max_state_allowed; ++qq)
            for (int bb = 0; bb < 2; ++bb)
                if (mc.t[qq][bb].q > max_used)
                    max_used = mc.t[qq][bb].q;
        int lim_q = std::min(max_state_allowed, max_used + 1);
        for (int tw = 0; tw < 2; ++tw) {
            for (int td : {-1, +1}) {
                for (int tq = 0; tq <= lim_q; ++tq) {
                    mc.t[hit_q][hit_b] = {(signed char)tw, (signed char)td, (signed char)tq};
                    branch_startup_dfs(mc, canon_q, form_type, max_state_allowed, r1_A1, r1_A2);
                }
            }
        }
        mc.t[hit_q][hit_b] = {0, 0, -1};
        return;
    }
    StartupInfo st = check_blank_startup(mc, canon_q, form_type, 25000);
    if (st.found_list || st.max_ones_run >= 6) {
        g_hits.push_back({fmt_machine(mc, max_state_allowed + 1), char('A' + canon_q), form_type, r1_A1, r1_A2, st});
    }
}

static void dfs_r1_r2(Machine &m, int canon_q, int form_type, int stage, int max_state_allowed,
                      const std::vector<unsigned char> &w_r1,
                      const std::vector<unsigned char> &w_r2) {
    const auto &w = (stage == 0) ? w_r1 : w_r2;
    int max_s = (stage == 0) ? 250 : 320;
    RunResult rr = run_sim(m, w, canon_q, canon_q, form_type, max_s, 1, 28);

    if (rr.status == ST_BRANCH) {
        int bq = rr.br_q, bb = rr.br_b;
        if (bq == 4 && bb == 0) return;
        if (bq < 5 || bq > max_state_allowed) return;

        int max_used = std::max(5, canon_q);
        for (int q = 5; q <= max_state_allowed; ++q)
            for (int b = 0; b < 2; ++b)
                if (m.t[q][b].q > max_used)
                    max_used = m.t[q][b].q;
        int lim_q = std::min(max_state_allowed, max_used + 1);

        for (int tw = 0; tw < 2; ++tw) {
            for (int td : {-1, +1}) {
                for (int tq = 0; tq <= lim_q; ++tq) {
                    m.t[bq][bb] = {(signed char)tw, (signed char)td, (signed char)tq};
                    dfs_r1_r2(m, canon_q, form_type, stage, max_state_allowed, w_r1, w_r2);
                }
            }
        }
        m.t[bq][bb] = {0, 0, -1};
        return;
    }

    if (rr.status != ST_BFORM) return;

    if (stage == 0) {
        if (rr.L.size() == 2 && rr.L[0] == 2 && rr.L[1] == 1 && rr.A >= 3) {
            ++g_r1_pass;
            dfs_r1_r2(m, canon_q, form_type, 1, max_state_allowed, w_r1, w_r2);
        }
    } else {
        if (rr.L.size() == 4 && rr.L[0] == 2 && rr.L[1] == 1 && rr.L[2] >= 3 && rr.L[3] == 1) {
            ++g_r2_pass;
            int E = (form_type == 0) ? 1 : 0;
            int A1 = run_sim(m, w_r1, canon_q, canon_q, form_type, 250, 1, 28).A;
            auto w_r1_2 = make_word({2, 7}, 4 - E, form_type);
            RunResult rr1_2 = run_sim(m, w_r1_2, canon_q, canon_q, form_type, 1500, 1, 48);
            if (rr1_2.status != ST_BFORM || rr1_2.L != std::vector<int>{2, 4} || rr1_2.A <= A1) return;

            auto w_r2_2 = make_word({2, 6, 1, 1, 1}, 4 - E, form_type);
            RunResult rr2_2 = run_sim(m, w_r2_2, canon_q, canon_q, form_type, 1500, 1, 48);
            if (rr2_2.status != ST_BFORM || rr2_2.L.size() != 5 || rr2_2.L[0] != 2 || rr2_2.L[1] != 3 || rr2_2.L[3] != 1 || rr2_2.L[4] != 1) return;

            ++g_full_r12_pass;
            branch_startup_dfs(m, canon_q, form_type, max_state_allowed, A1, rr1_2.A);
        }
    }
}

// Part B: Incremental Blank-Tape Lazy DFS
long long g_blank_leaves = 0;
long long g_blank_survived = 0;
long long g_blank_e0 = 0;

struct BlankHit {
    std::string mstr;
    int max_101_run;
    int steps;
    bool hit_e0;
    int ones_at_end;
    int width_at_end;
};
std::vector<BlankHit> g_blank_hits;

static int count_max_101_tokens(const unsigned char *tape, int lo, int hi) {
    int best = 0;
    for (int rem = 0; rem < 3; ++rem) {
        int cur = 0;
        for (int i = lo + rem; i + 2 <= hi; i += 3) {
            if (tape[i] == 1 && tape[i + 1] == 0 && tape[i + 2] == 1) {
                ++cur;
                if (cur > best) best = cur;
            } else {
                cur = 0;
            }
        }
    }
    return best;
}

static void dfs_blank_inc(Machine &m, int max_state_allowed, unsigned char *tape, int lo, int hi, int h, int q, int steps, int max_steps) {
    const int OFF = 4096;
    int init_lo = lo, init_hi = hi;
    while (steps < max_steps) {
        int b = tape[h];
        const Tr &tr = m.t[q][b];
        if (tr.q < 0) {
            if (q >= 5 && q <= max_state_allowed) {
                int max_used = 5;
                for (int qq = 5; qq <= max_state_allowed; ++qq)
                    for (int bb = 0; bb < 2; ++bb)
                        if (m.t[qq][bb].q > max_used)
                            max_used = m.t[qq][bb].q;
                int lim_q = std::min(max_state_allowed, max_used + 1);

                int span = hi - lo + 1;
                std::vector<unsigned char> saved(tape + lo, tape + hi + 1);
                int saved_lo = lo, saved_hi = hi, saved_h = h, saved_q = q, saved_steps = steps;

                for (int tw = 0; tw < 2; ++tw) {
                    for (int td : {-1, +1}) {
                        for (int tq = 0; tq <= lim_q; ++tq) {
                            m.t[saved_q][b] = {(signed char)tw, (signed char)td, (signed char)tq};
                            dfs_blank_inc(m, max_state_allowed, tape, saved_lo, saved_hi, saved_h, saved_q, saved_steps, max_steps);
                            std::memcpy(tape + saved_lo, saved.data(), span);
                        }
                    }
                }
                m.t[saved_q][b] = {0, 0, -1};
                if (lo < init_lo) std::memset(tape + lo, 0, init_lo - lo);
                if (hi > init_hi) std::memset(tape + init_hi + 1, 0, hi - init_hi);
                return;
            }
            // Hit E0 = ---
            ++g_blank_leaves;
            ++g_blank_e0;
            if (steps >= 400) {
                int c101 = count_max_101_tokens(tape, lo, hi);
                if (c101 >= 10) {
                    int ones = 0;
                    for (int i = lo; i <= hi; ++i) ones += tape[i];
                    g_blank_hits.push_back({fmt_machine(m, 8), c101, steps, true, ones, hi - lo + 1});
                }
            }
            if (lo < init_lo) std::memset(tape + lo, 0, init_lo - lo);
            if (hi > init_hi) std::memset(tape + init_hi + 1, 0, hi - init_hi);
            return;
        }
        tape[h] = tr.w;
        h += tr.d;
        q = tr.q;
        ++steps;
        if (h < lo) {
            lo = h;
            if (lo < OFF - 2000) break;
            tape[lo] = 0;
        }
        if (h > hi) {
            hi = h;
            if (hi > OFF + 2000) break;
            tape[hi] = 0;
        }
    }
    ++g_blank_leaves;
    ++g_blank_survived;
    int c101 = count_max_101_tokens(tape, lo, hi);
    if (c101 >= 6) {
        int max_c101 = c101;
        bool hit_e0_later = false;
        while (steps < 12000) {
            int b = tape[h];
            const Tr &tr = m.t[q][b];
            if (tr.q < 0) {
                if (q == 4 && b == 0) hit_e0_later = true;
                break;
            }
            tape[h] = tr.w;
            h += tr.d;
            q = tr.q;
            ++steps;
            if (h < lo) { lo = h; if (lo < OFF - 2000) break; tape[lo] = 0; }
            if (h > hi) { hi = h; if (hi > OFF + 2000) break; tape[hi] = 0; }
            if ((steps & 511) == 0) {
                int cc = count_max_101_tokens(tape, lo, hi);
                if (cc > max_c101) max_c101 = cc;
            }
        }
        int cc = count_max_101_tokens(tape, lo, hi);
        if (cc > max_c101) max_c101 = cc;
        if (max_c101 >= 10) {
            int ones = 0;
            for (int i = lo; i <= hi; ++i) ones += tape[i];
            g_blank_hits.push_back({fmt_machine(m, 8), max_c101, steps, hit_e0_later, ones, hi - lo + 1});
        }
    }
    if (lo < init_lo) std::memset(tape + lo, 0, init_lo - lo);
    if (hi > init_hi) std::memset(tape + init_hi + 1, 0, hi - init_hi);
}

int main(int argc, char **argv) {
    g_out = fopen("C:\\Users\\jeffr\\Downloads\\bb8\\bb8_list\\investigations\\bb10_deep_fgh_and_bb9_bouncer\\enum_fgh_out.txt", "w");
    auto t0 = std::chrono::steady_clock::now();

    logp("=== PART A0: 5-slot (F1=1LD fixed, F0,G0,G1,H0,H1 free) R1/R2-first search over A..H (8 states) ===\n");
    for (int form_type = 0; form_type <= 1; ++form_type) {
        int E = (form_type == 0) ? 1 : 0;
        auto w_r1 = make_word({2, 4}, E, form_type);
        auto w_r2 = make_word({2, 4, 1, 1}, E, form_type);
        for (int cs : {5, 6, 7}) {
            Machine m;
            m.t[5][1] = {1, -1, 3}; // F1 = 1LD
            dfs_r1_r2(m, cs, form_type, 0, 7, w_r1, w_r2);
        }
    }
    auto t0b = std::chrono::steady_clock::now();
    logp("Done 5-slot 8-state R1/R2 search in %.2fs: R1_pass=%lld, R2_pass=%lld, full_R12=%lld, startup_hits=%zu\n",
         std::chrono::duration<double>(t0b - t0).count(), g_r1_pass, g_r2_pass, g_full_r12_pass, g_hits.size());
    for (const auto &h : g_hits) {
        logp("  [HIT-5-8] %s  cs=%c form=%d R1:(%d->%d) found=%d steps=%d d0=%d n=%d A0=%d max1=%d e0=%d\n",
             h.mstr.c_str(), h.cs, h.form_type, h.r1_A1, h.r1_A2,
             h.st.found_list ? 1 : 0, h.st.steps_at_list, h.st.d0, h.st.n_ones, h.st.A0, h.st.max_ones_run, h.st.e0_steps);
    }

    g_r1_pass = g_r2_pass = g_full_r12_pass = 0;
    g_hits.clear();
    logp("\n=== PART A1: Exhaustive 6-slot (F0,F1,G0,G1,H0,H1 all free) R1/R2-first search over A..H (8 states) ===\n");
    for (int form_type = 0; form_type <= 1; ++form_type) {
        int E = (form_type == 0) ? 1 : 0;
        auto w_r1 = make_word({2, 4}, E, form_type);
        auto w_r2 = make_word({2, 4, 1, 1}, E, form_type);
        for (int cs : {5, 6, 7}) {
            Machine m;
            dfs_r1_r2(m, cs, form_type, 0, 7, w_r1, w_r2);
        }
    }
    auto t1 = std::chrono::steady_clock::now();
    logp("Done 6-slot 8-state R1/R2 search in %.2fs: R1_pass=%lld, R2_pass=%lld, full_R12=%lld, startup_hits=%zu\n",
         std::chrono::duration<double>(t1 - t0b).count(), g_r1_pass, g_r2_pass, g_full_r12_pass, g_hits.size());
    for (const auto &h : g_hits) {
        logp("  [HIT-6-8] %s  cs=%c form=%d R1:(%d->%d) found=%d steps=%d d0=%d n=%d A0=%d max1=%d e0=%d\n",
             h.mstr.c_str(), h.cs, h.form_type, h.r1_A1, h.r1_A2,
             h.st.found_list ? 1 : 0, h.st.steps_at_list, h.st.d0, h.st.n_ones, h.st.A0, h.st.max_ones_run, h.st.e0_steps);
    }

    logp("\n=== PART B1: Exhaustive 5-slot (F1=1LD fixed, F0,G0,G1,H0,H1 free) Blank-Tape Lazy DFS ===\n");
    {
        static unsigned char tape[8192];
        std::memset(tape, 0, sizeof(tape));
        Machine m;
        m.t[5][1] = {1, -1, 3}; // F1 = 1LD
        g_blank_leaves = g_blank_survived = g_blank_e0 = 0;
        g_blank_hits.clear();
        dfs_blank_inc(m, 7, tape, 4096, 4096, 4096, 0, 0, 2000);
        auto t2 = std::chrono::steady_clock::now();
        logp("Done 5-slot Blank-Tape DFS in %.2fs: leaves=%lld, survived=%lld, hit_e0=%lld, hits(n>=10)=%zu\n",
             std::chrono::duration<double>(t2 - t1).count(), g_blank_leaves, g_blank_survived, g_blank_e0, g_blank_hits.size());
        for (const auto &bh : g_blank_hits) {
            logp("  [BLANK-5] %s  max_101=%d steps=%d hit_e0=%d ones=%d width=%d\n",
                 bh.mstr.c_str(), bh.max_101_run, bh.steps, bh.hit_e0 ? 1 : 0, bh.ones_at_end, bh.width_at_end);
        }
    }

    auto t3 = std::chrono::steady_clock::now();
    logp("\n=== PART A2: Exhaustive 5-slot + I (F1=1LD, F0,G0,G1,H0,H1,I0,I1 free over A..I) R1/R2-first search ===\n");
    g_r1_pass = g_r2_pass = g_full_r12_pass = 0;
    g_hits.clear();
    for (int form_type = 0; form_type <= 1; ++form_type) {
        int E = (form_type == 0) ? 1 : 0;
        auto w_r1 = make_word({2, 4}, E, form_type);
        auto w_r2 = make_word({2, 4, 1, 1}, E, form_type);
        for (int cs : {5, 6, 7}) {
            Machine m;
            m.t[5][1] = {1, -1, 3}; // F1 = 1LD
            dfs_r1_r2(m, cs, form_type, 0, 8, w_r1, w_r2);
        }
    }
    auto t4 = std::chrono::steady_clock::now();
    logp("Done 9-state (F1=1LD) R1/R2 search in %.2fs: R1_pass=%lld, R2_pass=%lld, full_R12=%lld, startup_hits=%zu\n",
         std::chrono::duration<double>(t4 - t3).count(), g_r1_pass, g_r2_pass, g_full_r12_pass, g_hits.size());
    for (const auto &h : g_hits) {
        logp("  [HIT-9] %s  cs=%c form=%d R1:(%d->%d) found=%d steps=%d d0=%d n=%d A0=%d max1=%d e0=%d\n",
             h.mstr.c_str(), h.cs, h.form_type, h.r1_A1, h.r1_A2,
             h.st.found_list ? 1 : 0, h.st.steps_at_list, h.st.d0, h.st.n_ones, h.st.A0, h.st.max_ones_run, h.st.e0_steps);
    }

    if (g_out) fclose(g_out);
    return 0;
}
