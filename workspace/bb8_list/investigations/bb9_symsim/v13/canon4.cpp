    // v14 (step 2): canonical re-encoding of the exact small runs on top of a stack (representation only, always sound).
    // The cells of the region (farthest-first) are encoded by maximal periodic stretches (period 2..12, >= 3 copies),
    // each started at its lexicographically smallest rotation, so a block has the same run whatever phase the machine
    // last left it in.  Whole copies next to the deeper run are merged into it.  Touches the runs it rewrites.
    ll canonCount = 0;
    static string minRot(const string &u) { string b = u; for (size_t i = 1; i < u.size(); ++i) { string r = u.substr(i) + u.substr(0, i); if (r < b) b = r; } return b; }
    void canonTop(int s) {
        auto &V = c.st[s]; int n = (int)V.size(), k = 0; size_t cells = 0;
        while (k < n) {
            const Run &r = V[n - 1 - k];
            if (!r.n.isExact() || r.n.c * (i128)r.w.size() > 256) break;
            cells += (size_t)(r.n.c * (i128)r.w.size()); if (cells > 512) break;
            ++k;
        }
        if (k < 2) return;
        string S; for (int i = k - 1; i >= 0; --i) { const Run &r = V[n - 1 - i]; string w = rev(r.w); for (i128 t = 0; t < r.n.c; ++t) S += w; }   // farthest-first
        // the run below the region absorbs whole copies of its word from the far end of the region
        i128 deepM = 0; size_t start = 0;
        if (n - k - 1 >= 0) {
            const Run &d = V[n - k - 1]; string u = rev(d.w); size_t L = u.size();
            while (S.size() >= start + L && S.compare(start, L, u) == 0) { start += L; ++deepM; }
        }
        vector<pair<string, i128>> res;   // farthest-first words
        auto add = [&](const string &u, i128 cnt) { if (cnt <= 0 || u.empty()) return; if (!res.empty() && res.back().first == u) res.back().second += cnt; else res.push_back({u, cnt}); };
        std::function<void(size_t, size_t)> enc = [&](size_t a, size_t b) {
            if (a >= b) return;
            size_t ba = a, bcov = 0, bi = a; int bp = 0;
            for (int p = 2; p <= 12; ++p) {
                size_t i = a;
                while (i + (size_t)p < b) {
                    if (S[i] != S[i + p]) { ++i; continue; }
                    size_t j = i; while (j + (size_t)p < b && S[j] == S[j + p]) ++j;   // S[i .. j+p) has period p
                    size_t end = j + p;
                    if ((end - i) / p >= 3 && primRoot(S.substr(i, p)) == p) {
                        string mr = minRot(S.substr(i, p)); size_t i2 = i; while (S.compare(i2, p, mr) != 0) ++i2;   // canonical phase
                        size_t cov = ((end - i2) / p) * p;
                        if (cov / p >= 3 && cov > bcov) { bcov = cov; ba = i2; bp = p; bi = i; }
                    }
                    i = j + 1;
                }
            }
            (void)bi;
            if (bp == 0) { for (size_t i = a; i < b; ++i) add(string(1, S[i]), 1); return; }
            enc(a, ba); add(S.substr(ba, bp), (i128)(bcov / bp)); enc(ba + bcov, b);
        };
        enc(start, S.size());
        // only rewrite when the encoding differs from the current one
        bool same = deepM == 0 && (int)res.size() == k;
        for (int i = 0; same && i < k; ++i) { const Run &r = V[n - 1 - (k - 1 - i)]; if (rev(r.w) != res[i].first || !(r.n.c == res[i].second)) same = false; }
        if (same) return;
        for (int i = 0; i < k; ++i) touch(s, V[n - 1 - i]);
        V.resize(n - k);
        if (deepM) { touch(s, V.back()); V.back().n = laddc(V.back().n, deepM); normCount(V.back().n); }
        for (auto &pr : res) pushRaw(s, Run{rev(pr.first), LC(pr.second)});   // farthest first; pushRaw merges into an equal deeper run
        ++canonCount;
    }
