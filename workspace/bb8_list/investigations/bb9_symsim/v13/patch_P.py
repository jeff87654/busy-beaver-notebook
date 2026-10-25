import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(a, b, c=1):
    global s
    assert s.count(a) == c, (a[:60], s.count(a))
    s = s.replace(a, b)
rep('    ll kjumps = 0;', '    ll kjumps = 0, bigClears = 0, symClears = 0;   // v14: CDP clears with symbolic depth j (bigClears) or symbolic v (symClears)')
rep('''        if (!proof) { jlog.push_back("C" + linstr(j) + "," + linstr(v) + "," + linstr(b) + (B2.isExact() ? "" : "*")); if (jlog.size() > 8) jlog.erase(jlog.begin()); }''',
    '''        if (!proof) { jlog.push_back("C" + linstr(j) + "," + linstr(v) + "," + linstr(b) + (B2.isExact() ? "" : "*")); if (jlog.size() > 8) jlog.erase(jlog.begin()); if (!j.isExact()) ++bigClears; if (!v.isExact()) ++symClears; }''')
rep('''            ++R.uses; ++ruleApps; if (R.affine) ++affApps; if (R.iter) ++iterApps;''', '''            ++R.uses; ++ruleApps; if (R.affine) ++affApps; if (R.iter) { ++iterApps; if (!k.isExact()) ++iterSym; }''')
rep('    ll macro = 0, jumps = 0, ruleApps = 0, affApps = 0, iterApps = 0, iterStops = 0;', '    ll macro = 0, jumps = 0, ruleApps = 0, affApps = 0, iterApps = 0, iterStops = 0, iterSym = 0;')
rep('apps=%lld syms=%zu it=%lld |%s |%s\\n", mach.c_str()', 'apps=%lld syms=%zu it=%lld bc=%lld sc=%lld its=%lld |%s |%s\\n", mach.c_str()')
rep('RS.R.size(), M.ruleApps, GS.size(), M.iterApps, jl.c_str(), sd.c_str());', 'RS.R.size(), M.ruleApps, GS.size(), M.iterApps, M.bigClears, M.symClears, M.iterSym, jl.c_str(), sd.c_str());')
open(fn, 'w').write(s)
