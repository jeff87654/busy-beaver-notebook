#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <windows.h>

struct Trans {
    int w;
    int dir;
    int nxt;
};

static const int SZ = 524288;
static const int OFFSET = 320000;
static const int MIN_SAFE_H = 4096;
static unsigned char g_tape[SZ];

void parse_tm9(const char* s, Trans* tr) {
    for (int q = 0; q < 9; ++q) {
        for (int b = 0; b < 2; ++b) {
            const char* p = s + q * 7 + b * 3;
            if (p[0] == '-') {
                tr[2 * q + b] = {-1, 0, -1};
            } else {
                tr[2 * q + b] = {p[0] - '0', (p[1] == 'R') ? 1 : -1, p[2] - 'A'};
            }
        }
    }
}

struct VerifyRes {
    char kind;
    long long step;
    int slot;
    int k_len;
    int untouched_tail_ones; // how many (1100) blocks at the right end were never even stepped into!
    int a_val;
    std::vector<int> digits;
    int macro_clears;
    int iters;
};

VerifyRes run_c1_verify(const Trans* tr, int k, int N, int max_iters) {
    unsigned char* tape = g_tape;
    memset(tape, 0, sizeof(g_tape));
    int pos = OFFSET;
    int lo = pos;
    for (int i = 0; i < 2 * k - 1; ++i) {
        tape[pos++] = 1;
        tape[pos++] = 0;
    }
    tape[pos++] = 1; tape[pos++] = 1; tape[pos++] = 0; tape[pos++] = 0; tape[pos++] = 1;
    int h = pos;
    tape[pos++] = 1; tape[pos++] = 1; tape[pos++] = 0; tape[pos++] = 0;
    int first_block_start = pos;
    for (int i = 0; i < N; ++i) {
        tape[pos++] = 1; tape[pos++] = 1; tape[pos++] = 0; tape[pos++] = 0;
    }
    tape[pos++] = 1;
    int hi = pos;
    int max_h_reached = h;

    int q = 2;
    long long step = 0;
    int iters = 0;
    bool collapsed = false;
    int macro_clears = 0;
    long long d_const = 56LL;

    while (iters < max_iters) {
        iters++;
        if (h > max_h_reached) max_h_reached = h;
        if (q == 4 && tape[h] == 0) {
            while (lo <= hi && tape[lo] == 0) lo++;
            while (hi >= lo && tape[hi] == 0) hi--;
            if (lo <= hi && h == lo - 1 && h + 4 <= hi &&
                tape[h + 1] == 1 && tape[h + 2] == 0 && tape[h + 3] == 0 &&
                tape[hi] == 1 && tape[hi - 1] == 0 && tape[hi - 2] == 0) {
                int p = h + 4;
                std::vector<int> runs;
                bool ok = true;
                while (p <= hi - 1) {
                    int ones = 0;
                    while (p <= hi - 1 && tape[p] == 1) { ones++; p++; }
                    if (ones % 2 != 0 || p + 1 > hi - 1 || tape[p] != 0 || tape[p + 1] != 0) {
                        ok = false; break;
                    }
                    p += 2;
                    runs.push_back(ones / 2);
                }
                if (ok && (int)runs.size() >= N) {
                    int untouched = (hi - 1 - max_h_reached) / 4;
                    std::vector<int> digs(runs.begin() + 1, runs.end());
                    return {collapsed ? 'k' : 'K', step, -1, (int)runs.size() - 1, untouched, runs[0], digs, macro_clears, iters};
                }
            }

            if (lo <= hi && h == lo - 1 && h + 4 <= hi && tape[h + 1] == 1 && tape[h + 2] == 0 && tape[h + 3] == 0) {
//                 int p0 = h + 4;
//                 while (p0 <= hi && tape[p0] == 1) p0++;
//                 int u0 = p0 - (h + 4);
//                 if (u0 % 2 == 1 && p0 + 1 <= hi && tape[p0] == 0 && tape[p0 + 1] == 0) {
//                     int p = p0 + 2;
//                     int s_digits = 0;
//                     bool has_nz = false;
//                     while (p <= hi - 1) {
//                         int ones = 0;
//                         int p_start = p;
//                         while (p <= hi - 1 && tape[p] == 1) { ones++; p++; }
//                         if (ones % 2 == 0 && p + 1 <= hi - 1 && tape[p] == 0 && tape[p + 1] == 0) {
//                             if (ones > 0) has_nz = true;
//                             s_digits++;
//                             p += 2;
//                         } else {
//                             p = p_start;
//                             break;
//                         }
//                     }
//                     if (s_digits >= 1 && has_nz && 3 * u0 + 6 >= 2 * s_digits) {
//                         if (p > max_h_reached) max_h_reached = p;
//                         collapsed = true;
//                         macro_clears++;
//                         if (k <= 7 && N == 15) {
//                             printf("    [k=%d] Macro4(S_odd) #%d: u0=%d, s_digits=%d, hi-p=%d, tape[p]=%d, tape[p+1]=%d\n",
//                                    k, macro_clears, u0, s_digits, hi - p, tape[p], tape[p + 1]);
//                         }
//                         int base_u = 6 * ((s_digits + 10) / 6 + 1);
//                         if (base_u < 60) base_u = 60;
//                         if (base_u % 12 != 0) base_u += 6;
//                         int u_cap = base_u + 3;
//                         int zeros_span = 2 * s_digits + 2;
//                         int new_h = p - zeros_span - u_cap - 4;
//                         memset(tape + lo, 0, p - lo);
//                         h = new_h;
//                         tape[h + 1] = 1; tape[h + 2] = 0; tape[h + 3] = 0;
//                         memset(tape + h + 4, 1, (size_t)u_cap);
//                         lo = h + 1;
//                         step += 1000000000LL;
//                         continue;
//                     }
//                 }

                int p = h + 4;
                int even_count = 0;
                int first_even_val = 0;
                bool has_nonzero_even_digit = false;
                long long sum_even = 0;
                int odd_pos = -1;
                int odd_len = -1;
                while (p <= hi) {
                    int ones = 0;
                    int p_start = p;
                    while (p <= hi && tape[p] == 1) { ones++; p++; }
                    if (ones % 2 == 1) {
                        odd_pos = p_start;
                        odd_len = ones;
                        break;
                    }
                    if (p + 1 <= hi && tape[p] == 0 && tape[p + 1] == 0) {
                        int val = ones / 2;
                        if (even_count == 0) first_even_val = val;
                        else if (val > 0) has_nonzero_even_digit = true;
                        sum_even += val;
                        even_count++;
                        p += 2;
                    } else break;
                }
                if (even_count >= 1 && odd_pos != -1) {
                    int s_digits = even_count - 1;
                    int d_odd = odd_len / 2;
                    if (first_even_val >= 2 && (has_nonzero_even_digit || d_odd >= 1)) {
                        int m0 = 0;
                        int p_scan = h + 4 + 2 * first_even_val + 2;
                        while (m0 < s_digits && tape[p_scan] == 0 && tape[p_scan + 1] == 0) {
                            m0++; p_scan += 2;
                        }
                        if (3 * first_even_val + 3 >= m0) {
                            int rem_one_pos = odd_pos + 2 * d_odd;
                            if (rem_one_pos > max_h_reached) max_h_reached = rem_one_pos;
                            collapsed = true;
                            macro_clears++;
                            if (k <= 7 && N == 15) {
                                printf("    [k=%d] Macro5(even_odd) #%d: first_even=%d, s_digits=%d, d_odd=%d\n",
                                       k, macro_clears, first_even_val, s_digits, d_odd);
                            }
                            int total_parity = (int)((sum_even + d_odd) % 2);
                            int base_u = 6 * ((s_digits + 10) / 6 + 1);
                            if (base_u < 60) base_u = 60;
                            if (base_u % 12 != 0) base_u += 6;
                            int u_cap = base_u + 6 * total_parity;
                            int zeros_span = 2 * s_digits + 2;
                            int new_h = rem_one_pos - zeros_span - u_cap - 4;
                            memset(tape + lo, 0, rem_one_pos - lo);
                            h = new_h;
                            tape[h + 1] = 1; tape[h + 2] = 0; tape[h + 3] = 0;
                            memset(tape + h + 4, 1, (size_t)u_cap);
                            lo = h + 1;
                            step += 1000000000LL;
                            continue;
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
                    if (pr > max_h_reached) max_h_reached = pr;
                    if (zeros_left >= 2 * u + 4) {
                        long long u_ll = u;
                        while (r >= 2 && zeros_left >= 2 * u_ll + 4 && h - (int)(2 * u_ll + 4) >= MIN_SAFE_H && !(h < lo && u_ll >= 60)) {
                            int shift = (int)(2 * u_ll + 4);
                            step += 3LL * u_ll * u_ll + 33LL * u_ll + d_const;
                            h -= shift; zeros_left -= shift; u_ll = 3LL * u_ll + 6LL; r -= 2;
                        }
                        if (r >= 2 && h < lo && (u_ll >= 60 || h - (int)(2 * u_ll + 4) < MIN_SAFE_H)) {
                            collapsed = true; macro_clears++;
                            if (k <= 7 && N == 15) {
                                printf("    [k=%d] Macro1(E0) #%d: u_ll=%lld, r=%d\n", k, macro_clears, u_ll, r);
                            }
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
                    long long u_ll = u;
                    if (pz + 2 > max_h_reached) max_h_reached = pz + 2;
                    if (zeros_left >= 2 * u + 4 && 3LL * u_ll + 6LL >= 2LL * m) {
                        int shift = 2 * u + 4;
                        step += 3LL * u_ll * u_ll + 33LL * u_ll + 56LL + 12LL * u_ll * m + 22LL * m - 4LL * m * m;
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
                    if (c > 0 && h - 2 * c >= MIN_SAFE_H) {
                        int h_new = h - 2 * c;
                        int new_ones = m + 3 * c;
                        memset(tape + h_new + 1, 1, (size_t)new_ones);
                        int z_pos = h + m + c + 1;
                        tape[z_pos] = 0; tape[z_pos + 1] = 0;
                        if (z_pos > max_h_reached) max_h_reached = z_pos;
                        h = h_new;
                        if (h + 1 < lo) lo = h + 1;
                        long long cl = c, ml = m;
                        step += cl * (2LL * ml + 10LL) + 3LL * cl * (cl - 1LL);
                        continue;
                    }
                }
            }
        }

        int b = tape[h];
        if (b == 1) {
            if (q == 1) {
                int p = h + 1;
                while (p <= hi && tape[p] == 1) p++;
                step += (p - h); h = p; continue;
            } else if (q == 4 || q == 5) {
                int p = h - 1;
                while (p >= lo && tape[p] == 1) p--;
                step += (h - p); h = p; continue;
            }
        }
        const Trans& act = tr[2 * q + b];
        if (act.w < 0) {
            int untouched = (hi - 1 - max_h_reached) / 4;
            return {collapsed ? 'h' : 'H', step + 1, 2 * q + b, 0, untouched, 0, {}, macro_clears, iters};
        }
        tape[h] = (unsigned char)act.w;
        if (act.w == 1) {
            if (h < lo) lo = h;
            if (h > hi) hi = h;
        }
        h += act.dir;
        q = act.nxt;
        step++;
    }
    return {'T', step, -1, 0, 0, 0, {}, macro_clears, iters};
}

int main() {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    const char* m_a = "1RB0RG_1RC1RB_0RD1LH_0LE0LH_0LF1LE_1RA1LF_0LD0RB_0LE0LI_1LG---";
    const char* m_b = "1RB0RG_1RC1RB_0RD1LH_0LE0LH_0LF1LE_1RA1LF_0LD0RB_0RG0LI_1LG---";

    for (const char* m_str : {m_a, m_b}) {
        printf("====================================================================\n");
        printf("Verifying 7-Round Halter: %s\n", m_str);
        printf("====================================================================\n");
        Trans tr[18];
        parse_tm9(m_str, tr);

        // 1. Verify blank-tape startup reaches K(8; 0, 1^19) (k_1 = 20)
        memset(g_tape, 0, sizeof(g_tape));
        int h = OFFSET, lo = OFFSET, hi = OFFSET, q = 0;
        long long h1_hits = 0, i_hits = 0;
        for (int st = 1; st <= 5000; ++st) {
            int b = g_tape[h];
            if (q == 7 && b == 1) h1_hits++;
            if (q == 8) i_hits++;
            const Trans& act = tr[2 * q + b];
            g_tape[h] = (unsigned char)act.w;
            if (act.w == 1) {
                if (h < lo) lo = h;
                if (h > hi) hi = h;
            }
            h += act.dir;
            q = act.nxt;
            if (st == 3921) {
                printf("Blank-tape step %d: q=%c, h-lo=%d, h1_hits=%lld, i_hits=%lld\n",
                       st, 'A' + q, h - lo, h1_hits, i_hits);
            }
        }

        // 2. Verify k = 1 .. 30 on canonical exhaustion configuration (with N = 15 fixed!)
        printf("\nTesting k = 1..30 with fixed N = 15:\n");
        for (int k = 1; k <= 30; ++k) {
            int N = 15;
            VerifyRes r = run_c1_verify(tr, k, N, 60000);
            if (r.kind == 'K' || r.kind == 'k') {
                int dL = r.k_len - N;
                printf("  k=%2d (k%%3=%d): %s  dL=%+2d (exp %+2d), a=%3d, untouched_N=%2d/%2d, clears=%2d, prefix_digs=[",
                       k, k % 3, (r.kind == 'k' ? "K*" : "K "), dL, k / 3, r.a_val, r.untouched_tail_ones, N, r.macro_clears);
                for (int j = 0; j < (int)r.digits.size() - (N - 1); ++j) {
                    printf("%s%d", j ? "," : "", r.digits[j]);
                }
                printf("] + 1^%d\n", N - 1);
            } else if (r.kind == 'H' || r.kind == 'h') {
                printf("  k=%2d (k%%3=%d): %s  slot=%c%d, untouched_N=%2d/%2d, clears=%2d, iters=%d\n",
                       k, k % 3, (r.kind == 'h' ? "H*" : "H "), 'A' + (r.slot / 2), r.slot % 2, r.untouched_tail_ones, N, r.macro_clears, r.iters);
            } else {
                printf("  k=%2d (k%%3=%d): TIMEOUT!\n", k, k % 3);
            }
        }
        // 3. Test k in {4, 7, 10} across N = 6 .. 25 to see if H*(I1) depends on N!
        printf("\nTesting k in {4, 7, 10} across N = 6..25:\n");
        for (int k : {4, 7, 10}) {
            printf("  k=%2d: ", k);
            for (int N = 6; N <= 25; ++N) {
                VerifyRes r = run_c1_verify(tr, k, N, 60000);
                printf("N%d=%c(c%d) ", N, r.kind, r.macro_clears);
            }
            printf("\n");
        }
    }
    return 0;
}
