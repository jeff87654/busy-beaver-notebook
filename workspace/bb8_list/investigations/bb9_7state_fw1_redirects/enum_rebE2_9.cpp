#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <windows.h>

struct Trans {
    int w;   // 0 or 1; -1 for HALT (---); -2 for UNASSIGNED
    int dir; // -1 for L, +1 for R
    int nxt; // 0..8 (A..I)
};

static const char* BASE_STR = "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC_------_------";
Trans base_tr[18];

void init_base() {
    for (int q = 0; q < 9; ++q) {
        for (int b = 0; b < 2; ++b) {
            const char* p = BASE_STR + q * 7 + b * 3;
            if (p[0] == '-') base_tr[2 * q + b] = {-2, 0, 0};
            else base_tr[2 * q + b] = {p[0] - '0', (p[1] == 'R') ? 1 : -1, p[2] - 'A'};
        }
    }
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

struct SimRes {
    char kind; // 'K' (reached K), 'U' (hit unassigned -2), 'H' (hit halt -1), 'T' (timeout/oob)
    int step;
    int slot;
    std::vector<int> ds; // [d_k, ..., d_1]
    int a;
};

// Check if real unmirrored tape is at canonical b=1 K-config of reb_E2:
// [F0] 0 1 0 1^a 0 1^(d_1) 0 ... 0 1^(d_k)
// Note: F is state 5, reading 0 at h = mn - 1, where tape[mn] == 0? Wait:
// In reb_E2: kl.word(ds, a, 1) = 1^(d_k) 0 ... 1^(d_1) 0 1^a 0 1 0.
// Placed at 0, -1, ..., -(L-1) with head at -L in state F (5).
// So at -L: tape[-L] = 0 (head is here in state F).
// At -L+1: 0 (the trailing '0' of '1 0').
// At -L+2: 1 (the '1' of '1 0', since b=1).
// At -L+3: 0 (separator before 1^a).
// Then 1^a (a >= 1), then 0, then 1^(d_1), 0, ..., 1^(d_k) at mx!
bool check_K_rebE2(const unsigned char* tape, int lo, int hi, int h, int q, std::vector<int>& ds_out, int& a_out) {
    if (q != 5 || tape[h] != 0) return false;
    int mn = hi + 1, mx = lo - 1;
    for (int i = lo; i <= hi; ++i) {
        if (tape[i]) {
            if (i < mn) mn = i;
            if (i > mx) mx = i;
        }
    }
    if (mn > mx) return false;
    // The leftmost '1' on the tape must be at h + 2 (so tape[h] = 0, tape[h+1] = 0, tape[h+2] = 1, tape[h+3] = 0)
    if (mn != h + 2) return false;
    if (h + 4 > mx) return false;
    if (tape[h + 1] != 0 || tape[h + 2] != 1 || tape[h + 3] != 0) return false;

    int pos = h + 4;
    std::vector<int> runs;
    while (pos <= mx) {
        int ones = 0;
        while (pos <= mx && tape[pos] == 1) {
            ones++;
            pos++;
        }
        runs.push_back(ones);
        if (pos <= mx) {
            if (tape[pos] != 0) return false;
            pos++; // skip single '0' separator
        }
    }
    if (runs.empty() || runs[0] < 1) return false;
    a_out = runs[0];
    ds_out.clear();
    for (int i = (int)runs.size() - 1; i >= 1; --i) {
        ds_out.push_back(runs[i]);
    }
    return true;
}

SimRes run_sim(const Trans* tr, const std::vector<int>* init_ds, int init_a, int max_steps, int min_k_len) {
    const int SZ = 4096;
    const int OFF = 2048;
    unsigned char tape[SZ];
    memset(tape, 0, SZ);

    int h = OFF, q = 0, lo = OFF, hi = OFF;
    if (init_ds != nullptr) {
        // Place [F0] 0 1 0 1^a 0 1^(d_1) 0 ... 0 1^(d_k)
        int pos = OFF;
        h = pos;
        q = 5; // F
        pos += 2; // tape[h]=0, tape[h+1]=0
        tape[pos++] = 1;
        tape[pos++] = 0;
        for (int i = 0; i < init_a; ++i) tape[pos++] = 1;
        for (int idx = (int)init_ds->size() - 1; idx >= 0; --idx) {
            tape[pos++] = 0;
            int d = (*init_ds)[idx];
            for (int i = 0; i < d; ++i) tape[pos++] = 1;
        }
        lo = h;
        hi = pos;
    }

    for (int step = 1; step <= max_steps; ++step) {
        int b = tape[h];
        int slot = 2 * q + b;
        const Trans& act = tr[slot];
        if (act.w == -2) return {'U', step, slot, {}, 0};
        if (act.w == -1) return {'H', step, slot, {}, 0};
        tape[h] = (unsigned char)act.w;
        h += act.dir;
        q = act.nxt;
        if (h < 8 || h >= SZ - 8) return {'T', step, -1, {}, 0};
        if (h - 2 < lo) lo = h - 2;
        if (h + 2 > hi) hi = h + 2;

        if (q == 5 && tape[h] == 0) {
            std::vector<int> ds;
            int a;
            if (check_K_rebE2(tape, lo, hi, h, q, ds, a)) {
                if ((int)ds.size() >= min_k_len) {
                    if (init_ds == nullptr || ds != *init_ds) {
                        return {'K', step, -1, ds, a};
                    }
                }
            }
        }
    }
    return {'T', max_steps, -1, {}, 0};
}

std::string fmt_ds(const std::vector<int>& ds) {
    std::string s = "[";
    for (size_t i = 0; i < ds.size(); ++i) {
        if (i > 0) s += ",";
        s += std::to_string(ds[i]);
    }
    s += "]";
    return s;
}

FILE* out_fp = nullptr;
long long total_nodes = 0;
long long valid_db_leaves = 0;
long long halting_e_leaves = 0;

void dfs(Trans* tr, int redir_slot, int assigned_count, int max_state) {
    total_nodes++;

    // 1. Test D: [5, 4]; 3 -> [5, 2]; 9
    static const std::vector<int> d_in = {5, 4}, d_exp = {5, 2};
    SimRes r_d = run_sim(tr, &d_in, 3, 400, 2);
    if (r_d.kind == 'K') {
        if (r_d.ds != d_exp || r_d.a != 9) return; // broken D
    } else if (r_d.kind != 'U') {
        return; // broken D without hitting unassigned
    }

    // 2. Test B1: [5, 4, 0]; 9 -> [5, 2, 18]; 3
    static const std::vector<int> b1_in = {5, 4, 0}, b1_exp = {5, 2, 18};
    SimRes r_b1 = run_sim(tr, &b1_in, 9, 1000, 3);
    if (r_b1.kind == 'K') {
        if (r_b1.ds != b1_exp || r_b1.a != 3) return; // broken B1
    } else if (r_b1.kind != 'U') {
        return;
    }

    // 3. Test B2: [5, 4, 0, 0]; 9 -> [5, 2, 16, 2]; 3
    static const std::vector<int> b2_in = {5, 4, 0, 0}, b2_exp = {5, 2, 16, 2};
    SimRes r_b2 = run_sim(tr, &b2_in, 9, 1200, 4);
    if (r_b2.kind == 'K') {
        if (r_b2.ds != b2_exp || r_b2.a != 3) return; // broken B2
    } else if (r_b2.kind != 'U') {
        return;
    }

    // 4. Test Blank -> K with len >= 4
    SimRes r_bl = run_sim(tr, nullptr, 0, 2000, 4);
    if (r_bl.kind != 'K' && r_bl.kind != 'U') return;

    // Find first unassigned slot hit among D, B1, B2, Blank, and E1
    int u_slot = -1;
    if (r_d.kind == 'U') u_slot = r_d.slot;
    else if (r_b1.kind == 'U') u_slot = r_b1.slot;
    else if (r_b2.kind == 'U') u_slot = r_b2.slot;
    else if (r_bl.kind == 'U') u_slot = r_bl.slot;

    static const std::vector<int> e1_k5 = {1, 0, 0, 0, 0, 0};
    static const std::vector<int> e2_k5 = {1, 0, 0, 0, 0, 0, 1};
    SimRes r_e1_7 = {'T', 0, -1, {}, 0};
    SimRes r_e1_9 = {'T', 0, -1, {}, 0};
    SimRes r_e2_7 = {'T', 0, -1, {}, 0};

    if (u_slot == -1) {
        r_e1_7 = run_sim(tr, &e1_k5, 7, 4000, 4);
        r_e1_9 = run_sim(tr, &e1_k5, 9, 4000, 4);
        r_e2_7 = run_sim(tr, &e2_k5, 7, 4000, 4);
        if (r_e1_7.kind == 'U') u_slot = r_e1_7.slot;
        else if (r_e1_9.kind == 'U') u_slot = r_e1_9.slot;
        else if (r_e2_7.kind == 'U') u_slot = r_e2_7.slot;
    }

    if (u_slot == -1 || assigned_count >= 4) {
        // Leaf! Verify D, B1, B2, Blank are all 'K'
        if (r_d.kind == 'K' && r_b1.kind == 'K' && r_b2.kind == 'K' && r_bl.kind == 'K') {
            valid_db_leaves++;
            bool e1_halt = (r_e1_7.kind == 'H' || r_e1_7.kind == 'U') && (r_e1_9.kind == 'H' || r_e1_9.kind == 'U');
            bool e2_halt = (r_e1_7.kind == 'K' && r_e1_9.kind == 'K' && (r_e2_7.kind == 'H' || r_e2_7.kind == 'U'));
            bool e1_diff = (r_e1_7.kind == 'K' && (r_e1_7.ds != std::vector<int>{5,2,3,0,2,2,2,2} || r_e1_7.a != 3));
            if (e1_halt || e2_halt || e1_diff) {
                if (e1_halt || e2_halt) halting_e_leaves++;
                char buf[128];
                format_tr(tr, buf);
                fprintf(out_fp, "redir=%c%d\t%s\t%s\tblank=%s;%d@%d\tE1(7)=%c@%d\tE1(9)=%c@%d\tE2(7)=%c@%d\n",
                    'A' + (redir_slot / 2), redir_slot % 2,
                    e2_halt ? "E2_HALT" : (e1_halt ? "E1_HALT" : "E1_MOD"),
                    buf,
                    fmt_ds(r_bl.ds).c_str(), r_bl.a, r_bl.step,
                    r_e1_7.kind, r_e1_7.step,
                    r_e1_9.kind, r_e1_9.step,
                    r_e2_7.kind, r_e2_7.step);
                fflush(out_fp);
            }
        }
        return;
    }

    // Branch 1: Set u_slot to HALT (-1)
    tr[u_slot] = {-1, 0, 0};
    dfs(tr, redir_slot, assigned_count, max_state);

    // Branch 2: Assign u_slot to a non-halting transition (if assigned_count < 4)
    int lim_state = (max_state < 8) ? (max_state + 1) : 8;
    for (int nxt = 0; nxt <= lim_state; ++nxt) {
        int next_max = (nxt > max_state) ? nxt : max_state;
        for (int w = 0; w < 2; ++w) {
            for (int d = -1; d <= 1; d += 2) {
                tr[u_slot] = {w, d, nxt};
                dfs(tr, redir_slot, assigned_count + 1, next_max);
            }
        }
    }
    tr[u_slot] = {-2, 0, 0};
}

int main() {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    init_base();
    out_fp = fopen("enum_rebE2_9.tsv", "w");
    fprintf(out_fp, "redir\ttype\tmachine\tblank\tE1_7\tE1_9\tE2_7\n");

    // Redirect each of the 13 defined slots of reb_E2:
    // Choice A: redirect slot to H (state 7), keeping same or different w, dir
    // Choice B: for A0 specifically (slot 0), test all assignments of A0 + {G0, H0, H1, I0, I1}!
    for (int sl = 0; sl < 14; ++sl) {
        if (base_tr[sl].w < 0) continue; // skip G0 (12)
        Trans tr[18];
        memcpy(tr, base_tr, sizeof(base_tr));
        if (sl == 0) {
            // Unassign A0 completely and let DFS branch on A0 + {G0, H0, H1, I0, I1} (up to 5 non-halting among 6 slots)
            tr[0] = {-2, 0, 0};
            dfs(tr, sl, -1, 6);
        } else {
            // Redirect sl to state H (7) with original (w, dir)
            tr[sl].nxt = 7;
            dfs(tr, sl, 0, 7);
        }
        printf("Finished slot %c%d: total_nodes=%lld, valid_db=%lld, halting_e=%lld\n",
               'A' + (sl / 2), sl % 2, total_nodes, valid_db_leaves, halting_e_leaves);
        fflush(stdout);
    }
    fclose(out_fp);
    return 0;
}
