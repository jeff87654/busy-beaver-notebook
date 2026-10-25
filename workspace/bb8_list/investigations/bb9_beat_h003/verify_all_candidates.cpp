#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <iostream>
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

struct KRes {
    char kind; // 'K', 'k', 'H', 'h', 'T'
    int dL;
    int I_par;
    int a_val;
    int d1;
    int d_last;
    int slot;
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
    int a_val = 0, d1 = 0, d_last = 0;
    long long sum_d = 0;
    while (pos <= hi - 1) {
        int ones = 0;
        while (pos <= hi - 1 && tape[pos] == 1) { ones++; pos++; }
        if ((ones & 1) != 0) return false;
        if (pos + 1 > hi - 1 || tape[pos] != 0 || tape[pos + 1] != 0) return false;
        pos += 2;
        int val = ones >> 1;
        if (run_cnt == 0) a_val = val;
        else {
            if (run_cnt == 1) d1 = val;
            d_last = val;
            sum_d += val;
        }
        run_cnt++;
    }
    if (run_cnt < 2) return false;
    int k_len = run_cnt - 1;
    out.kind = collapsed ? 'k' : 'K';
    out.dL = k_len - N;
    out.I_par = (int)((a_val + sum_d) & 1);
    out.a_val = a_val;
    out.d1 = d1;
    out.d_last = d_last;
    out.slot = -1;
    out.clears = clears;
    return true;
}

KRes run_c1_exact(const Trans* tr, int k, int N, int max_iters, int init_q = 2) {
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

    int q = init_q;
    int iters = 0;
    bool collapsed = false;
    int macro_clears = 0;

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
            if (q == 1 && skip_b1) {
                int p = h + 1;
                while (p <= hi && tape[p] == 1) p++;
                h = p; continue;
            } else if ((q == 4 && skip_e1) || (q == 5 && skip_f1)) {
                int p = h - 1;
                while (p >= lo && tape[p] == 1) p--;
                h = p; continue;
            }
        }
        const Trans& act = tr[2 * q + b];
        if (act.w < 0) {
            cleanup();
            return {collapsed ? 'h' : 'H', 0, 0, 0, 0, 0, 2 * q + b, macro_clears};
        }
        tape[h] = (unsigned char)act.w;
        if (act.w == 1) {
            if (h < lo) lo = h;
            if (h > hi) hi = h;
        }
        h += act.dir;
        q = act.nxt;
        if (h < min_touched) min_touched = h;
        if (h > max_touched) max_touched = h;
    }
    cleanup();
    return {'T', 0, 0, 0, 0, 0, -1, macro_clears};
}

int main() {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    memset(g_tape, 0, sizeof(g_tape));

    auto scan_file = [&](const char* fname, bool has_fam) {
        printf("====================================================================\n");
        printf("Scanning %s across k = 1..36:\n", fname);
        printf("====================================================================\n");
        std::ifstream in(fname);
        std::string line;
        int idx = 0;
        while (std::getline(in, line)) {
            if (line.rfind("MIXED_KH", 0) != 0) continue;
            if (line.find("| k20=K") == std::string::npos) continue;
            std::stringstream ss(line);
            std::string cat, fam, tm;
            if (has_fam) {
                ss >> cat >> fam >> tm;
            } else {
                ss >> cat >> tm;
                fam = "STD9";
            }
            idx++;
            Trans tr[18];
            parse_tm9(tm.c_str(), tr);
            int init_q = (fam.find("CS7_") == 0) ? 7 : 2;

            std::vector<int> h_ks;
            std::string summary;
            for (int k = 1; k <= 36; ++k) {
                KRes r = run_c1_exact(tr, k, 2 * k + 6, 60000, init_q);
                if (r.kind == 'H' || r.kind == 'h') {
                    h_ks.push_back(k);
                    char buf[32];
                    snprintf(buf, sizeof(buf), "k%d=H ", k);
                    summary += buf;
                } else if (r.kind == 'K' || r.kind == 'k') {
                    char buf[32];
                    snprintf(buf, sizeof(buf), "k%d=%c(%+d,I%d,d%d) ", k, r.kind, r.dL, r.I_par, r.d_last % 2);
                    summary += buf;
                } else {
                    char buf[32];
                    snprintf(buf, sizeof(buf), "k%d=T ", k);
                    summary += buf;
                }
            }
            bool has_large_h = false;
            for (int hk : h_ks) if (hk >= 6) has_large_h = true;
            if (has_large_h) {
                printf("[%2d] %-22s %s | H at k={", idx, fam.c_str(), tm.c_str());
                for (size_t i = 0; i < h_ks.size(); ++i) printf("%s%d", i ? "," : "", h_ks[i]);
                printf("}\n     %s\n", summary.c_str());
            }
        }
    };

    scan_file("std9_exact_231.tsv", false);
    scan_file("std9_exact_232.tsv", false);
    return 0;
}
