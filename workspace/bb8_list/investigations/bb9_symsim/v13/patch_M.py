import sys
fn = sys.argv[1]; s = open(fn).read()
i0 = s.index('        // encoded from the FAR end (anchored at the deeper run, so the phase does not drift as the head moves)')
i1 = s.index('        if ((int)res.size() >= k) return;', i0)
s = s[:i0] + r'''        // maximal-segment encoding: the longest periodic stretch (period 1..12, at least 3 copies for period > 1) becomes
        // one run starting where the stretch starts; the two remainders are encoded the same way (independent of where
        // the head currently is, so the representation of a block is stable)
        string S; for (int i = k - 1; i >= 0; --i) { const Run &r = V[n - 1 - i]; string w = rev(r.w); for (i128 t = 0; t < r.n.c; ++t) S += w; }   // farthest-first
        vector<Run> res;
        std::function<void(size_t, size_t)> enc = [&](size_t a, size_t b) {
            if (a >= b) return;
            size_t ba = a, bcov = 0; int bp = 0;
            for (int p = 1; p <= 12; ++p) {
                size_t i = a;
                while (i + (size_t)p < b) {
                    if (S[i] != S[i + p]) { ++i; continue; }
                    size_t j = i; while (j + (size_t)p < b && S[j] == S[j + p]) ++j;   // S[i..j+p) has period p
                    size_t len = j + p - i, cov = (len / p) * p;
                    if ((len / p) >= (p == 1 ? 1u : 3u) && cov > bcov) {
                        string u = S.substr(i, p);
                        if (primRoot(u) == p) { bcov = cov; ba = i; bp = p; }
                    }
                    i = j + 1;
                }
            }
            if (bp == 0) {   // no stretch: single cells, merged by symbol
                for (size_t i = a; i < b; ++i) { string u(1, S[i]); if (!res.empty() && res.back().w == u) res.back().n = laddc(res.back().n, 1); else res.push_back(Run{u, LC(1)}); }
                return;
            }
            enc(a, ba);
            string u = S.substr(ba, bp);
            if (!res.empty() && res.back().w == u) res.back().n = laddc(res.back().n, (i128)(bcov / bp)); else res.push_back(Run{u, LC((i128)(bcov / bp))});
            enc(ba + bcov, b);
        };
        enc(0, S.size());
''' + s[i1:]
open(fn, 'w').write(s)
