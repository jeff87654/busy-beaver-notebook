import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(a, b, c=1):
    global s
    assert s.count(a) == c, (a[:70], s.count(a))
    s = s.replace(a, b)
# overflowSym: X = x*kx + y*ky (all terms nonnegative) >= x, >= y
rep('''    return LV(newG(max(lb, (i128)1), bres, "O(" + linstr(x) + "*" + s128(kx) + "+" + linstr(y) + "*" + s128(ky) + ")", best));''',
    '''    { int id = newG(max(lb, (i128)1), bres, "O(" + linstr(x) + "*" + s128(kx) + "+" + linstr(y) + "*" + s128(ky) + ")", best);
      if (kx >= 1) domAdd(id, x, false); if (ky >= 1) domAdd(id, y, false); return LV(id); }''')
# consolidate: X = (sum a_t Y_t + c)/D, all a_t > 0: X >= Y_t when a_t >= D and c >= 0
rep('''    ++consolidations;
    return LV(newG(lb, bres, desc, best));''', '''    ++consolidations;
    int id = newG(lb, bres, desc, best);
    if (DOMON && c >= 0) for (auto &tt : T) if (tt.second / g >= D && tt.first < PBASE) GS[id].dL.push_back(tt.first);
    return LV(id);''')
# W_2(b) = (3^(b+3)-5)/2 >= 2^b
rep('''    int id = newG(lb, r.r, "W(" + linstr(j) + "," + linstr(b) + ")");
    return LV(id);''', '''    int id = newG(lb, r.r, "W(" + linstr(j) + "," + linstr(b) + ")");
    if (j.isExact() && j.c == 2) { domAdd(id, b, true); domAdd(id, b, false); }
    return LV(id);''')
# I(2,a,b) = W_2^a(b) >= W_2(b) >= 2^b  (a >= 1)
rep('''    return LV(newG(lb, r.r, "I(" + linstr(j) + "," + linstr(a) + "," + linstr(b) + ")"));''',
    '''    { int id = newG(lb, r.r, "I(" + linstr(j) + "," + linstr(a) + "," + linstr(b) + ")");
      if (j.isExact() && j.c == 2 && (a.isExact() ? a.c >= 1 : true)) { domAdd(id, b, true); domAdd(id, b, false); }
      return LV(id); }''')
# C(j,v,b) = U_j^v(b), v >= 1:  >= 2^b, >= 2^j, >= 2^(v-1), >= b
rep('''    return LV(newG(lb, r.r, "C(" + linstr(j) + "," + linstr(v) + "," + linstr(b) + ")"));''',
    '''    { int id = newG(lb, r.r, "C(" + linstr(j) + "," + linstr(v) + "," + linstr(b) + ")");
      bool v1 = v.isExact() ? v.c >= 1 : true;   // v >= 1 here (v = 0 returned b above; symbolic v >= orbit length + 1)
      if (v1) { domAdd(id, b, true); domAdd(id, j, true); domAdd(id, laddc(v, -1), true); domAdd(id, b, false); }
      return LV(id); }''')
# P(k,r) = 2^k (r+4) - 4 >= 2^k (k >= 1), >= r
rep('''        return LV(newG(max(lb, (i128)1), (ll)pmod((i128)p2 * (rr + 4) - 4, MG), "P(" + linstr(k) + "," + linstr(r) + ")"));''',
    '''        { int id = newG(max(lb, (i128)1), (ll)pmod((i128)p2 * (rr + 4) - 4, MG), "P(" + linstr(k) + "," + linstr(r) + ")"); domAdd(id, r, false); return LV(id); }''')
rep('''    return LV(newG(SYMCAP, (ll)pmod((i128)p2 * (rr + 4) - 4, MG), "P(" + linstr(k) + "," + linstr(r) + ")"));''',
    '''    { int id = newG(SYMCAP, (ll)pmod((i128)p2 * (rr + 4) - 4, MG), "P(" + linstr(k) + "," + linstr(r) + ")"); domAdd(id, k, true); domAdd(id, r, false); return LV(id); }''')
# A(a,c,k,x) = a^k x + c (a^k-1)/(a-1) with a >= 2, c >= 0, x >= 1, k >= 1:  >= 2^k, >= x
rep('''    return LV(newG(max(lb, (i128)1), res, "A(" + s128(a) + "," + s128(c) + "," + linstr(k) + "," + linstr(x) + ")"));''',
    '''    { int id = newG(max(lb, (i128)1), res, "A(" + s128(a) + "," + s128(c) + "," + linstr(k) + "," + linstr(x) + ")");
      bool xok = x.isExact() ? x.c >= 1 : lbG(x) >= 1, kok = k.isExact() ? k.c >= 1 : lbG(k) >= 1;
      if (a >= 2 && c >= 0 && xok && kok) domAdd(id, k, true);
      if (a >= 1 && c >= 0) domAdd(id, x, false);
      return LV(id); }''')
# T(k,x0) = F^k(x0) with F(y) >= y + 1: >= x0 + k
rep('''    ++wSymCount;
    return LV(newG(max(lb, (i128)1), rr, "T(" + linstr(k) + "," + linstr(x0) + ")"));
}''', '''    ++wSymCount;
    { int id = newG(max(lb, (i128)1), rr, "T(" + linstr(k) + "," + linstr(x0) + ")");
      if (R.grows) { domAdd(id, x0, false); domAdd(id, k, false); }
      return LV(id); }
}''')
rep('''        else if (a == "--multi") MULTI = true;''', '''        else if (a == "--multi") MULTI = true;
        else if (a == "--dom") DOMON = true;''')
rep('''    if (ITERCHECK) fprintf(stderr, "ITERCHECK-SUMMARY''', '''    if (DOMON && ITERSTAT) fprintf(stderr, "DOMSTAT tries=%lld decided=%lld\\n", DOMTRY, DOMDEC);
    if (ITERCHECK) fprintf(stderr, "ITERCHECK-SUMMARY''')
open(fn, 'w').write(s)
