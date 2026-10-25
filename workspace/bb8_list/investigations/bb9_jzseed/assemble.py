# assemble jz.cpp from symsim_orig.cpp (bb9_symsim, copied 2026-10-17) + part_ulaw.cpp + part_kd.cpp
S = open('symsim_orig.cpp').read().split('\n')
def L(a, b): return S[a - 1:b]          # 1-based inclusive
ulaw = open('part_ulaw.cpp').read().rstrip('\n').split('\n')
kd = open('part_kd.cpp').read().rstrip('\n').split('\n')
out = []
hdr = L(1, 17)
hdr[0] = '// jz.cpp: symbolic macro simulator for 2-symbol TMs (bb9_jzseed, 2026-10-17), derived from bb9_symsim/symsim.cpp:'
hdr[1] = '// sound HUGE counts, Ligocki-style rule prover (linear rules + inductive CYCLE certificates), and the exact'
hdr[2] = '// Jacobzheng digit cascade (KR1-KR3 iterated, Coq CDPx) when the 12 core slots of the BB(9) champion are intact.'
out += hdr + L(18, 107)
out += ['struct KOp { bool bulk = false; Lin depth; Lin v; vector<int> digs; Lin m; };   // cascade operation (see kValue)',
        'struct KStruct { Lin B0; vector<KOp> ops; };']
out += ["struct PSym { char kind; Lin shadow; Lin J, B; char sub = 'K'; Lin A, K; int kd = -1; };   // kind 'P' variable, 'Z' = cascade value PC->ks[kd]"]
out += L(109, 109)
out += ['struct PCtx { vector<PSym> s; vector<Cons> cons; set<string> seen; vector<KStruct> ks; };']
out += L(111, 240)
out += ulaw
out += L(449, 453)
out += ['static const char *CHAMP = "1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH";',
        'static const int CORE[12] = {0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 13};   // A0 A1 B0 B1 C0 C1 D0 D1 E1 F0 F1 G1']
# parseMachine 456-465
out += L(456, 465)
out += ['static bool coreIntact() {',
        '    Tr B[16][2]; int ns; parseMachine(CHAMP, B, ns);',
        '    if (NS < 7) return false;',
        '    for (int i = 0; i < 12; ++i) {',
        '        int q = CORE[i] / 2, c = CORE[i] % 2; const Tr &a = TT[q][c], &b = B[q][c];',
        '        if (a.halt || a.w != b.w || a.d != b.d || a.nx != b.nx) return false;',
        '    }',
        '    return true;',
        '}']
out += L(475, 678)
out += kd
out += L(874, 950)
out += ['        if (chOK && c.q == 3 && tryKd()) return S_OK;']
out += L(953, 1034)
out += ['    i128 LBZ(int v) {',
        '        auto it = lbz.find(v); if (it != lbz.end()) return it->second;',
        '        const PSym &z = PC->s[v];',
        '        i128 w = kLower(PC->ks[z.kd], [&](const Lin &e) -> i128 { try { return LBe(e); } catch (Undec &) { return (i128)0; } });',
        '        lbz[v] = w; return w;',
        '    }']
out += L(1043, 1064)
out += ['    ll resZ(int v, ll m) {',
        '        if (MG % m != 0) UD("Z residue modulus");',
        '        const PSym &z = PC->s[v];',
        '        struct PP { Pres *P; bool exact(const Lin &e, i128 &x) { if (e.isExact()) { x = e.c; return true; } return false; }',
        '                    ll res(const Lin &e, ll mm) { return P->resAbs(e, mm); } void ge(const Lin &e, i128 c) { P->requireLB(e, c); } } pp{this};',
        '        KStruct K = PC->ks[z.kd];',
        '        VC r = kValue(K, pp);',
        '        if (!r.huge) UD("Z: small");',
        '        return r.r % m;',
        '    }']
out += L(1102, len(S))
src = '\n'.join(out)
# small fixes
src = src.replace('Lin w = lbZ', 'Lin w = lbZ')
open('jz.cpp', 'w').write(src)
print(len(out))
# driver
s = open('jz.cpp').read()
cut = s.index('static void runOne(')
s = s[:cut] + open('part_drv.cpp').read()
s = s.replace('        if (t.halt) { pushRaw(f, Run{"1", LC(1)}); addSteps(LC(1)); return S_HALT; }',
              "        if (t.halt) { haltQ = c.q; haltS = cb; pushRaw(f, Run{string(1, char('0' + cb)), LC(1)}); return S_HALT; }   // tape as before the halting step")
s = s.replace('    ll macro = 0, jumps = 0, ruleApps = 0;', '    ll macro = 0, jumps = 0, ruleApps = 0; int haltQ = -1, haltS = 0;')
open('jz.cpp', 'w').write(s)
s = open('jz.cpp').read()
s = s.replace('            if (o.st == 2) { M.cyc = o.kind + (mult > 1 ? "x" + to_string(mult) : ""); ++PROOFOK; return 2; }',
              '            if (o.st == 2) { if (NOCYCLE) return 0; M.cyc = o.kind + (mult > 1 ? "x" + to_string(mult) : ""); ++PROOFOK; return 2; }')
s = s.replace('static ll PROOFS = 0, PROOFOK = 0;', 'static ll PROOFS = 0, PROOFOK = 0; static bool NOCYCLE = false;   // --nocycle: never claim CYCLE (validation)')
s = s.replace('        else if (a == "--kd1") OPT.kd1 = true;', '        else if (a == "--kd1") OPT.kd1 = true;\n        else if (a == "--nocycle") NOCYCLE = true;')
open('jz.cpp', 'w').write(s)

s = open('jz.cpp').read()
s = s.replace("struct GSym { i128 lb; ll mod, res; string desc; };", "struct GSym { i128 lb; ll mod, res; string desc; Lin lbf; bool hasLbf = false; };   // lbf: X >= lbf (cascade symbols)")
old = """        if (allneg && (ovf || s < 0)) return -1;
    }
    UD("sign:" + linstr(e));"""
new = """        if (allneg && (ovf || s < 0)) return -1;
    }
    {   // positivity through linear lower-bound forms (X >= lbf) of positively weighted symbols
        Lin f = e;
        try {
            for (int round = 0; round < 4; ++round) {
                bool ch = false;
                for (int k = 0; k < f.n && !ch; ++k)
                    if (f.a[k] > 0 && GS[f.id[k]].hasLbf) { f = ladd(f, lscale(lsub(GS[f.id[k]].lbf, LV(f.id[k])), f.a[k], f.D)); ch = true; }
                if (!ch) break;
                bool ap = true; for (int k = 0; k < f.n; ++k) if (f.a[k] < 0) ap = false;
                if (ap) {
                    i128 s = f.c; bool ovf = false;
                    for (int k = 0; k < f.n && !ovf; ++k) { i128 t; if (__builtin_mul_overflow(f.a[k], GS[f.id[k]].lb, &t) || __builtin_add_overflow(s, t, &s)) ovf = true; }
                    if (ovf || s > 0) return 1;
                }
            }
        } catch (Undec &) {}
    }
    UD("sign:" + linstr(e));"""
assert old in s; s = s.replace(old, new)
open('jz.cpp', 'w').write(s)
s = open('jz.cpp').read()
old = "        for (ll t = 0; t < nsteps; ++t) { int st = P.macroStep(); if (st != S_OK) { o.why = \"stopped\"; return o; } }"
new = """        for (ll t = 0; t < nsteps; ++t) {
            int st = P.macroStep(); if (st != S_OK) { o.why = "stopped"; return o; }
            if (UNTILBLANK && isBlankKd(P.c)) break;   // rebuild-cycle proofs: one round = up to the next used-up list
        }"""
assert old in s; s = s.replace(old, new)
s = s.replace("static ll MAXDELTA = 20000;", """static ll MAXDELTA = 20000;
static bool UNTILBLANK = false;
static bool isBlankKd(const Cfg &c) { return c.q == 3 && c.f == 0 && c.st[0].empty() && c.st[1].size() == 1 && c.st[1][0].w == "1" && !c.st[1][0].n.isExact(); }""")
open('jz.cpp', 'w').write(s)
