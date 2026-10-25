import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(a, b, c=1):
    global s
    assert s.count(a) == c, (a[:70], s.count(a))
    s = s.replace(a, b)
rep('''    int macroStep() {
        ++macro;''', '''    // v13 (step 2): canonical re-encoding of the small exact runs on top of a stack (representation only, always sound):
    // greedy best-coverage periods 1..12; the result is merged into the deeper run when the words agree.  Touches the runs.
    ll canonCount = 0;
    void canonTop(int s) {
        auto &V = c.st[s]; int n = (int)V.size(), k = 0; size_t cells = 0;
        while (k < n) {
            const Run &r = V[n - 1 - k];
            if (!r.n.isExact() || r.n.c * (i128)r.w.size() > 256) break;
            cells += (size_t)(r.n.c * (i128)r.w.size()); if (cells > 512) break;
            ++k;
        }
        if (k < 4) return;
        string S; for (int i = 0; i < k; ++i) { const Run &r = V[n - 1 - i]; for (i128 t = 0; t < r.n.c; ++t) S += r.w; }   // nearest-first
        vector<Run> res; size_t pos = 0, N = S.size();
        while (pos < N) {
            int bp = 1; size_t bc = 0;
            for (int p = 1; p <= 12 && pos + (size_t)p <= N; ++p) {
                size_t r = 1; while (pos + (r + 1) * p <= N && S.compare(pos + r * p, p, S, pos, p) == 0) ++r;
                if ((p == 1 || r >= 2) && r * p > bc) { bc = r * p; bp = p; }
            }
            string u = S.substr(pos, bp);
            if (primRoot(u) != bp) { u = S.substr(pos, 1); size_t r = 1; while (pos + r < N && S[pos + r] == S[pos]) ++r; bc = r; bp = 1; }
            if (!res.empty() && res.back().w == u) res.back().n = laddc(res.back().n, (i128)(bc / bp));
            else res.push_back(Run{u, LC((i128)(bc / bp))});
            pos += bc;
        }
        if ((int)res.size() >= k) return;
        for (int i = 0; i < k; ++i) touch(s, V[n - 1 - i]);
        V.resize(n - k);
        if (!V.empty()) touch(s, V.back());
        for (int i = (int)res.size() - 1; i >= 0; --i) pushRaw(s, res[i]);
        ++canonCount;
    }
    int macroStep() {
        ++macro;
        if (CANON) { canonTop(0); canonTop(1); }''')
rep('static bool NOAFF = false, KTFORCE = false, AFFC = true, PAFF = true, ITERON = true, PITER = true, RETRY = true, GSTRUNC = true;',
    'static bool NOAFF = false, KTFORCE = false, AFFC = true, PAFF = true, ITERON = true, PITER = true, RETRY = true, GSTRUNC = true, CANON = false;')
rep('''        else if (a == "--itercheck") ITERCHECK = true;''', '''        else if (a == "--itercheck") ITERCHECK = true;
        else if (a == "--canon") CANON = true;''')
open(fn, 'w').write(s)
