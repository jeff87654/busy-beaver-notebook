// bb34search.cpp  -- single-file 4-symbol TM search built on the Kropitz BB(3,4) core
//
// Core (fixed, from 1RB3LB1RZ2RA_2LC3RB1LC2RA_3RB1LB3LC2RC):
//   A: 1RB 3LB  ?   2RA        (A2 is the core's halt/redirect transition -> free)
//   B: 2LC 3RB 1LC 2RA
//   C: 3RB 1LB 3LC 2RC
//
// Seed family (the shape the fold produces; head on the FIRST 1, one 2 at the far right):
//   0^inf 3^a 2^b  A> 1^c 2  0^inf     a,b,c >= 1
//
// Modes
//   check    run one machine string on the seed grid and print fold events
//   maxhalt  states 4 / 5 (budgeted): max halting time over machine x seed
//   gadget   states 6 / 7 (budgeted): look for an f_(omega+1) gadget.
//            A candidate must halt on every seed, fold with strictly rising
//            levels inside each run, and fold strictly more often for larger
//            seeds (>= 3 seeds, monotone fold count).  Machines that never
//            halt but keep folding with rising levels are reported as f_w
//            engines (cat 2) instead.
//
// Machine strings in check/sim must use canonical state names A..G
// (block i is state 'A'+i); e.g. the 6-state fold machine is
//   1RB3LB2LD2RA_2LC3RB1LC2RA_3RB1LB3LC2RC_3RE0LD1LD2LD_0RE1LF2RE0RE_0LA0LA2RA0LA
//
// Everything is a SIMULATION search, not a proof (see AGENTS.md).
//
// Build:  g++ -O3 -march=native -o bb34search bb34search.cpp
// Run  :  ./bb34search check   --machine 1RB3LB2LD2RA_2LC3RB1LC2RA_3RB1LB3LC2RC_3RE0LD1LD2LD_0RE1LF2RE0RE_0LA0LA2RA0LA
//         ./bb34search maxhalt --states 4 --cap 50000 --bmax 3 --cmax 4 --amax 1
//         ./bb34search maxhalt --states 5 --budget 3e9
//         ./bb34search gadget  --states 7 --fixfold --budget 3e9 --minfolds 3
//         ./bb34search gadget  --states 6 --budget 3e9

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <cctype>
#include <string>
#include <vector>
#include <algorithm>
#include <ctime>

// ---------------------------------------------------------------- constants
static const int NSYM   = 4;       // symbols 0,1,2,3
static const int MAXST  = 8;       // A..H
static const int BANK   = 4096;    // tape cells per seed run (runaway machines stop here)
static const int MAXBANK= 64;      // max number of seeds
static const int CELLS  = BANK * MAXBANK;

static const int8_t UNASSIGNED = -2;   // free slot: the DFS must branch here
static const int8_t HALT_UNDEF = -1;   // '---' : halt before write/move
static const int8_t HALT_Z     = -3;   // 'wRZ' : write, move, then halt

struct Tr  { int8_t w, mv, nst; };
struct Choice { int8_t w, mv, nst; };
struct Seed { int a, b, c; };

// results of one seed run
struct RunRes { int8_t kind; int8_t grow; int32_t folds; int32_t lastLevel; int64_t steps; };
// kind: 1 halt, 2 cap, 3 cycle, 4 tape-overflow

// ---------------------------------------------------------------- globals
static Tr      trans_[MAXST][NSYM];
static int     nstates  = 4;
static int     mode     = 0;          // 1 = maxhalt, 2 = gadget
static long long CAP    = 50000;
static long long BUDGET = 0;          // 0 = unlimited (in TM steps)
static int     MINFOLDS = 3;
static bool    FIXFOLD  = false;
static int     TRACE    = 0;
static long long gSteps = 0;
static bool    gAbort   = false;

static uint8_t  tape_[CELLS];
static uint64_t zob_[NSYM * CELLS];
static uint64_t zpos_[CELLS];
static uint64_t zst_[MAXST];

static std::vector<int>     tpos_;
static std::vector<uint8_t> tval_;

static const int HB = 22;                 // 4M slots
static const int HS = 1 << HB;
static uint64_t hkey_[HS];
static uint8_t  hocc_[HS];
static std::vector<int> htrail_;

static std::vector<Choice> choices_;
static std::vector<Seed>   seeds_;
static RunRes gres_[MAXBANK];
static size_t smark_[MAXBANK];      // hash-trail size at the start of each seed run

// fold events of the current run
static long long gfoldCount = 0;
static int gfoldGrow  = 1;          // levels strictly increasing so far?
static int gfoldLast  = 0;          // level (2-run) of the most recent event
static int gfoldStep[64], gfoldLevel[64], gfold3[64];

struct FoldState {
    long long count; int grow; int last;
    int step[64], level[64], three[64];
};
static FoldState saveFold() {
    FoldState f;
    f.count = gfoldCount; f.grow = gfoldGrow; f.last = gfoldLast;
    memcpy(f.step, gfoldStep, sizeof(gfoldStep));
    memcpy(f.level, gfoldLevel, sizeof(gfoldLevel));
    memcpy(f.three, gfold3, sizeof(gfold3));
    return f;
}
static void restoreFold(const FoldState &f) {
    gfoldCount = f.count; gfoldGrow = f.grow; gfoldLast = f.last;
    memcpy(gfoldStep, f.step, sizeof(gfoldStep));
    memcpy(gfoldLevel, f.level, sizeof(gfoldLevel));
    memcpy(gfold3, f.three, sizeof(gfold3));
}

// best records
struct Best {
    long long steps = -1;
    int seed = -1;
    int used = 0;
    Tr tab[MAXST][NSYM];
};
static Best bestAll, bestRedir;     // maxhalt
struct GadgetHit {
    int cat;            // 1 = f_(w+1) candidate, 2 = f_w engine
    int folds;          // max fold count
    int spread;         // max-min fold count over halting seeds
    int used;
    Tr tab[MAXST][NSYM];
    int foldPerSeed[MAXBANK];
};
static std::vector<GadgetHit> gadgetHits_;

static long long gNodes = 0;
static long long gEval  = 0;
static time_t gLastPrint = 0;

// ---------------------------------------------------------------- helpers
static inline uint64_t splitmix64(uint64_t &x) {
    x += 0x9E3779B97F4A7C15ull;
    uint64_t z = x;
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}

static void initZobrist() {
    uint64_t s = 0x123456789abcdefull;
    for (int i = 0; i < NSYM * CELLS; ++i) zob_[i] = splitmix64(s);
    for (int i = 0; i < CELLS; ++i)        zpos_[i] = splitmix64(s);
    for (int i = 0; i < MAXST; ++i)        zst_[i]  = splitmix64(s);
}

static inline void twrite(int p, uint8_t v) {
    tpos_.push_back(p); tval_.push_back(tape_[p]); tape_[p] = v;
}
static inline void tundo(size_t m) {
    while (tpos_.size() > m) {
        tape_[tpos_.back()] = tval_.back();
        tpos_.pop_back(); tval_.pop_back();
    }
}
static inline bool htTry(uint64_t k) {
    int i = (int)(k & (uint64_t)(HS - 1));
    int probes = 0;
    while (hocc_[i]) {
        if (hkey_[i] == k) return false;          // seen before -> cycle
        i = (i + 1) & (HS - 1);
        if (++probes > 4096) return true;         // table saturated: skip (never hang)
    }
    hocc_[i] = 1; hkey_[i] = k; htrail_.push_back(i);
    return true;
}
static inline void htUndo(size_t m) {
    while (htrail_.size() > m) { hocc_[htrail_.back()] = 0; htrail_.pop_back(); }
}

static inline bool stateUsed(int s) {
    for (int y = 0; y < NSYM; ++y) if (trans_[s][y].nst != UNASSIGNED) return true;
    return false;
}
static inline bool allowNst(int s) {           // canonical state-introduction order
    if (s < 3) return true;
    for (int j = 3; j < s; ++j) if (!stateUsed(j)) return false;
    return true;
}

static int countUsedStates() {
    int n = 0;
    for (int s = 0; s < nstates; ++s) if (stateUsed(s)) ++n;
    return n;
}

static void setRow(int s, const char *blk) {   // blk = 4 transitions, 3 chars each
    for (int y = 0; y < NSYM; ++y) {
        const char *t = blk + 3 * y;
        if (t[0] == '-') { trans_[s][y] = {0, 0, HALT_UNDEF}; continue; }
        int w = t[0] - '0';
        int mv = (t[1] == 'L') ? -1 : 1;
        int8_t ns;
        if (t[2] == 'Z') ns = HALT_Z;
        else ns = (int8_t)(t[2] - 'A');
        trans_[s][y] = {(int8_t)w, (int8_t)mv, ns};
    }
}

static void setupCore() {
    for (int s = 0; s < MAXST; ++s)
        for (int y = 0; y < NSYM; ++y) trans_[s][y] = {0, 0, UNASSIGNED};
    trans_[0][0] = {1, 1, 1};                  // A0 = 1RB
    trans_[0][1] = {3, -1, 1};                 // A1 = 3LB
    trans_[0][2] = {0, 0, UNASSIGNED};         // A2 = FREE (the core's halt / redirect)
    trans_[0][3] = {2, 1, 0};                  // A3 = 2RA
    setRow(1, "2LC3RB1LC2RA");                 // B
    setRow(2, "3RB1LB3LC2RC");                 // C
}

static void buildChoices() {
    choices_.clear();
    for (int w = 0; w < NSYM; ++w)
        for (int mv = -1; mv <= 1; mv += 2) {
            for (int s = 0; s < nstates; ++s)
                choices_.push_back({(int8_t)w, (int8_t)mv, (int8_t)s});
            choices_.push_back({(int8_t)w, (int8_t)mv, HALT_Z});
        }
    choices_.push_back({0, 0, HALT_UNDEF});
}

// ---------------------------------------------------------------- fold note
// A real "fold event" is a hallt-type config of the core:
//     0^inf 3^(2m+1) 2^k  A> 2  0^inf        (3-run must be odd, right cell blank)
// Anything else where A happens to read a 2 is machinery noise and is ignored.
static void noteFold(long long step, int pos, int lo, int hi) {
    int i = pos - 1, n2 = 0, n3 = 0;
    while (i >= lo && tape_[i] == 2) { ++n2; --i; }
    while (i >= lo && tape_[i] == 3) { ++n3; --i; }
    if (n3 < 1 || (n3 & 1) == 0) return;
    if (i >= lo && tape_[i] != 0) return;
    if ((pos + 1 < hi ? tape_[pos + 1] : 0) != 0) return;
    if (gfoldCount > 0 && n2 <= gfoldLast) gfoldGrow = 0;
    if (gfoldCount < 64) {
        gfoldStep[gfoldCount] = (int)step;
        gfoldLevel[gfoldCount] = n2;
        gfold3[gfoldCount] = n3;
    }
    gfoldLast = n2;
    ++gfoldCount;
}

// ---------------------------------------------------------------- evaluation
static void printTab(const Tr tab[MAXST][NSYM], int used) {
    for (int s = 0; s < nstates; ++s) {
        if (s >= used) { printf("[unused] "); }
        for (int y = 0; y < NSYM; ++y) {
            Tr t = tab[s][y];
            if (t.nst == UNASSIGNED || t.nst == HALT_UNDEF) printf("---");
            else if (t.nst == HALT_Z) printf("%d%cZ", t.w, t.mv < 0 ? 'L' : 'R');
            else printf("%d%c%c", t.w, t.mv < 0 ? 'L' : 'R', 'A' + t.nst);
        }
        if (s + 1 < nstates) printf("_");
    }
    printf("\n");
}

static void copyTab(Tr dst[MAXST][NSYM], const Tr src[MAXST][NSYM]) {
    for (int s = 0; s < MAXST; ++s)
        for (int y = 0; y < NSYM; ++y) dst[s][y] = src[s][y];
}

static void evaluate() {
    int used = countUsedStates();
    ++gEval;

    if (mode == 3) {                    // sim: dump every seed result
        for (int i = 0; i < (int)seeds_.size(); ++i)
            printf("  seed (%d,%d,%d): kind=%d steps=%lld folds=%d grow=%d lastLevel=%d\n",
                   seeds_[i].a, seeds_[i].b, seeds_[i].c, gres_[i].kind, (long long)gres_[i].steps,
                   (int)gres_[i].folds, (int)gres_[i].grow, (int)gres_[i].lastLevel);
        fflush(stdout);
        return;
    }

    if (mode == 1) {
        long long bs = -1; int bseed = -1;
        for (int i = 0; i < (int)seeds_.size(); ++i)
            if (gres_[i].kind == 1 && gres_[i].steps > bs) { bs = gres_[i].steps; bseed = i; }
        if (bs < 0) return;

        bool a2redir = !(trans_[0][2].nst == HALT_UNDEF || trans_[0][2].nst == HALT_Z);
        if (bs > bestAll.steps) {
            bestAll.steps = bs; bestAll.seed = bseed; bestAll.used = used;
            copyTab(bestAll.tab, trans_);
            printf("\n[maxhalt] NEW BEST steps=%lld  seed(a=%d,b=%d,c=%d)  states_used=%d\n",
                   bs, seeds_[bseed].a, seeds_[bseed].b, seeds_[bseed].c, used);
            printf("          "); printTab(trans_, used);
            fflush(stdout);
        }
        if (a2redir && bs > bestRedir.steps) {
            bestRedir.steps = bs; bestRedir.seed = bseed; bestRedir.used = used;
            copyTab(bestRedir.tab, trans_);
            printf("\n[maxhalt] NEW BEST(A2 redirected) steps=%lld  seed(a=%d,b=%d,c=%d)  states_used=%d\n",
                   bs, seeds_[bseed].a, seeds_[bseed].b, seeds_[bseed].c, used);
            printf("          "); printTab(trans_, used);
            fflush(stdout);
        }
    } else if (mode == 2) {
        // A genuine f_(omega+1) gadget must do more folding for larger seeds,
        // and each run must fold with strictly rising levels.  Requiring a
        // monotone fold-count sequence over >= 3 seeds kills the noise where two
        // different branches merely fold a different number of times.
        const int ns = (int)seeds_.size();
        int perSeed[MAXBANK], perLevel[MAXBANK], perGrow[MAXBANK];
        int nhalt = 0, maxF = 0, minF = 1 << 20;
        bool allHalt = true, allGrow = true;
        for (int i = 0; i < ns; ++i) {
            perSeed[i] = gres_[i].folds;
            perLevel[i] = gres_[i].lastLevel;
            perGrow[i] = gres_[i].grow;
            maxF = std::max(maxF, (int)gres_[i].folds);
            if (gres_[i].kind == 1) {
                ++nhalt;
                minF = std::min(minF, (int)gres_[i].folds);
                if (!gres_[i].grow) allGrow = false;
            } else {
                allHalt = false;
                if (!gres_[i].grow) allGrow = false;
            }
        }
        bool monotone = true;
        for (int i = 1; i < ns; ++i) if (perSeed[i] <= perSeed[i - 1]) monotone = false;
        // cat 1: a halting f_(omega+1) gadget
        bool cat1 = (ns >= 3) && allHalt && allGrow && monotone && (maxF >= MINFOLDS);
        // cat 2: an f_omega engine (never halts, folds with rising levels)
        bool cat2 = (nhalt == 0) && (maxF >= MINFOLDS) && allGrow;
        if (cat1 || cat2) {
            GadgetHit h;
            h.cat = cat1 ? 1 : 2;
            h.folds = maxF;
            h.spread = (nhalt >= 1) ? (maxF - minF) : 0;
            h.used = used;
            copyTab(h.tab, trans_);
            for (int i = 0; i < MAXBANK; ++i) h.foldPerSeed[i] = (i < ns) ? perSeed[i] : -1;
            gadgetHits_.push_back(h);
            if (h.cat == 1) {
                printf("\n[gadget] F_(w+1) CANDIDATE  folds=%d spread=%d states_used=%d\n", maxF, h.spread, used);
            } else if (gadgetHits_.size() <= 20) {
                printf("\n[gadget] f_w engine  folds=%d states_used=%d\n", maxF, used);
            } else return;
            printf("         folds/level/grow per seed:");
            for (int i = 0; i < ns; ++i)
                printf(" (%d,%d,%d):%d/%d/%d", seeds_[i].a, seeds_[i].b, seeds_[i].c,
                       perSeed[i], perLevel[i], perGrow[i]);
            printf("\n         "); printTab(trans_, used);
            fflush(stdout);
        }
    }
}

// ---------------------------------------------------------------- search
static void startSeed(int si);
static void finish(int si, int kind, long long steps, int folds);

static void search(int si, int pos, int st, long long steps, uint64_t h, int lo, int hi) {
    for (;;) {
        if (gAbort) return;
        if (steps >= CAP) { finish(si, 2, steps, gfoldCount); return; }
        if (pos < lo || pos >= hi) { finish(si, 4, steps, gfoldCount); return; }

        int sym = tape_[pos];
        if (st == 0 && sym == 2) noteFold(steps, pos, lo, hi);

        uint64_t key = h ^ zst_[st] ^ zpos_[pos];
        if (!htTry(key)) { finish(si, 3, steps, gfoldCount); return; }

        Tr t = trans_[st][sym];
        if (t.nst == UNASSIGNED) {
            ++gNodes;
            // Fold counters are global, but every DFS branch re-simulates from here.
            // Save the count at the branch point and restore it after each child,
            // otherwise later branches inherit events from earlier ones (false hits).
            FoldState fs = saveFold();
            const int nch = (int)choices_.size();
            for (int ci = 0; ci < nch; ++ci) {
                Choice c = choices_[ci];
                if (c.nst >= 3 && !allowNst(c.nst)) continue;
                trans_[st][sym] = {c.w, c.mv, c.nst};
                size_t tm = tpos_.size(), hm = htrail_.size();
                if (c.nst == HALT_UNDEF) {
                    finish(si, 1, steps + 1, gfoldCount);
                } else {
                    uint8_t old = tape_[pos];
                    twrite(pos, (uint8_t)c.w);
                    uint64_t nh = h ^ zob_[old * CELLS + pos] ^ zob_[(int)c.w * CELLS + pos];
                    if (c.nst == HALT_Z) finish(si, 1, steps + 1, gfoldCount);
                    else                 search(si, pos + c.mv, c.nst, steps + 1, nh, lo, hi);
                }
                tundo(tm); htUndo(hm);
                trans_[st][sym] = {0, 0, UNASSIGNED};
                restoreFold(fs);
                if (gAbort) return;
            }
            return;
        }

        if (t.nst == HALT_UNDEF) { finish(si, 1, steps + 1, gfoldCount); return; }

        uint8_t old = tape_[pos];
        twrite(pos, (uint8_t)t.w);
        h ^= zob_[old * CELLS + pos] ^ zob_[(int)t.w * CELLS + pos];
        pos += t.mv;
        ++steps;
        ++gSteps;
        if ((gSteps & 0xFFFFFF) == 0) {
            if (BUDGET && gSteps > BUDGET) { gAbort = true; return; }
            time_t now = time(NULL);
            if (now != gLastPrint) {
                gLastPrint = now;
                fprintf(stderr, "  ... steps=%lld nodes=%lld\n", gSteps, gNodes);
            }
        }
        if (t.nst == HALT_Z) { finish(si, 1, steps, gfoldCount); return; }
        st = t.nst;
    }
}

static void finish(int si, int kind, long long steps, int folds) {
    gres_[si].kind = (int8_t)kind;
    gres_[si].steps = steps;
    gres_[si].folds = (int32_t)folds;
    gres_[si].grow = (int8_t)gfoldGrow;
    gres_[si].lastLevel = (folds > 0 && folds <= 64) ? gfoldLevel[folds - 1] : -1;
    htUndo(smark_[si]);                 // drop this seed's cycle-detection entries
    if (si + 1 < (int)seeds_.size()) startSeed(si + 1);
    else evaluate();
}

static void startSeed(int si) {
    smark_[si] = htrail_.size();
    int lo = si * BANK, hi = lo + BANK;
    int p = lo + BANK / 2 - 64;
    const Seed &sd = seeds_[si];
    for (int i = 0; i < sd.a; ++i) twrite(p++, 3);
    for (int i = 0; i < sd.b; ++i) twrite(p++, 2);
    int head = p;
    for (int i = 0; i < sd.c; ++i) twrite(p++, 1);
    twrite(p++, 2);
    gfoldCount = 0;
    gfoldGrow = 1;
    gfoldLast = 0;
    search(si, head, 0, 0, 0, lo, hi);
}

// ---------------------------------------------------------------- check mode
static void runCheck(const std::vector<Seed> &ss) {
    for (size_t k = 0; k < ss.size(); ++k) {
        int lo = 0, hi = CELLS;
        memset(tape_, 0, sizeof(tape_));
        tpos_.clear(); tval_.clear(); htrail_.clear(); memset(hocc_, 0, sizeof(hocc_));
        int p = CELLS / 2 - 64;
        for (int i = 0; i < ss[k].a; ++i) tape_[p++] = 3;
        for (int i = 0; i < ss[k].b; ++i) tape_[p++] = 2;
        int head = p;
        for (int i = 0; i < ss[k].c; ++i) tape_[p++] = 1;
        tape_[p++] = 2;
        gfoldCount = 0;
        gfoldGrow = 1;
        gfoldLast = 0;
        int pos = head, st = 0; long long h = 0; long long steps = 0;
        const char *res = "CAP";
        for (;;) {
            if (steps >= CAP) { res = "CAP"; break; }
            if (pos < lo || pos >= hi) { res = "TAPE"; break; }
            int sym = tape_[pos];
            if (st == 0 && sym == 2) noteFold(steps, pos, lo, hi);
            uint64_t key = (uint64_t)h ^ zst_[st] ^ zpos_[pos];
            if (!htTry(key)) { res = "CYCLE"; break; }
            Tr t = trans_[st][sym];
            if (t.nst == HALT_UNDEF) { ++steps; res = "HALT"; break; }
            uint8_t old = tape_[pos];
            tape_[pos] = (uint8_t)t.w;
            h ^= (long long)(zob_[old * CELLS + pos] ^ zob_[(int)t.w * CELLS + pos]);
            pos += t.mv; ++steps;
            if (TRACE && steps <= TRACE) {
                printf("    step %lld: state %c pos %d write %d -> %c%c%c\n",
                       steps, 'A' + st, pos - t.mv, (int)t.w,
                       t.w, t.mv < 0 ? 'L' : 'R', t.nst == HALT_Z ? 'Z' : ('A' + (char)t.nst));
            }
            if (t.nst == HALT_Z) { res = "HALT"; break; }
            st = t.nst;
        }
        printf("seed a=%d b=%d c=%d : %s steps=%lld folds=%lld", ss[k].a, ss[k].b, ss[k].c, res, steps, gfoldCount);
        if (gfoldCount > 0) {
            printf("  events:");
            int lim = (int)std::min<long long>(gfoldCount, 8);
            for (int i = 0; i < lim; ++i)
                printf(" (step %d, 3-run %d, 2-run %d)", gfoldStep[i], gfold3[i], gfoldLevel[i]);
        }
        printf("\n");
        fflush(stdout);
    }
}

// ---------------------------------------------------------------- main
static void usage() {
    printf("usage:\n");
    printf("  bb34search check   --machine STR [--a 1 --b 1,3 --c 1,2,3] [--cap N]\n");
    printf("  bb34search maxhalt --states 4|5 [--cap N] [--amax 1 --bmax 3 --cmax 4] [--budget N]\n");
    printf("  bb34search gadget  --states 6|7 [--fixfold] [--minfolds 3] [--budget N] [--cap N]\n");
}

static std::vector<int> parseList(const char *s) {
    std::vector<int> v;
    const char *p = s;
    while (*p) {
        char *e;
        long x = strtol(p, &e, 10);
        if (e == p) break;
        v.push_back((int)x);
        p = e;
        while (*p == ',' || *p == ' ') ++p;
    }
    if (v.empty()) v.push_back(0);
    return v;
}

static void addSeeds(const std::vector<int> &A, const std::vector<int> &B,
                     const std::vector<int> &C) {
    seeds_.clear();
    for (int a : A) for (int b : B) for (int c : C) {
        if ((int)seeds_.size() >= MAXBANK) { fprintf(stderr, "too many seeds (max %d)\n", MAXBANK); exit(1); }
        seeds_.push_back({a, b, c});
    }
}

int main(int argc, char **argv) {
    if (argc < 2) { usage(); return 1; }
    std::string cmd = argv[1];
    std::string machine;
    std::vector<int> A{1}, B{1, 2}, C{1, 2, 3};
    bool Aexact = false, Bexact = false, Cexact = false;

    for (int i = 2; i < argc; ++i) {
        std::string k = argv[i];
        auto next = [&](const char *def) -> const char * {
            if (i + 1 < argc) return argv[++i];
            return def;
        };
        if      (k == "--machine") machine = next("");
        else if (k == "--states")  nstates = atoi(next("4"));
        else if (k == "--cap")     CAP = atoll(next("50000"));
        else if (k == "--budget")  BUDGET = atoll(next("0"));
        else if (k == "--minfolds")MINFOLDS = atoi(next("3"));
        else if (k == "--fixfold") FIXFOLD = true;
        else if (k == "--trace")   TRACE = atoi(next("30"));
        else if (k == "--amax")    { std::vector<int> v = parseList(next("1")); A.clear(); for (int a = 1; a <= v[0]; ++a) A.push_back(a); Aexact = true; }
        else if (k == "--bmax")    { std::vector<int> v = parseList(next("2")); B.clear(); for (int b = 1; b <= v[0]; ++b) B.push_back(b); Bexact = true; }
        else if (k == "--cmax")    { std::vector<int> v = parseList(next("3")); C.clear(); for (int c = 1; c <= v[0]; ++c) C.push_back(c); Cexact = true; }
        else if (k == "--a")       { A = parseList(next("1")); Aexact = true; }
        else if (k == "--b")       { B = parseList(next("1")); Bexact = true; }
        else if (k == "--c")       { C = parseList(next("1")); Cexact = true; }
        else { fprintf(stderr, "unknown option %s\n", k.c_str()); usage(); return 1; }
    }
    if (nstates < 3 || nstates > MAXST) { fprintf(stderr, "bad --states\n"); return 1; }

    initZobrist();
    memset(tape_, 0, sizeof(tape_));
    memset(hocc_, 0, sizeof(hocc_));

    if (cmd == "check" || cmd == "sim") {
        if (machine.empty()) { fprintf(stderr, "--machine required\n"); return 1; }
        // parse machine string
        for (int s = 0; s < MAXST; ++s)
            for (int y = 0; y < NSYM; ++y) trans_[s][y] = {0, 0, UNASSIGNED};
        int s = 0; size_t i = 0;
        while (i < machine.size() && s < MAXST) {
            size_t j = machine.find('_', i);
            std::string blk = machine.substr(i, j == std::string::npos ? std::string::npos : j - i);
            if (blk.size() != 12) { fprintf(stderr, "bad block '%s'\n", blk.c_str()); return 1; }
            setRow(s, blk.c_str());
            ++s;
            if (j == std::string::npos) break;
            i = j + 1;
        }
        nstates = s;
        // Machine strings MUST use canonical state names A..G (block i is state 'A'+i).
        for (int q = 0; q < nstates; ++q)
            for (int y = 0; y < NSYM; ++y) {
                int8_t ns = trans_[q][y].nst;
                if (ns >= nstates) {
                    fprintf(stderr,
                        "block %d (%c) symbol %d targets state '%c' but only %d states exist; "
                        "use canonical names A..%c\n",
                        q, 'A' + q, y, 'A' + ns, nstates, 'A' + nstates - 1);
                    return 1;
                }
            }
        if (TRACE) {
            printf("parsed table:\n");
            for (int q = 0; q < nstates; ++q) {
                printf("  %c:", 'A' + q);
                for (int y = 0; y < NSYM; ++y) {
                    Tr t = trans_[q][y];
                    if (t.nst == HALT_UNDEF) printf(" ---");
                    else printf(" %d%c%c(w=%d,mv=%d,ns=%d)", t.w, t.mv < 0 ? 'L' : 'R',
                                t.nst == HALT_Z ? 'Z' : (char)('A' + t.nst), (int)t.w, (int)t.mv, (int)t.nst);
                }
                printf("\n");
            }
        }
        addSeeds(A, B, C);
        if (cmd == "sim") {                 // same machine, but through the search/startSeed path
            mode = 3;
            printf("sim states=%d seeds=%zu cap=%lld\n", nstates, seeds_.size(), CAP);
            startSeed(0);
            return 0;
        }
        mode = 0;
        runCheck(seeds_);
        return 0;
    }

    setupCore();
    if (FIXFOLD) {
        // fold6c gadget fixed; only A2 (already free) and the last state stay free
        if (nstates < 7) { fprintf(stderr, "--fixfold needs --states 7\n"); return 1; }
        trans_[3][0] = {3, 1, 4};  trans_[3][1] = {0, -1, 3};
        trans_[3][2] = {1, -1, 3}; trans_[3][3] = {2, -1, 3};       // X
        trans_[4][0] = {0, 1, 4};  trans_[4][1] = {1, -1, 5};
        trans_[4][2] = {2, 1, 4};  trans_[4][3] = {0, 1, 4};        // Y
        trans_[5][0] = {0, -1, 0}; trans_[5][1] = {0, -1, 0};
        trans_[5][2] = {2, 1, 0};  trans_[5][3] = {0, -1, 0};       // W
    }
    buildChoices();

    if (cmd == "maxhalt") {
        mode = 1;
        addSeeds(A, B, C);
    } else if (cmd == "gadget") {
        mode = 2;
        addSeeds(A, B, C);
    } else { usage(); return 1; }

    printf("mode=%s states=%d seeds=%zu cap=%lld budget=%lld fixfold=%d\n",
           cmd.c_str(), nstates, seeds_.size(), CAP, BUDGET, (int)FIXFOLD);
    printf("seeds:");
    for (auto &s : seeds_) printf(" (%d,%d,%d)", s.a, s.b, s.c);
    printf("\n");

    gLastPrint = time(NULL);
    startSeed(0);

    printf("\n---- done ----\n");
    printf("steps=%lld nodes=%lld tables=%lld abort=%d\n", gSteps, gNodes, gEval, (int)gAbort);
    if (mode == 1) {
        if (bestAll.steps >= 0) {
            printf("best overall: steps=%lld seed(a=%d,b=%d,c=%d) states_used=%d\n",
                   bestAll.steps, seeds_[bestAll.seed].a, seeds_[bestAll.seed].b,
                   seeds_[bestAll.seed].c, bestAll.used);
            printf("  "); printTab(bestAll.tab, bestAll.used);
        }
        if (bestRedir.steps >= 0) {
            printf("best with A2 redirected: steps=%lld seed(a=%d,b=%d,c=%d) states_used=%d\n",
                   bestRedir.steps, seeds_[bestRedir.seed].a, seeds_[bestRedir.seed].b,
                   seeds_[bestRedir.seed].c, bestRedir.used);
            printf("  "); printTab(bestRedir.tab, bestRedir.used);
        }
    } else if (mode == 2) {
        int c1 = 0, c2 = 0;
        for (auto &h : gadgetHits_) { if (h.cat == 1) ++c1; else ++c2; }
        printf("gadget hits: f_(w+1) candidates=%d  f_w engines=%d\n", c1, c2);
        int shown = 0;
        for (auto &h : gadgetHits_) {
            if (h.cat != 1) continue;
            printf("  [CAT1] folds=%d spread=%d states_used=%d\n    ", h.folds, h.spread, h.used);
            printTab(h.tab, h.used);
            if (++shown >= 20) break;
        }
    }
    return 0;
}
