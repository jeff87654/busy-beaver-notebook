    // v14 (step 2): canonical re-encoding near the top of a stack (representation only, always sound).
    // Region: top runs that are exact with <= 256 cells, or symbolic (proof variables).  "Anchors" (>= CANONANCHOR copies
    // or symbolic) are never taken apart: they are rotated to the minimal rotation of their word (the shifted partial copy
    // becomes loose cells), absorb whole copies of their word from adjacent loose cells, and stop at symbolic/big runs.
    // Loose cells (from runs with fewer copies) are encoded by maximal periodic stretches (period 2..12, >= 3 copies)
    // started at their minimal rotation.  The same rules apply to exact anchors in the main run and to the proof-variable
    // anchors of a proof, so a proof sees the representation the main run would see.  Rewrites only when it changes.
    ll canonCount = 0;
    static string minRot(const string &u) { string b = u; for (size_t i = 1; i < u.size(); ++i) { string r = u.substr(i) + u.substr(0, i); if (r < b) b = r; } return b; }
    void canonTop(int s) {
        auto &V = c.st[s]; int n = (int)V.size(), k = 0; size_t cells = 0;
        while (k < n && k < 48) {
            const Run &r = V[n - 1 - k];
            if (r.tag == 1000000) break;   // KT_SENT sentinel
            bool anchor = !r.n.isExact() || r.n.c >= CANONANCHOR;
            if (r.n.isExact() && r.n.c * (i128)r.w.size() > 256) break;
            if (!anchor) { cells += (size_t)(r.n.c * (i128)r.w.size()); if (cells > 512) break; }
            ++k;
        }
        if (k < 2) return;
        struct It { bool anchor; string w; Lin cnt; string cells; };   // farthest-first words
        vector<It> it;
        auto addLoose = [&](const string &cs) { if (cs.empty()) return; if (!it.empty() && !it.back().anchor) it.back().cells += cs; else it.push_back(It{false, "", LC(0), cs}); };
        for (int i = k - 1; i >= 0; --i) {
            const Run &r = V[n - 1 - i]; string wf = rev(r.w);
            bool anchor = !r.n.isExact() || r.n.c >= CANONANCHOR;
            if (!anchor) { string cs; for (i128 t = 0; t < r.n.c; ++t) cs += wf; addLoose(cs); continue; }
            // rotate to the minimal rotation: wf^n = wf[0:sh] + (rot)^(n-1) + wf[sh:], rot = wf[sh:] + wf[0:sh]
            string mr = minRot(wf); size_t sh = 0; while ((wf.substr(sh) + wf.substr(0, sh)) != mr) ++sh;
            if (sh == 0) { it.push_back(It{true, wf, r.n, ""}); continue; }
            if (r.n.isExact() ? r.n.c < 1 : sgn(laddc(r.n, -1)) < 0) { it.push_back(It{true, wf, r.n, ""}); continue; }
            addLoose(wf.substr(0, sh)); it.push_back(It{true, mr, laddc(r.n, -1), ""}); addLoose(wf.substr(sh));
        }
        // anchors absorb whole copies of their word from adjacent loose cells
        for (size_t a = 0; a < it.size(); ++a) if (it[a].anchor) {
            const string u = it[a].w; size_t L = u.size();
            if (a + 1 < it.size() && !it[a + 1].anchor) { string &cs = it[a + 1].cells; size_t m = 0; while (cs.size() >= (m + 1) * L && cs.compare(m * L, L, u) == 0) ++m; if (m) { it[a].cnt = laddc(it[a].cnt, (i128)m); cs.erase(0, m * L); } }
            if (a > 0 && !it[a - 1].anchor) { string &cs = it[a - 1].cells; size_t m = 0; while (cs.size() >= (m + 1) * L && cs.compare(cs.size() - (m + 1) * L, L, u) == 0) ++m; if (m) { it[a].cnt = laddc(it[a].cnt, (i128)m); cs.erase(cs.size() - m * L); } }
        }
        i128 deepM = 0;
        if (n - k - 1 >= 0 && !it.empty() && !it[0].anchor && V[n - k - 1].tag != 1000000) {
            const Run &d = V[n - k - 1]; string u = rev(d.w); string &cs = it[0].cells; size_t m = 0, L = u.size();
            while (cs.size() >= (m + 1) * L && cs.compare(m * L, L, u) == 0) ++m;
            if (m) { deepM = (i128)m; cs.erase(0, m * L); }
        }
        vector<pair<string, Lin>> res;
        auto add = [&](const string &u, const Lin &cnt) { if (u.empty() || (cnt.isExact() && cnt.c <= 0)) return; if (!res.empty() && res.back().first == u) res.back().second = ladd(res.back().second, cnt); else res.push_back({u, cnt}); };
        std::function<void(const string &, size_t, size_t)> enc = [&](const string &S, size_t a, size_t b) {
            if (a >= b) return;
            size_t ba = a, bcov = 0; int bp = 0;
            for (int p = 2; p <= 12; ++p) {
                size_t i = a;
                while (i + (size_t)p < b) {
                    if (S[i] != S[i + p]) { ++i; continue; }
                    size_t j = i; while (j + (size_t)p < b && S[j] == S[j + p]) ++j;
                    size_t end = j + p;
                    if ((end - i) / p >= 3 && primRoot(S.substr(i, p)) == p) {
                        string mr = minRot(S.substr(i, p)); size_t i2 = i; while (S.compare(i2, p, mr) != 0) ++i2;
                        size_t cov = ((end - i2) / p) * p;
                        if (cov / p >= 3 && cov > bcov) { bcov = cov; ba = i2; bp = p; }
                    }
                    i = j + 1;
                }
            }
            if (bp == 0) { size_t i = a; while (i < b) { size_t j = i; while (j < b && S[j] == S[i]) ++j; add(string(1, S[i]), LC((i128)(j - i))); i = j; } return; }
            enc(S, a, ba); add(S.substr(ba, bp), LC((i128)(bcov / bp))); enc(S, ba + bcov, b);
        };
        for (auto &x : it) { if (x.anchor) add(x.w, x.cnt); else enc(x.cells, 0, x.cells.size()); }
        bool same = deepM == 0 && (int)res.size() == k;
        for (int i = 0; same && i < k; ++i) { const Run &r = V[n - 1 - (k - 1 - i)]; if (rev(r.w) != res[i].first || !lequal(r.n, res[i].second)) same = false; }
        if (same) return;
        for (int i = 0; i < k; ++i) touch(s, V[n - 1 - i]);
        V.resize(n - k);
        if (deepM) { touch(s, V.back()); V.back().n = laddc(V.back().n, deepM); normCount(V.back().n); }
        for (auto &pr : res) pushRaw(s, Run{rev(pr.first), pr.second});
        ++canonCount;
    }
