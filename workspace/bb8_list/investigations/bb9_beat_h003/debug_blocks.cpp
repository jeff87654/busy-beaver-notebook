#include <cstdio>
#include <cstdlib>
#include <cstring>

struct Trans { int w, dir, nxt; };
static const int SZ = 524288;
static const int OFFSET = 320000;
static const int MIN_SAFE_H = 4096;
static unsigned char g_tape[SZ];

void parse_tm9(const char* s, Trans* tr) {
    for (int q = 0; q < 9; ++q) {
        for (int b = 0; b < 2; ++b) {
            const char* p = s + q * 7 + b * 3;
            if (p[0] == '-') tr[2 * q + b] = {-1, 0, -1};
            else tr[2 * q + b] = {p[0] - '0', (p[1] == 'R') ? 1 : -1, p[2] - 'A'};
        }
    }
}

void print_blocks(const unsigned char* tape, int lo, int hi, int h, char q_ch, int iters, const char* tag) {
    while (lo <= hi && tape[lo] == 0) lo++;
    while (hi >= lo && tape[hi] == 0) hi--;
    printf("  [%5d] %-12s q=%c h=%d (lo=%d, hi=%d): ", iters, tag, q_ch, h, lo, hi);
    int p = lo;
    int shown = 0;
    while (p <= hi && shown < 18) {
        if (tape[p] == 1) {
            int c = 0;
            while (p <= hi && tape[p] == 1) { c++; p++; }
            printf("1^%d ", c);
            shown++;
        } else {
            int c = 0;
            while (p <= hi && tape[p] == 0) { c++; p++; }
            printf("0^%d ", c);
            shown++;
        }
    }
    if (p <= hi) printf("...");
    printf("\n");
}

void debug_blocks(const char* name, const char* tm_s, int k, int N) {
    Trans tr[18];
    parse_tm9(tm_s, tr);
    memset(g_tape, 0, sizeof(g_tape));
    unsigned char* tape = g_tape;
    int pos = OFFSET;
    int lo = pos;
    for (int i = 0; i < 2 * k - 1; ++i) { tape[pos++] = 1; tape[pos++] = 0; }
    tape[pos++] = 1; tape[pos++] = 1; tape[pos++] = 0; tape[pos++] = 0; tape[pos++] = 1;
    int h = pos;
    tape[pos++] = 1; tape[pos++] = 1; tape[pos++] = 0; tape[pos++] = 0;
    for (int i = 0; i < N; ++i) {
        tape[pos++] = 1; tape[pos++] = 1; tape[pos++] = 0; tape[pos++] = 0;
    }
    tape[pos++] = 1;
    int hi = pos;
    int q = 2;
    bool skip_b1 = (tr[3].w == 1 && tr[3].dir == 1 && tr[3].nxt == 1);
    bool skip_e1 = (tr[9].w == 1 && tr[9].dir == -1 && tr[9].nxt == 4);
    bool skip_f1 = (tr[11].w == 1 && tr[11].dir == -1 && tr[11].nxt == 5);

    printf("=== %s (k=%d, N=%d) ===\n", name, k, N);
    for (int iters = 1; iters <= 30000; ++iters) {
        if (q == 4 && tape[h] == 0) {
            while (lo <= hi && tape[lo] == 0) lo++;
            while (hi >= lo && tape[hi] == 0) hi--;
            if (lo <= hi && h == lo - 1) {
                if (h + 4 <= hi && tape[h+1]==1 && tape[h+2]==0 && tape[h+3]==0 && tape[hi]==1 && tape[hi-1]==0 && tape[hi-2]==0) {
                    int p = h + 4, run_cnt = 0;
                    bool ok = true;
                    while (p <= hi - 1) {
                        int ones = 0;
                        while (p <= hi - 1 && tape[p] == 1) { ones++; p++; }
                        if ((ones & 1) != 0 || p + 1 > hi - 1 || tape[p] != 0 || tape[p+1] != 0) { ok = false; break; }
                        p += 2; run_cnt++;
                    }
                    if (ok && run_cnt >= 2 && run_cnt - 1 >= 2) {
                        print_blocks(tape, lo, hi, h, 'E', iters, "CHECK_K");
                        printf("  -> MATCH k_len=%d, dL=%d\n", run_cnt - 1, (run_cnt - 1) - N);
                        return;
                    }
                }
                if (h + 4 <= hi && tape[h + 1] == 1 && tape[h + 2] == 0 && tape[h + 3] == 0) {
                    int p = h + 4, even_count = 0, first_even_val = 0, odd_pos = -1, odd_len = -1;
                    bool has_nonzero_even_digit = false;
                    long long sum_even = 0;
                    while (p <= hi) {
                        int ones = 0, p_start = p;
                        while (p <= hi && tape[p] == 1) { ones++; p++; }
                        if (ones % 2 == 1) { odd_pos = p_start; odd_len = ones; break; }
                        if (p + 1 <= hi && tape[p] == 0 && tape[p + 1] == 0) {
                            int val = ones / 2;
                            if (even_count == 0) first_even_val = val;
                            else if (val > 0) has_nonzero_even_digit = true;
                            sum_even += val; even_count++; p += 2;
                        } else break;
                    }
                    if (even_count >= 1 && odd_pos != -1) {
                        int s_digits = even_count - 1;
                        int d_odd = odd_len / 2;
                        if (first_even_val >= 2 && (has_nonzero_even_digit || d_odd >= 1)) {
                            int m0 = 0, p_scan = h + 4 + 2 * first_even_val + 2;
                            while (m0 < s_digits && tape[p_scan] == 0 && tape[p_scan + 1] == 0) { m0++; p_scan += 2; }
                            if (3 * first_even_val + 3 >= m0) {
                                print_blocks(tape, lo, hi, h, 'E', iters, "PRE_M5");
                                int total_parity = (int)((sum_even + d_odd) % 2);
                                int base_u = 6 * ((s_digits + 10) / 6 + 1);
                                if (base_u < 60) base_u = 60;
                                if (base_u % 12 != 0) base_u += 6;
                                int u_cap = base_u + 6 * total_parity;
                                int rem_one_pos = odd_pos + 2 * d_odd;
                                int zeros_span = 2 * s_digits + 2;
                                int new_h = rem_one_pos - zeros_span - u_cap - 4;
                                memset(tape + lo, 0, rem_one_pos - lo);
                                h = new_h;
                                tape[h + 1] = 1; tape[h + 2] = 0; tape[h + 3] = 0;
                                memset(tape + h + 4, 1, (size_t)u_cap);
                                lo = h + 1;
                                print_blocks(tape, lo, hi, h, 'E', iters, "POST_M5");
                                continue;
                            }
                        }
                    }
                }
            }
            int zeros_left = 0;
            if (h < lo) zeros_left = h - MIN_SAFE_H;
            else {
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
                        while (r >= 2 && zeros_left >= 2 * u_ll + 4 && !(h < lo && u_ll >= 60)) {
                            int shift = (int)(2 * u_ll + 4);
                            h -= shift; zeros_left -= shift; u_ll = 3LL * u_ll + 6LL; r -= 2;
                        }
                        if (r >= 2 && h < lo && u_ll >= 60) {
                            int rem_dec = r / 2; r = r % 2;
                            int u_cap = (u_ll % 2 == 0) ? (int)(60 + 6 * (((u_ll / 2) + rem_dec) % 2)) : (int)(69 - 6 * ((u_ll / 2) % 2));
                            int new_h = (pr - r - 2) - u_cap - 4;
                            if (lo < pr - r) memset(tape + lo, 0, (pr - r) - lo);
                            h = new_h; u_ll = u_cap; lo = h + 1;
                        }
                        u = (int)u_ll;
                        tape[h] = 0; tape[h + 1] = 1; tape[h + 2] = 0; tape[h + 3] = 0;
                        memset(tape + h + 4, 1, (size_t)u);
                        tape[h + 4 + u] = 0; tape[h + 5 + u] = 0;
                        if (h + 1 < lo) lo = h + 1;
                        continue;
                    }
                } else if (zeros >= 4 && (zeros % 2 == 0) && pz + 1 <= hi && tape[pz] == 1 && tape[pz + 1] == 1) {
                    int m = (zeros / 2) - 1;
                    if (zeros_left >= 2 * u + 4 && 3LL * u + 6LL >= 2LL * m) {
                        int shift = 2 * u + 4;
                        h -= shift;
                        tape[h] = 0; tape[h + 1] = 1; tape[h + 2] = 0; tape[h + 3] = 0;
                        int pos_w = h + 4;
                        for (int j = 0; j < m; ++j) {
                            tape[pos_w] = 1; tape[pos_w + 1] = 1; tape[pos_w + 2] = 0; tape[pos_w + 3] = 0;
                            pos_w += 4;
                        }
                        int rem_ones = 3 * u + 6 - 2 * m;
                        if (rem_ones > 0) { memset(tape + pos_w, 1, (size_t)rem_ones); pos_w += rem_ones; }
                        tape[pos_w] = 0; tape[pos_w + 1] = 0;
                        if (h + 1 < lo) lo = h + 1;
                        continue;
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
                    if (c > 0) {
                        int h_new = h - 2 * c;
                        memset(tape + h_new + 1, 1, (size_t)(m + 3 * c));
                        int z_pos = h + m + c + 1;
                        tape[z_pos] = 0; tape[z_pos + 1] = 0;
                        h = h_new;
                        if (h + 1 < lo) lo = h + 1;
                        continue;
                    }
                }
            }
        }
        int b = tape[h];
        if (b == 1) {
            if (q == 1 && skip_b1) { int p = h + 1; while (p <= hi && tape[p] == 1) p++; h = p; continue; }
            else if ((q == 4 && skip_e1) || (q == 5 && skip_f1)) { int p = h - 1; while (p >= lo && tape[p] == 1) p--; h = p; continue; }
        }
        const Trans& act = tr[2 * q + b];
        if (act.w < 0) {
            print_blocks(tape, lo, hi, h, 'A'+q, iters, "HALT");
            return;
        }
        if (q == 2 && b == 1) {
            print_blocks(tape, lo, hi, h, 'C', iters, "C1_TRIG");
        }
        if (k == 10 && iters >= 959 && iters <= 1035 && (q == 4 && tape[h] == 0)) {
            print_blocks(tape, lo, hi, h, 'E', iters, "E0_STEP");
        }
        tape[h] = (unsigned char)act.w;
        if (act.w == 1) { if (h < lo) lo = h; if (h > hi) hi = h; }
        h += act.dir; q = act.nxt;
    }
}

int main() {
    debug_blocks("CS3 [12] k=8",  "1RB0RG_1RC1RB_0RD1LD_0LE0LH_0LF1LE_1RA1LF_0LD0RB_0LE0LI_0LA---", 8, 20);
    debug_blocks("CS3 [12] k=9",  "1RB0RG_1RC1RB_0RD1LD_0LE0LH_0LF1LE_1RA1LF_0LD0RB_0LE0LI_0LA---", 9, 20);
    debug_blocks("CS3 [12] k=10", "1RB0RG_1RC1RB_0RD1LD_0LE0LH_0LF1LE_1RA1LF_0LD0RB_0LE0LI_0LA---", 10, 20);
    debug_blocks("STD9 [30] k=7", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LD1LI_1LH---", 7, 20);
    debug_blocks("STD9 [30] k=8", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LD1LI_1LH---", 8, 20);
    debug_blocks("STD9 [38] k=8", "1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_0LA1RH", 8, 20);
    debug_blocks("STD9 [38] k=9", "1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_0LA1RH", 9, 20);
    return 0;
}
