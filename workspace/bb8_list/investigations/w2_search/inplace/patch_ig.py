s = open('igstage.cpp').read()
def rep(a, b):
    global s
    assert a in s, a[:60]
    s = s.replace(a, b, 1)
BS = chr(92)
rep("// stage35g.cpp: GENERALISED", "// igstage.cpp (inplace/): gstage + leftmost-visit/change report: every result line gets\n//   ' | X LO MW L1 P' before ' | U=': LO = leftmost head cell, MW = leftmost cell whose value changed (1e18 = none),\n//   L1 = leftmost 1 at the end (J lines), P = cell left of the farthest parsed token (J lines); all relative to the\n//   input word's first cell.\n// stage35g.cpp: GENERALISED")
rep("struct Cfg { std::vector<unsigned char> t; long long pos, lo, hi, r1; int q; long long steps; };",
    "struct Cfg { std::vector<unsigned char> t; long long pos, lo, hi, r1; int q; long long steps; long long off, mw; };")
rep("c.t.swap(nt); c.pos += n; c.lo += n; c.hi += n; c.r1 += n;", "c.t.swap(nt); c.pos += n; c.lo += n; c.hi += n; c.r1 += n; c.off += n; c.mw += n;")
rep("    unsigned long long used = 0;", "    c.off = off; c.mw = (long long)4e18;\n    unsigned long long used = 0;")
rep("putchar('0' + c.t[i]);\n", "putchar('0' + c.t[i]);\n                    xr(c, l1, p);\n")
rep('printf("H %lld %c %d %lld | U=%llx' + BS + 'n", c.steps, \'A\' + c.q, s, k, used);',
    'printf("H %lld %c %d %lld", c.steps, \'A\' + c.q, s, k); xr(c, c.off, c.off); printf(" | U=%llx' + BS + 'n", used);')
rep("        c.t[c.pos] = x.w;\n", "        if (c.t[c.pos] != x.w && c.pos < c.mw) c.mw = c.pos;\n        c.t[c.pos] = x.w;\n")
for L in 'TW':
    rep('printf("%s %%lld | U=%%llx%sn", c.steps, used);' % (L, BS), 'printf("%s %%lld", c.steps); xr(c, c.off, c.off); printf(" | U=%%llx%sn", used);' % (L, BS))
rep("static void run_one(", """static void xr(const Cfg &c, long long l1, long long p) {
    printf(" | X %lld %lld %lld %lld", c.lo - c.off, c.mw > (long long)1e18 ? (long long)1e18 : c.mw - c.off, l1 - c.off, p - c.off);
}
static void run_one(""")
open('igstage.cpp','w').write(s)
