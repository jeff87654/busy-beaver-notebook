#include <cstdio>
#include <cstdlib>
#include <cstring>

struct Trans { int w, dir, nxt; };
static const int SZ = 4194304;
static const int OFFSET = 3500000;
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

void run_exact_no_collapse(const char* name, const char* tm_s, int k, int N) {
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

    for (long long iters = 1; iters <= 2000000LL; ++iters) {
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
                    if (ok && run_cnt >= 2) {
                        int k_len = run_cnt - 1;
                        if (k_len >= 2) {
                            printf("  %s k=%d N=%d -> EXACT K-MATCH at iter %lld: k_len=%d, dL=%d\n", name, k, N, iters, k_len, k_len - N);
                            return;
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
                    if (zeros_left >= 2 * u + 4 && h - (2 * u + 4) >= MIN_SAFE_H) {
                        int shift = 2 * u + 4;
                        h -= shift;
                        u = 3 * u + 6;
                        tape[h] = 0; tape[h + 1] = 1; tape[h + 2] = 0; tape[h + 3] = 0;
                        memset(tape + h + 4, 1, (size_t)u);
                        tape[h + 4 + u] = 0; tape[h + 5 + u] = 0;
                        if (h + 1 < lo) lo = h + 1;
                        continue;
                    }
                } else if (zeros >= 4 && (zeros % 2 == 0) && pz + 1 <= hi && tape[pz] == 1 && tape[pz + 1] == 1) {
                    int m = (zeros / 2) - 1;
                    if (zeros_left >= 2 * u + 4 && 3LL * u + 6LL >= 2LL * m && h - (2 * u + 4) >= MIN_SAFE_H) {
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
                    if (c > 0 && h - 2 * c >= MIN_SAFE_H) {
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
            printf("  %s k=%d N=%d -> EXACT HALT(%c%d) at iter %lld (h=%d, lo=%d)\n", name, k, N, 'A'+q, b, iters, h, lo);
            return;
        }
        tape[h] = (unsigned char)act.w;
        if (act.w == 1) { if (h < lo) lo = h; if (h > hi) hi = h; }
        h += act.dir; q = act.nxt;
        if (h < MIN_SAFE_H + 1000) {
            printf("  %s k=%d N=%d -> HIT LEFT WALL (tower grew > 3.5M cells!) at iter %lld\n", name, k, N, iters);
            return;
        }
    }
    printf("  %s k=%d N=%d -> TIMEOUT\n", name, k, N);
}

int main() {
    for (int k = 1; k <= 6; ++k) {
        run_exact_no_collapse("STD9 [32]", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_0RA0RI", k, 20);
    }
    for (int k = 1; k <= 6; ++k) {
        run_exact_no_collapse("STD9 [16]", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_1RA0RD", k, 20);
    }
    for (int k = 1; k <= 6; ++k) {
        run_exact_no_collapse("CS3 [12]",  "1RB0RG_1RC1RB_0RD1LD_0LE0LH_0LF1LE_1RA1LF_0LD0RB_0LE0LI_0LA---", k, 20);
    }
    return 0;
}
