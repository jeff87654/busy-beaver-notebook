    // ---- Jacobzheng's digit cascade (KR1 iterated = R1iter, then KR2/KR3 iterated = CDPx, digit by digit), used
    // when the 12 core slots A0 A1 B0 B1 C0 C1 D0 D1 E1 F0 F1 G1 (champion labels) are intact.
    //   Kd ds a b = 0^inf <D 1^(b+1) 0 1^a (0 1^d)*   -->*   Kd (0^k ++ rest) 0 B
    // The digit at depth j (j digits above it, all 0 by then) is cleared by iter v (U j) when B >= 2j.  That
    // condition is tracked as a lower-bound form SL <= B - 2*depth (exact while B is exact), using Ugrow.
    // The tail of the list after the first digit not cleared is left in place (untouched runs keep their tags).
    struct KPos { int pi = -1; Lin copy; int ch = 0; };   // cell where a digit starts (its leading 0): piece, copy, char
    struct KItem { bool pat = false; Lin v; vector<int> digs, offs; Lin n; KPos pos; };
    static string encDigs(const vector<int> &d) { string s; for (int x : d) { s += '0'; s += string((size_t)x, '1'); } return s; }
    ll kdJumps = 0, kdBig = 0;
    bool tryKd() {
        auto &L = c.st[0], &R = c.st[1];
        for (int i = (int)L.size() - 1; i >= 0; --i) if (!allZero(L[i].w)) return false;
        struct Piece { string w; Lin n; int orig; };   // orig: index in R, or -1 (derived from the head run)
        vector<Piece> rp;
        if (c.f == 0) { for (int i = (int)R.size() - 1; i >= 0; --i) rp.push_back({R[i].w, R[i].n, i}); }
        else {
            if (R.empty() || R.back().w[0] != '0') return false;
            const Run &t = R.back();
            if (t.w.size() > 1) rp.push_back({t.w.substr(1), LC(1), -1});
            if (!isOne(t.n)) rp.push_back({t.w, laddc(t.n, -1), -1});
            for (int i = (int)R.size() - 2; i >= 0; --i) rp.push_back({R[i].w, R[i].n, i});
        }
        if (rp.empty() || rp[0].w[0] != '1') return false;
        // parse 1^(b+1) 0 1^a (0 1^d)*
        int phase = 0; Lin bones = LC(0), aL = LC(0), cur = LC(0); KPos curPos; vector<KItem> items;
        auto addOnes = [&](const Lin &k) { if (phase == 0) bones = ladd(bones, k); else if (phase == 1) aL = ladd(aL, k); else cur = ladd(cur, k); };
        auto pushDigit = [&]() { KItem it; it.v = cur; it.pos = curPos; items.push_back(it); };
        auto zeroCell = [&](int pi, const Lin &cp, int ch) {
            if (phase == 2) pushDigit();
            if (phase < 2) ++phase;
            if (phase == 2) { cur = LC(0); curPos = KPos{pi, cp, ch}; }
        };
        try {
            for (int pi = 0; pi < (int)rp.size(); ++pi) {
                const string &w = rp[pi].w; Lin n = rp[pi].n;
                if (n.isExact() && n.c * (i128)w.size() <= 512) {
                    for (i128 t = 0; t < n.c; ++t) for (size_t i = 0; i < w.size(); ++i) { if (w[i] == '1') addOnes(LC(1)); else zeroCell(pi, LC(t), (int)i); }
                    continue;
                }
                if (allOne(w)) { addOnes(lscale(n, (i128)w.size())); continue; }
                if (allZero(w)) {
                    if (w.size() != 1) return false;
                    i128 t = 0; bool done = false;
                    while (phase < 2) { zeroCell(pi, LC(t), 0); ++t; if (sgn(laddc(n, -t)) == 0) { done = true; break; } }
                    if (done) continue;
                    // zeros t .. n-1: zero #t closes cur, zeros t .. n-2 start zero digits, zero n-1 starts the open digit
                    pushDigit();
                    Lin z1 = laddc(n, -t - 1);
                    if (!(z1.isExact() && z1.c == 0)) { KItem it; it.pat = true; it.digs = {0}; it.offs = {0}; it.n = z1; it.pos = KPos{pi, LC(t), 0}; items.push_back(it); }
                    cur = LC(0); curPos = KPos{pi, laddc(n, -1), 0};
                    continue;
                }
                i128 t1 = 0; bool doneRun = false;
                while (phase < 2) {   // single copies until the digit list starts
                    for (size_t i = 0; i < w.size(); ++i) { if (w[i] == '1') addOnes(LC(1)); else zeroCell(pi, LC(t1), (int)i); }
                    ++t1;
                    if (sgn(laddc(n, -t1)) == 0) { doneRun = true; break; }
                }
                if (doneRun) continue;
                // copies t1 .. n-1:  w^n' = 1^u (0 v 1^u)^(n'-1) 0 v
                size_t u = 0; while (w[u] == '1') ++u;
                string v = w.substr(u + 1);
                string beta = "0" + v + string(u, '1');
                vector<int> bd, offs; for (size_t i = 0; i < beta.size(); ++i) { if (beta[i] == '0') { bd.push_back(0); offs.push_back((int)i); } else ++bd.back(); }
                cur = laddc(cur, (i128)u); pushDigit();
                Lin nb = laddc(n, -t1 - 1);
                if (!(nb.isExact() && nb.c == 0)) { KItem it; it.pat = true; it.digs = bd; it.offs = offs; it.n = nb; it.pos = KPos{pi, LC(t1), (int)u}; items.push_back(it); }
                Lin lastCopy = laddc(n, -1);
                for (size_t k = 0; k + 1 < bd.size(); ++k) { cur = LC(bd[k]); curPos = KPos{pi, lastCopy, (int)u + offs[k]}; pushDigit(); }
                cur = LC(bd.back() - (int)u); curPos = KPos{pi, lastCopy, (int)u + offs.back()};
            }
        } catch (Undec &) { return false; }
        if (phase == 2) pushDigit();
        if (bones.isExact() && bones.c < 1) return false;
        auto zeroItem = [&](const KItem &it) {
            if (!it.pat) return it.v.isExact() && it.v.c == 0;
            for (int d : it.digs) if (d) return false;
            return true;
        };
        while (!items.empty() && zeroItem(items.back())) items.pop_back();
        // structure pass
        Lin B0 = ladd(laddc(bones, -1), lscale(aL, 3));
        KStruct K; K.B0 = B0;
        deque<KItem> Q(items.begin(), items.end());
        Lin depth = LC(0), SL = B0; bool exTrack = B0.isExact(); i128 Bex = exTrack ? B0.c : 0; bool hugeB = false;
        auto sgnOK = [&](const Lin &e) -> int { try { return sgn(e); } catch (Undec &) { return -2; } };
        if (!B0.isExact() && sgnOK(laddc(B0, -HUGEMIN)) >= 0) hugeB = true;   // symbolic counter already huge
        auto peelBlock = [&](const KItem &it) {   // block at it.pos (copy c0) -> digits, then the pattern from copy c0+1
            KItem rest = it; rest.n = laddc(it.n, -1); rest.pos.copy = laddc(it.pos.copy, 1);
            Q.push_front(rest);
            for (int p = (int)it.digs.size() - 1; p >= 0; --p) { KItem d; d.v = LC(it.digs[p]); d.pos = KPos{it.pos.pi, it.pos.copy, it.pos.ch + it.offs[p]}; Q.push_front(d); }
        };
        int peels = 0;
        while (!Q.empty()) {
            KItem it = Q.front();
            if (it.pat) {
                int k = (int)it.digs.size(); ll D = 0; for (int d : it.digs) D += d;
                if (it.n.isExact() && it.n.c <= 0) { Q.pop_front(); continue; }
                if (D == 0) { Q.pop_front(); depth = ladd(depth, lscale(it.n, k)); SL = lsub(SL, lscale(it.n, 2 * k)); continue; }
                if (it.n.isExact() && it.n.c <= 64) { Q.pop_front(); peelBlock(it); continue; }
                bool ok = hugeB && sgnOK(laddc(depth, -JINF)) >= 0;
                if (ok) {
                    i128 cst = -2 * k; for (int p = 0; p < k; ++p) if (it.digs[p]) cst += (i128)it.digs[p] * (2 * p + 5);
                    ok = sgnOK(laddc(lscale(depth, 2 * D), cst)) >= 0;
                }
                if (ok) {
                    Lin s = SL;
                    for (int p = 0; p < k && ok; ++p) {
                        int d = it.digs[p];
                        if (d) { if (sgnOK(s) < 0) { ok = false; break; } s = ladd(s, laddc(lscale(laddc(depth, p), 2 * d), 5 * d)); }
                        s = laddc(s, -2);
                    }
                }
                if (ok) {
                    KOp op; op.bulk = true; op.depth = depth; op.digs = it.digs; op.m = it.n; K.ops.push_back(op);
                    depth = ladd(depth, lscale(it.n, k)); exTrack = false; Q.pop_front();
                    continue;
                }
                if (peels >= 64 || sgnOK(laddc(it.n, -1)) < 0) break;
                ++peels; Q.pop_front(); peelBlock(it);
                continue;
            }
            int sv = it.v.isExact() ? (it.v.c > 0 ? 1 : 0) : sgnOK(it.v);
            if (sv < 0) break;
            if (sv == 0) { Q.pop_front(); depth = laddc(depth, 1); SL = laddc(SL, -2); continue; }
            if (sgnOK(SL) < 0) break;
            bool dex = depth.isExact();
            if (!dex && sgnOK(laddc(depth, -JINF)) < 0) break;
            KOp op; op.depth = depth; op.v = it.v; K.ops.push_back(op); Q.pop_front();
            i128 dlb = it.v.isExact() ? it.v.c : 1;
            if (exTrack && dex && it.v.isExact()) { i128 r = Uiterex(depth.c, dlb, Bex, VT); if (r >= 0) Bex = r; else exTrack = false; }
            else exTrack = false;
            if (!dex || depth.c >= 2) hugeB = true;
            if (exTrack) { depth = laddc(depth, 1); SL = lsub(LC(Bex), lscale(depth, 2)); }
            else { SL = ladd(SL, laddc(lscale(depth, 2 * dlb), 5 * dlb)); depth = laddc(depth, 1); SL = laddc(SL, -2); }
        }
        if (K.ops.empty() && aL.isExact() && aL.c == 0) return false;
        while (!Q.empty() && zeroItem(Q.back())) Q.pop_back();
        // value
        Lin Bres;
        try {
            if (K.ops.empty()) Bres = B0;
            else {
                bool pf = hasProof(B0);
                for (auto &op : K.ops) pf = pf || hasProof(op.depth) || hasProof(op.v) || hasProof(op.m);
                KStruct Ks = K;
                if (pf) { Ks.B0 = shadowOf(K.B0); for (auto &op : Ks.ops) { op.depth = shadowOf(op.depth); op.v = shadowOf(op.v); op.m = shadowOf(op.m); } }
                ProvMain pm; VC r = kValue(Ks, pm);
                Lin sh;
                if (r.huge && REPBASE > 0 && !pf) { sh = LC(REPBASE + pmod((i128)r.r - REPBASE, MG)); ++kdBig; }   // --rep: representative (screening only)
                else if (r.huge) {
                    i128 lb = kLower(Ks, [](const Lin &e) -> i128 { try { return lbG(e); } catch (Undec &) { return 0; } });
                    lb = max(lb, HUGEMIN);
                    string desc = "K(B0=" + linstr(Ks.B0) + ";n=" + to_string(Ks.ops.size()) + ";dep=" + linstr(shadowOf(depth)) + ")";
                    int gid = newG(lb, r.r, desc); sh = LV(gid); ++kdBig;
                    // linear lower bound: the last application at depth J gives >= X_(J-1) >= 2^(J+1) J >= 128 J for J >= 6
                    // (Coq Xbound; U_J(x) = iter _ U_(J-1) X_(J-1) >= X_(J-1); iterates only increase)
                    try { const Lin &J = Ks.ops.back().depth; if (sgnG(laddc(J, -6)) >= 0) { GS[gid].lbf = lscale(J, 128); GS[gid].hasLbf = true; } } catch (Undec &) {}
                } else sh = LC(r.v);
                if (!pf) Bres = sh;
                else { PC->ks.push_back(K); PSym z{'Z', sh, Lin(), Lin()}; z.sub = 'K'; z.kd = (int)PC->ks.size() - 1; PC->s.push_back(z); Bres = LV(PBASE + (int)PC->s.size() - 1); }
            }
        } catch (Undec &) { if (proof) throw; return false; }
        // rebuild the right side: new prefix 1^(B+1) 0 0^depth, then the list from the first digit not cleared
        for (auto &r : L) touch(0, r);
        touchBottom(0);
        vector<Run> keepFar;   // runs pushed (far to near) between the kept original runs and the new prefix
        int cutIdx = -1;       // R[0..cutIdx] stay as they are
        if (Q.empty()) { for (auto &r : R) touch(1, r); touchBottom(1); cutIdx = -1; }
        else {
            const KPos &p = Q.front().pos;
            int pi = p.pi;
            for (int k = pi + 1; k < (int)rp.size(); ++k) if (rp[k].orig >= 0) { cutIdx = rp[k].orig; break; }
            for (int k = (int)rp.size() - 1; k > pi; --k) if (rp[k].orig < 0) keepFar.push_back(Run{rp[k].w, rp[k].n});
            for (int i = (int)R.size() - 1; i > cutIdx; --i) touch(1, R[i]);
            if (cutIdx >= 0) touch(1, R[cutIdx]);   // the run just beyond the read part (its first cell bounds the digit)
            const string &w = rp[pi].w;
            Lin restCopies = lsub(laddc(rp[pi].n, -1), p.copy);
            if (!(restCopies.isExact() && restCopies.c == 0)) keepFar.push_back(Run{w, restCopies});
            keepFar.push_back(Run{w.substr((size_t)p.ch), LC(1)});
        }
        L.clear(); R.resize((size_t)(cutIdx + 1));
        for (auto &r : keepFar) pushRaw(1, r);
        if (!Q.empty()) {
            if (!(depth.isExact() && depth.c == 0)) pushRaw(1, Run{"0", depth});
            pushRaw(1, Run{"0", LC(1)});
        }
        pushRaw(1, Run{"1", laddc(Bres, 1)});
        c.q = 3; c.f = 0; stepsKnown = false; ++kdJumps;
        if (!proof) {
            jlog.push_back("K" + to_string(K.ops.size()) + (Q.empty() ? "" : "p") + ":" + linstr(B0) + ">" + linstr(Bres) + "@" + linstr(depth));
            if (jlog.size() > 12) jlog.erase(jlog.begin());
        }
        return true;
    }
