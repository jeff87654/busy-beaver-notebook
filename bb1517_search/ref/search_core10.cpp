#include <cstdio>
#include <cstring>
#include <vector>

struct Trans {
    int w;   // 0 or 1
    int mv;  // -1 or +1
    int nst; // 0..12 for A..M, 13 for Z, -1 for UNDEF
};

Trans trans[13][2];
Trans choices[53];
int n_choices = 0;
int max_states = 13; // 12 (no K) or 13

void init_base(int n_st) {
    max_states = n_st;
    for (int s = 0; s < 13; ++s)
        for (int b = 0; b < 2; ++b)
            trans[s][b] = {-1, 0, -1};

    auto set = [&](char st, int b, int w, char dir, char nst) {
        trans[st - 'A'][b] = {w, dir == 'L' ? -1 : 1, nst - 'A'};
    };
    // 10-state core: A, B, C, D, E, F, G, H, L, M (17 transitions fixed!)
    // Free in core: A0, E0, F0
    // Free states: I (I0, I1), J (J0, J1), and K (K0, K1) if n_st == 13
                              set('A', 1, 0, 'L', 'L');
    set('B', 0, 1, 'R', 'A'); set('B', 1, 1, 'R', 'C');
    set('C', 0, 0, 'L', 'D'); set('C', 1, 1, 'L', 'G');
    set('D', 0, 0, 'R', 'E'); set('D', 1, 1, 'L', 'D');
                              set('E', 1, 1, 'R', 'F');
                              set('F', 1, 0, 'R', 'M');
    set('G', 0, 1, 'R', 'M'); set('G', 1, 0, 'L', 'H');
    set('H', 0, 1, 'L', 'G'); set('H', 1, 1, 'L', 'H');
    set('L', 0, 1, 'L', 'H'); set('L', 1, 1, 'L', 'A');
    set('M', 0, 1, 'R', 'B'); set('M', 1, 1, 'R', 'M');

    n_choices = 0;
    for (int w = 0; w < 2; ++w)
        for (int mv : {-1, 1})
            for (int s = 0; s < 13; ++s) {
                if (n_st == 12 && s == ('K' - 'A')) continue;
                choices[n_choices++] = {w, mv, s};
            }
    choices[n_choices++] = {1, 1, 13}; // 1RZ
}

struct Res {
    int kind; // 0=BAD, 1=UNDEF, 2=HALT, 3=C_REL, 4=D_REL
    int undef_st;
    int undef_sym;
    int p_out, a_out, c_out, d_out;
};

// Simulate from Ca_exit(p, a, c=0, d):
// tape: 0^20 (10)^p 1^(a+2) [0] 1^d 0*
// Head starts at [0] in state A.
// Look for return to state A on the first '1' of (10)^c_out:
// Left of pos: 0+ (10)^p_out 1^(a_out+2) with a_out >= 0 EVEN (ones_a >= 2 even)
// Right of pos: (10)^c_out 0 1^d_out 0* with c_out >= 1
Res sim_ca(int p, int d, int A, int delta_d, int max_steps = 180) {
    int tape[100];
    memset(tape, 0, sizeof(tape));
    int idx = 24;
    for (int i = 0; i < p; ++i) {
        tape[idx++] = 1;
        tape[idx++] = 0;
    }
    for (int i = 0; i < A + 2; ++i) tape[idx++] = 1;
    int pos = idx;
    tape[idx++] = 0;
    for (int i = 0; i < d; ++i) tape[idx++] = 1;

    int st = 'A' - 'A';
    for (int step = 1; step <= max_steps; ++step) {
        if (pos < 2 || pos >= 98) return {0, 0, 0, 0, 0, 0, 0};
        int sym = tape[pos];
        Trans t = trans[st][sym];
        if (t.nst == -1) return {1, st, sym, 0, 0, 0, 0};
        if (t.nst == 13) return {2, 0, 0, 0, 0, 0, 0};
        tape[pos] = t.w;
        pos += t.mv;
        st = t.nst;

        if (st == ('A' - 'A') && pos >= 4 && pos < 96 && tape[pos] == 1 && tape[pos + 1] == 0) {
            int i = pos - 1;
            int ones_a = 0;
            while (i >= 0 && tape[i] == 1) { ones_a++; i--; }
            if (ones_a < 2 || (ones_a % 2) != 0) continue;
            int p_out = 0;
            while (i >= 1 && tape[i] == 0 && tape[i - 1] == 1) {
                p_out++;
                i -= 2;
            }
            bool ok_left = (i >= 1);
            for (int k = 0; k <= i; ++k) if (tape[k] != 0) { ok_left = false; break; }
            if (!ok_left) continue;

            int j = pos;
            int c_out = 0;
            while (j + 1 < 100 && tape[j] == 1 && tape[j + 1] == 0) {
                c_out++;
                j += 2;
            }
            if (c_out < 1) continue;
            if (j >= 100 || tape[j] != 0) continue;
            j++; // skip the 0 separator after (10)^c_out
            int d_out = 0;
            while (j < 100 && tape[j] == 1) { d_out++; j++; }
            bool ok_right = true;
            for (int k = j; k < 100; ++k) if (tape[k] != 0) { ok_right = false; break; }
            if (!ok_right) continue;

            int a_out = ones_a - 2;
            if (c_out >= (A / 2) && d >= delta_d && d_out == d - delta_d)
                return {3, 0, 0, p_out, a_out, c_out, d_out};
            if (c_out >= 1 && d_out >= (A / 2))
                return {4, 0, 0, p_out, a_out, c_out, d_out};
            return {0, 0, 0, 0, 0, 0, 0};
        }
    }
    return {0, 0, 0, 0, 0, 0, 0};
}

void print_machine(const char* tag, int n_def, const std::vector<Res>& res) {
    printf("[%s n_def=%d] ", tag, n_def);
    for (int s = 0; s < 13; ++s) {
        if (max_states == 12 && s == ('K' - 'A')) continue;
        for (int b = 0; b < 2; ++b) {
            Trans t = trans[s][b];
            if (t.nst == -1) printf("---");
            else if (t.nst == 13) printf("1RZ");
            else printf("%d%c%c", t.w, t.mv == -1 ? 'L' : 'R', 'A' + t.nst);
        }
        if (s < 12) printf("_");
    }
    for (size_t i = 0; i < res.size(); ++i) {
        printf(" | %zu:k%d(p%d,a%d,c%d,d%d)", i, res[i].kind, res[i].p_out, res[i].a_out, res[i].c_out, res[i].d_out);
    }
    printf("\n");
    fflush(stdout);
}

struct Test { int p, d, A; };
long long nodes = 0;
int crel_by_ndef[10] = {0};
int hits = 0;

void dfs(int idx, int n_def, int max_crel_def, int max_tot_def, bool used_i, bool used_j, bool has_z, int delta_d, std::vector<Res>& results) {
    nodes++;
    Test tests[7] = {
        {2, delta_d, 8}, {2, delta_d + 1, 8}, {2, delta_d, 6}, {2, delta_d + 1, 6},
        {2, 0, 8}, {2, 1, 8}, {1, 0, 8}
    };
    if (idx == 2) {
        if (results[0].c_out != results[1].c_out || results[0].p_out != results[1].p_out || results[0].a_out != results[1].a_out) return;
    }
    if (idx == 3) {
        if (results[0].c_out <= results[2].c_out) return;
    }
    if (idx == 4) {
        if (results[2].c_out != results[3].c_out) return;
        crel_by_ndef[n_def]++;
    }
    if (idx == 7) {
        int k_d0 = results[4].kind;
        int k_d1 = results[5].kind;
        int k_p1 = results[6].kind;
        if (delta_d == 2 && ((k_d0 == 4 && k_d1 == 2) || (k_d0 == 2 && k_d1 == 4))) {
            hits++;
            bool parity_ok = (k_d0 == 4 && (results[4].d_out % 2 == 1)) || (k_d1 == 4 && (results[5].d_out % 2 == 0));
            print_machine(parity_ok ? "HIT_D0_VS_D1_PARITY_OK" : "HIT_D0_VS_D1", n_def, results);
        }
        if ((k_d0 == 4 && k_p1 == 2) || (k_d0 == 2 && k_p1 == 4)) {
            hits++;
            print_machine("HIT_P1_VS_P2", n_def, results);
        }
        return;
    }
    Res r = sim_ca(tests[idx].p, tests[idx].d, tests[idx].A, delta_d);
    if (r.kind == 1) {
        if (idx < 4 && n_def >= max_crel_def) return;
        if (n_def >= max_tot_def) return;
        // At most max_tot_def - 1 non-halt transitions if we still need to place 1RZ
        if (!has_z && n_def == max_tot_def - 1 && idx < 4) return;
        int st = r.undef_st, sym = r.undef_sym;
        for (int i = 0; i < n_choices; ++i) {
            Trans ch = choices[i];
            if (ch.nst == 13 && (idx < 4 || has_z)) continue;
            if (!has_z && n_def == max_tot_def - 1 && ch.nst != 13) continue;
            // TNF symmetry on free states I, J, K:
            if (ch.nst == ('J' - 'A') && !used_i) continue;
            if (ch.nst == ('K' - 'A') && !used_j) continue;
            // A0 must move right to read d!
            if (st == ('A' - 'A') && sym == 0 && ch.mv != 1) continue;
            trans[st][sym] = ch;
            dfs(idx, n_def + 1, max_crel_def, max_tot_def,
                used_i || (ch.nst == ('I' - 'A')),
                used_j || (ch.nst == ('J' - 'A')),
                has_z || (ch.nst == 13), delta_d, results);
            trans[st][sym] = {-1, 0, -1};
        }
        return;
    }
    if (idx < 4 && r.kind != 3) return;
    results.push_back(r);
    dfs(idx + 1, n_def, max_crel_def, max_tot_def, used_i, used_j, has_z, delta_d, results);
    results.pop_back();
}

int main() {
    std::vector<Res> results;

    for (int d_step : {1, 2, 3}) {
        printf("=== 12 STATES (7 free slots), delta_d = %d ===\n", d_step); fflush(stdout);
        init_base(12);
        memset(crel_by_ndef, 0, sizeof(crel_by_ndef)); nodes = 0; hits = 0;
        dfs(0, 0, 6, 7, false, false, false, d_step, results);
        printf("Done 12st d=%d: nodes=%lld, hits=%d\n", d_step, nodes, hits);
        for (int i = 0; i < 8; ++i) if (crel_by_ndef[i]) printf("  crel_by_ndef[%d] = %d\n", i, crel_by_ndef[i]);
    }

    return 0;
}
