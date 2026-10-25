#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>
#include <windows.h>

struct Trans {
    int w;
    int dir;
    int nxt;
};

static const int SZ = 262144;
static const int OFFSET = 131072;
static const int MIN_SAFE_H = 2048;
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

struct KInfo {
    bool found;
    int max_k;
    int first_k;
    long long first_step;
    int first_a;
    long long max_sum_d;
    std::string max_desc;
};

bool check_K(const unsigned char* tape, int lo, int hi, int h, int q, int& k_len, int& a_val, long long& sum_d, std::string* desc) {
    if (q != 4 || tape[h] != 0) return false;
    if (lo > hi || h != lo - 1) return false;
    if (h + 4 > hi) return false;
    if (tape[h + 1] != 1 || tape[h + 2] != 0 || tape[h + 3] != 0) return false;
    if (tape[hi] != 1 || tape[hi - 1] != 0 || tape[hi - 2] != 0) return false;

    int pos = h + 4;
    int runs = 0;
    int first_r = 0;
    long long sd = 0;
    std::vector<int> rv;
    while (pos <= hi - 1) {
        int ones = 0;
        while (pos <= hi - 1 && tape[pos] == 1) { ones++; pos++; }
        if (ones % 2 != 0) return false;
        if (pos + 1 > hi - 1 || tape[pos] != 0 || tape[pos + 1] != 0) return false;
        pos += 2;
        int val = ones / 2;
        if (runs == 0) first_r = val;
        else sd += val;
        if (desc) rv.push_back(val);
        runs++;
    }
    if (runs < 2) return false;
    k_len = runs - 1;
    a_val = first_r;
    sum_d = sd;
    if (desc) {
        char buf[256];
        int p = snprintf(buf, sizeof(buf), "K(%d;", a_val);
        for (size_t i = 1; i < rv.size(); ) {
            size_t j = i;
            while (j < rv.size() && rv[j] == rv[i]) j++;
            if (j - i > 1) p += snprintf(buf + p, sizeof(buf) - p, "%s%d^%zu", (i > 1) ? "," : "", rv[i], j - i);
            else p += snprintf(buf + p, sizeof(buf) - p, "%s%d", (i > 1) ? "," : "", rv[i]);
            i = j;
            if (p > 200) { p += snprintf(buf + p, sizeof(buf) - p, ",..."); break; }
        }
        snprintf(buf + p, sizeof(buf) - p, ")");
        *desc = buf;
    }
    return true;
}

KInfo sim_startup(const Trans* tr, int redirected_slot, int max_iters) {
    unsigned char* tape = g_tape;
    int h = OFFSET;
    int lo = OFFSET, hi = OFFSET;
    int min_t = OFFSET - 4, max_t = OFFSET + 4;
    ClearGuard guard{tape, min_t, max_t};

    int q = 0;
    long long step = 0;
    KInfo ki = {false, 0, 0, 0, 0, 0, ""};

    bool skip_b1 = (redirected_slot != 3);
    bool skip_e1 = (redirected_slot != 9);
    bool skip_f1 = (redirected_slot != 11);

    for (int it = 1; it <= max_iters; ++it) {
        if (q == 4 && tape[h] == 0) {
            while (lo <= hi && tape[lo] == 0) lo++;
            while (hi >= lo && tape[hi] == 0) hi--;
            if (lo <= hi && h == lo - 1) {
                int kl = 0, av = 0;
                long long sd = 0;
                if (check_K(tape, lo, hi, h, q, kl, av, sd, nullptr)) {
                    if (!ki.found && kl >= 2) {
                        ki.found = true;
                        ki.first_k = kl;
                        ki.first_step = step;
                        ki.first_a = av;
                    }
                    if (kl > ki.max_k || (kl == ki.max_k && sd > ki.max_sum_d)) {
                        ki.max_k = kl;
                        ki.max_sum_d = sd;
                        check_K(tape, lo, hi, h, q, kl, av, sd, &ki.max_desc);
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
                if (hi > max_t) max_t = hi;
                continue;
            } else if ((q == 4 && skip_e1) || (q == 5 && skip_f1)) {
                int p = h - 1;
                while (tape[p] == 1) p--;
                step += (h - p);
                h = p;
                if (h - 2 < lo) lo = h - 2;
                if (lo < min_t) min_t = lo;
                continue;
            }
        }

        const Trans& act = tr[2 * q + b];
        if (act.w < 0) break;
        tape[h] = (unsigned char)act.w;
        h += act.dir;
        q = act.nxt;
        step++;
        if (h < MIN_SAFE_H || h >= SZ - MIN_SAFE_H) break;
        if (h - 2 < lo) lo = h - 2;
        if (h + 2 > hi) hi = h + 2;
        if (lo < min_t) min_t = lo;
        if (hi > max_t) max_t = hi;
    }
    return ki;
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

    FILE* fp = fopen("C:\\Users\\jeffr\\Downloads\\bb8\\bb8_list\\investigations\\bb8_c231_clonesplit\\search1_all_startup_amp.tsv", "w");
    fprintf(fp, "base\tslot\tmachine\tmax_k\tfirst_k\tfirst_step\tmax_desc\n");

    for (int is_232 = 0; is_232 < 2; ++is_232) {
        const char* s = is_232
            ? "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB_------"
            : "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB_------";
        Trans base[16];
        for (int q = 0; q < 8; ++q) {
            for (int b = 0; b < 2; ++b) {
                const char* p = s + q * 7 + b * 3;
                if (p[0] == '-') base[2 * q + b] = {-1, 0, 0};
                else base[2 * q + b] = {p[0] - '0', (p[1] == 'R') ? 1 : -1, p[2] - 'A'};
            }
        }

        // Test all 13 slots t != 5 (C1):
        // Preserve original (w, d) of slot t -> w_t d_t H, and test all 32 x 32 (H0, H1)
        int max_k_overall = 0;
        int count_gt20 = 0;
        int count_eq20 = 0;
        int count_ge5 = 0;

        for (int slot = 0; slot < 14; ++slot) {
            if (slot == 5) continue; // C1
            for (int tw = 0; tw < 2; ++tw) {
                for (int td = -1; td <= 1; td += 2) {
                    // To keep runtime fast while covering 100% of clone-splits + G0/A0/G1/D1/B0 redirects:
                    // For slot in {0 (A0), 1 (A1), 2 (B0), 7 (D1), 12 (G0), 13 (G1)}, test all 4 (tw, td).
                    // For other slots, test their original (w, d) -> H.
                    bool is_key = (slot == 0 || slot == 1 || slot == 2 || slot == 7 || slot == 12 || slot == 13);
                    if (!is_key && (tw != base[slot].w || td != base[slot].dir)) continue;

                    for (int h0 = 0; h0 < 32; ++h0) {
                        for (int h1 = 0; h1 < 32; ++h1) {
                            Trans tr[16];
                            memcpy(tr, base, sizeof(base));
                            tr[slot] = {tw, td, 7};
                            tr[14] = {(h0 >> 4) & 1, ((h0 >> 3) & 1) ? 1 : -1, h0 & 7};
                            tr[15] = {(h1 >> 4) & 1, ((h1 >> 3) & 1) ? 1 : -1, h1 & 7};

                            KInfo ki = sim_startup(tr, slot, 8000);
                            if (ki.max_k >= 5) {
                                count_ge5++;
                                if (ki.max_k == 20) count_eq20++;
                                if (ki.max_k > 20) count_gt20++;
                                if (ki.max_k > max_k_overall) max_k_overall = ki.max_k;
                                char buf[128], slb[8];
                                format_tr8(tr, buf);
                                snprintf(slb, sizeof(slb), "%c%d", 'A' + (slot / 2), slot % 2);
                                fprintf(fp, "%s\t%s\t%s\t%d\t%d\t%lld\t%s\n",
                                        is_232 ? "champ_232" : "champ_231", slb, buf,
                                        ki.max_k, ki.first_k, ki.first_step, ki.max_desc.c_str());
                            }
                        }
                    }
                }
            }
        }
        printf("[%s] Startup amp scan complete: max_k=%d count_gt20=%d count_eq20=%d count_ge5=%d\n",
               is_232 ? "champ_232" : "champ_231", max_k_overall, count_gt20, count_eq20, count_ge5);
    }
    fclose(fp);
    return 0;
}
