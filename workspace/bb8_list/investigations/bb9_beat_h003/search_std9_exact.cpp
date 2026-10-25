#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>
#include <windows.h>

struct Trans {
    int w;   // 0 or 1; -1 for assigned '---' (HALT); -2 for UNASSIGNED
    int dir; // -1 for L, +1 for R
    int nxt; // 0..8
};

Trans base_tr[18];
bool g_is_232 = false;

void init_base(bool is_232) {
    g_is_232 = is_232;
    const char* s = is_232
        ? "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB_------_------"
        : "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB_------_------";
    for (int q = 0; q < 9; ++q) {
        for (int b = 0; b < 2; ++b) {
            const char* p = s + q * 7 + b * 3;
            if (p[0] == '-') {
                base_tr[2 * q + b] = {-2, 0, 0}; // UNASSIGNED
            } else {
                base_tr[2 * q + b] = {p[0] - '0', (p[1] == 'R') ? 1 : -1, p[2] - 'A'};
            }
        }
    }
}

struct KResult {
    char kind; // 'K' (clean K), 'k' (collapsed K*), 'H' (halt), 'h' (collapsed H*), 'U' (unassigned), 'u' (collapsed U*), 'T' (timeout)
    long long step;
    int slot;  // slot hit for H/U
    int k_len;
    int a_val;
    int parity_I;
    int d_inner1;
    int d_inner2;
    int macro_clears;
    int iters;
};

static const int SZ = 524288;
static const int OFFSET = 320000;
static const int MIN_SAFE_H = 4096;
static unsigned char g_tape[SZ];

bool check_K_fast(const unsigned char* tape, int lo, int hi, int h, int q, KResult& res, long long step, bool collapsed, int macro_clears, int iters) {
    if (q != 4 || tape[h] != 0) return false;
    if (lo > hi || h != lo - 1) return false;
    if (h + 4 > hi) return false;
    if (tape[h + 1] != 1 || tape[h + 2] != 0 || tape[h + 3] != 0) return false;
    if (tape[hi] != 1 || tape[hi - 1] != 0 || tape[hi - 2] != 0) return false;

    int pos = h + 4;
    int num_runs = 0;
    int first_run = -1;
    int d1 = -1, d2 = -1;
    long long sum_vals = 0;
    while (pos <= hi - 1) {
        int ones = 0;
        while (pos <= hi - 1 && tape[pos] == 1) {
            ones++;
            pos++;
        }
        if (ones % 2 != 0) return false;
        if (pos + 1 > hi - 1 || tape[pos] != 0 || tape[pos + 1] != 0) return false;
        pos += 2;
        int val = ones / 2;
        sum_vals += val;
        if (num_runs == 0) first_run = val;
        else if (num_runs == 1) d1 = val;
        else if (num_runs == 2) d2 = val;
        num_runs++;
    }
    if (num_runs < 2) return false;
    int k_len = num_runs - 1;
    int a_val = first_run;
    int parity_I = (int)(sum_vals % 2);
    res = {collapsed ? 'k' : 'K', step, -1, k_len, a_val, parity_I, d1, d2, macro_clears, iters};
    return true;
}

struct ClearGuard {
    unsigned char* tape;
    int& lo;
    int& hi;
    ~ClearGuard() {
        int c_lo = (lo < 0) ? 0 : lo;
        int c_hi = (hi >= SZ) ? (SZ - 1) : hi;
        if (c_lo <= c_hi) {
            memset(tape + c_lo, 0, c_hi - c_lo + 1);
        }
    }
};

KResult run_c1_sim(const Trans* tr, int k, int N, int max_iters, bool allow_collapse, std::vector<int>* out_ones = nullptr, int* out_h = nullptr, int* out_q = nullptr) {
    unsigned char* tape = g_tape;
    int pos = OFFSET;
    int lo = pos;
    for (int i = 0; i < 2 * k - 1; ++i) {
        tape[pos++] = 1;
        tape[pos++] = 0;
    }
    tape[pos++] = 1;
    tape[pos++] = 1;
    tape[pos++] = 0;
    tape[pos++] = 0;
    tape[pos++] = 1;
    int h = pos;
    tape[pos++] = 1;
    tape[pos++] = 1;
    tape[pos++] = 0;
    tape[pos++] = 0;
    for (int i = 0; i < N; ++i) {
        tape[pos++] = 1;
        tape[pos++] = 1;
        tape[pos++] = 0;
        tape[pos++] = 0;
    }
    tape[pos++] = 1;
    int hi = pos;
    int min_touched = lo - 4;
    int max_touched = hi + 4;
    ClearGuard guard{tape, min_touched, max_touched};

    int q = 2; // state C
    long long step = 0;
    int iters = 0;
    bool collapsed = false;
    int macro_clears = 0;
    long long d_const = g_is_232 ? 58LL : 56LL;

    while (iters < max_iters) {
        iters++;
        if (q == 4 && tape[h] == 0) {
            while (lo <= hi && tape[lo] == 0) lo++;
            while (hi >= lo && tape[hi] == 0) hi--;
            if (lo <= hi && h == lo - 1) {
                KResult kr;
                if (check_K_fast(tape, lo, hi, h, q, kr, step, collapsed, macro_clears, iters)) {
                    int min_valid_len = N - 2 * k - 3;
                    if (min_valid_len < 2) min_valid_len = 2;
                    if (kr.k_len >= min_valid_len) {
                        if (out_ones) {
                            out_ones->clear();
                            for (int i = lo; i <= hi; ++i) if (tape[i]) out_ones->push_back(i - OFFSET);
                        }
                        if (out_h) *out_h = h - OFFSET;
                        if (out_q) *out_q = q;
                        return kr;
                    }
                }

                // Macro 4: Multi-Digit Ackermann Tower Collapse when h == lo - 1 (no 1s on left)
                if (allow_collapse && h + 4 <= hi && tape[h + 1] == 1 && tape[h + 2] == 0 && tape[h + 3] == 0) {
                    int pos = h + 4;
                    int even_count = 0;
                    int first_even_val = 0;
                    bool has_nonzero_even_digit = false;
                    long long sum_even = 0;
                    int odd_pos = -1;
                    int odd_len = -1;
                    while (pos <= hi) {
                        int ones = 0;
                        int p_start = pos;
                        while (pos <= hi && tape[pos] == 1) {
                            ones++;
                            pos++;
                        }
                        if (ones % 2 == 1) {
                            odd_pos = p_start;
                            odd_len = ones;
                            break;
                        }
                        if (pos + 1 <= hi && tape[pos] == 0 && tape[pos + 1] == 0) {
                            int val = ones / 2;
                            if (even_count == 0) first_even_val = val;
                            else if (val > 0) has_nonzero_even_digit = true;
                            sum_even += val;
                            even_count++;
                            pos += 2;
                        } else {
                            break;
                        }
                    }
                    if (even_count >= 1 && odd_pos != -1) {
                        int s_digits = even_count - 1;
                        int d_odd = odd_len / 2;
                        int m0 = 0;
                        int p_scan = h + 4 + 2 * first_even_val + 2;
                        while (m0 < s_digits && tape[p_scan] == 0 && tape[p_scan + 1] == 0) { m0++; p_scan += 2; }
                        if (first_even_val >= 2 && (has_nonzero_even_digit || d_odd >= 1) && 3 * first_even_val + 3 >= m0) {
                            collapsed = true;
                            macro_clears++;
                            int total_parity = (int)((sum_even + d_odd) % 2);
                            int base_u = 6 * ((s_digits + 10) / 6 + 1);
                            if (base_u < 60) base_u = 60;
                            if (base_u % 12 != 0) base_u += 6;
                            int u_cap = base_u + 6 * total_parity;
                            int rem_one_pos = odd_pos + 2 * d_odd;
                            int zeros_span = 2 * s_digits + 2;
                            int new_h = rem_one_pos - zeros_span - u_cap - 4;
                            if (new_h >= MIN_SAFE_H) {
                                memset(tape + lo, 0, rem_one_pos - lo);
                                h = new_h;
                                tape[h + 1] = 1;
                                tape[h + 2] = 0;
                                tape[h + 3] = 0;
                                memset(tape + h + 4, 1, (size_t)u_cap);
                                lo = h + 1;
                                if (lo < min_touched) min_touched = lo;
                                step += 1000000000LL;
                                continue;
                            }
                        }
                    }
                }
            }

            int zeros_left;
            if (h < lo) {
                zeros_left = h - MIN_SAFE_H;
            } else {
                int p_left = h - 1;
                while (tape[p_left] == 0) p_left--;
                zeros_left = h - 1 - p_left;
            }

            // Macro 1: General-u Chained Rule D (m = 0) and Borrow B_m (m >= 1)
            if (tape[h + 1] == 1 && tape[h + 2] == 0 && tape[h + 3] == 0) {
                int p = h + 4;
                while (tape[p] == 1) p++;
                long long u = p - (h + 4);
                int pz = p;
                while (pz <= hi + 2 && tape[pz] == 0) pz++;
                int zeros = pz - p;
                if (zeros == 2 && tape[pz] == 1 && tape[pz + 1] == 1) {
                    int pr = pz;
                    while (tape[pr] == 1) pr++;
                    int r = pr - pz;
                    if (zeros_left >= 2 * u + 4 && h - (2 * u + 4) >= MIN_SAFE_H) {
                        while (r >= 2 && zeros_left >= 2 * u + 4 && h - (2 * u + 4) >= MIN_SAFE_H && !(allow_collapse && h < lo && u >= 60)) {
                            int shift = (int)(2 * u + 4);
                            step += 3LL * u * u + 33LL * u + d_const;
                            h -= shift;
                            zeros_left -= shift;
                            u = 3 * u + 6;
                            r -= 2;
                        }
                        if (allow_collapse && r >= 2 && h < lo && (u >= 60 || h - (2 * u + 4) < MIN_SAFE_H)) {
                            collapsed = true;
                            long long rem_dec = r / 2;
                            r = r % 2;
                            long long u_cap = (u % 2 == 0) ? (60 + 6 * (((u / 2) + rem_dec) % 2)) : (69 - 6 * ((u / 2) % 2));
                            int new_h = (pr - r - 2) - (int)u_cap - 4;
                            if (lo < pr - r) {
                                memset(tape + lo, 0, (pr - r) - lo);
                            }
                            h = new_h;
                            u = u_cap;
                            lo = h + 1;
                            macro_clears++;
                        }
                        tape[h + 1] = 1;
                        tape[h + 2] = 0;
                        tape[h + 3] = 0;
                        memset(tape + h + 4, 1, (size_t)u);
                        tape[h + 4 + u] = 0;
                        tape[h + 5 + u] = 0;
                        if (h + 1 < lo) lo = h + 1;
                        if (lo < min_touched) min_touched = lo;
                        if (h + 5 + (int)u > hi) hi = h + 5 + (int)u;
                        if (hi > max_touched) max_touched = hi;
                        continue;
                    }
                } else if (zeros >= 4 && zeros % 2 == 0 && tape[pz] == 1 && tape[pz + 1] == 1) {
                    long long m = (zeros / 2) - 1;
                    if (zeros_left >= 2 * u + 4 && 3 * u + 6 >= 2 * m && h - (2 * u + 4) >= MIN_SAFE_H) {
                        int shift = (int)(2 * u + 4);
                        step += 3LL * u * u + 33LL * u + 56LL + 12LL * u * m + 22LL * m - 4LL * m * m + (g_is_232 ? 2LL * (m + 1) : 0LL);
                        h -= shift;
                        tape[h + 1] = 1;
                        tape[h + 2] = 0;
                        tape[h + 3] = 0;
                        int wpos = h + 4;
                        for (int j = 0; j < m; ++j) {
                            tape[wpos] = 1; tape[wpos + 1] = 1; tape[wpos + 2] = 0; tape[wpos + 3] = 0;
                            wpos += 4;
                        }
                        int rem_ones = (int)(3 * u + 6 - 2 * m);
                        memset(tape + wpos, 1, (size_t)rem_ones);
                        wpos += rem_ones;
                        tape[wpos] = 0;
                        tape[wpos + 1] = 0;
                        if (h + 1 < lo) lo = h + 1;
                        if (lo < min_touched) min_touched = lo;
                        if (wpos + 1 > hi) hi = wpos + 1;
                        if (hi > max_touched) max_touched = hi;
                        macro_clears++;
                        continue;
                    }
                }
            }

            // Macro 2: Expand E0 (0^(2c) [E0] 1^m 00 1^n -> [E0] 1^(m+3c) 00 1^(n-c))
            if (zeros_left >= 2 && tape[h + 1] == 1) {
                int p = h + 1;
                while (tape[p] == 1) p++;
                long long m = p - (h + 1);
                if (tape[p] == 0 && tape[p + 1] == 0 && tape[p + 2] == 1) {
                    int p2 = p + 2;
                    while (tape[p2] == 1) p2++;
                    long long n = p2 - (p + 2);
                    long long c = (n < (zeros_left / 2)) ? n : (zeros_left / 2);
                    if (c > 0 && h - 2 * c >= MIN_SAFE_H && h + m + c + 2 < SZ - MIN_SAFE_H) {
                        int h_new = h - (int)(2 * c);
                        memset(tape + h_new + 1, 1, (size_t)(m + 3 * c));
                        tape[h + m + c + 1] = 0;
                        tape[h + m + c + 2] = 0;
                        h = h_new;
                        if (h + 1 < lo) lo = h + 1;
                        if (lo < min_touched) min_touched = lo;
                        if (h + (int)(m + c + 2) > hi) hi = h + (int)(m + c + 2);
                        if (hi > max_touched) max_touched = hi;
                        step += c * (2LL * m + 10LL) + 3LL * c * (c - 1LL);
                        if (c >= 4) macro_clears++;
                        continue;
                    }
                }
            }
        }

        // Macro 3: Run-skip on B1 (1RB), E1 (1LE), F1 (1LF)
        int b = tape[h];
        if (b == 1) {
            if (q == 1) { // B1 = 1RB
                int p = h + 1;
                while (tape[p] == 1) p++;
                step += (p - h);
                h = p;
                if (h + 2 > hi) hi = h + 2;
                if (hi > max_touched) max_touched = hi;
                continue;
            } else if (q == 4 || q == 5) { // E1 = 1LE, F1 = 1LF
                int p = h - 1;
                while (tape[p] == 1) p--;
                step += (h - p);
                h = p;
                if (h - 2 < lo) lo = h - 2;
                if (lo < min_touched) min_touched = lo;
                continue;
            }
        }

        int slot = 2 * q + b;
        const Trans& act = tr[slot];
        if (act.w == -2) {
            if (out_ones) {
                out_ones->clear();
                for (int i = lo; i <= hi; ++i) if (tape[i]) out_ones->push_back(i - OFFSET);
            }
            if (out_h) *out_h = h - OFFSET;
            if (out_q) *out_q = q;
            return {collapsed ? 'u' : 'U', step + 1, slot, 0, 0, 0, 0, 0, macro_clears, iters};
        }
        if (act.w == -1) {
            if (out_ones) {
                out_ones->clear();
                for (int i = lo; i <= hi; ++i) if (tape[i]) out_ones->push_back(i - OFFSET);
            }
            if (out_h) *out_h = h - OFFSET;
            if (out_q) *out_q = q;
            return {collapsed ? 'h' : 'H', step + 1, slot, 0, 0, 0, 0, 0, macro_clears, iters};
        }
        tape[h] = (unsigned char)act.w;
        h += act.dir;
        q = act.nxt;
        step++;
        if (h < MIN_SAFE_H || h >= SZ - MIN_SAFE_H) {
            return {'T', step, -1, 0, 0, 0, 0, 0, macro_clears, iters};
        }
        if (h - 2 < lo) lo = h - 2;
        if (h + 2 > hi) hi = h + 2;
        if (lo < min_touched) min_touched = lo;
        if (hi > max_touched) max_touched = hi;
    }
    return {'T', step, -1, 0, 0, 0, 0, 0, macro_clears, iters};
}

// Exact unaccelerated base-step simulator for bit-for-bit verification
KResult run_base_sim(const Trans* tr, int k, int N, int max_steps, std::vector<int>& out_ones, int& out_h, int& out_q) {
    unsigned char* tape = g_tape;
    int pos = OFFSET;
    int lo = pos;
    for (int i = 0; i < 2 * k - 1; ++i) {
        tape[pos++] = 1;
        tape[pos++] = 0;
    }
    tape[pos++] = 1; tape[pos++] = 1; tape[pos++] = 0; tape[pos++] = 0; tape[pos++] = 1;
    int h = pos;
    tape[pos++] = 1; tape[pos++] = 1; tape[pos++] = 0; tape[pos++] = 0;
    for (int i = 0; i < N; ++i) {
        tape[pos++] = 1; tape[pos++] = 1; tape[pos++] = 0; tape[pos++] = 0;
    }
    tape[pos++] = 1;
    int hi = pos;
    int min_touched = lo - 4;
    int max_touched = hi + 4;
    ClearGuard guard{tape, min_touched, max_touched};

    int q = 2;
    for (int step = 1; step <= max_steps; ++step) {
        int b = tape[h];
        int slot = 2 * q + b;
        const Trans& act = tr[slot];
        if (act.w < 0) {
            while (lo <= hi && tape[lo] == 0) lo++;
            while (hi >= lo && tape[hi] == 0) hi--;
            out_ones.clear();
            for (int i = lo; i <= hi; ++i) if (tape[i]) out_ones.push_back(i - OFFSET);
            out_h = h - OFFSET;
            out_q = q;
            return {(act.w == -2) ? 'U' : 'H', step, slot, 0, 0, 0, 0, 0, 0, step};
        }
        tape[h] = (unsigned char)act.w;
        h += act.dir;
        q = act.nxt;
        if (h - 2 < lo) lo = h - 2;
        if (h + 2 > hi) hi = h + 2;
        if (lo < min_touched) min_touched = lo;
        if (hi > max_touched) max_touched = hi;
        if (q == 4 && tape[h] == 0) {
            while (lo <= hi && tape[lo] == 0) lo++;
            while (hi >= lo && tape[hi] == 0) hi--;
            if (lo <= hi && h == lo - 1) {
                KResult kr;
                if (check_K_fast(tape, lo, hi, h, q, kr, step, false, 0, step)) {
                    if (kr.k_len >= N - 3) {
                        out_ones.clear();
                        for (int i = lo; i <= hi; ++i) if (tape[i]) out_ones.push_back(i - OFFSET);
                        out_h = h - OFFSET;
                        out_q = q;
                        return kr;
                    }
                }
            }
        }
    }
    return {'T', max_steps, -1, 0, 0, 0, 0, 0, 0, max_steps};
}

void format_tr(const Trans* tr, char* buf) {
    int p = 0;
    for (int q = 0; q < 9; ++q) {
        if (q > 0) buf[p++] = '_';
        for (int b = 0; b < 2; ++b) {
            const Trans& t = tr[2 * q + b];
            if (t.w < 0) {
                buf[p++] = '-'; buf[p++] = '-'; buf[p++] = '-';
            } else {
                buf[p++] = '0' + t.w;
                buf[p++] = (t.dir == 1) ? 'R' : 'L';
                buf[p++] = 'A' + t.nxt;
            }
        }
    }
    buf[p] = '\0';
}

FILE* out_fp = nullptr;
long long total_nodes = 0;
long long total_k_leaves = 0;
long long mixed_kh_leaves = 0;
long long cascade_leaves = 0;

bool is_k_kind(char c) { return c == 'K' || c == 'k'; }
bool is_h_kind(char c) { return c == 'H' || c == 'h' || c == 'U' || c == 'u'; }

void print_kres(FILE* fp, int k, int N, const KResult& r) {
    if (is_k_kind(r.kind)) {
        fprintf(fp, "k%d=%s(dL%+d,I%d,a%d,d%d,%d,c%d)@%lld ",
                k, (r.kind == 'k') ? "K*" : "K",
                r.k_len - N, r.parity_I, r.a_val, r.d_inner1, r.d_inner2, r.macro_clears, r.step);
    } else if (is_h_kind(r.kind)) {
        bool col = (r.kind == 'h' || r.kind == 'u');
        fprintf(fp, "k%d=%s(%c%d,c%d)@%lld ",
                k, col ? "H*" : "H",
                'A' + (r.slot / 2), r.slot % 2, r.macro_clears, r.step);
    } else {
        fprintf(fp, "k%d=T(c%d)@%lld ", k, r.macro_clears, r.step);
    }
}

void evaluate_leaf(const Trans* tr) {
    KResult res[10];
    bool has_K = false;
    bool has_H = false;
    int k_count = 0;
    int h_count = 0;
    for (int k = 1; k <= 9; ++k) {
        int N = 2 * k + 6;
        res[k] = run_c1_sim(tr, k, N, 8000, true);
        if (is_k_kind(res[k].kind)) { has_K = true; k_count++; }
        if (is_h_kind(res[k].kind)) { has_H = true; h_count++; }
    }
    bool is_cascade = (res[6].macro_clears >= res[4].macro_clears + 2 &&
                       res[4].macro_clears >= res[2].macro_clears + 2 &&
                       res[2].macro_clears >= 2 && (has_H || has_K));
    if (!has_K && !is_cascade) return;
    if (has_K) total_k_leaves++;
    if (is_cascade) cascade_leaves++;

    int N20 = 46;
    KResult r20 = run_c1_sim(tr, 20, N20, 12000, true);
    if (is_k_kind(r20.kind)) has_K = true;
    if (is_h_kind(r20.kind)) has_H = true;

    if ((has_K && (has_H || k_count >= 2)) || is_cascade) {
        if (has_K && has_H) mixed_kh_leaves++;
        char buf[128];
        format_tr(tr, buf);
        const char* tag = (has_K && has_H) ? "MIXED_KH" : (is_cascade ? "CASCADE" : "CLEAN_K");
        fprintf(out_fp, "%s\t%s\t", tag, buf);
        for (int k = 1; k <= 9; ++k) {
            print_kres(out_fp, k, 2 * k + 6, res[k]);
        }
        fprintf(out_fp, "| ");
        print_kres(out_fp, 20, N20, r20);
        fprintf(out_fp, "\n");
        fflush(out_fp);
    }
}

void dfs(Trans* tr, int assigned_count, int max_state) {
    total_nodes++;
    int first_u_slot = -1;
    for (int k = 1; k <= 6; ++k) {
        KResult r = run_c1_sim(tr, k, 2 * k + 6, 3000, true);
        if ((r.kind == 'U' || r.kind == 'u') && first_u_slot == -1) {
            first_u_slot = r.slot;
            break;
        }
    }

    if (first_u_slot == -1 || assigned_count >= 4) {
        evaluate_leaf(tr);
        return;
    }

    // Branch 1: Set first_u_slot to HALT (-1)
    tr[first_u_slot] = {-1, 0, 0};
    dfs(tr, assigned_count, max_state);

    // Branch 2: Assign first_u_slot to a non-halting transition
    int lim_state = (max_state < 8) ? (max_state + 1) : 8;
    for (int nxt = 0; nxt <= lim_state; ++nxt) {
        int next_max = (nxt > max_state) ? nxt : max_state;
        for (int w = 0; w < 2; ++w) {
            for (int d = -1; d <= 1; d += 2) {
                tr[first_u_slot] = {w, d, nxt};
                dfs(tr, assigned_count + 1, next_max);
            }
        }
    }
    tr[first_u_slot] = {-2, 0, 0};
}

void verify_kkhkhk() {
    printf("=== Verifying Macro Accelerator vs Exact Base Simulation on KKHKHK ===\n");
    init_base(false);
    Trans tr[18];
    memcpy(tr, base_tr, sizeof(base_tr));
    // 1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---
    tr[5]  = {1, 1, 7};  // C1 = 1RH
    tr[14] = {0, 1, 1};  // H0 = 0RB
    tr[15] = {0, 1, 8};  // H1 = 0RI
    tr[16] = {0, -1, 6}; // I0 = 0LG
    tr[17] = {-1, 0, 0}; // I1 = ---

    for (int k = 1; k <= 5; ++k) {
        std::vector<int> ones_base, ones_acc;
        int h_base = 0, q_base = 0, h_acc = 0, q_acc = 0;
        KResult rb = run_base_sim(tr, k, 6, 100000, ones_base, h_base, q_base);
        KResult ra = run_c1_sim(tr, k, 6, 5000, false, &ones_acc, &h_acc, &q_acc);
        bool bit_match = (rb.kind == ra.kind && rb.step == ra.step && h_base == h_acc && q_base == q_acc && ones_base == ones_acc);
        printf("  k=%d: kind=%c step=%6lld (base=%6lld) iters=%3d ones=%zu | bit_for_bit_match=%s\n",
               k, ra.kind, ra.step, rb.step, ra.iters, ones_acc.size(), bit_match ? "TRUE" : "FALSE");
        if (!bit_match) {
            printf("ERROR: Verification failed on k=%d!\n", k);
            exit(1);
        }
    }
    printf("All verification checks passed with 100%% bit-for-bit agreement!\n\n");
}

void run_search(bool is_232, const char* out_path) {
    init_base(is_232);
    total_nodes = 0;
    total_k_leaves = 0;
    mixed_kh_leaves = 0;
    cascade_leaves = 0;

    out_fp = fopen(out_path, "w");
    if (!out_fp) {
        printf("Failed to open %s!\n", out_path);
        exit(1);
    }

    Trans tr[18];
    memcpy(tr, base_tr, sizeof(base_tr));
    for (int w = 0; w < 2; ++w) {
        for (int d = -1; d <= 1; d += 2) {
            tr[5] = {w, d, 7};
            printf("[%s] Starting C1 = %d%cH...\n", is_232 ? "champ_232" : "champ_231", w, (d == 1) ? 'R' : 'L');
            fflush(stdout);
            dfs(tr, 1, 7);
        }
    }

    fprintf(out_fp, "#summary total_nodes=%lld total_k_leaves=%lld mixed_kh_leaves=%lld cascade_leaves=%lld\n",
            total_nodes, total_k_leaves, mixed_kh_leaves, cascade_leaves);
    fclose(out_fp);
    printf("[%s] Done! total_nodes=%lld total_k_leaves=%lld mixed_kh_leaves=%lld cascade_leaves=%lld\n\n",
           is_232 ? "champ_232" : "champ_231", total_nodes, total_k_leaves, mixed_kh_leaves, cascade_leaves);
}

int main() {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    memset(g_tape, 0, sizeof(g_tape));
    verify_kkhkhk();
    run_search(false, "std9_exact_231.tsv");
    run_search(true,  "std9_exact_232.tsv");
    return 0;
}
