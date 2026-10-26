#include <cstdio>
#include <cstring>
#include <vector>

struct Trans {
    int w;   // 0 or 1
    int mv;  // -1 or +1
    int nst; // 0..12 for A..M, 13 for Z, -1 for UNDEF
};

Trans trans[13][2];
Trans choices[52];
int n_choices = 0;

void init_base() {
    for (int s = 0; s < 13; ++s)
        for (int b = 0; b < 2; ++b)
            trans[s][b] = {-1, 0, -1};

    auto set = [&](char st, int b, int w, char dir, char nst) {
        trans[st - 'A'][b] = {w, dir == 'L' ? -1 : 1, nst - 'A'};
    };
    set('A', 0, 0, 'L', 'H'); set('A', 1, 0, 'L', 'L');
    set('B', 0, 1, 'R', 'I'); set('B', 1, 1, 'R', 'C');
    set('C', 0, 0, 'L', 'D'); set('C', 1, 1, 'L', 'G');
    set('D', 0, 0, 'R', 'E'); set('D', 1, 1, 'L', 'D');
                              set('E', 1, 1, 'R', 'F');
                              set('F', 1, 0, 'R', 'M');
    set('G', 0, 1, 'R', 'M'); set('G', 1, 0, 'L', 'H');
    set('H', 0, 1, 'L', 'G'); set('H', 1, 1, 'L', 'H');
                              set('I', 1, 0, 'L', 'A');
    set('L', 0, 1, 'L', 'H'); set('L', 1, 1, 'L', 'A');
    set('M', 0, 1, 'R', 'B'); set('M', 1, 1, 'R', 'M');

    n_choices = 0;
    for (int w = 0; w < 2; ++w)
        for (int mv : {-1, 1})
            for (int s = 0; s < 13; ++s)
                choices[n_choices++] = {w, mv, s};
}

struct Res {
    int kind; // 0=BAD, 1=UNDEF, 2=HALT, 3=C_REL, 4=D_REL
    int undef_st;
    int undef_sym;
    int p_out, a_out, c_out, d_out;
};

Res sim_ci(int p, int d, int A, int max_steps = 160) {
    int tape[96];
    memset(tape, 0, sizeof(tape));
    int idx = 20;
    for (int i = 0; i < p; ++i) {
        tape[idx++] = 1;
        tape[idx++] = 0;
    }
    for (int i = 0; i < A + 1; ++i) tape[idx++] = 1;
    int pos = idx;
    tape[idx++] = 0;
    for (int i = 0; i < d; ++i) tape[idx++] = 1;

    int st = 'I' - 'A';
    for (int step = 1; step <= max_steps; ++step) {
        if (pos < 2 || pos >= 94) return {0, 0, 0, 0, 0, 0, 0};
        int sym = tape[pos];
        Trans t = trans[st][sym];
        if (t.nst == -1) return {1, st, sym, 0, 0, 0, 0};
        tape[pos] = t.w;
        pos += t.mv;
        st = t.nst;

        if (st == ('I' - 'A') && pos >= 4 && pos < 94 && tape[pos] == 1) {
            int i = pos - 1;
            int ones_a = 0;
            while (i >= 0 && tape[i] == 1) { ones_a++; i--; }
            if (ones_a < 1) continue;
            int p_out = 0;
            while (i >= 1 && tape[i] == 0 && tape[i - 1] == 1) {
                p_out++;
                i -= 2;
            }
            if (ones_a == 1 && p_out == 0) continue;
            bool ok_left = (i >= 1);
            for (int k = 0; k <= i; ++k) if (tape[k] != 0) { ok_left = false; break; }
            if (!ok_left) continue;

            int j = pos;
            int c_out = 0;
            while (j < 96 && tape[j] == 1) { c_out++; j++; }
            int d_out = 0;
            if (j < 96 && tape[j] == 0) {
                j++;
                while (j < 96 && tape[j] == 1) { d_out++; j++; }
            }
            bool ok_right = true;
            for (int k = j; k < 96; ++k) if (tape[k] != 0) { ok_right = false; break; }
            if (!ok_right) continue;

            int a_out = ones_a - 1;
            if (c_out >= A - 1 && d >= 1 && d_out == d - 1)
                return {3, 0, 0, p_out, a_out, c_out, d_out};
            if (c_out >= 1 && d_out >= A - 2 && d == 0)
                return {4, 0, 0, p_out, a_out, c_out, d_out};
            return {0, 0, 0, 0, 0, 0, 0};
        }
    }
    return {0, 0, 0, 0, 0, 0, 0};
}

struct Test { int p, d, A; };
int both_by_ndef[8] = {0};

void dfs_both(int idx, int n_def, bool used_j, std::vector<Res>& results) {
    static const Test tests[5] = {
        {4, 1, 8}, {4, 2, 8}, {4, 1, 7}, {4, 2, 7},
        {4, 0, 8}
    };
    if (idx == 5) {
        both_by_ndef[n_def]++;
        if (n_def <= 7) {
            printf("[BOTH n_def=%d] ", n_def);
            for (int s = 0; s < 13; ++s) {
                for (int b = 0; b < 2; ++b) {
                    Trans t = trans[s][b];
                    if (t.nst == -1) printf("---");
                    else printf("%d%c%c", t.w, t.mv == -1 ? 'L' : 'R', 'A' + t.nst);
                }
                if (s < 12) printf("_");
            }
            printf(" | d0: p=%d,a=%d,c=%d,d=%d\n", results[4].p_out, results[4].a_out, results[4].c_out, results[4].d_out);
            fflush(stdout);
        }
        return;
    }
    Res r = sim_ci(tests[idx].p, tests[idx].d, tests[idx].A);
    if (r.kind == 1) {
        if (n_def >= 7) return;
        int st = r.undef_st, sym = r.undef_sym;
        for (int i = 0; i < n_choices; ++i) {
            Trans ch = choices[i];
            if (ch.nst == ('K' - 'A') && !used_j) continue;
            if (st == ('I' - 'A') && sym == 0 && ch.mv != 1) continue;
            trans[st][sym] = ch;
            dfs_both(idx, n_def + 1, used_j || (ch.nst == ('J' - 'A')), results);
            trans[st][sym] = {-1, 0, -1};
        }
        return;
    }
    if (idx < 4 && r.kind != 3) return;
    if (idx == 4 && r.kind != 4) return;
    results.push_back(r);
    dfs_both(idx + 1, n_def, used_j, results);
    results.pop_back();
}

int main() {
    init_base();
    std::vector<Res> results;
    dfs_both(0, 0, false, results);
    for (int i = 0; i < 8; ++i) printf("both_by_ndef[%d] = %d\n", i, both_by_ndef[i]);
    return 0;
}
