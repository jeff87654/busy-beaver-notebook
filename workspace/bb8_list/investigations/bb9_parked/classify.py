"""classify.py LOG... : per-lead screening classification of lkf.py grow-world logs (one TSV row per log).
Columns: id, jumps, end status, esc (escalations: a cleared list k >= 1000 and > 2 * every earlier k = a list rebuilt
at accumulator size = one f_w application), lskip (fixed-depth counter loads skipped), maxk digits, k at the end,
verdict.  Verdict rules (screening):
  HALT-LOW    halts with esc <= 2: omega-level <= esc + O(1) (counters at fixed depth add f_(k+1) per load) -> << G
  NONHALT-IR  Ligocki Inf_Repeat proof inside the jump abstraction
  LOOP-W1     no halt, esc >= 10: f_(w+1)-shape looper (rebuild from the accumulator every few periods)
  RUN-FLAT    no halt, esc <= 2 (bounded depth): not a G candidate whether or not it halts later
  OPEN        anything else"""
import re, sys, os


def classify(fn):
    t = open(fn).read()
    ks = [int(x) for x in re.findall(r'^J\d+ CL t=\d+ k=(\d+)', t, re.M)]
    nj = len(re.findall(r'^J\d', t, re.M))
    esc = 0; mx = 0
    for k in ks:
        if k >= 1000 and k > 2 * mx:
            esc += 1
        mx = max(mx, k)
    nsk = len(re.findall(r'^  L skip', t, re.M))
    m = re.search(r'^(HALT\S* \S+|STOP|END|SIMSTATE \S+|Traceback)', t, re.M)
    st = m.group(1).replace('SIMSTATE ', '').replace(' ', '') if m else 'running'
    if st.startswith('HALT'):
        v = 'HALT-LOW' if esc <= 2 else 'HALT-ESC(%d)' % esc
    elif st == 'Inf_Repeat':
        v = 'NONHALT-IR'
    elif esc >= 10:
        v = 'LOOP-W1'
    elif esc <= 2:
        v = 'RUN-FLAT'
    else:
        v = 'OPEN'
    return [nj, st, esc, nsk, len(str(mx)) if mx else 0, len(str(ks[-1])) if ks else 0, v]


if __name__ == '__main__':
    print('\t'.join(['id', 'jumps', 'end', 'esc', 'lskip', 'maxk_dig', 'lastk_dig', 'verdict', 'log']))
    for fn in sys.argv[1:]:
        id = os.path.basename(fn).split('_')[0]
        print('\t'.join([id] + [str(x) for x in classify(fn)] + [fn]))
