s = open('jz.cpp').read()
NL = '\\n'
def P(tag, args): return 'if (getenv("KDDBG")) fprintf(stderr, "' + tag + NL + '"' + args + ');'
s = s.replace('            if (sgnOK(SL) < 0) break;',
              '            if (sgnOK(SL) < 0) { ' + P('KDSTOP SL %s dep %s', ', linstr(SL).c_str(), linstr(depth).c_str()') + ' break; }')
s = s.replace('            if (!dex && sgnOK(laddc(depth, -JINF)) < 0) break;',
              '            if (!dex && sgnOK(laddc(depth, -JINF)) < 0) { ' + P('KDSTOP depth %s', ', linstr(depth).c_str()') + ' break; }')
s = s.replace('            if (sv < 0) break;', '            if (sv < 0) { ' + P('KDSTOP sv %s', ', linstr(it.v).c_str()') + ' break; }')
s = s.replace('        } catch (Undec &) { if (proof) throw; return false; }',
              '        } catch (Undec &u) { ' + P('KDVAL %s', ', u.why.c_str()') + ' if (proof) throw; return false; }')
s = s.replace("        if (rp.empty() || rp[0].w[0] != '1') return false;",
              '        ' + P('KDTRY %s', ', show().c_str()') + "\n        if (rp.empty() || rp[0].w[0] != '1') return false;")
s = s.replace('        } catch (Undec &) { return false; }\n        if (phase == 2) pushDigit();',
              '        } catch (Undec &u) { ' + P('KDPARSE %s', ', u.why.c_str()') + ' return false; }\n        if (phase == 2) pushDigit();')
open('jz_dbg.cpp', 'w').write(s)
