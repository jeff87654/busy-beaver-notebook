static bool FREE[16][2];
static string machStr() {
    string s;
    for (int q = 0; q < NS; ++q) {
        if (q) s += '_';
        for (int c = 0; c < 2; ++c) { const Tr &t = TT[q][c]; if (t.halt) s += "---"; else { s += char('0' + t.w); s += t.d ? 'R' : 'L'; s += char('A' + t.nx); } }
    }
    return s;
}
struct Runner {
    RuleSet RS; Sim M; unordered_map<ull, array<ll, 3>> past; string verdict = "BUDGET", detail = "-"; ll lastBlank = -1; int blankFails = 0;
    Runner() {}
    Runner(const Runner &o) : RS(o.RS), M(o.M), lastBlank(o.lastBlank), blankFails(o.blankFails) { M.rules = &RS; }
    void run() {
        verdict = "BUDGET"; detail = "-";
        try {
            auto t0 = chrono::steady_clock::now();
            while (M.macro < OPT.budget) {
                if (OPT.tlimit > 0 && (M.macro & 1023) == 0 && chrono::duration<double>(chrono::steady_clock::now() - t0).count() > OPT.tlimit) { detail = "time"; break; }
                if (M.trace && M.macro < OPT.tracemax) fprintf(stderr, "%lld [%s] %s\n", M.macro, M.stepsKnown ? s128(M.steps.c).c_str() : "?", M.show().c_str());
                if (!OPT.noprove) {
                    ull sg = M.signature(); auto it = past.find(sg);
                    if (it == past.end()) past[sg] = {M.macro, -1, 0};
                    else {
                        auto &p = it->second; ll d = M.macro - p[0];
                        if (d == p[1] && p[2] < 3 && d <= MAXDELTA) {
                            int r = tryProve(M, d);
                            if (r == 2) { verdict = "CYCLE"; detail = M.cyc; break; }
                            if (r == 1) p[2] = 0; else p[2]++;
                        }
                        p[1] = d; p[0] = M.macro;
                    }
                    if (past.size() > 3000000) past.clear();
                }
                if ((M.macro & 511) == 0) for (int s = 0; s < 2; ++s) if (M.c.st[s].size() > 24) M.deepCompress(s);
                int st = M.macroStep();
                if (st == S_HALT) { verdict = "HALT"; break; }
                if (st == S_CYCLE) { verdict = "CYCLE"; detail = M.cyc; break; }
                // rebuild-cycle trigger: the list is used up (Kd 0^k 0 X, X symbolic) -- try a proof over one round
                if (!OPT.noprove && M.c.q == 3 && M.c.f == 0 && M.c.st[0].empty() && M.c.st[1].size() == 1 && M.c.st[1][0].w == "1" && !M.c.st[1][0].n.isExact()) {
                    if (lastBlank >= 0 && blankFails < 6 && M.macro - lastBlank <= 6 * MAXDELTA) {
                        UNTILBLANK = true; int r = tryProve(M, M.macro - lastBlank + 64); UNTILBLANK = false;
                        if (r == 2) { verdict = "CYCLE"; detail = M.cyc + "-KB"; break; }
                        if (r != 1) ++blankFails;
                    }
                    lastBlank = M.macro;
                }
            }
        } catch (Undec &u) { verdict = "UNDECIDED"; detail = u.why; }
        catch (std::exception &ex) { verdict = "UNDECIDED"; detail = string("exception ") + ex.what(); }
        for (auto &ch : detail) if (ch == ' ') ch = '_';
    }
    string report(const string &tag, const string &mach, int start) {
        string sig = "?", sd;
        try {
            Lin s = M.sigma();
            if (verdict == "HALT" && M.haltS == 0) s = laddc(s, 1);   // the halting transition writes a 1
            sig = linstr(s); if (verdict == "HALT") sd = symDescs(s);
        } catch (Undec &) {}
        string jl; for (auto &x : M.jlog) jl += " " + x;
        char buf[600];
        snprintf(buf, sizeof buf, " macro=%lld steps=%s sigma=%s kd=%lld big=%lld hslot=%c%d rules=%zu apps=%lld syms=%zu |", M.macro,
                 M.stepsKnown ? s128(M.steps.c).c_str() : "?", sig.c_str(), M.kdJumps, M.kdBig, verdict == "HALT" ? 'A' + M.haltQ : '-',
                 verdict == "HALT" ? M.haltS : 0, RS.R.size(), M.ruleApps, GS.size());
        return tag + " " + mach + " " + string(1, char('A' + start)) + " " + verdict + " " + detail + buf + jl + " |" + sd;
    }
};
static void runOne(const string &mach, int start, const vector<string> &tok) {
    GS.clear(); MINI.clear();
    if (!parseMachine(mach, TT, NS)) { printf("R %s %c BAD\n", mach.c_str(), 'A' + start); return; }
    Runner R; R.M.rules = &R.RS; R.M.chOK = !OPT.noch && coreIntact(); R.M.trace = OPT.trace;
    if (!initTape(R.M, start, tok)) { printf("R %s %c BADTAPE\n", mach.c_str(), 'A' + start); return; }
    if (OPT.kd1) {   // one cascade jump from the start tape (validation)
        bool ok = false; try { ok = R.M.chOK && R.M.c.q == 3 && R.M.tryKd(); } catch (Undec &) {}
        printf("KD1 %s %d %s\n", mach.c_str(), ok ? 1 : 0, tapeDump(R.M).c_str()); fflush(stdout); return;
    }
    R.run();
    printf("%s\n", R.report("R", mach, start).c_str());
    if (OPT.tape) {
        if (R.verdict == "HALT") { R.M.popCell(R.M.c.f); R.M.pushRaw(R.M.c.f, Run{"1", LC(1)}); printf("%s\n", tapeDump(R.M).c_str()); }
        else printf("TAPE notshown\n");
    }
    if (R.M.trace) fprintf(stderr, "END %s\n", R.M.show().c_str());
    fflush(stdout);
}
// free-slot tree: every '---' slot of the input machine is free.  When the run reads a free slot, the halting leaf
// is reported and the 2*2*NS defined values are explored depth first, each continuing from the configuration where
// the slot was read (rules learned so far stay valid: their proofs never read an undefined slot).
static ll NODES = 0, NODECAP = 0; static bool COMPACT = false; static ll CNT[7];   // CYCLE HALT big0 big1 big2 big3+ hold
static int SKIPQ = -1, SKIPS = 0; static Tr SKIPT;   // --skipval Qs:VAL  (subtree already covered elsewhere)
static void enumNode(Runner &R, int start) {
    R.run(); ++NODES;
    string mach = machStr();
    if (COMPACT) {   // counts only; print halters with a big cascade and holdouts
        if (R.verdict == "CYCLE") ++CNT[0]; else if (R.verdict == "HALT") { ++CNT[1]; CNT[2 + min<ll>(R.M.kdBig, 3)]++; } else ++CNT[6];
        if ((R.verdict == "HALT" && R.M.kdBig >= 1) || (R.verdict != "HALT" && R.verdict != "CYCLE")) printf("%s\n", R.report("T", mach, start).c_str());
    }
    else if (R.verdict == "CYCLE") printf("C %s %c %s kd=%lld big=%lld\n", mach.c_str(), 'A' + start, R.detail.c_str(), R.M.kdJumps, R.M.kdBig);
    else printf("%s\n", R.report("T", mach, start).c_str());
    fflush(stdout);
    if (!(R.verdict == "HALT" && FREE[R.M.haltQ][R.M.haltS])) return;
    if (NODECAP && NODES >= NODECAP) { printf("CAP %s %c\n", mach.c_str(), 'A' + start); return; }
    int q = R.M.haltQ, s = R.M.haltS;
    size_t gsz = GS.size();
    FREE[q][s] = false;
    for (int w = 0; w < 2; ++w) for (int d = 0; d < 2; ++d) for (int nx = 0; nx < NS; ++nx) {
        if (q == SKIPQ && s == SKIPS && w == SKIPT.w && d == SKIPT.d && nx == SKIPT.nx) continue;
        TT[q][s] = Tr{w, d, nx, false}; MINI.clear();
        { Runner C(R); enumNode(C, start); }
        GS.resize(gsz);
    }
    TT[q][s] = Tr{1, 1, -1, true}; MINI.clear(); FREE[q][s] = true;
}
static void enumRoot(const string &mach, int start) {
    GS.clear(); MINI.clear(); NODES = 0;
    if (!parseMachine(mach, TT, NS)) { printf("T %s %c BAD\n", mach.c_str(), 'A' + start); return; }
    for (int q = 0; q < NS; ++q) for (int c = 0; c < 2; ++c) FREE[q][c] = TT[q][c].halt;
    Runner R; R.M.rules = &R.RS; R.M.chOK = !OPT.noch && coreIntact(); R.M.trace = false;
    vector<string> tok; initTape(R.M, start, tok);
    enumNode(R, start);
    printf("S %s %c nodes=%lld cycle=%lld halt=%lld big0=%lld big1=%lld big2=%lld big3+=%lld hold=%lld\n", mach.c_str(), 'A' + start, NODES,
           CNT[0], CNT[1], CNT[2], CNT[3], CNT[4], CNT[5], CNT[6]); fflush(stdout);
}
int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: jz run|enum|utab [opts] < input\n"); return 1; }
    string mode = argv[1];
    for (int i = 2; i < argc; ++i) {
        string a = argv[i];
        auto nx = [&]() { return string(argv[++i]); };
        if (a == "--budget") OPT.budget = atoll(nx().c_str());
        else if (a == "--mg") MG = atoll(nx().c_str());
        else if (a == "--exmax") EXMAX = p128(nx().c_str());
        else if (a == "--hlb") OPT.hlb = p128(nx().c_str());
        else if (a == "--maxdelta") MAXDELTA = atoll(nx().c_str());
        else if (a == "--noch") OPT.noch = true;
        else if (a == "--noprove") OPT.noprove = true;
        else if (a == "--trace") OPT.trace = true;
        else if (a == "--tracemax") OPT.tracemax = atoll(nx().c_str());
        else if (a == "--tape") OPT.tape = true;
        else if (a == "--tlimit") OPT.tlimit = atof(nx().c_str());
        else if (a == "--showproof") SHOWPROOF = true;
        else if (a == "--nodecap") NODECAP = atoll(nx().c_str());
        else if (a == "--jmax") JMAX = atoi(nx().c_str());
        else if (a == "--vt") VT = p128(nx().c_str());
        else if (a == "--kd1") OPT.kd1 = true;
        else if (a == "--compact") COMPACT = true;
        else if (a == "--rep") REPBASE = p128(nx().c_str());
        else if (a == "--skipval") { string v = nx(); SKIPQ = v[0] - 'A'; SKIPS = v[1] - '0'; SKIPT = Tr{v[3] - '0', v[4] == 'R' ? 1 : 0, v[5] - 'A', false}; }
        else { fprintf(stderr, "bad option %s\n", a.c_str()); return 1; }
    }
    buildU();
    if (mode == "utab") {
        printf("MG=%lld LAM2=%lld A3=%d JINF=%d\n", MG, LAM2, A3, JINF);
        for (int j = 2; j <= min(JMAX, JINF + 2); ++j) {
            const UTab &T = UT[j]; printf("j=%d h=%d pre=", j, T.h); for (auto v : T.pre) printf("%s,", s128(v).c_str());
            printf(" mu=%d lam=%d X=%s%lld\n", T.mu, T.lam, XC[j].huge ? "h" : "e", XC[j].huge ? XC[j].r : (ll)XC[j].v);
        }
        // queries:  U j x  -> class of U_j(x) (x exact);  I j v x -> class of iter v (U j) x;  H j r -> U_j(huge x == r)
        string line;
        while (getline(cin, line)) {
            istringstream is(line); string k, a1, a2, a3; if (!(is >> k >> a1 >> a2)) continue; is >> a3;
            try {
                VC r;
                if (k == "U") r = UV((int)p128(a1.c_str()), vexact(p128(a2.c_str())));
                else if (k == "I") r = Uiter((int)p128(a1.c_str()), p128(a2.c_str()), vexact(p128(a3.c_str())));
                else if (k == "H") r = UV((int)p128(a1.c_str()), VC{true, 0, (ll)(p128(a2.c_str()) % MG)});
                else continue;
                printf("%s %s %s %s %s %s\n", k.c_str(), a1.c_str(), a2.c_str(), a3.c_str(), r.huge ? "huge" : "exact", r.huge ? to_string(r.r).c_str() : s128(r.v).c_str());
            } catch (Undec &u) { printf("%s %s %s %s UNDEC %s\n", k.c_str(), a1.c_str(), a2.c_str(), a3.c_str(), u.why.c_str()); }
        }
        return 0;
    }
    string line;
    while (getline(cin, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        istringstream is(line); string mach, st; if (!(is >> mach >> st)) continue;
        vector<string> tok; string t; while (is >> t) tok.push_back(t);
        if (mode == "enum") enumRoot(mach, st[0] - 'A');
        else runOne(mach, st[0] - 'A', tok);
    }
    return 0;
}
