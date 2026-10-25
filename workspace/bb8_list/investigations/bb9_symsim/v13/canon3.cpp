    void canonTop(int s) {
        auto &V = c.st[s]; int n = (int)V.size(), k = 0; size_t cells = 0;
        while (k < n) {
            const Run &r = V[n - 1 - k];
            if (!r.n.isExact() || r.n.c * (i128)r.w.size() > 256) break;
            cells += (size_t)(r.n.c * (i128)r.w.size()); if (cells > 512) break;
            ++k;
        }
        int smallc = 0; for (int i = 0; i < k; ++i) if (V[n - 1 - i].n.c <= 2) ++smallc;
        if (smallc < 4) return;
        // items in farthest-first order: anchors (runs with >= 3 copies, kept) and loose cells (runs with <= 2 copies)
        struct It { bool anchor; string w; i128 cnt; string cells; };
        vector<It> it;
        for (int i = k - 1; i >= 0; --i) {
            const Run &r = V[n - 1 - i]; string wf = rev(r.w);
            if (r.n.c >= 3) it.push_back(It{true, wf, r.n.c, ""});
            else { string cs; for (i128 t = 0; t < r.n.c; ++t) cs += wf; if (!it.empty() && !it.back().anchor) it.back().cells += cs; else it.push_back(It{false, "", 0, cs}); }
        }
        // anchors absorb whole copies of their word from the adjacent loose cells
        for (size_t a = 0; a < it.size(); ++a) if (it[a].anchor) {
            const string u = it[a].w; size_t L = u.size();
            if (a + 1 < it.size() && !it[a + 1].anchor) { string &cs = it[a + 1].cells; size_t m = 0; while (cs.size() >= (m + 1) * L && cs.compare(m * L, L, u) == 0) ++m; if (m) { it[a].cnt += (i128)m; cs.erase(0, m * L); } }
            if (a > 0 && !it[a - 1].anchor) { string &cs = it[a - 1].cells; size_t m = 0; while (cs.size() >= (m + 1) * L && cs.compare(cs.size() - (m + 1) * L, L, u) == 0) ++m; if (m) { it[a].cnt += (i128)m; cs.erase(cs.size() - m * L); } }
        }
        // the run below the region (any count) absorbs whole copies from the first loose cells
        i128 deepM = 0;
        if (n - k - 1 >= 0 && !it.empty() && !it[0].anchor) {
            const Run &d = V[n - k - 1]; string u = rev(d.w); string &cs = it[0].cells; size_t m = 0, L = u.size();
            while (cs.size() >= (m + 1) * L && cs.compare(m * L, L, u) == 0) ++m;
            if (m) { deepM = (i128)m; cs.erase(0, m * L); }
        }
        // loose cells: maximal periodic stretches (>= 3 copies) become runs, the rest single cells
        vector<pair<string, i128>> res;   // farthest-first words
        auto add = [&](const string &u, i128 cnt) { if (cnt <= 0 || u.empty()) return; if (!res.empty() && res.back().first == u) res.back().second += cnt; else res.push_back({u, cnt}); };
        std::function<void(const string &, size_t, size_t)> enc = [&](const string &S, size_t a, size_t b) {
            if (a >= b) return;
            size_t ba = a, bcov = 0; int bp = 0;
            for (int p = 2; p <= 12; ++p) {
                size_t i = a;
                while (i + (size_t)p < b) {
                    if (S[i] != S[i + p]) { ++i; continue; }
                    size_t j = i; while (j + (size_t)p < b && S[j] == S[j + p]) ++j;
                    size_t len = j + p - i, cov = (len / p) * p;
                    if (len / p >= 3 && cov > bcov && primRoot(S.substr(i, p)) == p) { bcov = cov; ba = i; bp = p; }
                    i = j + 1;
                }
            }
            if (bp == 0) { for (size_t i = a; i < b; ++i) add(string(1, S[i]), 1); return; }
            enc(S, a, ba); add(S.substr(ba, bp), (i128)(bcov / bp)); enc(S, ba + bcov, b);
        };
        for (auto &x : it) { if (x.anchor) add(x.w, x.cnt); else enc(x.cells, 0, x.cells.size()); }
        if ((int)res.size() >= k && deepM == 0) return;
        for (int i = 0; i < k; ++i) touch(s, V[n - 1 - i]);
        V.resize(n - k);
        if (deepM) { touch(s, V.back()); V.back().n = laddc(V.back().n, deepM); normCount(V.back().n); }
        for (auto &pr : res) pushRaw(s, Run{rev(pr.first), LC(pr.second)});   // farthest first; pushRaw merges into an equal deeper run
        ++canonCount;
    }
