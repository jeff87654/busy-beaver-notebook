#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>
#include <windows.h>

struct Trans {
    int w;   // 0 or 1; -1 for HALT ('---')
    int dir; // -1 for L, +1 for R
    int nxt; // 0..8 (A..I)
};

static const int SZ = 524288;
static const int OFFSET = 320000;
static const int MIN_SAFE_H = 4096;
static unsigned char g_tape[SZ];

struct ClearGuard {
    unsigned char* tape;
    int& lo;
    int& hi;
    ~ClearGuard() {
        int c_lo = (lo < 0) ? 0 : lo;
        int c_hi = (hi >= SZ) ? (SZ - 1) : hi;
        if (c_lo <= c_hi) memset(tape + c_lo, 0, c_hi - c_lo + 1);
    }
};

struct KResult {
    char kind; // 'K' (clean K), 'k' (collapsed K*), 'H' (halt), 'h' (collapsed H*), 'T' (timeout)
    long long step;
    int slot;  // 0..17 for A0..I1
    int k_len;
    int a_val;
    int parity_I;
    int d_inner1;
    int d_inner2;
    int macro_clears;
    int iters;
};

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

struct EngineCheck {
    bool ok_d;
    bool ok_b1;
    int extra_per_g0;
};

EngineCheck verify_engine(const Trans* tr) {
    unsigned char* tape = g_tape;
    int pos = OFFSET;
    int h = pos;
    const char* s_d = "010011110011";
    for (int i = 0; s_d[i]; ++i) tape[pos + i] = s_d[i] - '0';
    int min_t = OFFSET - 30, max_t = OFFSET + 30;
    int q = 4;
    int st_d = -1;
    for (int st = 1; st <= 300; ++st) {
        int b = tape[h];
        const Trans& act = tr[2 * q + b];
        if (act.w < 0) break;
        tape[h] = (unsigned char)act.w;
        h += act.dir;
        q = act.nxt;
        if (h < min_t) min_t = h;
        if (h > max_t) max_t = h;
        if (q == 4 && h == OFFSET - 12 && tape[h] == 0) {
            bool match = (tape[h+1] == 1 && tape[h+2] == 0 && tape[h+3] == 0);
            for (int j = 4; j < 22; ++j) if (tape[h + j] != 1) match = false;
            for (int j = min_t; j <= h; ++j) if (tape[j] != 0) match = false;
            for (int j = h + 22; j <= max_t; ++j) if (tape[j] != 0) match = false;
            if (match) { st_d = st; break; }
        }
    }
    memset(tape + min_t, 0, max_t - min_t + 1);
    if (st_d < 0) return {false, false, 0};

    h = OFFSET;
    const char* s_b = "01001111000011";
    for (int i = 0; s_b[i]; ++i) tape[OFFSET + i] = s_b[i] - '0';
    min_t = OFFSET - 30; max_t = OFFSET + 30;
    q = 4;
    int st_b = -1;
    for (int st = 1; st <= 400; ++st) {
        int b = tape[h];
        const Trans& act = tr[2 * q + b];
        if (act.w < 0) break;
        tape[h] = (unsigned char)act.w;
        h += act.dir;
        q = act.nxt;
        if (h < min_t) min_t = h;
        if (h > max_t) max_t = h;
        if (q == 4 && h == OFFSET - 12 && tape[h] == 0) {
            const char* exp = "010011001111111111111111";
            bool match = true;
            for (int j = 0; j < 24; ++j) if (tape[h + j] != exp[j] - '0') match = false;
            for (int j = min_t; j < h; ++j) if (tape[j] != 0) match = false;
            for (int j = h + 24; j <= max_t; ++j) if (tape[j] != 0) match = false;
            if (match) { st_b = st; break; }
        }
    }
    memset(tape + min_t, 0, max_t - min_t + 1);
    if (st_b < 0) return {true, false, st_d - 236};
    return {true, true, st_d - 236};
}

KResult run_c1_sim(const Trans* tr, const EngineCheck& ec, int k, int N, int max_iters, bool allow_collapse, int init_q = 2) {
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

    int q = init_q; // 2 for C1, 7 for H1 (in B0=1RH split)
    long long step = 0;
    int iters = 0;
    bool collapsed = false;
    int macro_clears = 0;
    bool use_m1 = (ec.ok_d && ec.ok_b1);
    long long d_const = 56LL + ec.extra_per_g0;

    bool skip_b1 = (tr[3].w == 1 && tr[3].dir == 1 && tr[3].nxt == 1);
    bool skip_e1 = (tr[9].w == 1 && tr[9].dir == -1 && tr[9].nxt == 4);
    bool skip_f1 = (tr[11].w == 1 && tr[11].dir == -1 && tr[11].nxt == 5);

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
                        return kr;
                    }
                }

                if (use_m1 && allow_collapse && h + 4 <= hi && tape[h + 1] == 1 && tape[h + 2] == 0 && tape[h + 3] == 0) {
//                     int p0 = h + 4;
//                     while (p0 <= hi && tape[p0] == 1) p0++;
//                     int u0 = p0 - (h + 4);
//                     if (u0 % 2 == 1 && p0 + 1 <= hi && tape[p0] == 0 && tape[p0 + 1] == 0) {
//                         int pos = p0 + 2;
//                         int s_digits = 0;
//                         bool has_nz = false;
//                         while (pos <= hi - 1) {
//                             int ones = 0;
//                             int p_start = pos;
//                             while (pos <= hi - 1 && tape[pos] == 1) { ones++; pos++; }
//                             if (ones % 2 == 0 && pos + 1 <= hi - 1 && tape[pos] == 0 && tape[pos + 1] == 0) {
//                                 if (ones > 0) has_nz = true;
//                                 s_digits++;
//                                 pos += 2;
//                             } else {
//                                 pos = p_start;
//                                 break;
//                             }
//                         }
//                         if (s_digits >= 1 && has_nz && 3 * u0 + 6 >= 2 * s_digits) {
//                             collapsed = true;
//                             macro_clears++;
//                             int base_u = 6 * ((s_digits + 10) / 6 + 1);
//                             if (base_u < 60) base_u = 60;
//                             if (base_u % 12 != 0) base_u += 6;
//                             int u_cap = base_u + 3;
//                             int zeros_span = 2 * s_digits + 2;
//                             int new_h = pos - zeros_span - u_cap - 4;
//                             if (new_h >= MIN_SAFE_H) {
//                                 memset(tape + lo, 0, pos - lo);
//                                 h = new_h;
//                                 tape[h + 1] = 1; tape[h + 2] = 0; tape[h + 3] = 0;
//                                 memset(tape + h + 4, 1, (size_t)u_cap);
//                                 lo = h + 1;
//                                 if (lo < min_touched) min_touched = lo;
//                                 step += 1000000000LL;
//                                 continue;
//                             }
//                         }
//                     }

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
                        while (pos <= hi && tape[pos] == 1) { ones++; pos++; }
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
                        if (first_even_val >= 2 && (has_nonzero_even_digit || d_odd >= 1)) {
                            int m0 = 0;
                            int p_scan = h + 4 + 2 * first_even_val + 2;
                            while (m0 < s_digits && tape[p_scan] == 0 && tape[p_scan + 1] == 0) {
                                m0++;
                                p_scan += 2;
                            }
                            if (3 * first_even_val + 3 >= m0) {
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
                                    tape[h + 1] = 1; tape[h + 2] = 0; tape[h + 3] = 0;
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
            }

            if (use_m1) {
                int zeros_left = 0;
                if (h < lo) {
                    zeros_left = h - MIN_SAFE_H;
                } else {
                    int p_left = h - 1;
                    while (p_left >= MIN_SAFE_H && tape[p_left] == 0) p_left--;
                    zeros_left = (h - 1) - p_left;
                }

                if (h + 4 <= hi && tape[h + 1] == 1 && tape[h + 2] == 0 && tape[h + 3] == 0) {
                    int p = h + 4;
                    while (p <= hi && tape[p] == 1) p++;
                    int u = p - (h + 4);
                    int pz = p;
                    while (pz <= hi + 2 && tape[pz] == 0) pz++;
                    int zeros = pz - p;
                    if (zeros == 2 && pz + 1 <= hi && tape[pz] == 1 && tape[pz + 1] == 1) {
                        int pr = pz;
                        while (pr <= hi && tape[pr] == 1) pr++;
                        int r = pr - pz;
                        if (zeros_left >= 2 * u + 4) {
                            long long u_ll = u;
                            int shift_first = 2 * u + 4;
                            if (h - shift_first >= MIN_SAFE_H) {
                                while (r >= 2 && zeros_left >= 2 * u_ll + 4 && h - (int)(2 * u_ll + 4) >= MIN_SAFE_H && !(allow_collapse && h < lo && u_ll >= 60)) {
                                    int shift = (int)(2 * u_ll + 4);
                                    step += 3LL * u_ll * u_ll + 33LL * u_ll + d_const;
                                    h -= shift;
                                    zeros_left -= shift;
                                    u_ll = 3LL * u_ll + 6LL;
                                    r -= 2;
                                }
                                if (allow_collapse && r >= 2 && h < lo && (u_ll >= 60 || h - (int)(2 * u_ll + 4) < MIN_SAFE_H)) {
                                    collapsed = true;
                                    macro_clears++;
                                    int rem_dec = r / 2;
                                    r = r % 2;
                                    int u_cap = (u_ll % 2 == 0) ? (int)(60 + 6 * (((u_ll / 2) + rem_dec) % 2)) : (int)(69 - 6 * ((u_ll / 2) % 2));
                                    int new_h = (pr - r - 2) - u_cap - 4;
                                    if (new_h >= MIN_SAFE_H) {
                                        if (lo < pr - r) memset(tape + lo, 0, (pr - r) - lo);
                                        h = new_h;
                                        u_ll = u_cap;
                                        lo = h + 1;
                                    }
                                }
                                u = (int)u_ll;
                                tape[h] = 0; tape[h + 1] = 1; tape[h + 2] = 0; tape[h + 3] = 0;
                                memset(tape + h + 4, 1, (size_t)u);
                                tape[h + 4 + u] = 0; tape[h + 5 + u] = 0;
                                if (h + 1 < lo) lo = h + 1;
                                if (h - 2 < min_touched) min_touched = h - 2;
                                continue;
                            }
                        }
                    } else if (zeros >= 4 && (zeros % 2 == 0) && pz + 1 <= hi && tape[pz] == 1 && tape[pz + 1] == 1) {
                        int m = (zeros / 2) - 1;
                        long long u_ll = u;
                        if (zeros_left >= 2 * u + 4 && 3LL * u_ll + 6LL >= 2LL * m) {
                            int shift = 2 * u + 4;
                            if (h - shift >= MIN_SAFE_H) {
                                step += 3LL * u_ll * u_ll + 33LL * u_ll + 56LL + 12LL * u_ll * m + 22LL * m - 4LL * m * m + (long long)(m + 1) * ec.extra_per_g0;
                                h -= shift;
                                tape[h] = 0; tape[h + 1] = 1; tape[h + 2] = 0; tape[h + 3] = 0;
                                int pos_w = h + 4;
                                for (int j = 0; j < m; ++j) {
                                    tape[pos_w] = 1; tape[pos_w + 1] = 1; tape[pos_w + 2] = 0; tape[pos_w + 3] = 0;
                                    pos_w += 4;
                                }
                                int rem_ones = 3 * u + 6 - 2 * m;
                                if (rem_ones > 0) {
                                    memset(tape + pos_w, 1, (size_t)rem_ones);
                                    pos_w += rem_ones;
                                }
                                tape[pos_w] = 0; tape[pos_w + 1] = 0;
                                if (h + 1 < lo) lo = h + 1;
                                if (h - 2 < min_touched) min_touched = h - 2;
                                continue;
                            }
                        }
                    }
                }

                if (zeros_left >= 2 && tape[h + 1] == 1) {
                    int p = h + 1;
                    while (p <= hi && tape[p] == 1) p++;
                    int m = p - (h + 1);
                    if (p + 2 <= hi && tape[p] == 0 && tape[p + 1] == 0 && tape[p + 2] == 1) {
                        int p2 = p + 2;
                        while (p2 <= hi && tape[p2] == 1) p2++;
                        int n = p2 - (p + 2);
                        int c = zeros_left / 2;
                        if (n < c) c = n;
                        if (c > 0 && h - 2 * c >= MIN_SAFE_H) {
                            int h_new = h - 2 * c;
                            int new_ones = m + 3 * c;
                            memset(tape + h_new + 1, 1, (size_t)new_ones);
                            int z_pos = h + m + c + 1;
                            tape[z_pos] = 0; tape[z_pos + 1] = 0;
                            h = h_new;
                            if (h + 1 < lo) lo = h + 1;
                            if (z_pos + 1 > hi) hi = z_pos + 1;
                            if (h - 2 < min_touched) min_touched = h - 2;
                            if (hi + 2 > max_touched) max_touched = hi + 2;
                            long long cl = c, ml = m;
                            step += cl * (2LL * ml + 10LL) + 3LL * cl * (cl - 1LL);
                            continue;
                        }
                    }
                }
            }
        }

        int b = tape[h];
        if (b == 1) {
            if (q == 1 && skip_b1) {
                int p = h + 1;
                while (p <= hi && tape[p] == 1) p++;
                int d = p - h;
                step += d;
                h = p;
                if (h + 2 > max_touched) max_touched = h + 2;
                continue;
            } else if ((q == 4 && skip_e1) || (q == 5 && skip_f1)) {
                int p = h - 1;
                while (p >= lo && tape[p] == 1) p--;
                int d = h - p;
                step += d;
                h = p;
                if (h - 2 < min_touched) min_touched = h - 2;
                continue;
            }
        }

        const Trans& act = tr[2 * q + b];
        if (act.w < 0) {
            return {collapsed ? 'h' : 'H', step + 1, 2 * q + b, 0, 0, 0, 0, 0, macro_clears, iters};
        }
        tape[h] = (unsigned char)act.w;
        if (act.w == 1) {
            if (h < lo) lo = h;
            if (h > hi) hi = h;
        }
        h += act.dir;
        q = act.nxt;
        step++;

        if (h < min_touched) min_touched = h;
        if (h > max_touched) max_touched = h;
        if (h <= MIN_SAFE_H || h >= SZ - MIN_SAFE_H) {
            return {'T', step, -1, 0, 0, 0, 0, 0, macro_clears, iters};
        }
    }
    return {'T', step, -1, 0, 0, 0, 0, 0, macro_clears, iters};
}

std::string format_tm9(const Trans* tr) {
    std::string s;
    for (int q = 0; q < 9; ++q) {
        if (q > 0) s += '_';
        for (int b = 0; b < 2; ++b) {
            const Trans& t = tr[2 * q + b];
            if (t.w < 0) {
                s += "---";
            } else {
                s += (char)('0' + t.w);
                s += (t.dir == 1 ? 'R' : 'L');
                s += (char)('A' + t.nxt);
            }
        }
    }
    return s;
}

void init_base9(Trans* tr, bool is_232) {
    tr[0]  = {1, +1, 1}; // A0: 1RB
    tr[1]  = {0, +1, 6}; // A1: 0RG
    tr[2]  = {1, +1, 2}; // B0: 1RC
    tr[3]  = {1, +1, 1}; // B1: 1RB
    tr[4]  = {0, +1, 3}; // C0: 0RD
    tr[5]  = {-1, 0, -1};// C1: ---
    tr[6]  = {0, -1, 4}; // D0: 0LE
    tr[7]  = {0, -1, 3}; // D1: 0LD
    tr[8]  = {0, -1, 5}; // E0: 0LF
    tr[9]  = {1, -1, 4}; // E1: 1LE
    tr[10] = {1, +1, 0}; // F0: 1RA
    tr[11] = {1, -1, 5}; // F1: 1LF
    if (!is_232) {
        tr[12] = {0, -1, 3}; // G0: 0LD
    } else {
        tr[12] = {1, -1, 2}; // G0: 1LC
    }
    tr[13] = {0, +1, 1}; // G1: 0RB
    tr[14] = {-1, 0, -1};// H0: ---
    tr[15] = {-1, 0, -1};// H1: ---
    tr[16] = {-1, 0, -1};// I0: ---
    tr[17] = {-1, 0, -1};// I1: ---
}

struct EvalSummary {
    KResult res[10]; // k=1..9 and k=20 at index 9
    int k_count;
    int h_count;
    int t_count;
    int max_clears;
    int first_halt_slot; // if any H/h occurred on an undefined slot, records it
    bool hits_i0;
    bool hits_i1;
};

static const int MAX_ITERS_C1 = 60000;
static long long g_total_evals = 0;
static long long g_written_rows = 0;

void evaluate_and_record(FILE* f_out, const char* fam, const Trans* tr, int init_q, EvalSummary& es) {
    g_total_evals++;
    EngineCheck ec = verify_engine(tr);
    int ks[10] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 20};
    es.k_count = 0; es.h_count = 0; es.t_count = 0; es.max_clears = 0;
    es.hits_i0 = false; es.hits_i1 = false;

    for (int idx = 0; idx < 10; ++idx) {
        int k = ks[idx];
        int N = 2 * k + 6;
        es.res[idx] = run_c1_sim(tr, ec, k, N, MAX_ITERS_C1, true, init_q);
        char kind = es.res[idx].kind;
        if (kind == 'K' || kind == 'k') es.k_count++;
        else if (kind == 'H' || kind == 'h') {
            es.h_count++;
            if (es.res[idx].slot == 16) es.hits_i0 = true;
            if (es.res[idx].slot == 17) es.hits_i1 = true;
        } else es.t_count++;
        if (es.res[idx].macro_clears > es.max_clears) es.max_clears = es.res[idx].macro_clears;
    }

    // Write row if MIXED_KH (k_count > 0 && h_count > 0) or CASCADE (max_clears >= 2 && h_count > 0) or K_ONLY with interesting structure
    if ((es.k_count > 0 && es.h_count > 0) || (es.k_count > 0 && es.max_clears >= 2)) {
        const char* tag = (es.k_count > 0 && es.h_count > 0) ? "MIXED_KH" : "K_CASCADE";
        std::string tm_s = format_tm9(tr);
        fprintf(f_out, "%s\t%s\t%s\tec=%d%d\t", tag, fam, tm_s.c_str(), ec.ok_d ? 1 : 0, ec.ok_b1 ? 1 : 0);
        for (int idx = 0; idx < 10; ++idx) {
            int k = ks[idx];
            int N = 2 * k + 6;
            const KResult& r = es.res[idx];
            if (idx == 9) fprintf(f_out, "| ");
            if (r.kind == 'K' || r.kind == 'k') {
                int dL = r.k_len - N;
                fprintf(f_out, "k%d=%s(dL%+d,I%d,a%d,d%d,%d,c%d)@%lld ",
                        k, (r.kind == 'k' ? "K*" : "K"), dL, r.parity_I, r.a_val, r.d_inner1, r.d_inner2, r.macro_clears, r.step);
            } else if (r.kind == 'H' || r.kind == 'h') {
                char sc = 'A' + (r.slot / 2);
                char sb = '0' + (r.slot % 2);
                fprintf(f_out, "k%d=%s(%c%c,c%d)@%lld ",
                        k, (r.kind == 'h' ? "H*" : "H"), sc, sb, r.macro_clears, r.step);
            } else {
                fprintf(f_out, "k%d=T(c%d)@%lld ", k, r.macro_clears, r.step);
            }
        }
        fprintf(f_out, "\n");
        g_written_rows++;
    }
}

// Lazy first-hit search over (I0, I1) when another slot (like H1 or C1) is already '---'
// OR when one of I0/I1 is '---'
void search_i0_i1_lazy(FILE* f_out, const char* fam, Trans* tr, int init_q, bool require_i_halt) {
    // First evaluate with I0 = ---, I1 = ---
    tr[16] = {-1, 0, -1};
    tr[17] = {-1, 0, -1};
    EvalSummary es0;
    evaluate_and_record(f_out, fam, tr, init_q, es0);

    // Branch on I0 if I0 was hit
    if (es0.hits_i0) {
        for (int w0 = 0; w0 < 2; ++w0) {
            for (int d0 = -1; d0 <= 1; d0 += 2) {
                for (int s0 = 0; s0 < 9; ++s0) {
                    tr[16] = {w0, d0, s0};
                    tr[17] = {-1, 0, -1};
                    EvalSummary es1;
                    evaluate_and_record(f_out, fam, tr, init_q, es1);
                    if (!require_i_halt && es1.hits_i1) {
                        for (int w1 = 0; w1 < 2; ++w1) {
                            for (int d1 = -1; d1 <= 1; d1 += 2) {
                                for (int s1 = 0; s1 < 9; ++s1) {
                                    tr[17] = {w1, d1, s1};
                                    EvalSummary es2;
                                    evaluate_and_record(f_out, fam, tr, init_q, es2);
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    // Branch on I1 if I1 was hit
    if (es0.hits_i1) {
        tr[16] = {-1, 0, -1};
        for (int w1 = 0; w1 < 2; ++w1) {
            for (int d1 = -1; d1 <= 1; d1 += 2) {
                for (int s1 = 0; s1 < 9; ++s1) {
                    tr[17] = {w1, d1, s1};
                    EvalSummary es1;
                    evaluate_and_record(f_out, fam, tr, init_q, es1);
                    if (!require_i_halt && es1.hits_i0) {
                        for (int w0 = 0; w0 < 2; ++w0) {
                            for (int d0 = -1; d0 <= 1; d0 += 2) {
                                for (int s0 = 0; s0 < 9; ++s0) {
                                    tr[16] = {w0, d0, s0};
                                    EvalSummary es2;
                                    evaluate_and_record(f_out, fam, tr, init_q, es2);
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

int main() {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    FILE* f_out = fopen("search_arch_a_d.tsv", "w");
    if (!f_out) return 1;

    // =========================================================================
    // PART 1: CS_C1_TO_I (CS1..CS6 with H1=---, C1 -> I, both I0 and I1 active;
    // plus CS7_B0_232 with B0=1RH, H0=0RD, C1=---, H1 -> I)
    // =========================================================================
    struct CSTemplate {
        const char* name;
        bool is_232;
        int s1, w1, d1, n1;
        int s2, w2, d2, n2;
        int h0_w, h0_d, h0_n;
        int init_q; // 2 for C1, 7 for H1
        int entry_slot; // 5 for C1, 15 for H1
    };
    CSTemplate cs_list[] = {
        {"CS1_231_G0_0LH",    false, 12, 0, -1, 7, -1, 0, 0, 0, 0, -1, 4, 2, 5},
        {"CS2_232_G0_1LH",    true,  12, 1, -1, 7, -1, 0, 0, 0, 0, +1, 3, 2, 5},
        {"CS3_231_D1_0LH",    false,  7, 0, -1, 7, -1, 0, 0, 0, 0, -1, 4, 2, 5},
        {"CS4_231_D1_0LH_RG", false,  7, 0, -1, 7, -1, 0, 0, 0, 0, +1, 6, 2, 5},
        {"CS5_232_D1_0LH",    true,   7, 0, -1, 7, -1, 0, 0, 0, 0, -1, 4, 2, 5},
        {"CS6_231_D1G0_0LH",  false,  7, 0, -1, 7, 12, 0, -1, 7, 0, -1, 4, 2, 5},
        {"CS7_232_B0_1RH",    true,   2, 1, +1, 7, -1, 0, 0, 0, 0, +1, 3, 7, 15}
    };

    printf("Running Part 1 (CS_C1_TO_I lazy tree)...\n");
    for (const auto& cs : cs_list) {
        for (int cw = 0; cw < 2; ++cw) {
            for (int cd = -1; cd <= 1; cd += 2) {
                Trans tr[18];
                init_base9(tr, cs.is_232);
                tr[cs.s1] = {cs.w1, cs.d1, cs.n1};
                if (cs.s2 >= 0) tr[cs.s2] = {cs.w2, cs.d2, cs.n2};
                tr[14] = {cs.h0_w, cs.h0_d, cs.h0_n}; // H0
                tr[cs.entry_slot] = {cw, cd, 8};       // C1 or H1 -> I
                // Notice the other slot (H1=15 or C1=5) remains {-1, 0, -1} (HALT), so both I0 and I1 can be non-halting!
                search_i0_i1_lazy(f_out, cs.name, tr, cs.init_q, false);
            }
        }
    }
    printf("After Part 1: evals=%lld, written=%lld\n", g_total_evals, g_written_rows);
    fflush(f_out);

    // =========================================================================
    // PART 2: CS_H1_TO_I (CS1..CS6 where C1 -> A..H hits H1, and H1 -> I with one of I0, I1 = ---)
    // =========================================================================
    printf("Running Part 2 (CS_H1_TO_I)...\n");
    for (int t_idx = 0; t_idx < 6; ++t_idx) {
        const auto& cs = cs_list[t_idx];
        for (int cw = 0; cw < 2; ++cw) {
            for (int cd = -1; cd <= 1; cd += 2) {
                for (int cs_nxt = 0; cs_nxt < 8; ++cs_nxt) {
                    // Quick test if C1=(cw, cd, cs_nxt) hits H1 when H1=---
                    Trans tr[18];
                    init_base9(tr, cs.is_232);
                    tr[cs.s1] = {cs.w1, cs.d1, cs.n1};
                    if (cs.s2 >= 0) tr[cs.s2] = {cs.w2, cs.d2, cs.n2};
                    tr[14] = {cs.h0_w, cs.h0_d, cs.h0_n};
                    tr[5]  = {cw, cd, cs_nxt};
                    EngineCheck ec = verify_engine(tr);
                    bool hits_h1 = false;
                    for (int k = 1; k <= 5; ++k) {
                        KResult kr = run_c1_sim(tr, ec, k, 2 * k + 6, 15000, true, 2);
                        if ((kr.kind == 'H' || kr.kind == 'h') && kr.slot == 15) {
                            hits_h1 = true;
                            break;
                        }
                    }
                    if (!hits_h1) continue;
                    // Route H1 -> w d I
                    for (int hw = 0; hw < 2; ++hw) {
                        for (int hd = -1; hd <= 1; hd += 2) {
                            tr[15] = {hw, hd, 8};
                            std::string fam = std::string(cs.name) + "_H1I";
                            search_i0_i1_lazy(f_out, fam.c_str(), tr, 2, true);
                        }
                    }
                }
            }
        }
    }
    printf("After Part 2: evals=%lld, written=%lld\n", g_total_evals, g_written_rows);
    fflush(f_out);

    // =========================================================================
    // PART 3: CS_DUAL_CHANNEL (14 all-k CS rebuilders + 2nd channel split into I)
    // =========================================================================
    printf("Running Part 3 (CS_DUAL_CHANNEL)...\n");
    Trans c1_rebuilders[14] = {
        {0, -1, 0}, {0, -1, 2}, {0, +1, 5}, {0, +1, 6},
        {1, -1, 0}, {1, -1, 1}, {1, -1, 2}, {1, -1, 3},
        {1, -1, 4}, {1, -1, 6}, {1, +1, 0}, {1, +1, 1},
        {1, +1, 3}, {1, +1, 4}
    };
    // Secondary channels into I:
    // Ch 0: G0 = 1RI, I1 = 1LD (I0 free)
    // Ch 1: G1 = 0RI, I1 = 1RB (I0 free)
    // Ch 2: A0 = 1RI, I1 = 1RB (I0 free)
    // Ch 3: B0 = 1RI, I0 = 0RD (I1 free, on 232)
    for (int r_idx = 0; r_idx < 14; ++r_idx) {
        for (int ch = 0; ch < 3; ++ch) {
            Trans tr[18];
            init_base9(tr, false);
            tr[7]  = {0, -1, 7}; // D1 = 0LH
            tr[14] = {0, -1, 4}; // H0 = 0LE
            tr[15] = {-1, 0, -1};// H1 = ---
            tr[5]  = c1_rebuilders[r_idx];
            if (ch == 0) {
                tr[12] = {1, +1, 8}; // G0 = 1RI
                tr[17] = {1, -1, 3}; // I1 = 1LD
            } else if (ch == 1) {
                tr[13] = {0, +1, 8}; // G1 = 0RI
                tr[17] = {1, +1, 1}; // I1 = 1RB
            } else {
                tr[0]  = {1, +1, 8}; // A0 = 1RI
                tr[17] = {1, +1, 1}; // I1 = 1RB
            }
            // Test I0 = --- (with H1 active in 36 choices) AND H1 = --- (with I0 active in 36 choices)
            tr[15] = {-1, 0, -1};
            for (int w0 = 0; w0 < 2; ++w0) {
                for (int d0 = -1; d0 <= 1; d0 += 2) {
                    for (int s0 = 0; s0 < 9; ++s0) {
                        tr[16] = {w0, d0, s0};
                        EvalSummary es;
                        evaluate_and_record(f_out, "CS_DUAL_H1HALT", tr, 2, es);
                    }
                }
            }
            tr[16] = {-1, 0, -1};
            for (int hw = 0; hw < 2; ++hw) {
                for (int hd = -1; hd <= 1; hd += 2) {
                    for (int hs = 0; hs < 9; ++hs) {
                        tr[15] = {hw, hd, hs};
                        EvalSummary es;
                        evaluate_and_record(f_out, "CS_DUAL_I0HALT", tr, 2, es);
                    }
                }
            }
        }
    }
    printf("After Part 3: evals=%lld, written=%lld\n", g_total_evals, g_written_rows);
    fflush(f_out);

    // =========================================================================
    // PART 4: Architecture D — Family X + 1RH/1RE + Flagged Classes F1..F5
    // with a Base-Engine Channel Split into State I!
    // =========================================================================
    printf("Running Part 4 (Arch D & C: Family X + Flagged Rebuilders with Engine Channel Split into I)...\n");
    struct PairCH {
        const char* label;
        Trans c1;
        Trans h1;
    };
    PairCH fx_and_flagged[] = {
        // 8 Clean / Family X rebuilders
        {"FX_0LH_1RB", {0, -1, 7}, {1, +1, 1}},
        {"FX_0RH_0LA", {0, +1, 7}, {0, -1, 0}},
        {"FX_1RH_0LB", {1, +1, 7}, {0, -1, 1}},
        {"FX_1RH_1RC", {1, +1, 7}, {1, +1, 2}},
        {"FX_1LH_1LF", {1, -1, 7}, {1, -1, 5}},
        {"FX_1LH_1RF", {1, -1, 7}, {1, +1, 5}},
        {"FX_1RH_1LF", {1, +1, 7}, {1, -1, 5}},
        {"CL_1RH_1RE", {1, +1, 7}, {1, +1, 4}},
        // Flagged Classes F1..F6
        {"F1_0LH_0LF", {0, -1, 7}, {0, -1, 5}},
        {"F1_1LH_1LD", {1, -1, 7}, {1, -1, 3}},
        {"F1_1LH_0LA", {1, -1, 7}, {0, -1, 0}},
        {"F2_0LH_0RE", {0, -1, 7}, {0, +1, 4}},
        {"F2_1LH_0RG", {1, -1, 7}, {0, +1, 6}},
        {"F3_0RH_0LD", {0, +1, 7}, {0, -1, 3}},
        {"F4_1LH_0RA", {1, -1, 7}, {0, +1, 0}},
        {"F4_1LH_1LA", {1, -1, 7}, {1, -1, 0}},
        {"F6_0RH_1RG", {0, +1, 7}, {1, +1, 6}}
    };

    // Channels into I:
    // 0: D1 = 0LI, I0 = 0LE (I1 free)
    // 1: G0 = 0LI, I0 = 0LE (I1 free)
    // 2: G0 = 1RI, I1 = 1LD (I0 free)
    // 3: G1 = 0RI, I1 = 1RB (I0 free)
    // 4: A0 = 1RI, I1 = 1RB (I0 free)
    for (const auto& pch : fx_and_flagged) {
        for (int ch = 0; ch < 5; ++ch) {
            Trans tr[18];
            init_base9(tr, false);
            tr[5]  = pch.c1;
            tr[15] = pch.h1;
            int free_i_slot = 17;
            if (ch == 0) {
                tr[7]  = {0, -1, 8}; // D1 = 0LI
                tr[16] = {0, -1, 4}; // I0 = 0LE
                free_i_slot = 17;
            } else if (ch == 1) {
                tr[12] = {0, -1, 8}; // G0 = 0LI
                tr[16] = {0, -1, 4}; // I0 = 0LE
                free_i_slot = 17;
            } else if (ch == 2) {
                tr[12] = {1, +1, 8}; // G0 = 1RI
                tr[17] = {1, -1, 3}; // I1 = 1LD
                free_i_slot = 16;
            } else if (ch == 3) {
                tr[13] = {0, +1, 8}; // G1 = 0RI
                tr[17] = {1, +1, 1}; // I1 = 1RB
                free_i_slot = 16;
            } else {
                tr[0]  = {1, +1, 8}; // A0 = 1RI
                tr[17] = {1, +1, 1}; // I1 = 1RB
                free_i_slot = 16;
            }
            // Subcase A: H0 = ---, free_i_slot in 36 choices
            tr[14] = {-1, 0, -1};
            for (int w = 0; w < 2; ++w) {
                for (int d = -1; d <= 1; d += 2) {
                    for (int s = 0; s < 9; ++s) {
                        tr[free_i_slot] = {w, d, s};
                        EvalSummary es;
                        evaluate_and_record(f_out, pch.label, tr, 2, es);
                    }
                }
            }
            // Subcase B: free_i_slot = ---, H0 in 36 choices (only matters if free_i_slot is hit and jumps to H0, or if C1/gadget hits H0)
            tr[free_i_slot] = {-1, 0, -1};
            EvalSummary es_base;
            evaluate_and_record(f_out, pch.label, tr, 2, es_base);
        }
    }
    printf("After Part 4: evals=%lld, written=%lld\n", g_total_evals, g_written_rows);
    fprintf(f_out, "#summary total_evals=%lld written_rows=%lld\n", g_total_evals, g_written_rows);
    fclose(f_out);
    return 0;
}
