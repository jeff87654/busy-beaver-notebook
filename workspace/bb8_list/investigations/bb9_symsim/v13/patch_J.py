import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(a, b, c=1):
    global s
    assert s.count(a) == c, (a[:70], s.count(a))
    s = s.replace(a, b)
rep('''        // literal stepping
        Sim P; P.c = c0; P.prover = false; P.ktOK = 0; P.chOK = false; RuleSet RS0; P.rules = &RS0; P.track = true;
        bool hit = false;
        try {
            for (ll t = 0; t < 3000000; ++t) {
                if (P.macroStep() != S_OK) break;
                if (P.maxTag[0] >= KT_SENT || P.maxTag[1] >= KT_SENT) break;
                if (P.c.q == A.c.q && P.c.f == A.c.f) { bool okP; string cur = cfgCells(P.c, okP); if (!okP) break; if (cur == target) { hit = true; break; } }
            }
        } catch (...) {}''', '''        // literal stepping on explicit cells (the sentinel is 0110 x 1000 and must come back unchanged)
        bool hit = false;
        {
            bool o1; string a0 = cfgCells(c0, o1);
            auto expand = [](const string &x, int &q, string &cells, ll &head) {
                q = x[0] - 'A'; bool f = x[1] == '>';
                size_t p1 = x.find('|'), p2 = x.find('|', p1 + 1);
                string L = x.substr(p1 + 1, p2 - p1 - 1), R2 = x.substr(p2 + 1), S4; for (int t = 0; t < 1000; ++t) S4 += "0110";
                auto sub = [&](string z) { size_t k; while ((k = z.find("[S]")) != string::npos) z.replace(k, 3, S4); return z; };
                L = sub(L); R2 = sub(R2); cells = L + R2; head = f ? (ll)L.size() : (ll)L.size() - 1;
            };
            int q0, qt; string c0s, cts; ll h0, ht; expand(a0, q0, c0s, h0); expand(target, qt, cts, ht);
            const ll N = 1 << 20, off = N / 2; vector<unsigned char> tp(N, 0), tg(N, 0);
            for (size_t i = 0; i < c0s.size(); ++i) tp[off + i] = c0s[i] - '0';
            for (size_t i = 0; i < cts.size(); ++i) tg[off + i] = cts[i] - '0';
            ll pos = off + h0, tpos = off + ht; int q = q0;
            for (ll t = 0; t < 20000000; ++t) {
                if (q == qt && pos == tpos && tp == tg) { hit = true; break; }
                const Tr &tr = TT[q][tp[pos]]; if (tr.halt) break;
                tp[pos] = (unsigned char)tr.w; pos += tr.d ? 1 : -1; q = tr.nx;
                if (pos <= 1 || pos >= N - 2) break;
            }
        }''')
open(fn, 'w').write(s)
