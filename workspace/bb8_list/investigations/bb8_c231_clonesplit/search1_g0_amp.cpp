#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>
#include <windows.h>

struct Trans {
    int w;   // 0 or 1; -1 for HALT
    int dir; // -1 for L, +1 for R
    int nxt; // 0..7
};

static const int SZ = 524288;
static const int OFFSET = 262144;
static const int MIN_SAFE_H = 4096;
static unsigned char g_tape[SZ];

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

struct KMoment {
    long long step;
    int iters;
    int k_len;
    int a_val;
    long long sum_digits;
    int max_digit;
    int nonzero_digits;
    std::string desc;
};

bool parse_K(const unsigned char* tape, int lo, int hi, int h, int q, long long step, int iters, KMoment& km) {
    if (q != 4 || tape[h] != 0) return false;
    if (lo > hi || h != lo - 1) return false;
    if (h + 4 > hi) return false;
    if (tape[h + 1] != 1 || tape[h + 2] != 0 || tape[h + 3] != 0) return false;
    if (tape[hi] != 1 || tape[hi - 1] != 0 || tape[hi - 2] != 0) return false;

    int pos = h + 4;
    std::vector<int> runs;
    long long sum_d = 0;
    int max_d = 0;
    int nz_d = 0;
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
        if (!runs.empty()) {
            sum_d += val;
            if (val > max_d) max_d = val;
            if (val > 0) nz_d++;
        }
        runs.push_back(val);
    }
    if (runs.size() < 2) return false;
    km.step = step;
    km.iters = iters;
    km.k_len = (int)runs.size() - 1;
    km.a_val = runs[0];
    km.sum_digits = sum_d;
    km.max_digit = max_d;
    km.nonzero_digits = nz_d;

    char buf[256];
    int p = snprintf(buf, sizeof(buf), "K(%d;", km.a_val);
    for (size_t i = 1; i < runs.size(); ) {
        size_t j = i;
        while (j < runs.size() && runs[j] == runs[i]) j++;
        if (j - i > 1) p += snprintf(buf + p, sizeof(buf) - p, "%s%d^%zu", (i > 1) ? "," : "", runs[i], j - i);
        else p += snprintf(buf + p, sizeof(buf) - p, "%s%d", (i > 1) ? "," : "", runs[i]);
        i = j;
        if (p > 200) { p += snprintf(buf + p, sizeof(buf) - p, ",..."); break; }
    }
    snprintf(buf + p, sizeof(buf) - p, ")");
    km.desc = buf;
    return true;
}

// Check if (G0, H0, H1) preserves the local gadget 0 1 0 [G0] 1^(2a) 0000 1 -> [E0] 100 1^(2a + delta) 0000 1
struct GadgetInfo {
    bool valid_d;
    int delta_ones;
    int extra_steps; // relative to G0=0LD (which takes 2 steps to reach E0)
    bool uses_h0;
    bool uses_h1;
};

GadgetInfo check_local_gadget(const Trans* tr) {
    unsigned char* tape = g_tape;
    int pos = OFFSET;
    int lo = pos;
    // Set up: 1 0 [G0] 1^8 0000 1
    tape[pos++] = 1;
    tape[pos++] = 0;
    int h = pos;
    tape[pos++] = 0; // at G0
    for (int i = 0; i < 8; ++i) tape[pos++] = 1;
    tape[pos++] = 0; tape[pos++] = 0; tape[pos++] = 0; tape[pos++] = 0;
    tape[pos++] = 1;
    int hi = pos;
    int min_t = lo - 20, max_t = hi + 20;
    ClearGuard guard{tape, min_t, max_t};

    int q = 6; // state G
    bool u_h0 = false, u_h1 = false;
    for (int st = 1; st <= 60; ++st) {
        int b = tape[h];
        if (q == 7) {
            if (b == 0) u_h0 = true;
            else u_h1 = true;
        }
        const Trans& act = tr[2 * q + b];
        if (act.w < 0) return {false, 0, 0, u_h0, u_h1};
        tape[h] = (unsigned char)act.w;
        h += act.dir;
        q = act.nxt;
        if (h < min_t) min_t = h;
        if (h > max_t) max_t = h;

        if (q == 4 && tape[h] == 0) {
            int cur_lo = min_t, cur_hi = max_t;
            while (cur_lo <= cur_hi && tape[cur_lo] == 0) cur_lo++;
            while (cur_hi >= cur_lo && tape[cur_hi] == 0) cur_hi--;
            if (cur_lo <= cur_hi && h == cur_lo - 1) {
                if (tape[h + 1] == 1 && tape[h + 2] == 0 && tape[h + 3] == 0) {
                    int p = h + 4;
                    int ones = 0;
                    while (p <= cur_hi && tape[p] == 1) { ones++; p++; }
                    if (p + 4 == cur_hi && tape[p] == 0 && tape[p+1] == 0 && tape[p+2] == 0 && tape[p+3] == 0 && tape[cur_hi] == 1) {
                        return {true, ones - 8, st - 3, u_h0, u_h1};
                    }
                }
            }
        }
    }
    return {false, 0, 0, u_h0, u_h1};
}

struct SimOutcome {
    char status; // 'H' = halt, 'T' = timeout, 'O' = out-of-bounds
    long long steps;
    int iters;
    int ones;
    int halt_slot;
    int k_events;
    KMoment first_k;
    KMoment max_k;
    KMoment last_k;
};

SimOutcome run_from_blank(const Trans* tr, const GadgetInfo& gi, int max_iters, bool allow_collapse) {
    unsigned char* tape = g_tape;
    int h = OFFSET;
    int lo = OFFSET, hi = OFFSET;
    int min_touched = OFFSET - 4, max_touched = OFFSET + 4;
    ClearGuard guard{tape, min_touched, max_touched};

    int q = 0; // start at A0 on blank tape
    long long step = 0;
    int iters = 0;
    SimOutcome out;
    out.status = 'T';
    out.steps = 0;
    out.iters = 0;
    out.ones = 0;
    out.halt_slot = -1;
    out.k_events = 0;
    out.max_k.k_len = 0;

    bool can_use_macro1 = (gi.valid_d && gi.delta_ones == 0);
    long long d_const = 56LL + gi.extra_steps;

    while (iters < max_iters) {
        iters++;
        if (q == 4 && tape[h] == 0) {
            while (lo <= hi && tape[lo] == 0) lo++;
            while (hi >= lo && tape[hi] == 0) hi--;
            if (lo <= hi && h == lo - 1) {
                KMoment km;
                if (parse_K(tape, lo, hi, h, q, step, iters, km)) {
                    if (out.k_events == 0) out.first_k = km;
                    if (km.k_len > out.max_k.k_len || (km.k_len == out.max_k.k_len && km.sum_digits > out.max_k.sum_digits)) {
                        out.max_k = km;
                    }
                    out.last_k = km;
                    out.k_events++;
                }

                // Macro 4 if can_use_macro1 and allow_collapse
                if (can_use_macro1 && allow_collapse && h + 4 <= hi && tape[h + 1] == 1 && tape[h + 2] == 0 && tape[h + 3] == 0) {
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

            int zeros_left;
            if (h < lo) zeros_left = h - MIN_SAFE_H;
            else {
                int p_left = h - 1;
                while (p_left >= min_touched && tape[p_left] == 0) p_left--;
                zeros_left = (p_left < min_touched) ? (h - MIN_SAFE_H) : (h - 1 - p_left);
            }

            // Macro 1 if can_use_macro1
            if (can_use_macro1 && tape[h + 1] == 1 && tape[h + 2] == 0 && tape[h + 3] == 0) {
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
                        }
                        if (allow_collapse && r >= 2 && h < lo && h - (2 * u + 4) < MIN_SAFE_H) {
                            long long rem_dec = r / 2;
                            r = r % 2;
                            long long u_cap = (u % 2 == 0) ? (60 + 6 * (((u / 2) + rem_dec) % 2)) : 63;
                            int new_h = (pr - r - 2) - (int)u_cap - 4;
                            if (lo < pr - r) memset(tape + lo, 0, (pr - r) - lo);
                            h = new_h;
                            u = u_cap;
                            lo = h + 1;
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
                    if (zeros_left >= 2 * u + 4 && 3 * u + 6 >= 2 * m && h - (2 * u + 4) >= MIN_SAFE_H) {
                        int shift = (int)(2 * u + 4);
                        step += 3LL * u * u + 33LL * u + 56LL + 12LL * u * m + 22LL * m - 4LL * m * m + (m + 1) * gi.extra_steps;
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
                        continue;
                    }
                }
            }

            // Macro 2: Expand E0 (NEVER uses G0, H0, H1 — 100% exact for ALL 4,096 machines!)
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
                        continue;
                    }
                }
            }
        }

        // Macro 3: Run-skip on B1, E1, F1 (NEVER uses G0, H0, H1 — 100% exact!)
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
        if (act.w < 0) {
            out.status = 'H';
            out.steps = step + 1;
            out.iters = iters;
            out.halt_slot = slot;
            int ones = 0;
            for (int i = min_touched; i <= max_touched; ++i) if (tape[i]) ones++;
            out.ones = ones;
            return out;
        }
        tape[h] = (unsigned char)act.w;
        h += act.dir;
        q = act.nxt;
        step++;
        if (h < MIN_SAFE_H || h >= SZ - MIN_SAFE_H) {
            out.status = 'O';
            out.steps = step;
            out.iters = iters;
            return out;
        }
        if (h - 2 < lo) lo = h - 2;
        if (h + 2 > hi) hi = h + 2;
        if (lo < min_touched) min_touched = lo;
        if (hi > max_touched) max_touched = hi;
    }
    out.status = 'T';
    out.steps = step;
    out.iters = iters;
    return out;
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

int main() {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    memset(g_tape, 0, sizeof(g_tape));

    const char* s = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB_------";
    Trans base[16];
    for (int q = 0; q < 8; ++q) {
        for (int b = 0; b < 2; ++b) {
            const char* p = s + q * 7 + b * 3;
            if (p[0] == '-') base[2 * q + b] = {-1, 0, 0};
            else base[2 * q + b] = {p[0] - '0', (p[1] == 'R') ? 1 : -1, p[2] - 'A'};
        }
    }

    // First verify baseline champ_231
    GadgetInfo gi_base = check_local_gadget(base);
    SimOutcome so_base = run_from_blank(base, gi_base, 50000, true);
    printf("Baseline champ_231: valid_d=%d delta=%d extra=%d | status=%c steps=%lld iters=%d k_ev=%d first=%s max_k=%d (%s)\n",
           gi_base.valid_d, gi_base.delta_ones, gi_base.extra_steps,
           so_base.status, so_base.steps, so_base.iters, so_base.k_events,
           so_base.first_k.desc.c_str(), so_base.max_k.k_len, so_base.max_k.desc.c_str());

    FILE* fp = fopen("C:\\Users\\jeffr\\Downloads\\bb8\\bb8_list\\investigations\\bb8_c231_clonesplit\\search1_g0_amp.tsv", "w");
    fprintf(fp, "machine\tg0\th0\th1\tvalid_d\tdelta_ones\textra_steps\tstatus\tsteps\titers\tones\tk_events\tmax_k_len\tmax_sum_d\tfirst_k\tmax_k\tlast_k\n");

    int total = 0, valid_d_cnt = 0, k_reached_cnt = 0, halted_cnt = 0;
    int best_k_len = 0;
    std::string best_tm;

    for (int gw = 0; gw < 2; ++gw) {
        for (int gd = -1; gd <= 1; gd += 2) {
            for (int h0w = 0; h0w < 2; ++h0w) {
                for (int h0d = -1; h0d <= 1; h0d += 2) {
                    for (int h0s = 0; h0s < 8; ++h0s) {
                        for (int h1w = 0; h1w < 2; ++h1w) {
                            for (int h1d = -1; h1d <= 1; h1d += 2) {
                                for (int h1s = 0; h1s < 8; ++h1s) {
                                    total++;
                                    Trans tr[16];
                                    memcpy(tr, base, sizeof(base));
                                    tr[12] = {gw, gd, 7};    // G0 -> H
                                    tr[14] = {h0w, h0d, h0s}; // H0
                                    tr[15] = {h1w, h1d, h1s}; // H1

                                    GadgetInfo gi = check_local_gadget(tr);
                                    if (gi.valid_d) valid_d_cnt++;

                                    SimOutcome so = run_from_blank(tr, gi, 40000, true);
                                    if (so.status == 'H') halted_cnt++;
                                    if (so.k_events > 0) {
                                        k_reached_cnt++;
                                        if (so.max_k.k_len > best_k_len) {
                                            best_k_len = so.max_k.k_len;
                                            char b[128];
                                            format_tr8(tr, b);
                                            best_tm = b;
                                        }
                                    }

                                    if (gi.valid_d || so.k_events > 0 || (so.status == 'H' && so.steps > 500)) {
                                        char buf[128], g0b[8], h0b[8], h1b[8];
                                        format_tr8(tr, buf);
                                        snprintf(g0b, sizeof(g0b), "%d%cH", gw, gd == 1 ? 'R' : 'L');
                                        snprintf(h0b, sizeof(h0b), "%d%c%c", h0w, h0d == 1 ? 'R' : 'L', 'A' + h0s);
                                        snprintf(h1b, sizeof(h1b), "%d%c%c", h1w, h1d == 1 ? 'R' : 'L', 'A' + h1s);
                                        fprintf(fp, "%s\t%s\t%s\t%s\t%d\t%d\t%d\t%c\t%lld\t%d\t%d\t%d\t%d\t%lld\t%s\t%s\t%s\n",
                                                buf, g0b, h0b, h1b,
                                                gi.valid_d ? 1 : 0, gi.delta_ones, gi.extra_steps,
                                                so.status, so.steps, so.iters, so.ones,
                                                so.k_events, so.max_k.k_len, so.max_k.sum_digits,
                                                so.k_events ? so.first_k.desc.c_str() : "-",
                                                so.k_events ? so.max_k.desc.c_str() : "-",
                                                so.k_events ? so.last_k.desc.c_str() : "-");
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    fclose(fp);
    printf("Search 1 complete: total=%d valid_d=%d k_reached=%d halted=%d best_k_len=%d (%s)\n",
           total, valid_d_cnt, k_reached_cnt, halted_cnt, best_k_len, best_tm.c_str());
    return 0;
}
