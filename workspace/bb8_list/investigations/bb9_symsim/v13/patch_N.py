import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(a, b, c=1):
    global s
    assert s.count(a) == c, (a[:70], s.count(a))
    s = s.replace(a, b)
rep('struct GSym { i128 lb; ll mod, res; string desc; };',
    'struct GSym { i128 lb; ll mod, res; string desc; vector<int> dE, dL; };   // v14c dominance edges: X >= 2^Y (dE), X >= Y (dL)')
# domSign before the sign refusal
rep('''    UD("sign:" + linstr(e));''', '''    { int ds = DOMON ? domSign(e) : 0; if (ds != 0) return ds; }
    UD("sign:" + linstr(e));''')
rep('static Lin consolidate(i128 c, i128 D, const vector<pair<int, i128>> &T);', r'''static Lin consolidate(i128 c, i128 D, const vector<pair<int, i128>> &T);
// ---- v14c (step 3): sound size ordering between HUGE symbols by provenance (dominance edges, see notes.txt):
//   X ->E Y : X >= 2^Y      X ->L Y : X >= Y      (both are lower-bound facts proved at X's creation)
// X >= 2^Z holds when a path X -> ... -> Z uses at least one E edge (2^ is monotone; X >= Y >= 2^Z; X >= 2^Y, Y >= Z).
// domSign decides a mixed-sign form  sum a_i Y_i - sum b_j Z_j + c  when some Y with a >= 1 satisfies Y >= 2^Z_j for
// every negative Z_j:  value >= 2^M - B M + c  with M = max Z_j >= L0 = max lb(Z_j), B = sum b_j; this is positive for all
// M >= L0 when L0 >= log2(B) + 2 and 2^L0 > B L0 - c.  Otherwise the comparison stays undecided.
static bool DOMON = false; static ll DOMDEC = 0, DOMTRY = 0;
static int domSign(const Lin &e);
static bool domReach(int X, int Z, bool &usedE, int depth, map<pair<int,int>, int> &memo);''')
rep('''static int newG(i128 lb, ll res, const string &desc, ll mod = 0) {''', r'''static bool domReach(int X, int Z, bool &usedE, int depth, map<pair<int,int>, int> &memo) {
    // is there a path X -> Z (usedE set if an E edge is on it)?  memo: 0 none, 1 path without E, 2 path with E
    if (depth > 64) return false;
    auto key = make_pair(X, Z); auto it = memo.find(key);
    if (it != memo.end()) { if (it->second == 2) usedE = true; return it->second > 0; }
    memo[key] = 0;
    int best = 0;
    if (X >= 0 && X < (int)GS.size()) {
        for (int Y : GS[X].dE) { if (Y == Z) { best = 2; break; } bool u = false; if (domReach(Y, Z, u, depth + 1, memo)) best = 2; if (best == 2) break; }
        if (best < 2) for (int Y : GS[X].dL) { if (Y == Z) { best = max(best, 1); continue; } bool u = false; if (domReach(Y, Z, u, depth + 1, memo)) best = max(best, u ? 2 : 1); if (best == 2) break; }
    }
    memo[key] = best; if (best == 2) usedE = true; return best > 0;
}
static int domSign(const Lin &e) {
    ++DOMTRY;
    vector<pair<int, i128>> P, N;
    for (int k = 0; k < e.n; ++k) { if (e.id[k] >= PBASE) return 0; if (e.a[k] > 0) P.push_back({e.id[k], e.a[k]}); else N.push_back({e.id[k], -e.a[k]}); }
    if (P.empty() || N.empty()) return 0;
    for (int pass = 0; pass < 2; ++pass) {   // pass 0: positive dominates; pass 1: negative dominates (form < 0)
        const auto &Pos = pass == 0 ? P : N; const auto &Neg = pass == 0 ? N : P; i128 c = pass == 0 ? e.c : -e.c;
        i128 B = 0, L0 = 0; bool ovf = false;
        for (auto &z : Neg) { i128 t; if (__builtin_add_overflow(B, z.second, &t)) ovf = true; else B = t; L0 = max(L0, GS[z.first].lb); }
        if (ovf || B > ((i128)1 << 100)) continue;
        for (auto &y : Pos) {
            bool all = true; map<pair<int,int>, int> memo;
            for (auto &z : Neg) { bool u = false; if (!(domReach(y.first, z.first, u, 0, memo) && u)) { all = false; break; } }
            if (!all) continue;
            // value >= 2^M - B M + c for M >= L0: needs L0 >= log2(B) + 2 and g(L0) > 0
            int lgB = 0; { i128 t = B; while (t > 1) { t >>= 1; ++lgB; } }
            if (L0 < lgB + 2) continue;
            bool pos;
            if (L0 >= 120) pos = c > -((i128)1 << 110);   // 2^L0 >= 2^120 dominates B L0 (< 2^108) and any |c| < 2^110
            else { i128 p2 = (i128)1 << (int)L0, t; if (__builtin_mul_overflow(B, L0, &t)) pos = false; else pos = p2 - t + c > 0; }
            if (pos) { ++DOMDEC; return pass == 0 ? 1 : -1; }
        }
    }
    return 0;
}
// record dominance facts for a new symbol X:  expo: X >= 2^f,  else X >= f  (f a global form); an edge to each symbol Y
// with f >= Y decided by lower bounds (coefficient of Y >= denominator, all other coefficients >= 0, constant >= 0)
static void domAdd(int X, const Lin &f, bool expo) {
    if (!DOMON || X < 0 || f.n == 0) return;
    for (int k = 0; k < f.n; ++k) if (f.id[k] < PBASE && f.a[k] > 0) {
        bool ok = f.a[k] >= f.D && f.c >= 0;
        for (int t = 0; t < f.n && ok; ++t) if (t != k && f.a[t] < 0) ok = false;
        if (!ok) continue;
        if (expo) GS[X].dE.push_back(f.id[k]); else GS[X].dL.push_back(f.id[k]);
    }
}
static int newG(i128 lb, ll res, const string &desc, ll mod = 0) {''')
open(fn, 'w').write(s)
