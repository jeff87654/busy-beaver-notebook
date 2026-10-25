import idle
"""Wait up to T seconds for new lines matching events in the build log; print them.  python waitlog.py LOG STATEFILE T"""
import sys, time, re, os
log, state, T = sys.argv[1], sys.argv[2], float(sys.argv[3])
pat = re.compile(r'ok,|FAILED|NOT COMPILED|COMPILE DONE|probe|Error')
seen = int(open(state).read()) if os.path.exists(state) else 0
t0 = time.time()
while True:
    lines = open(log, encoding='utf-8', errors='replace').read().splitlines()
    new = [l for l in lines[seen:] if pat.search(l)]
    if new or time.time() - t0 > T:
        open(state, 'w').write(str(len(lines)))
        print('\n'.join(new) if new else '(no new events, %d lines)' % len(lines)); break
    time.sleep(20)
