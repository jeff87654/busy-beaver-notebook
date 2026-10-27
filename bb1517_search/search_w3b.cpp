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
// Post-filters on the REAL blank-tape orbit (applied to HIT_STOP / HIT_FULL /
// NB_HIT only; PART_* diagnostics stay unfiltered).  The nine tests are local:
// they hand the machine a pre-built tape, so a machine can pass them while its
// actual orbit never visits the gadget at all.  All 39 HIT_STOP machines from
// the first three production batches were of that kind, so a candidate must now
// also pass, in this order:
//   1. blank non-trivial : running from the blank tape (state A, all zeros)
//                          must not halt within BLANK_CAP steps;
//   2. core reachability : that orbit must visit D, E, H and M (the M13 engine);
//   3. branch liveness   : at least BRANCH_MIN times, E0 (state E on 0) must be
//                          followed by a read of 1, i.e. the "e is present"
//                          branch of the third counter really fires on the real
//                          orbit (create-only machines read 0 forever);
//   4. chained decrement : starting from the dec return (test 6, e = 1), one
//                          more w+2 round must end in the real 1RZ halt.  This
//                          is the check the old test 7 missed: it restarted at
//                          e = 3 instead of continuing from the dec's own tape.
//   5. chained create   : starting from the create return (test 4, d = 0), the
//                          machine must run TWO more real rounds that consume
//                          the counters it just wrote (c or d strictly smaller,
//                          e unchanged, a even again).  This is the mechanism
//                          of M12 (the new 12-state f_{w+2} entry): its round 2
//                          is Kd_step^(a1/6+1)(D_reload pa1), i.e. it eats the
//                          REAL output of round 1, a1 = 2 mod 6, instead of
//                          rebuilding a hand-made tape.  M12's D_REL turns the
//                          even accumulator a into a/2+2 d-tokens, so created
//                          counters must scale with a; the 39 HIT_STOP fakes all
//                          create the constant d = 3, which is exactly the
//                          failure mode M12 rules out.  Hence tests 4, 6 and 8
//                          also require the accumulator to survive (a even and
//                          >= 2) and test 8 requires d(6) < d(8).
// A machine that fails any of them is counted in `rejected`, not in `hits`
// (the DONE line reports `rejected=<n>`).
// BLANK_CAP = 1,000,000 steps, CHAIN_CAP = 200,000, CHAIN_LOCAL_CAP = 20,000,
// BRANCH_MIN = 2; all are compile-time constants.  Their cost is negligible
// next to the search, because they run only on the few machines that already
// passed all nine tests.
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
// M12 filters (this revision).  Replayed against the 39 production HIT_STOP
// machines, the strengthened tests reject every one of them BEFORE the
// post-filters: 8 at test 4 (create returned a = 0, no accumulator left for the
// next round) and 31 at test 8 (create wrote the same d = 3 for a = 6 and
// a = 8, i.e. the counter was hand-written, not derived from a).  Filter 5
// (chained create) additionally caught a machine whose first post-create round
// dropped the e block (e = 10 -> 0).  So a hit now needs what M12 has: a create
// that leaves an even accumulator, counters that scale with a, and rounds that
// consume the previous round's real output.
//
// Diagnostic build: g++ -O2 -DRELAX8 -o search_w3b_diag search_w3b.cpp
// turns test 8 into "anything that returns", so reach[6..8] and the PART_*
// lines count the machines that have a halt / dec / e-independence gadget at
// all, independently of the create-scaling gate.  Use it only to see how far a
// space gets, never as a success test.  Adding -DPF_TRACE to either build makes
// post_filter write "PF reject @<n>" to stderr, naming the filter that fired.
//
// ---------------------------------------------------------------------------
// -layout m12  (new): search the same f_{w+3} question in the shape of M12,
// the 12-state f_{w+2} machine
//     1RB1RA_1RI1RC_0LD1LG_0RE1LD_1LK1RF_1RG0RA_1RA0LH_1LG1LH_1RE0LJ_1LH1LI_1RZ0LL_0LH1LK
// M12 is not a relabelling of the M13 core (its B0 is 1RI and G0 is 1RA, and
// its d counter is a (10)^d digit string that halts at d = 0, whereas M13's d
// is 1^d and its round boundary is d = 1).  So it gets its own core, tape
// layout, tests and post-filters; -layout m13 (the default) is untouched.
//
// Configurations (note the head is in state I, not A):
//   Ce p a c d e = 0^inf (10)^p 1^(a+2) I> (10)^c 0 (10)^d 0^GAP 1^e 0^inf
//   Cd p b d e   = 0^inf (10)^p 1^(b+2) I> (10)^d 0^GAP 1^e 0^inf
// The e block is the third counter that has to turn M12's f_{w+2} into
// f_{w+3}; it sits GAP zeros beyond the d block, exactly as the m13 layout
// puts it beyond the 1^d block.  GAP = 2 was measured, not guessed: at
// GAP <= 1 the plain M12 halt path (I0 -> E0 -> K/L walk) reads the e block
// and diverges, at GAP >= 2 it halts cleanly, and the e block stays invisible
// until a mutant deliberately walks out to it.
//
// Verified rules (minimal instances, real M12 orbit, gap 2):
//   CE_EVEN : Ce (p+1) (2k) (c+1) d -> Ce (p+k+1) (W_p(1)) c d
//   C_REL   : Cd (p+1) (2m+1) (d+1) -> Ce p (W_p(3)) m d
//   D_STEP  : Ce p a 0 (d+2)       -> Cd p (W_p(a+4)) d
//   D_REL   : Ce (p+1) (2k) 0 0    -> Cd p (W_p(0)) (k+2)
//   HALT    : Cd p (2m+1) 0        -> halt
// For example Cd 2 3 2 -> Ce 1 14 1 1 (146 steps) and Ce 2 8 0 0 -> a reload
// with 6 counter tokens (D_REL's d = a/2+2), which is what tests 0..4 pin.
//
// Fixed core: every M12 transition (22 of 24) except I0 and E0, which are the
// boundary/branch slots the third counter has to re-route.  K0 = 1RZ stays
// fixed as the halt.  Free: I0, E0 and the spare states M..Q (indices 12..16).
// So a 15-state run has 8 free slots, a 17-state run 12.
//
// Nine tests mirror the m13 ones but in M12 shapes (cd = 1 marks a Cd input):
//   0 C_REL  Cd 2 3 d=2 e=2 : Ce 1 14 1 1 2      (d drops by exactly 1)
//   1 C_REL  d=3            : same (p,a,c,e), d one larger (d independence)
//   2 C_REL  e=3            : same (p,a,c,d)                    (e independence)
//   3 C_REL  b=5            : c grows with the accumulator       (c from a)
//   4 create Ce 2 8 0 0    : a return with e >= 1 and reloaded counters
//   5 halt   Cd 1 5 d=0 e=1 : machine halts
//   6 dec    Cd 1 5 d=0 e=2 : a return with e = 1 and a reloaded counter
//   7 dec    Cd 1 5 d=0 e=3 : e = 2, same (p,a,c,d) as test 6
//   8 create Ce 2 6 0 0    : counters and e smaller than test 4's (a-scaling)
// Plain M12 passes 0..3 and 5, and fails 4 and 6: it never creates e and it
// halts whatever e is.  That is exactly the pressure we want: a hit must
// create the third counter at the d = 0 boundary, keep the halt for e = 1,
// and reload a round for e >= 2.
// Post-filters on the real blank orbit: blank non-trivial, core reachability
// {D,G,H,I}, driver liveness (I0 entered >= 2 times), chained dec (from the
// test-6 return at e = 1 one more real round must halt), chained create (from
// the test-4 return the machine must come back with e unchanged).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

static const int MAXT = 400;      // tape cells
static const int MAXS = 800;      // steps per test

// Post-filter budgets on the real blank-tape orbit.  They are paid only by the
// few machines that already passed all nine local tests, so they can be large.
static const int BLANK_CAP = 1000000;  // steps from the blank tape
static const int CHAIN_CAP = 200000;   // steps for the chained w+2 round
static const int CHAIN_LOCAL_CAP = 20000; // steps for a chained local round
static const int BRANCH_MIN = 2;       // E0 entries that must read 1
static const int ORBIT_PAD = 16;       // arena margin around the centre
static const int CHAIN_CELLS = 2048;   // tape arena for the chained rounds

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

// Run from an arbitrary tape in state A and report the first accepted return,
// an undefined slot, or a halt.  `cells` bounds every scan, so the same routine
// serves both the hand-built tests (MAXT cells, MAXS steps) and the chained
// rounds that start from a machine's real output (CHAIN_CELLS, a larger cap).
static Res run_from(int *tape, int cells, int pos, int cap) {
    int st = 0;                          // state A
    for (int step = 1; step <= cap; ++step) {
        if (pos < 2 || pos >= cells - 2) return {0, 0, 0, 0, 0, 0, 0, 0};
        int sym = tape[pos];
        Trans t = tr[st][sym];
        if (t.nst == -1)
            return undef_halt ? Res{2, 0, 0, 0, 0, 0, 0, 0} : Res{1, st, sym, 0, 0, 0, 0, 0};
        if (t.nst == 20) return {2, 0, 0, 0, 0, 0, 0, 0};
        tape[pos] = t.w; pos += t.mv; st = t.nst;

        if (st == 0 && pos >= 4 && pos < cells - 4 && tape[pos] == 1 && tape[pos + 1] == 0) {
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
            while (j + 1 < cells && tape[j] == 1 && tape[j + 1] == 0) { c_out++; j += 2; }
            if (c_out < 1 || j >= cells || tape[j] != 0) continue;
            j++;
            int d_out = 0;
            while (j < cells && tape[j] == 1) { d_out++; j++; }
            if (j >= cells || tape[j] != 0) continue;
            j++;
            for (int g = 1; g < GAP; ++g) { if (tape[j] != 0) { ok = false; break; } j++; }
            if (!ok) continue;
            int e_out = 0;
            while (j < cells && tape[j] == 1) { e_out++; j++; }
            for (int k = j; k < cells; ++k) if (tape[k]) { ok = false; break; }
            if (!ok) continue;
            return {3, 0, 0, p_out, ones_a - 2, c_out, d_out, e_out};
        }
    }
    return {0, 0, 0, 0, 0, 0, 0, 0};
}

static int sim_tape[MAXT];

static Res sim(int p, int a, int d, int e) {
    int *tape = sim_tape;
    memset(tape, 0, sizeof(sim_tape));
    int idx = 24;
    for (int i = 0; i < p; ++i) { tape[idx++] = 1; tape[idx++] = 0; }
    for (int i = 0; i < a + 2; ++i) tape[idx++] = 1;
    int pos = idx;                       // head on the separator 0
    tape[idx++] = 0;
    for (int i = 0; i < d; ++i) tape[idx++] = 1;
    tape[idx++] = 0;
    for (int g = 1; g < GAP; ++g) tape[idx++] = 0;
    for (int i = 0; i < e; ++i) tape[idx++] = 1;
    return run_from(tape, MAXT, pos, MAXS);
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

static long long nodes = 0, hits = 0, partial = 0, rejected = 0;
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
        // a must survive the create as an even accumulator >= 2: M13's D_REL
        // leaves a = 2, and M12's leaves W_p(0).  The 39 fakes returned a = 0.
        return r.kind == 3 && r.c >= 1
            && r.d >= 3 && (r.d & 1) && r.e >= 1
            && r.a >= 2 && !(r.a & 1);
    if (idx == 6)                                       // decrement e, reload d
        return r.kind == 3 && r.e == 1 && r.c >= 1
            && r.d >= 3 && (r.d & 1) && r.a >= 2 && !(r.a & 1);
    if (idx == 7)                                       // e changes by exactly 1
        return r.kind == 3 && r.e == 2
            && r.p == prev[6].p && r.a == prev[6].a && r.c == prev[6].c && r.d == prev[6].d;
    if (idx == 8)                                       // e is created from a
#ifdef RELAX8
        return r.kind == 3;
#else
        // Two created counters must scale with the accumulator a:
        //   * e, so that the number of w+2 rounds grows with a;
        //   * d, so that the number of w+1 sub-rounds inside one round grows
        //     too.  M12 is the witness for the second point: its D_REL writes
        //     d = a/2 + 2 tokens from the even accumulator, and its round 2 is
        //     Kd_step^(a1/6+1), so d is what carries the level of the round.
        //     M13 also satisfies d(6) = 7 < d(8) = 9.  The 39 fakes all wrote
        //     the constant d = 3 for a = 6 and a = 8, which is precisely the
        //     "hand-written counter" failure mode.  An earlier version dropped
        //     this comparison on the theory that a constant d could be fine;
        //     the fakes show that in practice it is the cheapest discriminator.
        return r.kind == 3 && r.c >= 1
            && r.d >= 3 && (r.d & 1) && r.a >= 2 && !(r.a & 1)
            && r.e >= 1 && r.e < prev[4].e && prev[4].e >= 4
            && r.d < prev[4].d;
#endif
    return false;
}

// ---------------------------------------------------------------------------
// Post-filters on the REAL blank-tape orbit.
//
// The nine tests are local: they hand the machine a pre-built tape and only
// check that the returned tape has the right shape.  A machine can satisfy all
// nine while its actual orbit never enters the gadget at all (all 39 HIT_STOP
// machines of the first three production batches did exactly that).  A
// candidate must therefore also pass, in this order:
//   1. blank non-trivial (checked first, cheapest discriminator),
//   2. core reachability, 3. branch liveness, 4. chained decrement,
//   5. chained create (the M12 mechanism: two real rounds after the create).
// Failures are counted in `rejected`, never in `hits`.
// ---------------------------------------------------------------------------

struct Orbit {
    bool halted;                     // reached 1RZ or an undefined slot
    long long steps;
    unsigned visited;                // bit s = state s was entered
    long long e0_entries;            // times state E read 0 (gadget entry)
    long long e0_read1;              // of those, times the next read was 1
};

// Ordinary bbchallenge semantics: "---" and "1RZ" both halt.  The head must
// stay inside the arena; running off it counts as a filter failure, since a
// machine that moves more than `cap` cells in `cap` steps needs no verdict.
static bool orbit_run(std::vector<int> &tape, int pos, int cap, Orbit &o) {
    o = Orbit{false, 0, 0, 0, 0};
    int st = 0;                                     // canonical start: state A
    bool pend_e0 = false;
    for (int step = 1; step <= cap; ++step) {
        if (pos < 1 || pos >= (int)tape.size() - 1) return false;
        int sym = tape[pos];
        o.visited |= 1u << st;
        if (pend_e0) { if (sym == 1) o.e0_read1++; pend_e0 = false; }
        if (st == 4 && sym == 0) { o.e0_entries++; pend_e0 = true; }   // E0
        Trans t = tr[st][sym];
        if (t.nst == -1 || t.nst == 20) { o.halted = true; o.steps = step; return true; }
        tape[pos] = t.w; pos += t.mv; st = t.nst;
    }
    o.steps = cap;
    return true;
}

// Rebuild the canonical return tape of r, with the head on the first 1 of the
// c-run.  That is exactly where sim() accepts a return, so continuing from it
// runs the machine from the configuration it was really in.  Caller zeroes the
// tape; `off` must leave room for the left-hand (10)^p 1^(a+2) blocks.
static void build_ret_tape(const Res &r, int *tape, int off, int &pos) {
    int i = off;
    for (int k = 0; k < r.p; ++k) { tape[i++] = 1; tape[i++] = 0; }
    for (int k = 0; k < r.a + 2; ++k) tape[i++] = 1;
    pos = i;                                        // A on the c-run's first 1
    for (int k = 0; k < r.c; ++k) { tape[i++] = 1; tape[i++] = 0; }
    tape[i++] = 0;
    for (int k = 0; k < r.d; ++k) tape[i++] = 1;
    tape[i++] = 0;
    for (int k = 1; k < GAP; ++k) tape[i++] = 0;
    for (int k = 0; k < r.e; ++k) tape[i++] = 1;
}

// One chained round: continue the computation from r's real return tape and
// report the next accepted return.  Used by filter 5 (create -> two rounds).
static int chain_tape[CHAIN_CELLS];
static Res chain_round(const Res &r) {
    memset(chain_tape, 0, sizeof(chain_tape));
    int pos = 0;
    build_ret_tape(r, chain_tape, 32, pos);
    return run_from(chain_tape, CHAIN_CELLS, pos, CHAIN_LOCAL_CAP);
}

static bool post_filter(const std::vector<Res> &prev) {
#ifdef PF_TRACE                    // diagnostic build only: say which filter failed
#define PF_FAIL(n) (fprintf(stderr, "PF reject @%d\n", (n)), false)
#else
#define PF_FAIL(n) false
#endif
    // 1. blank non-trivial.  The search defines slots lazily, and an undefined
    //    slot halts, so a machine whose gadgets are perfect can still die on
    //    step 5 from the blank tape.  That is not a record, so it goes first.
    std::vector<int> tape(2 * BLANK_CAP + 2 * ORBIT_PAD, 0);
    Orbit o;
    if (!orbit_run(tape, BLANK_CAP + ORBIT_PAD, BLANK_CAP, o)) return PF_FAIL(1);
    if (o.halted) return PF_FAIL(1);

    // 2. core reachability: the orbit must run the M13 engine, not just a
    //    treadmill over the outer states.
    unsigned need = (1u << 3) | (1u << 4) | (1u << 7) | (1u << 12);   // D E H M
    if ((o.visited & need) != need) return PF_FAIL(2);

    // 3. branch liveness: E0 must be followed by a read of 1, i.e. the third
    //    counter must still be present, at least BRANCH_MIN times.  Machines
    //    that only create e read 0 on every later entry, so e never decreases.
    if (o.e0_read1 < BRANCH_MIN) return PF_FAIL(3);

    // 4. chained decrement: from the test-6 dec return (e = 1, d reloaded) one
    //    more w+2 round must end in a real halt.  Test 7 restarted at e = 3
    //    instead of continuing from that tape, so it never checked this.
    if (prev.size() > 6 && prev[6].kind == 3) {
        std::vector<int> ct(2 * CHAIN_CAP + 2 * ORBIT_PAD, 0);
        int pos = 0;
        build_ret_tape(prev[6], ct.data(), CHAIN_CAP + ORBIT_PAD, pos);
        Orbit oc;
        if (!orbit_run(ct, pos, CHAIN_CAP, oc)) return PF_FAIL(4);
        if (!oc.halted) return PF_FAIL(4);
    }

    // 5. chained create: the create return (test 4, d = 0) must be the INPUT of
    //    a real round, and that round's own return must be the input of another
    //    one.  This is M12's round-2 mechanism (Kd_step^(a1/6+1) applied to the
    //    real pa1) expressed as an orbit check: two successive returns, each
    //    consuming a counter (c or d strictly smaller), keeping e untouched and
    //    leaving an even accumulator.  A machine that writes a create gadget
    //    nobody consumes fails here even if its test-4 return has the right
    //    shape.  Two rounds rather than one, because a single CE_EVEN only
    //    consumes a c-token and would not show that d drains.
    if (prev.size() > 4 && prev[4].kind == 3) {
        Res r1 = chain_round(prev[4]);
        bool ok1 = r1.kind == 3 && r1.e == prev[4].e
                && r1.a >= 2 && !(r1.a & 1)
                && (r1.c < prev[4].c || r1.d < prev[4].d);
        if (!ok1) return PF_FAIL(5);
        Res r2 = chain_round(r1);
        bool ok2 = r2.kind == 3 && r2.e == prev[4].e
                && r2.a >= 2 && !(r2.a & 1)
                && (r2.c < r1.c || r2.d < r1.d);
        if (!ok2) return PF_FAIL(5);
    }
#undef PF_FAIL
    return true;
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
        printf("  nodes=%lld hits=%lld part=%lld rejected=%lld reach=", nodes, hits, partial, rejected);
        for (int i = 0; i < 10; ++i) printf("%lld ", reach[i]);
        printf("\n"); fflush(stdout);
    }
    if (idx == stop_after) {
        if (!post_filter(prev)) { rejected++; return; }
        hits++; print_machine("HIT_STOP", n_def, prev); return;
    }
    if (idx == 6) { partial++; if (partial <= PART_CAP) print_machine("PART_CREATE_HALT", n_def, prev); }
    if (idx == 7) { partial++; if (partial <= PART_CAP) print_machine("PART_DEC", n_def, prev); }
    if (idx == 8) { partial++; if (partial <= PART_CAP) print_machine("PART_DEC_EINDEP", n_def, prev); }
    if (idx == 9) {
        if (!post_filter(prev)) { rejected++; return; }
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
    nodes = hits = partial = rejected = 0;
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
            if (!post_filter(g_prev)) { ++rejected; return; }
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

// ===========================================================================
// layout m12
//
// The M12 core (12 states A..L), its own tape layout and its own tests.
// Everything above is m13 and stays untouched; main() dispatches on -layout.
//
//   Ce p a c d e = 0^inf (10)^p 1^(a+2) I> (10)^c 0 (10)^d 0^GAP 1^e 0^inf
//   Cd p b d e   = 0^inf (10)^p 1^(b+2) I> (10)^d 0^GAP 1^e 0^inf
//
// The head is in state I (not A), so returns are parsed at I, not at A.
// Fixed core: 22 of the 24 M12 transitions.  Free slots: I0, E0 (the two
// boundary transitions the third counter has to re-route) and every slot of
// the spare states M..Q (indices 12..16).  K0 = 1RZ is fixed, so no further
// 1RZ is ever offered and there is no "last slot must be 1RZ" rule here.
// ===========================================================================

static const int MAXT12 = 256;    // the local tests are tiny; chained rounds use CHAIN_CELLS
static const int MAXS12 = 3000;

struct Res12 { int kind; int cd; int us, ub; int p, a, c, d, e; };
// kind: 0 BAD, 1 UNDEF, 2 HALT, 3 RET;  cd: 0 = Ce return, 1 = Cd return

struct Test12 { int cdf, p, n, c, d, e; };  // cdf: 0 = Ce input, 1 = Cd input
static Test12 tests12[9];

static void init_base_m12(int ns) {
    n_states = ns;
    for (int s = 0; s < 17; ++s) for (int b = 0; b < 2; ++b) {
        tr[s][b] = {-1, 0, -1};
        fixed_slot[s][b] = false;
    }
    auto set = [&](char st, int b, int w, char dir, char nst) {
        tr[st - 'A'][b] = {w, dir == 'L' ? -1 : 1, nst == 'Z' ? 20 : nst - 'A'};
        fixed_slot[st - 'A'][b] = true;
    };
    set('A', 0, 1, 'R', 'B'); set('A', 1, 1, 'R', 'A');
    set('B', 0, 1, 'R', 'I'); set('B', 1, 1, 'R', 'C');
    set('C', 0, 0, 'L', 'D'); set('C', 1, 1, 'L', 'G');
    set('D', 0, 0, 'R', 'E'); set('D', 1, 1, 'L', 'D');
                              set('E', 1, 1, 'R', 'F');       // E0 free
    set('F', 0, 1, 'R', 'G'); set('F', 1, 0, 'R', 'A');
    set('G', 0, 1, 'R', 'A'); set('G', 1, 0, 'L', 'H');
    set('H', 0, 1, 'L', 'G'); set('H', 1, 1, 'L', 'H');
                              set('I', 1, 0, 'L', 'J');       // I0 free
    set('J', 0, 1, 'L', 'H'); set('J', 1, 1, 'L', 'I');
    set('K', 0, 1, 'R', 'Z'); set('K', 1, 0, 'L', 'L');       // K0 = the halt
    set('L', 0, 0, 'L', 'H'); set('L', 1, 1, 'L', 'K');

    n_free = 0;
    for (int s = 12; s < ns; ++s) free_states[n_free++] = s;
    n_choices = 0;
    for (int w = 0; w < 2; ++w)
        for (int mv : {-1, 1})
            for (int s = 0; s < ns; ++s) choices[n_choices++] = {w, mv, s};
}

static void build_tests12() {
    tests12[0] = {1, 2, 3, 0, 2, 2};   // C_REL base
    tests12[1] = {1, 2, 3, 0, 3, 2};   // C_REL, d+1        (d independence)
    tests12[2] = {1, 2, 3, 0, 2, 3};   // C_REL, e+1        (e independence)
    tests12[3] = {1, 2, 5, 0, 2, 2};   // C_REL, b=5        (c built from b)
    tests12[4] = {0, 2, 8, 0, 0, 0};   // create, a=8, d=0, e absent
    tests12[5] = {1, 1, 5, 0, 0, 1};   // halt, e=1
    tests12[6] = {1, 1, 5, 0, 0, 2};   // dec, e=2
    tests12[7] = {1, 1, 5, 0, 0, 3};   // dec, e=3          (e changes by 1)
    tests12[8] = {0, 2, 6, 0, 0, 0};   // create, a=6       (counters scale)
}

// Left side: 0^inf (10)^p 1^(ones), head at pos.  p = number of (10) pairs,
// ones = length of the accumulator run (a+2 or b+2).
static bool left12(const int *t, int cells, int pos, int &p_out, int &ones_out) {
    int i = pos - 1, ones = 0;
    while (i >= 0 && t[i] == 1) { ++ones; --i; }
    int p = 0;
    while (i >= 1 && t[i] == 0 && t[i - 1] == 1) { ++p; i -= 2; }
    for (int k = 0; k <= i && k < cells; ++k) if (t[k]) return false;
    p_out = p; ones_out = ones;
    return true;
}

static bool parse_ce12(const int *t, int cells, int pos, Res12 &r) {
    int p, ones;
    if (!left12(t, cells, pos, p, ones) || ones < 2) return false;
    int j = pos, c = 0;
    if (j < cells && t[j] == 1) {
        while (j + 1 < cells && t[j] == 1 && t[j + 1] == 0) { ++c; j += 2; }
        if (j >= cells || t[j] != 0) return false;
    } else {
        if (j >= cells || t[j] != 0) return false;
    }
    ++j;                                              // Ce separator
    int d = 0;
    while (j + 1 < cells && t[j] == 1 && t[j + 1] == 0) { ++d; j += 2; }
    for (int g = 0; g < GAP; ++g) { if (j >= cells || t[j] != 0) return false; ++j; }
    int e = 0;
    while (j < cells && t[j] == 1) { ++e; ++j; }
    for (int k = j; k < cells; ++k) if (t[k]) return false;
    r = Res12{3, 0, 0, 0, p, ones - 2, c, d, e};
    return true;
}

static bool parse_cd12(const int *t, int cells, int pos, Res12 &r) {
    int p, ones;
    if (!left12(t, cells, pos, p, ones) || ones < 2) return false;
    int j = pos, d = 0;
    if (j < cells && t[j] == 1)
        while (j + 1 < cells && t[j] == 1 && t[j + 1] == 0) { ++d; j += 2; }
    for (int g = 0; g < GAP; ++g) { if (j >= cells || t[j] != 0) return false; ++j; }
    int e = 0;
    while (j < cells && t[j] == 1) { ++e; ++j; }
    for (int k = j; k < cells; ++k) if (t[k]) return false;
    r = Res12{3, 1, 0, 0, p, ones - 2, 0, d, e};
    return true;
}

// Run from an arbitrary tape in state I and report the first accepted Ce/Cd
// return, an undefined slot, or a halt.
static Res12 run12(int *tape, int cells, int pos, int cap) {
    int st = 8;                                       // state I
    for (int step = 1; step <= cap; ++step) {
        if (pos < 2 || pos >= cells - 2) return Res12{0, 0, 0, 0, 0, 0, 0, 0, 0};
        if (step > 1 && st == 8) {
            Res12 r;
            if (parse_ce12(tape, cells, pos, r)) return r;
            if (parse_cd12(tape, cells, pos, r)) return r;
        }
        int sym = tape[pos];
        Trans t = tr[st][sym];
        if (t.nst == -1)
            return undef_halt ? Res12{2, 0, 0, 0, 0, 0, 0, 0, 0}
                              : Res12{1, 0, st, sym, 0, 0, 0, 0, 0};
        if (t.nst == 20) return Res12{2, 0, 0, 0, 0, 0, 0, 0, 0};
        tape[pos] = t.w; pos += t.mv; st = t.nst;
    }
    return Res12{0, 0, 0, 0, 0, 0, 0, 0, 0};
}

static int sim12_tape[MAXT12];

static Res12 sim12(const Test12 &t) {
    int *tape = sim12_tape;
    memset(tape, 0, sizeof(sim12_tape));
    int idx = 24;
    for (int k = 0; k < t.p; ++k) { tape[idx++] = 1; tape[idx++] = 0; }
    for (int k = 0; k < t.n + 2; ++k) tape[idx++] = 1;
    int pos = idx;
    if (t.cdf == 0) {
        for (int k = 0; k < t.c; ++k) { tape[idx++] = 1; tape[idx++] = 0; }
        tape[idx++] = 0;                              // Ce separator
        for (int k = 0; k < t.d; ++k) { tape[idx++] = 1; tape[idx++] = 0; }
    } else {
        for (int k = 0; k < t.d; ++k) { tape[idx++] = 1; tape[idx++] = 0; }
    }
    for (int k = 0; k < GAP; ++k) tape[idx++] = 0;
    for (int k = 0; k < t.e; ++k) tape[idx++] = 1;
    return run12(tape, MAXT12, pos, MAXS12);
}

static std::vector<Res12> g_prev12;

static bool check12(int idx, const Res12 &r, const std::vector<Res12> &prev) {
    const Test12 &t = tests12[idx];
    if (idx == 0)                                     // C_REL base
        return r.kind == 3 && r.cd == 0 && r.p == t.p - 1 && r.d == t.d - 1 && r.e == t.e
            && r.a >= 2 && !(r.a & 1) && r.c >= 1;
    if (idx == 1)                                     // d independence
        return r.kind == 3 && r.d == t.d - 1 && r.e == t.e
            && r.p == prev[0].p && r.a == prev[0].a && r.c == prev[0].c && r.e == prev[0].e;
    if (idx == 2)                                     // e independence
        return r.kind == 3 && r.e == t.e
            && r.p == prev[0].p && r.a == prev[0].a && r.c == prev[0].c && r.d == prev[0].d;
    if (idx == 3)                                     // c is built from b
        return r.kind == 3 && r.d == t.d - 1 && r.e == t.e && r.a >= 2 && !(r.a & 1)
            && r.p == prev[0].p && r.a == prev[0].a && r.c > prev[0].c;
    // A reloaded round may come back as a Ce (even a) or as a Cd (odd a), so
    // the create / decrement checks only require a real accumulator (a >= 2),
    // not a particular parity.
    if (idx == 4)                                     // create at d = 0: e and a counter
        return r.kind == 3 && (r.c >= 1 || r.d >= 1)
            && r.e >= 1 && r.a >= 2;
    if (idx == 6)                                     // decrement e, reload a round
        return r.kind == 3 && r.e == 1 && (r.c >= 1 || r.d >= 1) && r.a >= 2;
    if (idx == 7)                                     // e changes by exactly 1
        return r.kind == 3 && r.e == 2
            && r.p == prev[6].p && r.a == prev[6].a && r.c == prev[6].c && r.d == prev[6].d;
    if (idx == 8)                                     // created counters scale with a
        return r.kind == 3 && (r.c >= 1 || r.d >= 1)
            && r.e >= 1 && r.a >= 2
            && prev[4].e >= 2 && r.e < prev[4].e
            && (r.c + r.d) < (prev[4].c + prev[4].d);
    return false;
}

static void report12(int i, const Res12 &r) {
    if (r.kind == 1) printf(" %d:UNDEF(st%c,%d)", i, 'A' + r.us, r.ub);
    else if (r.kind == 2) printf(" %d:HALT", i);
    else printf(" %d:k%d%s(q%d,a%d,c%d,d%d,e%d)", i, r.kind, r.cd ? "D" : "E",
                r.p, r.a, r.c, r.d, r.e);
}

static void print_machine12(const char *tag, int n_def, const std::vector<Res12> &res) {
    fprintf(out, "[%s n_st=%d n_def=%d layout=m12] ", tag, n_states, n_def);
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
        fprintf(out, " | %zu:k%d%s(q%d,a%d,c%d,d%d,e%d)", i, res[i].kind,
                res[i].cd ? "D" : "E", res[i].p, res[i].a, res[i].c, res[i].d, res[i].e);
    fputc('\n', out);
    fflush(out);
}

// Rebuild the canonical return tape of r, head in state I on the first c/d
// token (or on the terminator when there is none).
static void build_ret_tape12(const Res12 &r, int *tape, int off, int &pos) {
    int i = off;
    for (int k = 0; k < r.p; ++k) { tape[i++] = 1; tape[i++] = 0; }
    for (int k = 0; k < r.a + 2; ++k) tape[i++] = 1;
    pos = i;
    if (r.cd == 0) {
        for (int k = 0; k < r.c; ++k) { tape[i++] = 1; tape[i++] = 0; }
        tape[i++] = 0;
        for (int k = 0; k < r.d; ++k) { tape[i++] = 1; tape[i++] = 0; }
    } else {
        for (int k = 0; k < r.d; ++k) { tape[i++] = 1; tape[i++] = 0; }
    }
    for (int k = 0; k < GAP; ++k) tape[i++] = 0;
    for (int k = 0; k < r.e; ++k) tape[i++] = 1;
}

struct Orbit12 {
    int status;                       // 0 timeout, 1 halted (1RZ), 2 undefined/off-arena
    long long steps;
    unsigned visited;
    long long i0ent, i0r1, e0ent, e0r1;
};

static Orbit12 orbit12(int *tape, int cells, int pos, int start_st, int cap) {
    Orbit12 o{0, 0, 0, 0, 0, 0, 0};
    int st = start_st;
    bool pend_i0 = false, pend_e0 = false;
    for (int step = 1; step <= cap; ++step) {
        if (pos < 1 || pos >= cells - 1) { o.status = 2; o.steps = step; return o; }
        int sym = tape[pos];
        o.visited |= 1u << st;
        if (pend_i0) { if (sym == 1) o.i0r1++; pend_i0 = false; }
        if (pend_e0) { if (sym == 1) o.e0r1++; pend_e0 = false; }
        if (st == 8 && sym == 0) { o.i0ent++; pend_i0 = true; }
        if (st == 4 && sym == 0) { o.e0ent++; pend_e0 = true; }
        Trans t = tr[st][sym];
        if (t.nst == -1) { o.status = 2; o.steps = step; return o; }
        if (t.nst == 20) { o.status = 1; o.steps = step; return o; }
        tape[pos] = t.w; pos += t.mv; st = t.nst;
    }
    o.steps = cap;
    return o;
}

static int chain12_tape[CHAIN_CELLS];
static Res12 chain12(const Res12 &r) {
    memset(chain12_tape, 0, sizeof(chain12_tape));
    int pos = 0;
    build_ret_tape12(r, chain12_tape, 32, pos);
    return run12(chain12_tape, CHAIN_CELLS, pos, CHAIN_LOCAL_CAP);
}

static bool post_filter12(const std::vector<Res12> &prev) {
#ifdef PF_TRACE
#define PF_FAIL12(n) (fprintf(stderr, "PF12 reject @%d\n", (n)), false)
#else
#define PF_FAIL12(n) false
#endif
    // 1. blank non-trivial.
    std::vector<int> tape((size_t)2 * BLANK_CAP + 2 * ORBIT_PAD, 0);
    Orbit12 o = orbit12(tape.data(), (int)tape.size(), BLANK_CAP + ORBIT_PAD, 0, BLANK_CAP);
    if (o.status != 0) return PF_FAIL12(1);

    // 2. core reachability: the M12 engine is run by A, D, G, H, driven by I.
    unsigned need = (1u << 3) | (1u << 6) | (1u << 7) | (1u << 8);   // D G H I
    if ((o.visited & need) != need) return PF_FAIL12(2);

    // 3. driver liveness: I0 must be entered more than once (plain M12: 3).
    if (o.i0ent < 2) return PF_FAIL12(3);

    // 4. chained dec: from the test-6 return (e = 1) one more real round must
    //    end in the fixed 1RZ halt, not in an undefined slot.
    if (prev.size() > 6 && prev[6].kind == 3) {
        std::vector<int> ct((size_t)2 * CHAIN_CAP + 2 * ORBIT_PAD, 0);
        int pos = 0;
        build_ret_tape12(prev[6], ct.data(), CHAIN_CAP + ORBIT_PAD, pos);
        Orbit12 oc = orbit12(ct.data(), (int)ct.size(), pos, 8, CHAIN_CAP);
        if (oc.status != 1) return PF_FAIL12(4);
    }

    // 5. chained create: from the test-4 return two successive real returns
    //    must each consume a counter and leave e untouched.
    if (prev.size() > 4 && prev[4].kind == 3) {
        Res12 r1 = chain12(prev[4]);
        bool ok1 = r1.kind == 3 && r1.e == prev[4].e && r1.a >= 2
                && (r1.c + r1.d) < (prev[4].c + prev[4].d);
        if (!ok1) return PF_FAIL12(5);
        Res12 r2 = chain12(r1);
        bool ok2 = r2.kind == 3 && r2.e == prev[4].e && r2.a >= 2
                && (r2.c + r2.d) < (r1.c + r1.d);
        if (!ok2) return PF_FAIL12(5);
    }
#undef PF_FAIL12
    return true;
}

static void dfs12(int idx, int n_def, int max_def, int used_mask,
                  std::vector<Res12> &prev) {
    nodes++;
    if (nodes > max_nodes && max_nodes) { aborted = true; return; }
    reach[idx]++;
    if ((nodes & 0xFFFFFF) == 0) {
        printf("  nodes=%lld hits=%lld part=%lld rejected=%lld reach=", nodes, hits, partial, rejected);
        for (int i = 0; i < 10; ++i) printf("%lld ", reach[i]);
        printf("\n"); fflush(stdout);
    }
    if (idx == stop_after) {
        if (!post_filter12(prev)) { rejected++; return; }
        hits++; print_machine12("HIT_STOP", n_def, prev); return;
    }
    if (idx == 6) { partial++; if (partial <= PART_CAP) print_machine12("PART_CREATE_HALT", n_def, prev); }
    if (idx == 7) { partial++; if (partial <= PART_CAP) print_machine12("PART_DEC", n_def, prev); }
    if (idx == 8) { partial++; if (partial <= PART_CAP) print_machine12("PART_DEC_EINDEP", n_def, prev); }

    Res12 r = sim12(tests12[idx]);

    if (r.kind == 1) {                                  // need one more definition
        if (n_def >= max_def) return;
        int st = r.us, sym = r.ub;
        for (int i = 0; i < n_choices; ++i) {
            if (n_def == 0 && nshard > 1 && (i % nshard) != shard) continue;
            Trans ch = choices[i];
            if (ch.nst == 20) continue;                  // K0 is the only halt
            int nm = used_mask;
            if (ch.nst >= 12) {                          // spare state M..
                int fi = ch.nst - 12;
                if (fi > 0) {
                    bool ok = true;
                    for (int k = 0; k < fi; ++k) if (!(used_mask & (1 << k))) ok = false;
                    if (!ok) continue;
                }
                nm |= (1 << fi);
            }
            tr[st][sym] = ch;
            dfs12(idx, n_def + 1, max_def, nm, prev);
            tr[st][sym] = {-1, 0, -1};
        }
        return;
    }
    if (idx == 5) {                                     // halt test (e = 1, d = 0)
        if (r.kind != 2) return;
        prev.push_back(r);
        dfs12(6, n_def, max_def, used_mask, prev);
        prev.pop_back();
        return;
    }
    if (r.kind != 3) return;
    if (!check12(idx, r, prev)) return;
    prev.push_back(r);
    dfs12(idx + 1, n_def, max_def, used_mask, prev);
    prev.pop_back();
}

static bool run_tests12() {
    g_prev12.clear();
    for (int i = 0; i < 9; ++i) {
        Res12 r = sim12(tests12[i]);
        if (i == 5) {
            if (r.kind != 2) return false;
            g_prev12.push_back(r);
            continue;
        }
        if (!check12(i, r, g_prev12)) return false;
        g_prev12.push_back(r);
    }
    return true;
}

static void nb_assign12(int ci, int r, const int *chosen, Trans *saved) {
    if (ci == r) {
        ++nb_tried;
        if ((nb_tried & 0xFFFFF) == 0) {
            printf("  nb tried=%lld hits=%lld\n", nb_tried, nb_hits); fflush(stdout);
        }
        if (run_tests12()) {
            if (!post_filter12(g_prev12)) { ++rejected; return; }
            ++nb_hits;
            print_machine12("NB_HIT_M12", 0, g_prev12);
        }
        return;
    }
    int s = chosen[ci] / 2, b = chosen[ci] % 2;
    saved[ci] = tr[s][b];
    for (int i = 0; i <= n_choices; ++i) {              // i == n_choices: undefined
        tr[s][b] = (i == n_choices) ? Trans{-1, 0, -1} : choices[i];
        nb_assign12(ci + 1, r, chosen, saved);
    }
    tr[s][b] = saved[ci];
}

static void nb_choose12(int start, int k, int r, int *chosen, Trans *saved) {
    if (k == r) { nb_assign12(0, r, chosen, saved); return; }
    for (int i = start; i < nb_n; ++i) {
        chosen[k] = nb_slots[i];
        nb_choose12(i + 1, k + 1, r, chosen, saved);
    }
}

static void run_one12(int ns, int max_def, int stop, long long cap) {
    init_base_m12(ns);
    build_tests12();
    reset_stats();
    stop_after = stop;

    printf("== w3b m12 n_states=%d n_free=%d max_def=%d stop=%d gap=%d cap=%lld shard=%d/%d\n",
           ns, n_free, max_def, stop, GAP, cap, shard, nshard);
    printf("sanity:");
    for (int i = 0; i < 9; ++i) report12(i, sim12(tests12[i]));
    printf("\n");
    fflush(stdout);

    max_nodes = cap;
    std::vector<Res12> prev;
    dfs12(0, 0, max_def, 0, prev);
    printf("DONE m12 n_states=%d gap=%d nodes=%lld hits=%lld part=%lld rejected=%lld%s reach=",
           ns, GAP, nodes, hits, partial, rejected, aborted ? " ABORTED(cap)" : "");
    for (int i = 0; i < 10; ++i) printf("%lld ", reach[i]);
    printf("\n");
    fflush(stdout);
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
    printf("DONE n_states=%d DD=%d gap=%d nodes=%lld hits=%lld part=%lld rejected=%lld%s reach=",
           ns, DD, GAP, nodes, hits, partial, rejected, aborted ? " ABORTED(cap)" : "");
    for (int i = 0; i < 10; ++i) printf("%lld ", reach[i]);
    printf("\n");
    fflush(stdout);
}

// `-layout m12` is a keyword argument and is removed before the positional
// arguments below are read, so every existing m13 command line still works.
int main(int argc, char **argv) {
    const char *layout = "m13";
    std::vector<char *> pa;
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "-layout") == 0) {
            if (i + 1 < argc) layout = argv[++i];
            continue;
        }
        pa.push_back(argv[i]);
    }
    const bool m12 = (strcmp(layout, "m12") == 0);
    const int np = (int)pa.size();

    int ns = np > 0 ? atoi(pa[0]) : 16;
    int max_def = np > 1 ? atoi(pa[1]) : 8;
    out = (np > 2 && strcmp(pa[2], "-") != 0) ? fopen(pa[2], "w") : stdout;
    if (!out) { fprintf(stderr, "cannot open %s\n", np > 2 ? pa[2] : "-"); return 1; }
    if (np > 3) stop_after = atoi(pa[3]);
    if (np > 4) fix_crel = atoi(pa[4]);
    if (np > 5) GAP = atoi(pa[5]);
    if (np > 6) DD = atoi(pa[6]);
    if (GAP < 1) GAP = 1;
    if (DD < 1) DD = 1;
    long long cap = np > 7 ? atoll(pa[7]) : 0;
    int sweep = np > 8 ? atoi(pa[8]) : 0;   // 1 = DD 1..3 x gap 1..3
    const char *seed = np > 9 ? pa[9] : nullptr;
    int radius = np > 10 ? atoi(pa[10]) : 2;
    if (np > 11) shard = atoi(pa[11]);
    if (np > 12) nshard = atoi(pa[12]);
    if (nshard < 1) nshard = 1;
    if (shard < 0 || shard >= nshard) shard = 0;
    if (m12 && (ns < 12 || ns > 17)) {
        fprintf(stderr, "-layout m12 needs 12 <= n_states <= 17 (got %d)\n", ns);
        return 1;
    }

    if (fix_crel == 2 && m12) {                 // m12 neighbourhood mode
        init_base_m12(ns);
        undef_halt = true;
        build_tests12();
        reset_stats();
        if (!seed || !load_seed(seed)) return 1;
        printf("== w3b m12 neighbourhood n_states=%d seed=%s gap=%d radius=%d\n",
               ns, seed, GAP, radius);
        printf("seed:");
        for (int i = 0; i < 9; ++i) report12(i, sim12(tests12[i]));
        printf("\nseed passes all nine: %s\n", run_tests12() ? "YES" : "no");
        nb_build_slots();
        printf("outer (changeable) slots: %d\n", nb_n);
        fflush(stdout);
        int chosen[16];
        Trans saved[16];
        for (int r = 0; r <= radius; ++r) {
            printf("-- radius %d\n", r); fflush(stdout);
            nb_choose12(0, 0, r, chosen, saved);
        }
        printf("DONE nb tried=%lld hits=%lld rejected=%lld\n", nb_tried, nb_hits, rejected);
        if (out != stdout) fclose(out);
        return 0;
    }

    if (fix_crel == 2) {                        // m13 neighbourhood mode
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
        printf("DONE nb tried=%lld hits=%lld rejected=%lld\n", nb_tried, nb_hits, rejected);
        if (out != stdout) fclose(out);
        return 0;
    }

    if (m12) {
        run_one12(ns, max_def, stop_after, cap);
    } else if (!sweep) {
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
