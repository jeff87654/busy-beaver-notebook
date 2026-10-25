#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <windows.h>

struct Trans {
    int w;   // 0 or 1; -1 for assigned '---' (HALT); -2 for UNASSIGNED
    int dir; // -1 for L, +1 for R
    int nxt; // 0..8
};

Trans base_tr[18];

void init_base() {
    const char* s = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB_------_------";
    for (int q = 0; q < 9; ++q) {
        for (int b = 0; b < 2; ++b) {
            const char* p = s + q * 7 + b * 3;
            if (p[0] == '-') {
                base_tr[2 * q + b] = {-2, 0, 0}; // UNASSIGNED
            } else {
                base_tr[2 * q + b] = {p[0] - '0', (p[1] == 'R') ? 1 : -1, p[2] - 'A'};
            }
        }
    }
}

struct KResult {
    char kind; // 'K' (clean K), 'P' (prefix KP), 'H' (halt on -1), 'U' (hit unassigned -2), 'T' (timeout/oob)
    int step;
    int slot;  // slot hit for 'H' or 'U'
    int k_len;
    int a_val;
    int b_val;
    int prefix_len;
    int d_top;     // outermost non-1 digit or last digit
    int d_inner1;  // innermost digit d_1
    int d_inner2;  // second innermost digit d_2
};

bool check_K(const unsigned char* tape, int lo, int hi, int h, int q, KResult& res, int step) {
    if (q != 4 || tape[h] != 0) return false;
    int mn = hi + 1, mx = lo - 1;
    for (int i = lo; i <= hi; ++i) {
        if (tape[i]) {
            if (i < mn) mn = i;
            if (i > mx) mx = i;
        }
    }
    if (mn > mx || h >= mx) return false;
    if (h + 4 > mx) return false;
    if (tape[h + 1] != 1 || tape[h + 2] != 0 || tape[h + 3] != 0) return false;
    if (tape[mx] != 1 || tape[mx - 1] != 0 || tape[mx - 2] != 0) return false;

    int pos = h + 4;
    int num_runs = 0;
    int first_run = -1;
    int d1 = -1, d2 = -1;
    while (pos <= mx - 1) {
        int ones = 0;
        while (pos <= mx - 1 && tape[pos] == 1) {
            ones++;
            pos++;
        }
        if (ones % 2 != 0) return false;
        if (pos + 1 > mx - 1 || tape[pos] != 0 || tape[pos + 1] != 0) return false;
        pos += 2;
        int val = ones / 2;
        if (num_runs == 0) first_run = val;
        else if (num_runs == 1) d1 = val;
        else if (num_runs == 2) d2 = val;
        num_runs++;
    }
    if (num_runs < 2) return false;
    int k_len = num_runs - 1;
    int a_val = first_run;
    if (h == mn - 1) {
        res = {'K', step, -1, k_len, a_val, 0, 0, 0, d1, d2};
        return true;
    } else if (mn < h) {
        res = {'P', step, -1, k_len, a_val, 0, h - mn, 0, d1, d2};
        return true;
    }
    return false;
}

KResult run_c1_sim(const Trans* tr, int k, int N, int max_steps, bool stop_on_kp) {
    const int OFFSET = 2048;
    const int SZ = 4096;
    unsigned char tape[SZ];
    memset(tape, 0, SZ);

    int pos = OFFSET;
    int lo = pos;
    for (int i = 0; i < 2 * k - 1; ++i) {
        tape[pos++] = 1;
        tape[pos++] = 0;
    }
    tape[pos++] = 1;
    tape[pos++] = 1;
    tape[pos++] = 0;
    tape[pos++] = 0;
    tape[pos++] = 1;
    int h = pos;
    tape[pos++] = 1;
    tape[pos++] = 1;
    tape[pos++] = 0;
    tape[pos++] = 0;
    for (int i = 0; i < N; ++i) {
        tape[pos++] = 1;
        tape[pos++] = 1;
        tape[pos++] = 0;
        tape[pos++] = 0;
    }
    tape[pos++] = 1;
    int hi = pos;
    int q = 2; // state C

    for (int step = 1; step <= max_steps; ++step) {
        int b = tape[h];
        int slot = 2 * q + b;
        const Trans& act = tr[slot];
        if (act.w == -2) {
            return {'U', step, slot, 0, 0, 0, 0, 0, 0, 0};
        }
        if (act.w == -1) {
            return {'H', step, slot, 0, 0, 0, 0, 0, 0, 0};
        }
        tape[h] = (unsigned char)act.w;
        h += act.dir;
        q = act.nxt;
        if (h < 6 || h >= SZ - 6) {
            return {'T', step, -1, 0, 0, 0, 0, 0, 0, 0};
        }
        if (h - 2 < lo) lo = h - 2;
        if (h + 2 > hi) hi = h + 2;

        if (q == 4 && tape[h] == 0) {
            KResult kr;
            if (check_K(tape, lo, hi, h, q, kr, step)) {
                if (kr.kind == 'K' && kr.k_len >= N - 3) return kr;
                if (stop_on_kp && kr.kind == 'P' && kr.k_len >= N - 3) return kr;
            }
        }
    }
    return {'T', max_steps, -1, 0, 0, 0, 0, 0, 0, 0};
}

void format_tr(const Trans* tr, char* buf) {
    int p = 0;
    for (int q = 0; q < 9; ++q) {
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

FILE* out_fp = nullptr;
long long total_nodes = 0;
long long total_k_leaves = 0;
long long mixed_kh_leaves = 0;

void evaluate_leaf(const Trans* tr) {
    // Evaluate on k = 1..9 (N=6) and k = 20 (N=25)
    KResult res[10];
    bool has_K = false;
    bool has_H = false;
    int k_count = 0;
    int h_count = 0;
    for (int k = 1; k <= 9; ++k) {
        res[k] = run_c1_sim(tr, k, 6, 30000, false);
        if (res[k].kind == 'K') { has_K = true; k_count++; }
        if (res[k].kind == 'H' || res[k].kind == 'U') { has_H = true; h_count++; }
    }
    if (!has_K) return;
    total_k_leaves++;
    KResult r20 = run_c1_sim(tr, 20, 25, 40000, false);
    if (r20.kind == 'K') has_K = true;
    if (r20.kind == 'H' || r20.kind == 'U') has_H = true;

    // Print if it has both K and H, OR if k_count >= 2!
    if (has_K && (has_H || k_count >= 2)) {
        if (has_K && has_H) mixed_kh_leaves++;
        char buf[128];
        format_tr(tr, buf);
        fprintf(out_fp, "%s\t%s\t", (has_K && has_H) ? "MIXED_KH" : "CLEAN_K", buf);
        for (int k = 1; k <= 9; ++k) {
            if (res[k].kind == 'K') {
                fprintf(out_fp, "k%d=K(L%d,a%d,d%d,%d)@%d ", k, res[k].k_len, res[k].a_val, res[k].d_inner1, res[k].d_inner2, res[k].step);
            } else if (res[k].kind == 'H' || res[k].kind == 'U') {
                fprintf(out_fp, "k%d=H(%c%d)@%d ", k, 'A' + (res[k].slot / 2), res[k].slot % 2, res[k].step);
            } else {
                fprintf(out_fp, "k%d=T ", k);
            }
        }
        if (r20.kind == 'K') {
            fprintf(out_fp, "| k20=K(L%d,a%d,d%d,%d)@%d\n", r20.k_len, r20.a_val, r20.d_inner1, r20.d_inner2, r20.step);
        } else if (r20.kind == 'H' || r20.kind == 'U') {
            fprintf(out_fp, "| k20=H(%c%d)@%d\n", 'A' + (r20.slot / 2), r20.slot % 2, r20.step);
        } else {
            fprintf(out_fp, "| k20=T\n");
        }
        fflush(out_fp);
    }
}

void dfs(Trans* tr, int assigned_count, int max_state) {
    total_nodes++;
    // Run k = 1..6 (N=6) with max_steps = 15000 to find first unassigned slot hit
    int first_u_slot = -1;
    bool any_K = false;
    for (int k = 1; k <= 6; ++k) {
        KResult r = run_c1_sim(tr, k, 6, 15000, false);
        if (r.kind == 'K') any_K = true;
        if (r.kind == 'U' && first_u_slot == -1) {
            first_u_slot = r.slot;
        }
    }

    if (first_u_slot == -1 || assigned_count >= 4) {
        // No unassigned slot hit (or already assigned 4 of the 5 slots, so remaining slot must be HALT)
        evaluate_leaf(tr);
        return;
    }

    // Branch 1: Set first_u_slot to HALT (-1) and continue!
    // (Wait: even if any_K is false so far, setting first_u_slot = -1 might allow ANOTHER k to hit a different unassigned slot!)
    tr[first_u_slot] = {-1, 0, 0};
    dfs(tr, assigned_count, max_state);

    // Branch 2: Assign first_u_slot to a non-halting transition (if assigned_count < 4)
    int lim_state = (max_state < 8) ? (max_state + 1) : 8;
    for (int nxt = 0; nxt <= lim_state; ++nxt) {
        int next_max = (nxt > max_state) ? nxt : max_state;
        for (int w = 0; w < 2; ++w) {
            for (int d = -1; d <= 1; d += 2) {
                tr[first_u_slot] = {w, d, nxt};
                dfs(tr, assigned_count + 1, next_max);
            }
        }
    }
    tr[first_u_slot] = {-2, 0, 0};
}

int main() {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    init_base();
    out_fp = fopen("C:\\Users\\jeffr\\Downloads\\bb8\\bb8_list\\investigations\\bb9_triage7_and_1RB1LA\\enum_champ231_9.tsv", "w");
    if (!out_fp) {
        printf("Failed to open output file!\n");
        return 1;
    }

    Trans tr[18];
    memcpy(tr, base_tr, sizeof(base_tr));

    // C1 (slot 5) goes to H (state 7): 4 choices
    for (int w = 0; w < 2; ++w) {
        for (int d = -1; d <= 1; d += 2) {
            tr[5] = {w, d, 7};
            printf("Starting C1 = %d%cH...\n", w, (d == 1) ? 'R' : 'L');
            fflush(stdout);
            dfs(tr, 1, 7);
        }
    }

    fprintf(out_fp, "#summary total_nodes=%lld total_k_leaves=%lld mixed_kh_leaves=%lld\n",
            total_nodes, total_k_leaves, mixed_kh_leaves);
    fclose(out_fp);
    printf("Done! total_nodes=%lld total_k_leaves=%lld mixed_kh_leaves=%lld\n",
           total_nodes, total_k_leaves, mixed_kh_leaves);
    return 0;
}
