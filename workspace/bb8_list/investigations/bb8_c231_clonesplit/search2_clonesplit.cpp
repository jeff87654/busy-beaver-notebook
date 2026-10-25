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
    int nxt; // 0..7
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
    int slot;
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

// Check if the machine's A..H transitions preserve exact Rule D (m=0) and Borrow B_1 (m=1)
struct EngineCheck {
    bool ok_d;
    bool ok_b1;
    int extra_per_g0; // 0 for 231-like (2 steps from G0 to E0), 2 for 232-like (4 steps)
};

EngineCheck verify_engine(const Trans* tr) {
    unsigned char* tape = g_tape;
    // Test 1: Rule D on [E0] 100 1^4 00 11 -> [E0] 100 1^18 00 (expected h_new = -12)
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

    // Test 2: Borrow B_1 on [E0] 100 1^4 0000 11 -> [E0] 100 1100 1^16 00 (expected h_new = -12)
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

KResult run_c1_sim(const Trans* tr, const EngineCheck& ec, int k, int N, int max_iters, bool allow_collapse) {
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

    int q = 2; // state C at C1
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
                    int p0 = h + 4;
                    while (p0 <= hi && tape[p0] == 1) p0++;
                    int u0 = p0 - (h + 4);
                    if (u0 % 2 == 1 && p0 + 1 <= hi && tape[p0] == 0 && tape[p0 + 1] == 0) {
                        // Macro 5: Shifted-parity S_odd multi-digit tower collapse
                        // [E0] 100 1^(2a+1) 00 1^(2*d_1) 00 ... 1^(2*d_s) 00 <AFTER>
                        int pos = p0 + 2;
                        int s_digits = 0;
                        bool has_nz = false;
                        while (pos <= hi) {
                            int ones = 0;
                            int p_start = pos;
                            while (pos <= hi && tape[pos] == 1) { ones++; pos++; }
                            if (ones % 2 == 0 && pos + 1 <= hi && tape[pos] == 0 && tape[pos + 1] == 0) {
                                if (ones > 0) has_nz = true;
                                s_digits++;
                                pos += 2;
                            } else {
                                pos = p_start;
                                break;
                            }
                        }
                        if (s_digits >= 1 && has_nz) {
                            collapsed = true;
                            macro_clears++;
                            int base_u = 6 * ((s_digits + 10) / 6 + 1);
                            if (base_u < 60) base_u = 60;
                            if (base_u % 12 != 0) base_u += 6;
                            int u_cap = base_u + 3;
                            int zeros_span = 2 * s_digits + 2;
                            int new_h = pos - zeros_span - u_cap - 4;
                            if (new_h >= MIN_SAFE_H) {
                                memset(tape + lo, 0, pos - lo);
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
                        } else break;
                    }
                    if (even_count >= 1 && odd_pos != -1) {
                        int s_digits = even_count - 1;
                        int d_odd = odd_len / 2;
                        if ((s_digits >= 1 && has_nonzero_even_digit && (odd_pos < hi || d_odd >= 1)) ||
                            (s_digits == 0 && d_odd >= 1 && (first_even_val >= 100 || d_odd >= 6))) {
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

            if (use_m1) {
                int zeros_left;
                if (h < lo) zeros_left = h - MIN_SAFE_H;
                else {
                    int p_left = h - 1;
                    while (tape[p_left] == 0) p_left--;
                    zeros_left = h - 1 - p_left;
                }

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
                            while (r >= 2 && zeros_left >= 2 * u + 4 && h - (2 * u + 4) >= MIN_SAFE_H) {
                                int shift = (int)(2 * u + 4);
                                step += 3LL * u * u + 33LL * u + d_const;
                                h -= shift;
                                zeros_left -= shift;
                                u = 3 * u + 6;
                                r -= 2;
                                macro_clears++;
                            }
                            if (allow_collapse && r >= 2 && h < lo && h - (2 * u + 4) < MIN_SAFE_H) {
                                collapsed = true;
                                long long rem_dec = r / 2;
                                r = r % 2;
                                long long u_cap = (u % 2 == 0) ? (60 + 6 * (((u / 2) + rem_dec) % 2)) : 63;
                                int new_h = (pr - r - 2) - (int)u_cap - 4;
                                if (lo < pr - r) memset(tape + lo, 0, (pr - r) - lo);
                                h = new_h;
                                u = u_cap;
                                lo = h + 1;
                                macro_clears++;
                            }
                            tape[h + 1] = 1; tape[h + 2] = 0; tape[h + 3] = 0;
                            memset(tape + h + 4, 1, (size_t)u);
                            tape[h + 4 + u] = 0; tape[h + 5 + u] = 0;
                            if (h + 1 < lo) lo = h + 1;
                            if (lo < min_touched) min_touched = lo;
                            if (h + 5 + (int)u > hi) hi = h + 5 + (int)u;
                            if (hi > max_touched) max_touched = hi;
                            continue;
                        }
                    } else if (zeros >= 4 && zeros % 2 == 0 && tape[pz] == 1 && tape[pz + 1] == 1) {
                        long long m = (zeros / 2) - 1;
                        if (zeros_left >= 2 * u + 4 && 3 * u + 6 >= 2 * m + 2 && h - (2 * u + 4) >= MIN_SAFE_H) {
                            int shift = (int)(2 * u + 4);
                            step += 3LL * u * u + 33LL * u + 56LL + 12LL * u * m + 22LL * m - 4LL * m * m + (m + 1) * ec.extra_per_g0;
                            h -= shift;
                            tape[h + 1] = 1; tape[h + 2] = 0; tape[h + 3] = 0;
                            int wpos = h + 4;
                            for (int j = 0; j < m; ++j) {
                                tape[wpos] = 1; tape[wpos + 1] = 1; tape[wpos + 2] = 0; tape[wpos + 3] = 0;
                                wpos += 4;
                            }
                            int rem_ones = (int)(3 * u + 6 - 2 * m);
                            memset(tape + wpos, 1, (size_t)rem_ones);
                            wpos += rem_ones;
                            tape[wpos] = 0; tape[wpos + 1] = 0;
                            if (h + 1 < lo) lo = h + 1;
                            if (lo < min_touched) min_touched = lo;
                            if (wpos + 1 > hi) hi = wpos + 1;
                            if (hi > max_touched) max_touched = hi;
                            macro_clears++;
                            continue;
                        }
                    }
                }

                // Macro 2: Expand E0
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
        }

        int b = tape[h];
        if (b == 1) {
            if (q == 1 && skip_b1) {
                int p = h + 1;
                while (tape[p] == 1) p++;
                step += (p - h);
                h = p;
                if (h + 2 > hi) hi = h + 2;
                if (hi > max_touched) max_touched = hi;
                continue;
            } else if ((q == 4 && skip_e1) || (q == 5 && skip_f1)) {
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
        if (act.w < 0) {
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

void format_tr8(const Trans* tr, char* buf) {
    int p = 0;
    for (int q = 0; q < 8; ++q) {
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

bool is_k_kind(char c) { return c == 'K' || c == 'k'; }
bool is_h_kind(char c) { return c == 'H' || c == 'h'; }

void print_kres(FILE* fp, int k, int N, const KResult& r) {
    if (is_k_kind(r.kind)) {
        fprintf(fp, "k%d=%s(dL%+d,I%d,a%d,d%d,%d,c%d)@%lld ",
                k, (r.kind == 'k') ? "K*" : "K",
                r.k_len - N, r.parity_I, r.a_val, r.d_inner1, r.d_inner2, r.macro_clears, r.step);
    } else if (is_h_kind(r.kind)) {
        bool col = (r.kind == 'h');
        fprintf(fp, "k%d=%s(%c%d,c%d)@%lld ",
                k, col ? "H*" : "H",
                'A' + (r.slot / 2), r.slot % 2, r.macro_clears, r.step);
    } else {
        fprintf(fp, "k%d=T(c%d)@%lld ", k, r.macro_clears, r.step);
    }
}

void eval_and_write(FILE* fp, const char* family_tag, const Trans* tr, int& total_tested, int& total_k, int& total_mixed, int& total_cascade) {
    total_tested++;
    EngineCheck ec = verify_engine(tr);
    KResult res[10];
    bool has_K = false, has_H = false;
    int k_cnt = 0;
    for (int k = 1; k <= 9; ++k) {
        int N = 2 * k + 6;
        res[k] = run_c1_sim(tr, ec, k, N, 15000, true);
        if (is_k_kind(res[k].kind)) { has_K = true; k_cnt++; }
        if (is_h_kind(res[k].kind)) has_H = true;
    }
    bool is_cascade = (res[6].macro_clears >= res[4].macro_clears + 2 &&
                       res[4].macro_clears >= res[2].macro_clears + 2 &&
                       res[2].macro_clears >= 2 && (has_H || has_K));
    if (!has_K && !is_cascade) return;
    if (has_K) total_k++;
    if (is_cascade) total_cascade++;

    KResult r20 = run_c1_sim(tr, ec, 20, 46, 25000, true);
    if (is_k_kind(r20.kind)) has_K = true;
    if (is_h_kind(r20.kind)) has_H = true;
    if (has_K && has_H) total_mixed++;

    char buf[128];
    format_tr8(tr, buf);
    const char* cls = (has_K && has_H) ? "MIXED_KH" : (is_cascade ? "CASCADE" : "CLEAN_K");
    fprintf(fp, "%s\t%s\t%s\tec=%d%d\t", family_tag, cls, buf, ec.ok_d ? 1 : 0, ec.ok_b1 ? 1 : 0);
    for (int k = 1; k <= 9; ++k) print_kres(fp, k, 2 * k + 6, res[k]);
    fprintf(fp, "| ");
    print_kres(fp, 20, 46, r20);
    fprintf(fp, "\n");
    fflush(fp);
}

void parse_8(const char* s, Trans* tr) {
    for (int q = 0; q < 8; ++q) {
        for (int b = 0; b < 2; ++b) {
            const char* p = s + q * 7 + b * 3;
            if (p[0] == '-') tr[2 * q + b] = {-1, 0, 0};
            else tr[2 * q + b] = {p[0] - '0', (p[1] == 'R') ? 1 : -1, p[2] - 'A'};
        }
    }
}

int main() {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    memset(g_tape, 0, sizeof(g_tape));

    FILE* fp = fopen("C:\\Users\\jeffr\\Downloads\\bb8\\bb8_list\\investigations\\bb8_c231_clonesplit\\search2_clonesplit.tsv", "w");

    int total_tested = 0, total_k = 0, total_mixed = 0, total_cascade = 0;

    // 1. Test all Engine-Preserving Clone-Splits (CS-1..CS-9):
    // In these, C1 ranges over all 32 transitions {0,1}{L,R}{A..H}
    struct CSTemplate {
        const char* name;
        const char* tm_str;
    };
    CSTemplate cs_templates[] = {
        {"CS1_231_G0_0LH_H0_0LE", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LH0RB_0LE---"},
        {"CS2_231_G0_1LH_H0_0RD", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LH0RB_0RD---"},
        {"CS3_231_D1_0LH_H0_0LE", "1RB0RG_1RC1RB_0RD---_0LE0LH_0LF1LE_1RA1LF_0LD0RB_0LE---"},
        {"CS4_231_D1_0LH_H0_0RG", "1RB0RG_1RC1RB_0RD---_0LE0LH_0LF1LE_1RA1LF_0LD0RB_0RG---"},
        {"CS5_232_D1_0LH_H0_0LE", "1RB0RG_1RC1RB_0RD---_0LE0LH_0LF1LE_1RA1LF_1LC0RB_0LE---"},
        {"CS6_231_D1G0_0LH_H0_0LE", "1RB0RG_1RC1RB_0RD---_0LE0LH_0LF1LE_1RA1LF_0LH0RB_0LE---"},
        {"CS7_231_A0_1RH_H1_1RB", "1RH0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RB"},
        {"CS8_232_A0_1RH_H1_1RB", "1RH0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB_---1RB"},
        {"CS9_231_G0_1RH_H1_1LD", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1RH0RB_---1LD"},
        {"CS10_231_G1_0RH_H1_1RB", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RH_---1RB"},
        {"CS11_232_G1_0RH_H1_1RB", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RH_---1RB"},
    };

    for (const auto& tpl : cs_templates) {
        Trans base[16];
        parse_8(tpl.tm_str, base);
        for (int c1 = 0; c1 < 32; ++c1) {
            Trans tr[16];
            memcpy(tr, base, sizeof(base));
            tr[5] = {(c1 >> 4) & 1, ((c1 >> 3) & 1) ? 1 : -1, c1 & 7};
            eval_and_write(fp, tpl.name, tr, total_tested, total_k, total_mixed, total_cascade);
        }
    }
    printf("After CS templates: tested=%d k=%d mixed=%d cascade=%d\n", total_tested, total_k, total_mixed, total_cascade);

    // 2. Test ALL 1-slot redirects across all 13 engine slots where verify_engine(tr).ok_d && ok_b1 holds!
    for (int is_232 = 0; is_232 < 2; ++is_232) {
        const char* b_str = is_232
            ? "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB_------"
            : "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB_------";
        Trans base[16];
        parse_8(b_str, base);

        for (int slot = 0; slot < 14; ++slot) {
            if (slot == 5) continue;
            for (int tw = 0; tw < 2; ++tw) {
                for (int td = -1; td <= 1; td += 2) {
                    for (int h_halt = 0; h_halt < 2; ++h_halt) {
                        for (int h_def = 0; h_def < 32; ++h_def) {
                            Trans tr[16];
                            memcpy(tr, base, sizeof(base));
                            tr[slot] = {tw, td, 7};
                            if (h_halt == 0) {
                                tr[14] = {-1, 0, 0};
                                tr[15] = {(h_def >> 4) & 1, ((h_def >> 3) & 1) ? 1 : -1, h_def & 7};
                            } else {
                                tr[14] = {(h_def >> 4) & 1, ((h_def >> 3) & 1) ? 1 : -1, h_def & 7};
                                tr[15] = {-1, 0, 0};
                            }
                            EngineCheck ec = verify_engine(tr);
                            if (!ec.ok_d) continue;
                            for (int c1 = 0; c1 < 32; ++c1) {
                                tr[5] = {(c1 >> 4) & 1, ((c1 >> 3) & 1) ? 1 : -1, c1 & 7};
                                char tag[64];
                                snprintf(tag, sizeof(tag), "GEN_%s_%c%d_H%dHALT", is_232 ? "232" : "231", 'A' + (slot / 2), slot % 2, h_halt);
                                eval_and_write(fp, tag, tr, total_tested, total_k, total_mixed, total_cascade);
                            }
                        }
                    }
                }
            }
        }
    }
    printf("After GEN ok_d scan: tested=%d k=%d mixed=%d cascade=%d\n", total_tested, total_k, total_mixed, total_cascade);

    // 3. Test the 8 Clean Infinite Rebuilder Cores (Family X + 1RH/1RE) with:
    //    (a) H0 defined (32 choices) and G0 = --- (or another slot = ---)
    //    (b) H0 = --- and 1 engine slot modified to any of 32 transitions
    struct RebCore {
        const char* name;
        int c1_w, c1_d;
        int h1_w, h1_d, h1_nxt;
    };
    RebCore cores[] = {
        {"FamX_0LH_1RB", 0, -1, 1,  1, 1},
        {"FamX_0RH_0LA", 0,  1, 0, -1, 0},
        {"FamX_1LH_1LF", 1, -1, 1, -1, 5},
        {"FamX_1LH_1RF", 1, -1, 1,  1, 5},
        {"FamX_1RH_0LB", 1,  1, 0, -1, 1},
        {"FamX_1RH_1LF", 1,  1, 1, -1, 5},
        {"FamX_1RH_1RC", 1,  1, 1,  1, 2},
        {"Reb_1RH_1RE",  1,  1, 1,  1, 4},
    };

    for (int is_232 = 0; is_232 < 2; ++is_232) {
        const char* b_str = is_232
            ? "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB_------"
            : "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB_------";
        Trans base[16];
        parse_8(b_str, base);

        for (const auto& rc : cores) {
            // (a) H0 defined (32 choices), G0 = ---, and optionally A1 -> 0RH
            for (int a1_to_h = 0; a1_to_h < 2; ++a1_to_h) {
                for (int h0 = 0; h0 < 32; ++h0) {
                    Trans tr[16];
                    memcpy(tr, base, sizeof(base));
                    tr[5]  = {rc.c1_w, rc.c1_d, 7};
                    tr[12] = {-1, 0, 0}; // G0 = ---
                    if (a1_to_h) tr[1] = {0, 1, 7}; // A1 = 0RH
                    tr[14] = {(h0 >> 4) & 1, ((h0 >> 3) & 1) ? 1 : -1, h0 & 7};
                    tr[15] = {rc.h1_w, rc.h1_d, rc.h1_nxt};
                    char tag[64];
                    snprintf(tag, sizeof(tag), "%s_%s_G0HALT_A1H%d", rc.name, is_232 ? "232" : "231", a1_to_h);
                    eval_and_write(fp, tag, tr, total_tested, total_k, total_mixed, total_cascade);
                }
            }
            // (b) H0 = ---, and 1 engine slot (0..13 != 5) modified to any of 32 transitions
            for (int slot = 0; slot < 14; ++slot) {
                if (slot == 5) continue;
                for (int m = 0; m < 32; ++m) {
                    Trans tr[16];
                    memcpy(tr, base, sizeof(base));
                    tr[5]  = {rc.c1_w, rc.c1_d, 7};
                    tr[14] = {-1, 0, 0};
                    tr[15] = {rc.h1_w, rc.h1_d, rc.h1_nxt};
                    tr[slot] = {(m >> 4) & 1, ((m >> 3) & 1) ? 1 : -1, m & 7};
                    char tag[64];
                    snprintf(tag, sizeof(tag), "%s_%s_MOD_%c%d", rc.name, is_232 ? "232" : "231", 'A' + (slot / 2), slot % 2);
                    eval_and_write(fp, tag, tr, total_tested, total_k, total_mixed, total_cascade);
                }
            }
        }
    }

    fclose(fp);
    printf("Search 2 complete: total_tested=%d total_k=%d total_mixed=%d total_cascade=%d\n",
           total_tested, total_k, total_mixed, total_cascade);
    return 0;
}
