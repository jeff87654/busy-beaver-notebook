// partB_screen_x_parents.cpp
// Screen 9-state extensions of the k1 in {1, 2, 4} X-parents of champ_231 / champ_232:
//   1. Arch X-I1: C1 -> w d I, with all 37 x 37 choices of (I0, I1) (and in Group 2, also testing A1 = ---).
//   2. Arch X-I2: Clone-splits of D1, G0, B0, G1 into I (with I1=--- or I0=---), and all 36 choices of C1.
// Evaluates each machine across k = 1..16, 20 using run_c1_strict, and for every MIXED_KH machine,
// traces the exact multi-round trajectory starting from k1 in {1, 2, 4, 19, 20}!
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
};

static inline bool check_K(
    const unsigned char* tape, int lo, int hi, int h, int N,
    KRes& out, bool collapsed, int clears
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
    return true;
}

KRes run_c1_strict(const Trans* tr, int k, int N, int max_iters, int init_q = 2) {
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
    int min_touched = lo - 4;
    int max_touched = hi + 4;

    int q = init_q;
    int iters = 0;
    bool collapsed = false;
    int macro_clears = 0;
    int max_allowed_gap = 2 * k + 28;

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
                if (check_K(tape, lo, hi, h, N, kr, collapsed, macro_clears)) {
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
                            return {'G', 0, 0, macro_clears};
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
                    return {'G', 0, 0, macro_clears};
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
                        return {'G', 0, 0, macro_clears};
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
            return {collapsed ? 'h' : 'H', 0, 0, macro_clears};
        }
        tape[h] = (unsigned char)act.w;
        if (act.w == 1) { if (h < lo) lo = h; if (h > hi) hi = h; }
        h += act.dir;
        q = act.nxt;
        if (h < min_touched) min_touched = h;
        if (h > max_touched) max_touched = h;
        if (h <= 16 || h >= SZ - 16) {
            cleanup();
            return {'T', 0, 0, macro_clears};
        }
    }
    cleanup();
    return {'T', 0, 0, macro_clears};
}

struct ParentSpec {
    const char* name;
    int k1;
    const char* tm8; // with ??? at C1
    bool a1_free;
};

int main() {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    memset(g_tape, 0, sizeof(g_tape));

    // Distinct engine/exhaustion X-parent representatives:
    ParentSpec parents[] = {
        // Group 1 (A0=1RH, H1=1RB): k1 = 2 (H0 in {1LB, 1LH, 1RB}) and k1 = 4 (H0 in {0RB, 1LE, 1RD})
        {"G1_231_k2_1LB", 2, "1RH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LB1RB", false},
        {"G1_232_k2_1LB", 2, "1RH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RA1LF_1LC0RB_1LB1RB", false},
        {"G1_231_k2_1LH", 2, "1RH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LH1RB", false},
        {"G1_232_k2_1LH", 2, "1RH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RA1LF_1LC0RB_1LH1RB", false},
        {"G1_231_k2_1RB", 2, "1RH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RB1RB", false},
        {"G1_232_k2_1RB", 2, "1RH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RA1LF_1LC0RB_1RB1RB", false},
        {"G1_231_k4_0RB", 4, "1RH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB1RB", false},
        {"G1_232_k4_0RB", 4, "1RH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RA1LF_1LC0RB_0RB1RB", false},
        {"G1_231_k4_1LE", 4, "1RH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LE1RB", false},
        {"G1_232_k4_1LE", 4, "1RH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RA1LF_1LC0RB_1LE1RB", false},
        {"G1_231_k4_1RD", 4, "1RH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RD1RB", false},
        {"G1_232_k4_1RD", 4, "1RH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RA1LF_1LC0RB_1RD1RB", false},
        // Group 2 (F0=1RH, H=1RB0RG, A1 is 100% UNUSED!): k1 = 1 (A0=1LG) and k1 = 2 (A0 in 14 choices)
        {"G2_231_k1_1LG", 1, "1LG0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RH1LF_0LD0RB_1RB0RG", true},
        {"G2_232_k1_1LG", 1, "1LG0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RH1LF_1LC0RB_1RB0RG", true},
        {"G2_231_k2_0LC", 2, "0LC0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RH1LF_0LD0RB_1RB0RG", true},
        {"G2_232_k2_0LC", 2, "0LC0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RH1LF_1LC0RB_1RB0RG", true},
        {"G2_231_k2_0LD", 2, "0LD0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RH1LF_0LD0RB_1RB0RG", true},
        {"G2_231_k2_0LE", 2, "0LE0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RH1LF_0LD0RB_1RB0RG", true},
        {"G2_231_k2_0LF", 2, "0LF0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RH1LF_0LD0RB_1RB0RG", true},
        {"G2_231_k2_0LG", 2, "0LG0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RH1LF_0LD0RB_1RB0RG", true},
        {"G2_231_k2_1LC", 2, "1LC0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RH1LF_0LD0RB_1RB0RG", true},
        {"G2_231_k2_1LH", 2, "1LH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RH1LF_0LD0RB_1RB0RG", true},
        {"G2_231_k2_1RG", 2, "1RG0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RH1LF_0LD0RB_1RB0RG", true},
        {"G2_231_k2_1RH", 2, "1RH0RG_1RC1RB_0RD???_0LE0LD_0LF1LE_1RH1LF_0LD0RB_1RB0RG", true},
        // Group 3 (B1=1RH, H=1RC1RH, B0=1LG): Wait: B0=1LG breaks Rule D! Only valid if B0=1RC, Wait: in xh_0097, B0=1LG? No, B0=1RC is needed for Rule D!
    };
    int np = sizeof(parents) / sizeof(parents[0]);

    std::vector<std::string> acts9;
    acts9.push_back("---");
    for (int w = 0; w < 2; ++w)
        for (int d = 0; d < 2; ++d)
            for (int s = 0; s < 9; ++s) {
                char buf[8];
                snprintf(buf, sizeof(buf), "%d%c%c", w, d ? 'R' : 'L', 'A' + s);
                acts9.push_back(buf);
            }

    int ks[10] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 20};
    int total_tested = 0;
    int mixed_cnt = 0;

    auto replace_c1 = [](const std::string& s, const std::string& c1_str) {
        std::string r = s;
        size_t pos = r.find("???");
        if (pos != std::string::npos) r.replace(pos, 3, c1_str);
        return r;
    };

    for (int pi = 0; pi < np; ++pi) {
        const ParentSpec& ps = parents[pi];
        std::string base8 = ps.tm8;

        // 1. Arch X-I1: C1 = w d I, at least one of I0, I1 is --- (or in Group 2, A1 = --- and I0, I1 in A..I!)
        for (int cw = 0; cw < 2; ++cw) {
            for (int cd = 0; cd < 2; ++cd) {
                char c1_buf[8];
                snprintf(c1_buf, sizeof(c1_buf), "%d%cI", cw, cd ? 'R' : 'L');
                std::string b_c1 = replace_c1(base8, c1_buf);

                for (size_t i1 = 0; i1 < acts9.size(); ++i1) {
                    for (size_t i0 = 0; i0 < acts9.size(); ++i0) {
                        bool has_halt = (i0 == 0 || i1 == 0);
                        bool points_to_A = (acts9[i0][2] == 'A' || acts9[i1][2] == 'A');
                        if (!has_halt && (!ps.a1_free || !points_to_A)) continue;
                        if (ps.a1_free && pi >= 14 && !points_to_A) continue;
                        std::string tm = b_c1 + "_" + acts9[i0] + acts9[i1];
                        if (!has_halt && ps.a1_free) {
                            tm.replace(3, 3, "---"); // set A1 = ---!
                        }

                        Trans tr[18];
                        parse_tm9(tm.c_str(), tr);
                        total_tested++;

                        // Quick check at k = ps.k1: must rebuild K or k!
                        KRes rk1 = run_c1_strict(tr, ps.k1, 2 * ps.k1 + 10, 20000);
                        if (rk1.kind != 'K' && rk1.kind != 'k') {
                            if (i0 == 0 && i1 > 0 && rk1.kind != 'H' && rk1.kind != 'h') break;
                            continue;
                        }

                        // Check across ks[0..9]
                        bool hasH = false;
                        std::string summary;
                        for (int ki = 0; ki < 10; ++ki) {
                            int k = ks[ki];
                            KRes r1 = (k == ps.k1) ? rk1 : run_c1_strict(tr, k, 2 * k + 10, 20000);
                            if (r1.kind == 'H' || r1.kind == 'h') hasH = true;
                            char bf[48];
                            snprintf(bf, sizeof(bf), "k%d=%c(%d,I%d,c%d) ", k, r1.kind, r1.dL, r1.I_par, r1.clears);
                            summary += bf;
                        }
                        if (hasH) {
                            mixed_cnt++;
                            printf("[MIXED X-I1 %s k1=%d] %s | %s\n", ps.name, ps.k1, tm.c_str(), summary.c_str());
                        }
                        if (i0 == 0 && i1 > 0 && !hasH) break;
                    }
                }

            }
        }

        // 2. Arch X-I2: Clone-splits of D1, G0, B0 into I, with C1 in acts9[1..]
        struct CSMod { const char* cs_name; int slot_idx; const char* slot_str; const char* i_str; };
        CSMod cs_mods[] = {
            {"D1_0LI_0LE", 7, "0LI", "0LE---"},
            {"D1_0LI_0RG", 7, "0LI", "0RG---"},
            {"G0_0LI_0LE", 12, "0LI", "0LE---"},
            {"G0_1LI_0RD", 12, "1LI", "0RD---"},
            {"G0_1RI_1LD", 12, "1RI", "---1LD"},
            {"B0_1RI_0RD", 2, "1RI", "0RD---"},
        };
        for (int ci = 0; ci < 6; ++ci) {
            std::string b_cs = base8;
            int q_mod = cs_mods[ci].slot_idx / 2;
            int b_mod = cs_mods[ci].slot_idx % 2;
            b_cs.replace(q_mod * 7 + b_mod * 3, 3, cs_mods[ci].slot_str);
            for (size_t c1_i = 1; c1_i < acts9.size(); ++c1_i) {
                std::string tm = replace_c1(b_cs, acts9[c1_i]) + "_" + cs_mods[ci].i_str;
                Trans tr[18];
                parse_tm9(tm.c_str(), tr);
                total_tested++;

                KRes rk1 = run_c1_strict(tr, ps.k1, 2 * ps.k1 + 10, 40000);
                if (rk1.kind != 'K' && rk1.kind != 'k') continue;

                bool hasH = false;
                std::string summary;
                for (int ki = 0; ki < 10; ++ki) {
                    int k = ks[ki];
                    KRes r1 = (k == ps.k1) ? rk1 : run_c1_strict(tr, k, 2 * k + 10, 60000);
                    if (r1.kind == 'H' || r1.kind == 'h') hasH = true;
                    char bf[48];
                    snprintf(bf, sizeof(bf), "k%d=%c(%d,I%d,c%d) ", k, r1.kind, r1.dL, r1.I_par, r1.clears);
                    summary += bf;
                }
                if (hasH) {
                    mixed_cnt++;
                    printf("[MIXED X-I2 %s %s k1=%d] %s | %s\n",
                           ps.name, cs_mods[ci].cs_name, ps.k1, tm.c_str(), summary.c_str());
                }
            }
        }
    }
    printf("DONE: total_tested=%d, mixed_cnt=%d\n", total_tested, mixed_cnt);
    return 0;
}
