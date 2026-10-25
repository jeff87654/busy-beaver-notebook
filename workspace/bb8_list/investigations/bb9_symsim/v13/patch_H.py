import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(a, b, c=1):
    global s
    assert s.count(a) == c, (a[:70], s.count(a))
    s = s.replace(a, b)
# IterStop exception: the iteration's own constraints fail after t valid applications
rep('''static Lin iterPow(const Rule &R, int v, const Lin &x0, const Lin &k, bool orbitOnly = false);''',
    '''struct IterStop { i128 t; };   // an ITER rule's own constraint fails at the input of application t+1 (t applications valid)
static Lin iterPow(const Rule &R, int v, const Lin &x0, const Lin &k, bool orbitOnly = false);''')
# inner iterations inside a formula must run in full
rep('''            case 'T': v = zIterS(*z.rp, lin(z.B), lin(z.K)); break;''',
    '''            case 'T': try { v = zIterS(*z.rp, lin(z.B), lin(z.K)); } catch (IterStop &) { UD("iter: inner iteration stopped"); } break;''')
rep('''struct IterOrbit { vector<ll> rs; vector<i128> lbs; int mu = -1, lam = -1; };''',
    '''struct IterOrbit { vector<ll> rs; vector<i128> lbs; int mu = -1, lam = -1, stop = -1; };   // stop: valid applications if a constraint fails''')
rep('''            if (!iterConsOK(R, y, &E)) UD("iter: constraint");
            E.consts = &CV; y = E.lin(F);
        }
    } catch (...) { GS.resize(g0); throw; }
    GS.resize(g0);
    if (O.lam < 0) UD("iter: orbit");''', '''            if (!iterConsOK(R, y, &E)) { O.stop = t + 1; break; }
            E.consts = &CV; y = E.lin(F);
        }
    } catch (...) { GS.resize(g0); throw; }
    GS.resize(g0);
    if (O.lam < 0 && O.stop < 0) UD("iter: orbit");''')
rep('''        for (i128 t = 0; t < k.c; ++t) {
            if (t > 0 && !iterConsOK(R, y)) UD("iter: constraint");
            if (t > 0 && !y.isExact() && k.c - t > 2) return iterPow(R, v, y, LC(k.c - t), true);
            y = step(y);
        }
        return y;''', '''        for (i128 t = 0; t < k.c; ++t) {
            if (t > 0 && !iterConsOK(R, y)) throw IterStop{t};
            if (t > 0 && !y.isExact() && k.c - t > 2) { try { return iterPow(R, v, y, LC(k.c - t), true); } catch (IterStop &s2) { throw IterStop{t + s2.t}; } }
            y = step(y);
        }
        return y;''')
rep('''    IterOrbit O = iterOrbit(R, x0);
    ll rr; i128 lb;
    if (k.isExact()) {''', '''    IterOrbit O = iterOrbit(R, x0);
    if (O.stop >= 0 && !(k.isExact() && k.c <= O.stop)) throw IterStop{O.stop};
    if (O.stop >= 0) cOK = false;
    ll rr; i128 lb;
    if (k.isExact()) {''')
rep('''    if (k.isExact() && k.c == 1) return y1;
    if (!hasProof(y1) && !hasProof(k)) {   // the second iterate's input must satisfy the constraints too
        if (!iterConsOK(R, y1)) UD("iter: constraint");''', '''    if (k.isExact() && k.c == 1) return y1;
    if (!hasProof(y1) && !hasProof(k)) {   // the second iterate's input must satisfy the constraints too
        if (!iterConsOK(R, y1)) throw IterStop{1};
        try { return zIterS(R, y1, laddc(k, -1)); } catch (IterStop &s2) { throw IterStop{1 + s2.t}; }''')
# proof mode: a stopped shadow iteration is just undecided
rep('''    Lin sh = iterPow(R, R.fvar, shadowOf(x), shadowOf(k));
    static map<ll, std::shared_ptr<Rule>> RP;''', '''    Lin sh; try { sh = iterPow(R, R.fvar, shadowOf(x), shadowOf(k)); } catch (IterStop &) { UD("iter: shadow iteration stopped"); }
    static map<ll, std::shared_ptr<Rule>> RP;''')
# applyRule: compute the new counts first; on IterStop retry with the valid count
rep('''            for (int s = 0; s < 2; ++s) {
                size_t sz = C.st[s].size();
                for (size_t i = 0; i < R.g[s].size(); ++i) {
                    int v = R.rv[s][i]; if (v < 0) continue;
                    Lin nn = (R.iter && R.isF[v]) ? (v == R.fvar ? iterFirst(R, bind, k) : R.iterF[v]) : (R.affine && R.amul[v] > 1) ? zAffS(bind[v], R.amul[v], R.delta[v], k) : lcomb(bind[v], 1, k, R.delta[v]); normCount(nn);
                    C.st[s][sz - 1 - i].n = nn;
                }
            }''', '''            vector<Lin> nv(R.nv); vector<char> have(R.nv, 0);
            for (int pass = 0; pass < 2; ++pass) {
                try {
                    for (int v = 0; v < R.nv; ++v) if (bind[v].D != 0) {
                        Lin nn = (R.iter && R.isF[v]) ? (v == R.fvar ? iterFirst(R, bind, k) : R.iterF[v]) : (R.affine && R.amul[v] > 1) ? zAffS(bind[v], R.amul[v], R.delta[v], k) : lcomb(bind[v], 1, k, R.delta[v]);
                        normCount(nn); nv[v] = nn; have[v] = 1;
                    }
                    break;
                } catch (IterStop &st) {
                    if (proof || pass > 0 || st.t < 1) UD("iter: stopped");
                    k = LC(st.t); ++iterStops;
                }
            }
            for (int s = 0; s < 2; ++s) {
                size_t sz = C.st[s].size();
                for (size_t i = 0; i < R.g[s].size(); ++i) {
                    int v = R.rv[s][i]; if (v < 0) continue;
                    C.st[s][sz - 1 - i].n = nv[v];
                }
            }''')
rep('''    ll macro = 0, jumps = 0, ruleApps = 0, affApps = 0, iterApps = 0;''', '''    ll macro = 0, jumps = 0, ruleApps = 0, affApps = 0, iterApps = 0, iterStops = 0;''')
open(fn, 'w').write(s)
