// Route 1: f_{w+3} search on the M13 10-state core.  Single self-contained file.
//
// Method follows BB13/search_core10.cpp (the program that found M13):
//   * a transition slot is defined lazily, only when a test simulation reads it;
//   * normal form: free states are used in order, A0 must move right, at most
//     one 1RZ, and if the budget's last slot is used it must be the 1RZ;
//   * success is a set of shape invariants measured across several test
//     instances, not one simulation of one instance.
// Additions for f_{w+3}:
//   * the d-drop DD is swept (only DD=2 survives the M13 preset; DD is real
//     freedom only in a preset-free run);
//   * a third, outer counter e written on the tape, with three branches
//         d==0, e absent  -> create e  (both e and the reloaded d built from a)
//         d==1, e>=2      -> e := e-1, reload d      (one more w+2 round)
//         d==1, e==1      -> halt
//     which is what turns f_{w+2} into f_{w+3};
//   * a-sensitivity tests (a=6 vs a=8) in the spirit of core10's A=6/A=8 test.
//
// Fixed core (17 transitions), labels A..M:
//   A1=0LL  B0=1RA B1=1RC  C0=0LD C1=1LG  D0=0RE D1=1LD  E1=1RF
//   F1=0RM  G0=1RM G1=0LH  H0=1LG H1=1LH  L0=1LH L1=1LA  M0=1RB M1=1RM
// M13 preset (preset=1): A0=1RI I1=1RJ J0=1RE J1=0LA K0=1RA K1=0RF F0=1LI
// E0 is deliberately NOT preset: in M13 it is the 1RZ halt step, and that is
// exactly the transition the third counter has to re-route (d = 1 is the round
// boundary, so E0 must be free to branch on e).  The halt is then placed by the
// search as the single 1RZ, subject to the usual last-slot rule.
// Free with the preset: E0, I0 and the outer states N,O,P,Q.
// Free without it: A0,E0,F0,I,J,K,N,O,P,Q.
//
// Test shape.  State A starts on the 0 that follows 1^(a+2), head to the right:
//   left : 0^inf (10)^p 1^(a+2) [0]
//   right: 1^d 0 0^(gap-1) 1^e 0^inf
// A "return" is accepted when A stands on the first 1 of a (10)^c run, the
// 1^(a+2) run is intact with a even, and the right side reads
// 0 1^(d') 0 0^(gap-1) 1^(e') 0^inf again.
//
// The round boundary is d = 1, not d = 0: BB13_M13.v (D_reload_all) shows a
// reload writes d' = a+1, which is odd, so every drain of d reaches 1 and never
// 0 again.  d = 0 occurs exactly once, in the initial configuration, and that
// is where e is created.  Probing the three branches all at d = 0 would force a
// reload to write an even d and the machine could never use M13's halt step.
//
// Nine tests, ordered from the cheapest to the most selective, so that a
// machine which is only half right still shows up as a PART_* line
// (DD = d-drop per C_REL; e = 0 means the block is absent):
//   0 C_REL  a=8 d=DD   e=2 : d'=d-DD, e'=e, a' even, c' >= a/2+1
//   1 C_REL  a=8 d=DD+1 e=2 : same (p,a,c,e) as 0            (d independence)
//   2 C_REL  a=8 d=DD   e=3 : same (p,a,c,d) as 0            (e independence)
//   3 C_REL  a=6 d=DD   e=2 : c'(6) < c'(8)                  (c built from a)
//   4 create a=8 d=0    e absent : ret, c'>=1, d' odd >=3, e'>=1
//   5 halt   a=8 d=1    e=1 : machine halts
//   6 dec    a=8 d=1    e=2 : ret, e'=1, c'>=1, d' odd >=3
//   7 dec    a=8 d=1    e=3 : e'=2, same (p,a,c,d) as 6      (e independence)
//   8 create a=6 d=0    e absent : same, and e'(6) < e'(8), e'(8) >= 4
// Test 8 is the load-bearing one: the e block created at d=0 must grow with a
// and be of the same order as a, otherwise the machine is a plain M13 with a
// hard-wired e (=1), which is f_{w+2}, not f_{w+3}.  d is only required to be a
// valid odd counter, not to grow with a (see the comment at the test).
// It is put last on purpose: if it were early, every machine that fails it
// would hide whether the other gadgets (halt, dec, e-independence) exist.
// HIT_FULL passes all nine; HIT_FULL_DREL also has (p,a,c,d) identical between
// the create (test 4) and dec (test 6) returns.  PART_* tags name the last test
// a machine passed.
//
// Build: g++ -O2 -o search_w3b search_w3b.cpp
// Run  : ./search_w3b <n_states> <max_def> <out> [stop] [preset] [gap] [DD]
//                     [max_nodes] [sweep] [seed] [radius] [shard] [nshard]
//   n_states  15..17      number of states (10 core + outer)
//   max_def   free slots that may be defined (counts searched slots only)
//   out       output file ("-" for stdout)
//   stop      9 = full search (default); 6 = C_REL+create+halt only; 5 = C_REL+create only
//   preset    1 = start from the M13 C_REL gadget (default), 0 = free search,
//             2 = neighbourhood of a seed machine (see below)
//   gap       zeros between the d block and the e block (default 2; gap 1 never
//             lets the machine see the e block, gap 3 loses the e branch)
//   DD        d-drop per C_REL, 1..3 (default 2)
//   max_nodes abort after this many nodes, 0 = no limit (default 0)
//   sweep     1 = run DD in {1,2,3} x gap in {1,2,3} back to back
//   seed      machine string file, only read when preset=2
//   radius    neighbourhood radius, only read when preset=2 (default 2)
//   shard     keep only first-level choices with (choice index % nshard) == shard
//   nshard    number of shards, 1 = no sharding (default).  The space splits at
//             the first transition the search has to define (slot (I,0), 69
//             choices), so nshard copies run the whole search in parallel; the
//             union of their outputs is the unsharded result.
//
// Neighbourhood mode (preset=2) keeps one complete 17-state machine as the base
// and tries every assignment differing from it in at most `radius` transitions,
// over the 17 slots that are not part of the fixed core.  In this mode "---" is
// the ordinary bbchallenge halt, so a machine with one undefined transition is
// complete.  radius 2 is about 0.7M machines, radius 3 about 230M.
//   ./search_w3b 17 0 out.txt 9 2 1 2 0 0 seed.txt 2
//
// Local runs (costs measured on one core, ~0.7-1M nodes/s with -O2):
//   ./search_w3b 16 8  out.txt 9 1 2 2 0    16-state preset, gap 2
//   ./search_w3b 17 10 out.txt 9 1 2 2 0    main 17-state preset run, gap 2
//   ./search_w3b 17 10 out.txt 7 1 2 2 0    stop after the e=2 decrement test
//   ./search_w3b 17 0  out.txt 9 2 2 2 0 0 seedA.txt 3   radius-3 around seed A
//                                            (~223M machines, the best lead)
//   ./search_w3b 16 10 out.txt 9 0 2 2 0 1  16-state preset-free + sweep
//   ./search_w3b 17 11 out.txt 9 0 2 2 0 1  17-state preset-free + sweep
// The last two numbers are <sweep> <shard> <nshard>; see the CLI block above.
// For a preset-free run DD is a genuine parameter: use sweep=1 to cover it.
//
// Spaces already exhausted in this repository (complete, no cap):
//   15 states, preset, max_def=7, DD=2, gap=1 : 4,558,998 nodes, 0 hits
//   16 states, preset, max_def=8, DD=2, gap=1 : 129,271,986 nodes, 0 hits
//   16 states, preset, max_def=8, DD=2, gap=2 : 129,244,098 nodes, 0 hits
// 17 states, preset, max_def=10, gap=1, 300M nodes (not exhaustive): 0 hits,
// and only 2 machines ever reached the e=2 decrement test.  Both were probed:
// they halt at d=1 before ever reading the e block, so they are not a counter.
// 17 states, preset, max_def=10, gap=2, 400M nodes (not exhaustive): 0 hits.
// Funnel at that point: 81397 machines pass create+halt, 9010 pass the e=2
// decrement, 41 pass e-independence (e=3 -> e'=2 with identical p,a,c,d), and
// 2 reach the create-scaling test.  None passes it.
// Probing those two shows a clean picture (seed A below; seed B is the same
// string with slot (P,0) changed from 1RB0LO to 1RK0LO):
//   1RI0LL_1RA1RC_0LD1LG_0RE1LD_0RN1RF_1LI0RM_1RM0LH_1LG1LH_0LI1RJ_1RE0LA_1RA0RF_1LH1LA_1RB1RM_1LO0RQ_0LP1LO_1RB0LO_1RZ0LI
//   * the e branch is real: at (d=1,e=4) they return with e'=3 and d fixed;
//   * create writes d' = a+3 (9,11,13 for a=6,8,10) but e' = 1 for every a.
// So the missing piece is not the counter but its initial value: e has to be
// created from a, and their create gadget only ever writes a marker 1.
// A radius-2 neighbourhood of seed A (667,591 machines, gap=2) has 0 hits;
// radius 3 is the run left for a local machine.
// gap=3 is much worse than gap=2 (12919 create+halt passes at 400M, 0 pass the
// e=2 decrement), and gap=1 never lets the machine see the e block at all.
// The 16-state funnel is the same story one state earlier: tens of thousands of
// machines pass create, none passes the halt test with a working e branch.
//
// Diagnostic build: g++ -O2 -DRELAX8 -o search_w3b_diag search_w3b.cpp
// turns test 8 into "anything that returns", so reach[6..8] and the PART_*
// lines count the machines that have a halt / dec / e-independence gadget at
// all, independently of the create-scaling gate.  Use it only to see how far a
// space gets, never as a success test.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

static const int MAXT = 400;      // tape cells
static const int MAXS = 800;      // steps per test

static int GAP = 2;   // default layout; see the gap note in the header
static int DD = 2;

struct Trans { int w, mv, nst; }; // nst: 0..16 state, 20 = Z, -1 = UNDEF
static Trans tr[17][2];
static bool fixed_slot[17][2];     // true = one of the 17 core transitions
static bool undef_halt = false;    // neighbourhood mode: "---" is the halt
static int n_states = 15;
static Trans choices[96];
static int n_choices = 0;
static int free_states[8], n_free = 0;

static void init_base(int ns) {
    n_states = ns;
    for (int s = 0; s < 17; ++s) for (int b = 0; b < 2; ++b) {
        tr[s][b] = {-1, 0, -1};
        fixed_slot[s][b] = false;
    }
    auto set = [&](char st, int b, int w, char dir, char nst) {
        tr[st - 'A'][b] = {w, dir == 'L' ? -1 : 1, nst - 'A'};
        fixed_slot[st - 'A'][b] = true;
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

    static const int idx[7] = {8, 9, 10, 13, 14, 15, 16}; // I J K N O P Q
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
        if (t.nst == -1)
            return undef_halt ? Res{2, 0, 0, 0, 0, 0, 0, 0} : Res{1, st, sym, 0, 0, 0, 0, 0};
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
static Test tests[9];

static void build_tests() {
    tests[0] = {3, 8, DD,     2};   // C_REL base
    tests[1] = {3, 8, DD + 1, 2};   // C_REL, d+1          (d independence)
    tests[2] = {3, 8, DD,     3};   // C_REL, e+1          (e independence)
    tests[3] = {3, 6, DD,     2};   // C_REL, a=6          (c built from a)
    tests[4] = {3, 8, 0,      0};   // create e, a=8       (d = 0: initial boundary)
    tests[5] = {3, 8, 1,      1};   // halt, e=1           (d = 1: round boundary)
    tests[6] = {3, 8, 1,      2};   // decrement, e=2
    tests[7] = {3, 8, 1,      3};   // decrement, e=3      (e changes by exactly 1)
    tests[8] = {3, 6, 0,      0};   // create e, a=6       (both counters grow with a)
}

static long long nodes = 0, hits = 0, partial = 0;
static long long reach[10] = {0};
static long long max_nodes = 0;
static bool aborted = false;
static const long long PART_CAP = 20000;
static int stop_after = 9;
static int fix_crel = 1;
static int shard = 0, nshard = 1;   // split the first-level choice loop
static FILE *out = nullptr;

static void print_machine(const char *tag, int n_def, const std::vector<Res> &res) {
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
    for (size_t i = 0; i < res.size(); ++i)
        fprintf(out, " | %zu:k%d(p%d,a%d,c%d,d%d,e%d)", i, res[i].kind,
                res[i].p, res[i].a, res[i].c, res[i].d, res[i].e);
    fputc('\n', out);
    fflush(out);
}

static bool check(int idx, const Res &r, const std::vector<Res> &prev) {
    const Test &t = tests[idx];
    if (idx == 0)
        return r.kind == 3 && r.d == t.d - DD && r.e == t.e
            && r.a >= 2 && !(r.a & 1) && r.c >= t.a / 2 + 1;
    if (idx == 1)
        return r.kind == 3 && r.d == t.d - DD && r.e == t.e && r.a >= 2 && !(r.a & 1)
            && r.p == prev[0].p && r.a == prev[0].a && r.c == prev[0].c && r.e == prev[0].e;
    if (idx == 2)
        return r.kind == 3 && r.d == t.d - DD && r.e == t.e && r.a >= 2 && !(r.a & 1)
            && r.p == prev[0].p && r.a == prev[0].a && r.c == prev[0].c && r.d == prev[0].d;
    if (idx == 3)
        return r.kind == 3 && r.d == t.d - DD && r.e == t.e && r.a >= 2 && !(r.a & 1)
            && r.p == prev[0].p && r.a == prev[0].a && r.c < prev[0].c && r.c >= t.a / 2 + 1;
    if (idx == 4)                                       // create e and d from a
        return r.kind == 3 && r.c >= 1
            && r.d >= 3 && (r.d & 1) && r.e >= 1;
    if (idx == 6)                                       // decrement e, reload d
        return r.kind == 3 && r.e == 1 && r.c >= 1
            && r.d >= 3 && (r.d & 1);
    if (idx == 7)                                       // e changes by exactly 1
        return r.kind == 3 && r.e == 2
            && r.p == prev[6].p && r.a == prev[6].a && r.c == prev[6].c && r.d == prev[6].d;
    if (idx == 8)                                       // e is created from a
#ifdef RELAX8
        return r.kind == 3;
#else
        // The load-bearing condition is that the e block created at a=8 is
        // bigger than the one created at a=6, and is comparable to a itself
        // (>= a/2); a machine that always writes a fixed e (=1) is only M13
        // with an unused counter.  d only has to be a valid odd counter: the
        // reload re-creates it, so requiring d to grow with a as well (as an
        // earlier version did) was an accident of M13's W_0(b) = b + 3, and it
        // would reject a machine whose d is constant across rounds.
        return r.kind == 3 && r.c >= 1
            && r.d >= 3 && (r.d & 1) && r.e >= 1
            && r.e < prev[4].e && prev[4].e >= 4;
#endif
    return false;
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
}

static void mark_preset(int &used_mask, bool &has_z) {
    for (int k = 0; k < n_free; ++k) {
        int s = free_states[k];
        for (int b = 0; b < 2; ++b) if (tr[s][b].nst != -1) used_mask |= (1 << k);
    }
    for (int s = 0; s < 17; ++s)
        for (int b = 0; b < 2; ++b) if (tr[s][b].nst == 20) has_z = true;
}

static void dfs(int idx, int n_def, int max_def, int used_mask, bool has_z,
                std::vector<Res> &prev) {
    nodes++;
    if (nodes > max_nodes && max_nodes) { aborted = true; return; }
    reach[idx]++;
    if ((nodes & 0xFFFFFF) == 0) {
        printf("  nodes=%lld hits=%lld part=%lld reach=", nodes, hits, partial);
        for (int i = 0; i < 10; ++i) printf("%lld ", reach[i]);
        printf("\n"); fflush(stdout);
    }
    if (idx == stop_after) { hits++; print_machine("HIT_STOP", n_def, prev); return; }
    if (idx == 6) { partial++; if (partial <= PART_CAP) print_machine("PART_CREATE_HALT", n_def, prev); }
    if (idx == 7) { partial++; if (partial <= PART_CAP) print_machine("PART_DEC", n_def, prev); }
    if (idx == 8) { partial++; if (partial <= PART_CAP) print_machine("PART_DEC_EINDEP", n_def, prev); }
    if (idx == 9) {
        bool strict = prev[4].p == prev[6].p && prev[4].a == prev[6].a
                   && prev[4].c == prev[6].c && prev[4].d == prev[6].d;
        hits++;
        print_machine(strict ? "HIT_FULL_DREL" : "HIT_FULL", n_def, prev);
        return;
    }

    Res r = sim(tests[idx].p, tests[idx].a, tests[idx].d, tests[idx].e);

    if (r.kind == 1) {                                  // need one more definition
        if (n_def >= max_def) return;
        bool last = (n_def == max_def - 1) && !has_z;    // last slot must be the 1RZ
        int st = r.us, sym = r.ub;
        for (int i = 0; i < n_choices; ++i) {
            if (n_def == 0 && nshard > 1 && (i % nshard) != shard) continue;
            Trans ch = choices[i];
            bool is_z = (ch.nst == 20);
            if (is_z && (idx < 3 || has_z)) continue;
            if (last && !is_z) continue;
            int nm = used_mask;
            if (!is_z) {
                int fi = -1;
                for (int k = 0; k < n_free; ++k) if (free_states[k] == ch.nst) fi = k;
                if (fi > 0) {
                    bool ok = true;
                    for (int k = 0; k < fi; ++k) if (!(used_mask & (1 << k))) ok = false;
                    if (!ok) continue;
                }
                if (fi >= 0) nm |= (1 << fi);
                if (st == 0 && sym == 0 && ch.mv != 1) continue;  // A0 must move right
            }
            tr[st][sym] = ch;
            dfs(idx, n_def + 1, max_def, nm, has_z || is_z, prev);
            tr[st][sym] = {-1, 0, -1};
        }
        return;
    }
    if (idx == 5) {                                     // halt test (e = 1, d = 1)
        if (r.kind != 2) return;
        prev.push_back(r);
        dfs(6, n_def, max_def, used_mask, has_z, prev);
        prev.pop_back();
        return;
    }
    if (r.kind != 3) return;
    if (!check(idx, r, prev)) return;
    prev.push_back(r);
    dfs(idx + 1, n_def, max_def, used_mask, has_z, prev);
    prev.pop_back();
}

static void report(int i, const Res &r) {
    if (r.kind == 1) printf(" %d:UNDEF(st%c,%d)", i, 'A' + r.us, r.ub);
    else printf(" %d:k%d(p%d,a%d,c%d,d%d,e%d)", i, r.kind, r.p, r.a, r.c, r.d, r.e);
}

static void reset_stats() {
    nodes = hits = partial = 0;
    aborted = false;
    for (int i = 0; i < 10; ++i) reach[i] = 0;
}

// ---------------------------------------------------------------------------
// Neighbourhood mode (preset=2): take one complete machine as the base and try
// every assignment that differs from it in at most `radius` transitions.  This
// is the cheap way to follow up a PART_* lead, instead of re-enumerating a
// whole state count.  In this mode "---" is a real halt (undef_halt), i.e. the
// ordinary bbchallenge reading, so a machine with one undefined transition is
// complete and can be a hit.
// ---------------------------------------------------------------------------
static std::vector<Res> g_prev;
static long long nb_tried = 0, nb_hits = 0;

// True iff the current assignment passes all nine tests in order.
static bool run_tests() {
    g_prev.clear();
    for (int i = 0; i < 9; ++i) {
        Res r = sim(tests[i].p, tests[i].a, tests[i].d, tests[i].e);
        if (i == 5) {                                   // halt test
            if (r.kind != 2) return false;
            g_prev.push_back(r);
            continue;
        }
        if (!check(i, r, g_prev)) return false;
        g_prev.push_back(r);
    }
    return true;
}

static bool load_seed(const char *fn) {
    FILE *f = fopen(fn, "r");
    if (!f) { fprintf(stderr, "cannot open seed %s\n", fn); return false; }
    char buf[4096];
    bool loaded = false;
    while (fgets(buf, sizeof buf, f)) {
        int slot = 0;
        for (char *q = buf; *q && slot < 2 * n_states; ) {
            if (*q == '_' || *q == ' ' || *q == '\t') { ++q; continue; }
            if (q[0] == '-' && q[1] == '-' && q[2] == '-') {
                tr[slot / 2][slot % 2] = {-1, 0, -1}; q += 3; ++slot;
            } else if ((q[0] == '0' || q[0] == '1') && (q[1] == 'L' || q[1] == 'R') && q[2]) {
                int tgt = (q[2] == 'Z') ? 20 : q[2] - 'A';
                tr[slot / 2][slot % 2] = {q[0] - '0', q[1] == 'L' ? -1 : 1, tgt};
                q += 3; ++slot;
            } else ++q;
        }
        if (slot == 2 * n_states) { loaded = true; break; }
    }
    fclose(f);
    return loaded;
}

static int nb_slots[64], nb_n = 0;

static void nb_build_slots() {
    nb_n = 0;
    for (int s = 0; s < n_states; ++s)
        for (int b = 0; b < 2; ++b)
            if (!fixed_slot[s][b]) nb_slots[nb_n++] = s * 2 + b;
}

static void nb_assign(int ci, int r, const int *chosen, Trans *saved) {
    if (ci == r) {
        ++nb_tried;
        if ((nb_tried & 0xFFFFF) == 0) {
            printf("  nb tried=%lld hits=%lld\n", nb_tried, nb_hits); fflush(stdout);
        }
        if (run_tests()) {
            ++nb_hits;
            print_machine("NB_HIT", 0, g_prev);
        }
        return;
    }
    int s = chosen[ci] / 2, b = chosen[ci] % 2;
    saved[ci] = tr[s][b];
    for (int i = 0; i <= n_choices; ++i) {              // i == n_choices: undefined
        tr[s][b] = (i == n_choices) ? Trans{-1, 0, -1} : choices[i];
        nb_assign(ci + 1, r, chosen, saved);
    }
    tr[s][b] = saved[ci];
}

static void nb_choose(int start, int k, int r, int *chosen, Trans *saved) {
    if (k == r) { nb_assign(0, r, chosen, saved); return; }
    for (int i = start; i < nb_n; ++i) {
        chosen[k] = nb_slots[i];
        nb_choose(i + 1, k + 1, r, chosen, saved);
    }
}

// One complete search for a fixed (n_states, max_def, stop, preset, gap, DD).
static void run_one(int ns, int max_def, int stop, int preset_flag, long long cap) {
    init_base(ns);
    build_tests();
    reset_stats();
    int used0 = 0;
    bool has_z = false;
    if (preset_flag) { preset(); mark_preset(used0, has_z); }

    printf("== w3b n_states=%d n_free=%d max_def=%d stop=%d preset=%d gap=%d DD=%d cap=%lld shard=%d/%d\n",
           ns, n_free, max_def, stop, preset_flag, GAP, DD, cap, shard, nshard);
    printf("sanity:");
    for (int i = 0; i < 9; ++i) {
        Res r = sim(tests[i].p, tests[i].a, tests[i].d, tests[i].e);
        report(i, r);
    }
    printf("\n");
    if (preset_flag) {                    // the preset itself must already satisfy C_REL
        std::vector<Res> pv;
        bool all = true;
        for (int i = 0; i <= 3; ++i) {
            Res r = sim(tests[i].p, tests[i].a, tests[i].d, tests[i].e);
            if (!check(i, r, pv)) { all = false; break; }
            pv.push_back(r);
        }
        printf("preset C_REL 0..3: %s\n", all ? "PASS" : "FAIL");
    }
    fflush(stdout);

    max_nodes = cap;
    std::vector<Res> prev;
    dfs(0, 0, max_def, used0, has_z, prev);
    printf("DONE n_states=%d DD=%d gap=%d nodes=%lld hits=%lld part=%lld%s reach=",
           ns, DD, GAP, nodes, hits, partial, aborted ? " ABORTED(cap)" : "");
    for (int i = 0; i < 10; ++i) printf("%lld ", reach[i]);
    printf("\n");
    fflush(stdout);
}

int main(int argc, char **argv) {
    int ns = argc > 1 ? atoi(argv[1]) : 16;
    int max_def = argc > 2 ? atoi(argv[2]) : 8;
    out = (argc > 3 && strcmp(argv[3], "-") != 0) ? fopen(argv[3], "w") : stdout;
    if (!out) { fprintf(stderr, "cannot open %s\n", argv[3]); return 1; }
    if (argc > 4) stop_after = atoi(argv[4]);
    if (argc > 5) fix_crel = atoi(argv[5]);
    if (argc > 6) GAP = atoi(argv[6]);
    if (argc > 7) DD = atoi(argv[7]);
    if (GAP < 1) GAP = 1;
    if (DD < 1) DD = 1;
    long long cap = argc > 8 ? atoll(argv[8]) : 0;
    int sweep = argc > 9 ? atoi(argv[9]) : 0;   // 1 = DD 1..3 x gap 1..3
    const char *seed = argc > 10 ? argv[10] : nullptr;
    int radius = argc > 11 ? atoi(argv[11]) : 2;
    if (argc > 12) shard = atoi(argv[12]);
    if (argc > 13) nshard = atoi(argv[13]);
    if (nshard < 1) nshard = 1;
    if (shard < 0 || shard >= nshard) shard = 0;

    if (fix_crel == 2) {                        // neighbourhood mode
        init_base(ns);
        undef_halt = true;
        build_tests();
        reset_stats();
        if (!seed || !load_seed(seed)) return 1;
        printf("== w3b neighbourhood n_states=%d seed=%s gap=%d DD=%d radius=%d\n",
               ns, seed, GAP, DD, radius);
        printf("seed:");
        for (int i = 0; i < 9; ++i) {
            Res r = sim(tests[i].p, tests[i].a, tests[i].d, tests[i].e);
            report(i, r);
        }
        printf("\nseed passes all nine: %s\n", run_tests() ? "YES" : "no");
        nb_build_slots();
        printf("outer (changeable) slots: %d\n", nb_n);
        fflush(stdout);
        int chosen[8];
        Trans saved[8];
        for (int r = 0; r <= radius; ++r) {
            printf("-- radius %d\n", r); fflush(stdout);
            nb_choose(0, 0, r, chosen, saved);
        }
        printf("DONE nb tried=%lld hits=%lld\n", nb_tried, nb_hits);
        if (out != stdout) fclose(out);
        return 0;
    }

    if (!sweep) {
        run_one(ns, max_def, stop_after, fix_crel, cap);
    } else {
        for (int dd = 1; dd <= 3; ++dd)
            for (int gp = 1; gp <= 3; ++gp) {
                DD = dd; GAP = gp;
                run_one(ns, max_def, stop_after, fix_crel, cap);
            }
    }
    if (out != stdout) fclose(out);
    return 0;
}
