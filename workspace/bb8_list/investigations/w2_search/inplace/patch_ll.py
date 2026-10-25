s = open('igstage.cpp').read()
def rep(a, b):
    global s
    assert a in s, a[:60]
    s = s.replace(a, b, 1)
rep("static long long EOFF = 1;", "static long long EOFF = 1;\nstatic long long LLIM = -(1LL << 60), LVS = 0;   // left limit (word coords): change < LLIM or visit < LLIM-LVS -> 'L'")
rep("        if (c.t[c.pos] != x.w && c.pos < c.mw) c.mw = c.pos;\n",
    "        if (c.t[c.pos] != x.w && c.pos < c.mw) c.mw = c.pos;\n"
    "        if ((c.t[c.pos] != x.w && c.pos - c.off < LLIM) || c.pos - c.off < LLIM - LVS) { printf(\"L %lld\", c.steps); xr(c, c.off, c.off); printf(\" | U=%llx\n\", used); return; }\n")
rep('while (scanf("%255s %7s %lld %lld %lld %lld %lld %255s %lld", ms, st, &head, &MAXS, &MAXW, &RCAP, &Q, suf, &E) == 9) {',
    'while (scanf("%255s %7s %lld %lld %lld %lld %lld %255s %lld %lld %lld", ms, st, &head, &MAXS, &MAXW, &RCAP, &Q, suf, &E, &LLIM, &LVS) == 11) {')
open('igstage.cpp','w').write(s)
