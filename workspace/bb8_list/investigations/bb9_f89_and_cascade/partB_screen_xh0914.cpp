// partB_screen_xh0914.cpp
// Exhaustive screen of all 8-state and 9-state extensions of xh_0914 and xh_0980
// obtained by filling H0 (36 direct transitions in A..H, or 4 * 37 * 37 = 5476 via H0 -> w d I, I0, I1).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <windows.h>

struct Trans { int w, dir, nxt; };
static const int SZ = 524288;
static const int OFFSET = 320000;
static const int MIN_SAFE_H = 4096;
static unsigned char g_tape[SZ];

void parse_tm9(const char* s, Trans* tr) {
    int ns = (strlen(s) + 1) / 7;
    for (int q = 0; q < 9; ++q) {
        for (int b = 0; b < 2; ++b) {
            if (q >= ns) { tr[2 * q + b] = {-1, 0, -1}; continue; }
            const char* p = s + q * 7 + b * 3;
            if (p[0] == '-') tr[2 * q + b] = {-1, 0, -1};
            else tr[2 * q + b] = {p[0] - '0', (p[1] == 'R') ? 1 : -1, p[2] - 'A'};
        }
    }
}

struct KRes {
    char kind; // 'K', 'k', 'H', 'h', 'T', 'G'
    int dL;
    int I_par;
    int clears;
    int steps;
};

static inline bool check_K(
    const unsigned char* tape, int lo, int hi, int h, int N,
    KRes& out, bool collapsed, int clears, int steps
) {
    if (h + 4 > hi) return false;
    if (tape[h + 1] != 1 || tape[h + 2] != 0 || tape[h + 3] != 0) return false;
    if (tape[hi] != 1 || tape[hi - 1] != 0 || tape[hi - 2] != 0) return false;
    int pos = h + 4;
    int run_cnt = 0;
    int a_val = 0;
    long long sum_d = 0;
    while (pos <= hi - 1) {
        int ones = 0;
        while (pos <= hi - 1 && tape[pos] == 1) { ones++; pos++; }
        if ((ones & 1) != 0) return false;
        if (pos + 1 > hi - 1 || tape[pos] != 0 || tape[pos + 1] != 0) return false;
        pos += 2;
        int val = ones >> 1;
        if (run_cnt == 0) a_val = val;
        else sum_d += val;
        run_cnt++;
    }
    if (run_cnt < 2) return false;
    int k_len = run_cnt - 1;
    out.kind = collapsed ? 'k' : 'K';
    out.dL = k_len - N;
    out.I_par = (int)((a_val + sum_d) & 1);
    out.clears = clears;
    out.steps = steps;
    return true;
}

// Also check Kc format: [E0] 0 1^(2b+1) 00 1^(2a) 00 (1^(2d_i) 00)+ 1
static inline bool check_Kc(
    const unsigned char* tape, int lo, int hi, int h, int N,
    KRes& out, bool collapsed, int clears, int steps
) {
    if (h + 6 > hi) return false;
    if (tape[h + 1] != 1) return false;
    if (tape[hi] != 1 || tape[hi - 1] != 0 || tape[hi - 2] != 0) return false;
    int pos = h + 1;
    int b_ones = 0;
    while (pos <= hi - 1 && tape[pos] == 1) { b_ones++; pos++; }
    if ((b_ones & 1) == 0 || b_ones < 3) return false; // b >= 1 so 2b+1 >= 3
    if (pos + 1 > hi - 1 || tape[pos] != 0 || tape[pos + 1] != 0) return false;
    pos += 2;
    int run_cnt = 0;
    int a_val = 0;
    long long sum_d = 0;
    while (pos <= hi - 1) {
        int ones = 0;
        while (pos <= hi - 1 && tape[pos] == 1) { ones++; pos++; }
        if ((ones & 1) != 0) return false;
        if (pos + 1 > hi - 1 || tape[pos] != 0 || tape[pos + 1] != 0) return false;
        pos += 2;
        int val = ones >> 1;
        if (run_cnt == 0) a_val = val;
        else sum_d += val;
        run_cnt++;
    }
    if (run_cnt < 2) return false;
    int k_len = run_cnt - 1;
    out.kind = collapsed ? 'k' : 'K';
    out.dL = k_len - N;
    out.I_par = (int)((a_val + sum_d) & 1);
    out.clears = clears;
    out.steps = steps;
    return true;
}

// Simulate starting directly from the exact H0 configuration after the 2nd tower collapses:
// For k >= 2:
//   k == 2: 1 0 0 1 1 [H0] 00000 1^U 0000 (1100)^(N-1) 1
//   k >= 3: (10)^(2k-5) 1100 11 [H0] 00000 1^U 0000 (1100)^(N-1) 1
// where U == 9 (mod 12), e.g. U = 69 (or U = 81).
KRes run_from_h0(const Trans* tr, int k, int U, int N, int max_iters) {
    unsigned char* tape = g_tape;
    int pos = OFFSET;
    int lo = pos;
    if (k == 2) {
        tape[pos++] = 1; tape[pos++] = 0; tape[pos++] = 0; tape[pos++] = 1; tape[pos++] = 1;
    } else {
        for (int i = 0; i < 2 * k - 5; ++i) { tape[pos++] = 1; tape[pos++] = 0; }
        tape[pos++] = 1; tape[pos++] = 1; tape[pos++] = 0; tape[pos++] = 0;
        tape[pos++] = 1; tape[pos++] = 1;
    }
    int h = pos;
    for (int i = 0; i < 5; ++i) tape[pos++] = 0;
    for (int i = 0; i < U; ++i) tape[pos++] = 1;
    for (int i = 0; i < 4; ++i) tape[pos++] = 0;
    for (int i = 0; i < N - 1; ++i) {
        tape[pos++] = 1; tape[pos++] = 1; tape[pos++] = 0; tape[pos++] = 0;
    }
    tape[pos++] = 1;
    int hi = pos - 1;
    int min_touched = lo - 4;
    int max_touched = hi + 4;

    int q = 7; // state H = 7 (reading 0 at h)
    int iters = 0;
    bool collapsed = false;
    int macro_clears = 0;
    int max_allowed_gap = 2 * k + 40;

    bool skip_b1 = (tr[3].w == 1 && tr[3].dir == 1 && tr[3].nxt == 1);
    bool skip_e1 = (tr[9].w == 1 && tr[9].dir == -1 && tr[9].nxt == 4);
    bool skip_f1 = (tr[11].w == 1 && tr[11].dir == -1 && tr[11].nxt == 5);

    auto cleanup = [&]() {
        if (min_touched < 0) min_touched = 0;
        if (max_touched >= SZ) max_touched = SZ - 1;
        memset(tape + min_touched, 0, max_touched - min_touched + 1);
    };

    while (iters < max_iters) {
        iters++;
        if (q == 4 && tape[h] == 0) {
            while (lo <= hi && tape[lo] == 0) lo++;
            while (hi >= lo && tape[hi] == 0) hi--;
            if (lo <= hi && h == lo - 1) {
                KRes kr;
                if (check_K(tape, lo, hi, h, N, kr, collapsed, macro_clears, iters) ||
                    check_Kc(tape, lo, hi, h, N, kr, collapsed, macro_clears, iters)) {
                    int min_valid_len = N - 2 * k - 3;
                    if (min_valid_len < 2) min_valid_len = 2;
                    if (kr.dL + N >= min_valid_len) {
                        cleanup();
                        return kr;
                    }
                }

                if (h + 4 <= hi && tape[h + 1] == 1 && tape[h + 2] == 0 && tape[h + 3] == 0) {
                    int p = h + 4;
                    int even_count = 0, first_even_val = 0, odd_pos = -1, odd_len = -1;
                    bool has_nonzero_even_digit = false;
                    long long sum_even = 0;
                    int max_zero_run = 0, cur_zero_run = 0;
                    while (p <= hi) {
                        int ones = 0, p_start = p;
                        while (p <= hi && tape[p] == 1) { ones++; p++; }
                        if (ones == 0) cur_zero_run += 2;
                        else { if (cur_zero_run > max_zero_run) max_zero_run = cur_zero_run; cur_zero_run = 0; }
                        if (ones % 2 == 1) { odd_pos = p_start; odd_len = ones; break; }
                        if (p + 1 <= hi && tape[p] == 0 && tape[p + 1] == 0) {
                            int val = ones / 2;
                            if (even_count == 0) first_even_val = val;
                            else if (val > 0) has_nonzero_even_digit = true;
                            sum_even += val; even_count++; p += 2;
                        } else break;
                    }
                    if (even_count >= 1 && odd_pos != -1) {
                        if (collapsed && max_zero_run > max_allowed_gap) {
                            cleanup();
                            return {'G', 0, 0, macro_clears, iters};
                        }
                        int s_digits = even_count - 1;
                        int d_odd = odd_len / 2;
                        if (first_even_val >= 2 && (has_nonzero_even_digit || d_odd >= 1)) {
                            int m0 = 0, p_scan = h + 4 + 2 * first_even_val + 2;
                            while (m0 < s_digits && tape[p_scan] == 0 && tape[p_scan + 1] == 0) { m0++; p_scan += 2; }
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
                                    continue;
                                }
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
                if (collapsed && zeros_left > max_allowed_gap) {
                    cleanup();
                    return {'G', 0, 0, macro_clears, iters};
                }
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
                            while (r >= 2 && zeros_left >= 2 * u_ll + 4 && h - (int)(2 * u_ll + 4) >= MIN_SAFE_H && !(h < lo && u_ll >= 60)) {
                                int shift = (int)(2 * u_ll + 4);
                                h -= shift;
                                zeros_left -= shift;
                                u_ll = 3LL * u_ll + 6LL;
                                r -= 2;
                            }
                            if (r >= 2 && h < lo && (u_ll >= 60 || h - (int)(2 * u_ll + 4) < MIN_SAFE_H)) {
                                collapsed = true;
                                macro_clears++;
                                int rem_dec = r / 2;
                                r = r % 2;
                                int u_cap = (u_ll % 2 == 0)
                                    ? (int)(60 + 6 * (((u_ll / 2) + rem_dec) % 2))
                                    : (int)(69 - 6 * ((u_ll / 2) % 2));
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
                    if (collapsed && zeros > max_allowed_gap) {
                        cleanup();
                        return {'G', 0, 0, macro_clears, iters};
                    }
                    int m = (zeros / 2) - 1;
                    long long u_ll = u;
                    if (zeros_left >= 2 * u + 4 && 3LL * u_ll + 6LL >= 2LL * m) {
                        int shift = 2 * u + 4;
                        if (h - shift >= MIN_SAFE_H) {
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
                        if (h - 2 < min_touched) min_touched = h - 2;
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
            cleanup();
            return {collapsed ? 'h' : 'H', 0, 0, macro_clears, iters};
        }
        tape[h] = (unsigned char)act.w;
        if (act.w == 1) { if (h < lo) lo = h; if (h > hi) hi = h; }
        h += act.dir;
        q = act.nxt;
        if (h < min_touched) min_touched = h;
        if (h > max_touched) max_touched = h;
        if (h <= 16 || h >= SZ - 16) {
            cleanup();
            return {'T', 0, 0, macro_clears, iters};
        }
    }
    cleanup();
    return {'T', 0, 0, macro_clears, iters};
}

int main() {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    memset(g_tape, 0, sizeof(g_tape));

    const char* bases[2] = {
        "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_",
        "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_"
    };
    const char* bnames[2] = {"xh_0914", "xh_0980"};

    std::vector<std::string> acts9;
    acts9.push_back("---");
    for (int w = 0; w < 2; ++w)
        for (int d = 0; d < 2; ++d)
            for (int s = 0; s < 9; ++s) {
                char buf[8];
                snprintf(buf, sizeof(buf), "%d%c%c", w, d ? 'R' : 'L', 'A' + s);
                acts9.push_back(buf);
            }

    int ks[8] = {2, 3, 4, 5, 6, 7, 8, 20};

    int total_tested = 0;
    int any_K = 0;
    int mixed_KH = 0;
    int cascade_H = 0;

    for (int bi = 0; bi < 2; ++bi) {
        // 1. Direct 8-state H0 in A..H (32 choices)
        for (int w = 0; w < 2; ++w) {
            for (int d = 0; d < 2; ++d) {
                for (int s = 0; s < 8; ++s) {
                    char h0[8];
                    snprintf(h0, sizeof(h0), "%d%c%c", w, d ? 'R' : 'L', 'A' + s);
                    std::string tm = std::string(bases[bi]) + h0 + "1RD_------";
                    Trans tr[18];
                    parse_tm9(tm.c_str(), tr);
                    total_tested++;
                    bool hasK = false, hasH = false, hasCascH = false;
                    std::string summary;
                    for (int ki = 0; ki < 8; ++ki) {
                        int k = ks[ki];
                        KRes r1 = run_from_h0(tr, k, 69, 2 * k + 10, 80000);
                        if (r1.kind == 'K' || r1.kind == 'k') hasK = true;
                        if (r1.kind == 'H' || r1.kind == 'h') hasH = true;
                        if (r1.kind == 'h' || (r1.kind == 'H' && r1.clears > 0)) hasCascH = true;
                        char bf[64];
                        snprintf(bf, sizeof(bf), "k%d=%c(dL=%d,c=%d,s=%d) ", k, r1.kind, r1.dL, r1.clears, r1.steps);
                        summary += bf;
                    }
                    if (hasK || hasCascH) {
                        printf("[8st %s H0=%s] %s\n", bnames[bi], h0, summary.c_str());
                    }
                }
            }
        }

        // 2. 9-state H0 -> w d I (4 choices) x I0 (37) x I1 (37) = 5,476 machines
        for (int w = 0; w < 2; ++w) {
            for (int d = 0; d < 2; ++d) {
                char h0[8];
                snprintf(h0, sizeof(h0), "%d%cI", w, d ? 'R' : 'L');
                for (size_t i0 = 0; i0 < acts9.size(); ++i0) {
                    for (size_t i1 = 0; i1 < acts9.size(); ++i1) {
                        std::string tm = std::string(bases[bi]) + h0 + "1RD_" + acts9[i0] + acts9[i1];
                        Trans tr[18];
                        parse_tm9(tm.c_str(), tr);
                        total_tested++;
                        bool hasK = false, hasH = false, hasCascH = false;
                        int max_halt_steps = 0;
                        std::string summary;
                        for (int ki = 0; ki < 8; ++ki) {
                            int k = ks[ki];
                            KRes r1 = run_from_h0(tr, k, 69, 2 * k + 10, 80000);
                            if (r1.kind == 'K' || r1.kind == 'k') hasK = true;
                            if (r1.kind == 'H' || r1.kind == 'h') {
                                hasH = true;
                                if (r1.steps > max_halt_steps) max_halt_steps = r1.steps;
                            }
                            if (r1.kind == 'h' || (r1.kind == 'H' && r1.clears > 0)) hasCascH = true;
                            char bf[64];
                            snprintf(bf, sizeof(bf), "k%d=%c(%d,c%d,s%d) ", k, r1.kind, r1.dL, r1.clears, r1.steps);
                            summary += bf;
                        }
                        if (hasK) any_K++;
                        if (hasK && hasH) mixed_KH++;
                        if (hasCascH) cascade_H++;
                        if (hasK || hasCascH || max_halt_steps > 500) {
                            printf("[9st %s H0=%s I=%s%s] %s\n",
                                   bnames[bi], h0, acts9[i0].c_str(), acts9[i1].c_str(), summary.c_str());
                        }
                    }
                }
            }
        }
    }
    printf("DONE: total_tested=%d, any_K=%d, mixed_KH=%d, cascade_H=%d\n",
           total_tested, any_K, mixed_KH, cascade_H);
    return 0;
}
