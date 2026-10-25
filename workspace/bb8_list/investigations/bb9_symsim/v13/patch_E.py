import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
a = '    if (OPT.tape) printf("%s\\n", verdict == "HALT" ? tapeDump(M).c_str()'
rep(a, '    if (ITERSTAT) fprintf(stderr, "ITERSTAT itersyms=%lld orbits=%lld orbitsteps=%lld cachehits=%lld GS=%zu\\n", ITERSYMS, ITERORB, ITERORBST, ITERHIT, GS.size());\n' + a)
rep('static ll ITERSYMS = 0;', 'static ll ITERSYMS = 0, ITERORB = 0, ITERORBST = 0, ITERHIT = 0; static bool ITERSTAT = false;')
rep('        auto it = OC.find(key); if (it != OC.end()) return it->second;', '        auto it = OC.find(key); if (it != OC.end()) { ++ITERHIT; return it->second; }')
rep('''        Lin y = step(x0); map<ll, int> seen;
        for (int t = 0; t < 20000; ++t) {''', '''        Lin y = step(x0); map<ll, int> seen; ++ITERORB;
        for (int t = 0; t < 20000; ++t) { ++ITERORBST;''')
a = '        else if (a == "--nopiter") PITER = false;'
rep(a, a + '\n        else if (a == "--iterstat") ITERSTAT = true;')
open(fn, 'w').write(s)
