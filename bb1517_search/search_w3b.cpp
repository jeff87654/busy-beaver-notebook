// Route 1b: genuine 3-counter (f_{w+3}) search on the M13 10-state core.
//
// Difference from search_w3.cpp: the D_REL gadget must *create* the outer
// counter e when it is absent, decrement it when present (e >= 2), and halt
// when e == 1.  That is what turns f_{w+2} into f_{w+3}: the d-run (an
// f_{w+2} computation) is repeated e times, and e is initialised from the
// accumulator at the first d-exhaustion.
//
// Fixed core (17 transitions), core labels A..M:
//   A1=0LL  B0=1RA B1=1RC  C0=0LD C1=1LG  D0=0RE D1=1LD  E1=1RF
//   F1=0RM  G0=1RM G1=0LH  H0=1LG H1=1LH  L0=1LH L1=1LA  M0=1RB M1=1RM
// C_REL gadget preset (as in M13/M15):
//   A0=1RI I1=1RJ J0=1RE J1=0LA K0=1RA K1=0RF F0=1LI E0=1RZ
// Searched: I0 (D_REL entry) and the extra outer states N,O,(P,Q).
//
// Test configuration Ce3(p,a,c=0,d,e):
//   left  : (10)^p 1^(a+2) 0^inf
//   head  : state A on the 0 that follows 1^(a+2)   (c = 0 entry)
//   right : 0 1^d 0 (gap-1 zeros) 1^e 0^inf
// Requirements (dd = 2):
//   C_REL : d>=2 -> d-=2, e unchanged
//   A     : d==0, e absent -> e' >= a/2 created, d' even > 0
//   B     : d==0, e>=2     -> e' = e-1, d' even > 0
//   C     : d==0, e==1     -> HALT
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

static const int MAXT = 400;      // tape cells
static const int MAXS = 500;      // steps per test
static int GAP = 1;               // zeros between the d block and the e block

struct Trans { int w, mv, nst; }; // nst: 0..16 state, 20 = Z, -1 = UNDEF
static Trans tr[17][2];
static int n_states = 15;
static Trans choices[80];
static int n_choices = 0;

static int free_states[8], n_free = 0;

static void init_base(int ns) {
    n_states = ns;
    for (int s = 0; s < 17; ++s) for (int b = 0; b < 2; ++b) tr[s][b] = {-1, 0, -1};
    auto set = [&](char st, int b, int w, char dir, char nst) {
        tr[st - 'A'][b] = {w, dir == 'L' ? -1 : 1, nst - 'A'};
    };
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

    static const int idx[7] = {8, 9, 10, 13, 14, 15, 16};
    n_free = 0;
    for (int i = 0; i < 7; ++i) {
        if (idx[i] < ns) free_states[n_free++] = idx[i];
        else break;
    }
    n_choices = 0;
    for (int w = 0; w < 2; ++w)
        for (int mv : {-1, 1})
            for (int s = 0; s < ns; ++s) choices[n_choices++] = {w, mv, s};
    choices[n_choices++] = {1, 1, 20};   // 1RZ
}

struct Res { int kind; int us, ub; int p, a, c, d, e; };
// kind: 0 BAD, 1 UNDEF, 2 HALT, 3 RET

static Res sim(int p, int a, int d, int e) {
    static int tape[MAXT];
    memset(tape, 0, sizeof(tape));
    int idx = 24;
    for (int i = 0; i < p; ++i) { tape[idx++] = 1; tape[idx++] = 0; }
    for (int i = 0; i < a + 2; ++i) tape[idx++] = 1;
    int pos = idx;                       // head on the separator 0
    tape[idx++] = 0;
    for (int i = 0; i < d; ++i) tape[idx++] = 1;
    tape[idx++] = 0;
    for (int g = 1; g < GAP; ++g) tape[idx++] = 0;
    for (int i = 0; i < e; ++i) tape[idx++] = 1;

    int st = 0;                          // state A
    for (int step = 1; step <= MAXS; ++step) {
        if (pos < 2 || pos >= MAXT - 2) return {0, 0, 0, 0, 0, 0, 0, 0};
        int sym = tape[pos];
        Trans t = tr[st][sym];
        if (t.nst == -1) return {1, st, sym, 0, 0, 0, 0, 0};
        if (t.nst == 20) return {2, 0, 0, 0, 0, 0, 0, 0};
        tape[pos] = t.w; pos += t.mv; st = t.nst;

        if (st == 0 && pos >= 4 && pos < MAXT - 4 && tape[pos] == 1 && tape[pos + 1] == 0) {
            int i = pos - 1, ones_a = 0;
            while (i >= 0 && tape[i] == 1) { ones_a++; i--; }
            if (ones_a < 2 || (ones_a & 1)) continue;
            int p_out = 0;
            while (i >= 1 && tape[i] == 0 && tape[i - 1] == 1) { p_out++; i -= 2; }
            if (i < 1) continue;
            bool ok = true;
            for (int k = 0; k <= i; ++k) if (tape[k]) { ok = false; break; }
            if (!ok) continue;
            int j = pos, c_out = 0;
            while (j + 1 < MAXT && tape[j] == 1 && tape[j + 1] == 0) { c_out++; j += 2; }
            if (c_out < 1 || j >= MAXT || tape[j] != 0) continue;
            j++;
            int d_out = 0;
            while (j < MAXT && tape[j] == 1) { d_out++; j++; }
            if (j >= MAXT || tape[j] != 0) continue;
            j++;
            for (int g = 1; g < GAP; ++g) { if (tape[j] != 0) { ok = false; break; } j++; }
            if (!ok) continue;
            int e_out = 0;
            while (j < MAXT && tape[j] == 1) { e_out++; j++; }
            for (int k = j; k < MAXT; ++k) if (tape[k]) { ok = false; break; }
            if (!ok) continue;
            return {3, 0, 0, p_out, ones_a - 2, c_out, d_out, e_out};
        }
    }
    return {0, 0, 0, 0, 0, 0, 0, 0};
}

struct Test { int p, a, d, e; };
static const int DD = 2;
static Test tests[7] = {
    {3, 8, DD,     2},   // 0 C_REL base
    {3, 8, DD + 1, 2},   // 1 C_REL d+1 (independence of d)
    {3, 8, DD,     3},   // 2 C_REL e+1 (independence of e)
    {3, 8, 0,      0},   // 3 D_REL e absent -> create e
    {3, 8, 0,      2},   // 4 D_REL e=2 -> e-1
    {3, 8, 0,      3},   // 5 D_REL e=3 -> e-1 (independence)
    {3, 8, 0,      1},   // 6 D_REL e=1 -> HALT
};

static long long nodes = 0, hits = 0;
static long long reach[8] = {0};
static int stop_after = 7;
static int fix_crel = 1;
static FILE *out = nullptr;

static void print_machine(const char *tag, int n_def) {
    fprintf(out, "[%s n_st=%d n_def=%d] ", tag, n_states, n_def);
    for (int s = 0; s < n_states; ++s) {
        if (s) fputc('_', out);
        for (int b = 0; b < 2; ++b) {
            Trans t = tr[s][b];
            if (t.nst == -1) fputs("---", out);
            else if (t.nst == 20) fputs("1RZ", out);
            else fprintf(out, "%d%c%c", t.w, t.mv == -1 ? 'L' : 'R', 'A' + t.nst);
        }
    }
    fputc('\n', out); fflush(out);
}

static bool check(int idx, const Res &r, const std::vector<Res> &prev) {
    if (idx <= 2) {
        if (r.kind != 3) return false;
        if (r.d != tests[idx].d - DD) return false;      // C_REL: d -= DD
        if (r.e != tests[idx].e) return false;           // e untouched
        if (r.p >= tests[idx].p) return false;           // some progress
        if (r.a < 2 || (r.a & 1)) return false;          // a stays even
        if (r.c < tests[idx].a / 2) return false;
        if (idx == 1) {
            if (r.p != prev[0].p || r.a != prev[0].a || r.c != prev[0].c || r.e != prev[0].e) return false;
        }
        if (idx == 2) {
            if (r.p != prev[0].p || r.a != prev[0].a || r.c != prev[0].c || r.d != prev[0].d) return false;
        }
        return true;
    }
    if (idx == 3) {                                      // create e from a
        if (r.kind != 3) return false;
        if (r.e < tests[3].a / 2) return false;          // e' >= a/2
        if (r.d < 2 || (r.d & 1)) return false;          // d' even
        if (r.p >= tests[3].p) return false;
        if (r.a < 2 || (r.a & 1)) return false;
        if (r.c < 1) return false;
        return true;
    }
    if (idx == 4 || idx == 5) {                          // D_REL: e -= 1
        if (r.kind != 3) return false;
        if (r.e != tests[idx].e - 1) return false;
        if (r.d < 2 || (r.d & 1)) return false;          // d' even
        if (r.p >= tests[idx].p) return false;
        if (r.a < 2 || (r.a & 1)) return false;
        if (r.c < 1) return false;
        if (idx == 5) {
            if (r.p != prev[4].p || r.a != prev[4].a || r.c != prev[4].c || r.d != prev[4].d) return false;
        }
        return true;
    }
    return false;                                        // idx 6: halt
}

static void preset() {
    auto set = [&](char st, int b, int w, char dir, char nst) {
        tr[st - 'A'][b] = {w, dir == 'L' ? -1 : 1, nst - 'A'};
    };
    set('A', 0, 1, 'R', 'I');
    set('I', 1, 1, 'R', 'J');
    set('J', 0, 1, 'R', 'E');
    set('J', 1, 0, 'L', 'A');
    set('K', 0, 1, 'R', 'A');
    set('K', 1, 0, 'R', 'F');
    set('F', 0, 1, 'L', 'I');
    set('E', 0, 1, 'R', 'Z');
}

static void mark_preset(int &used_mask) {
    for (int k = 0; k < n_free; ++k) {
        int s = free_states[k];
        for (int b = 0; b < 2; ++b) if (tr[s][b].nst != -1) used_mask |= (1 << k);
    }
}

static void dfs(int idx, int n_def, int max_def, int used_mask, std::vector<Res> &prev);

static bool try_choices(int idx, int st, int sym, int n_def, int max_def, int used_mask,
                        std::vector<Res> &prev) {
    for (int i = 0; i < n_choices; ++i) {
        Trans ch = choices[i];
        int nm = used_mask;
        if (ch.nst < 17 && ch.nst != 20) {
            int fi = -1;
            for (int k = 0; k < n_free; ++k) if (free_states[k] == ch.nst) fi = k;
            if (fi > 0) {
                bool ok = true;
                for (int k = 0; k < fi; ++k) if (!(used_mask & (1 << k))) ok = false;
                if (!ok) continue;
            }
            if (fi >= 0) nm |= (1 << fi);
        }
        tr[st][sym] = ch;
        dfs(idx, n_def + 1, max_def, nm, prev);
        tr[st][sym] = {-1, 0, -1};
    }
    return true;
}

static void dfs(int idx, int n_def, int max_def, int used_mask, std::vector<Res> &prev);

static void dfs(int idx, int n_def, int max_def, int used_mask, std::vector<Res> &prev) {
    nodes++;
    reach[idx]++;
    if (nodes % 20000000 == 0) {
        printf("  nodes=%lld hits=%lld reach=", nodes, hits);
        for (int i = 0; i < 8; ++i) printf("%lld ", reach[i]);
        printf("\n"); fflush(stdout);
    }
    if (idx == stop_after) {
        hits++;
        print_machine("HIT_W3", n_def);
        return;
    }

    Res r = sim(tests[idx].p, tests[idx].a, tests[idx].d, tests[idx].e);

    if (r.kind == 1) {
        int lim = (idx <= 2) ? 7 : max_def;
        if (n_def >= lim) return;
        try_choices(idx, r.us, r.ub, n_def, max_def, used_mask, prev);
        return;
    }
    if (idx == 6) {
        if (r.kind == 2) { prev.push_back(r); dfs(7, n_def, max_def, used_mask, prev); prev.pop_back(); }
        return;
    }
    if (r.kind == 2) return;
    if (!check(idx, r, prev)) return;
    prev.push_back(r);
    dfs(idx + 1, n_def, max_def, used_mask, prev);
    prev.pop_back();
}

int main(int argc, char **argv) {
    int ns = argc > 1 ? atoi(argv[1]) : 16;
    int max_def = argc > 2 ? atoi(argv[2]) : 9;
    out = argc > 3 ? fopen(argv[3], "w") : stdout;
    if (argc > 4) stop_after = atoi(argv[4]);
    if (argc > 5) fix_crel = atoi(argv[5]);
    if (argc > 6) GAP = atoi(argv[6]);
    init_base(ns);
    int used0 = 0, dummy = 0;
    if (fix_crel) { preset(); mark_preset(used0); }
    std::vector<Res> prev;
    printf("w3b n_states=%d n_free=%d max_def=%d gap=%d stop=%d\n", ns, n_free, max_def, GAP, stop_after);
    // sanity: the preset must already satisfy the C_REL tests
    {
        Res r0 = sim(tests[0].p, tests[0].a, tests[0].d, tests[0].e);
        printf("preset C_REL(0): kind=%d p=%d a=%d c=%d d=%d e=%d\n", r0.kind, r0.p, r0.a, r0.c, r0.d, r0.e);
    }
    fflush(stdout);
    dfs(0, 0, max_def, used0, prev);
    printf("DONE n_states=%d nodes=%lld hits=%lld\n", ns, nodes, hits);
    if (out != stdout) fclose(out);
    return 0;
}
