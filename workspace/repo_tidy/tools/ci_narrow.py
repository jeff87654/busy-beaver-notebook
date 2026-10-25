"""Apply the ci-narrow change to .github/workflows/coq.yml (usage: python ci_narrow.py path/to/coq.yml)."""
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)

rep('''BB10/, BB12/ and stage 2 of BB9/verify_fw2 take hours and are not
# built here.''', '''Not built here, because they take long
# (recorded local builds are in their directories): BB10/ (about 20 minutes), BB12/ (about 3 hours) and stage 2 of
# BB9/verify_fw2 (about 2 hours).''')
rep('''# When the jobs run: on pull requests and on pushes to main, a job runs only if its entry's files changed (job `changes`,
# below; a skipped job counts as passed). Changes under .github/ (this file, the busycoq pin) run every job, and so do
# the weekly scheduled run and manual runs (workflow_dispatch).''',
'''# When the jobs run: on pull requests and on pushes to main, a job runs only if its entry's files, or the files of an
# entry it depends on, changed (job `changes`, below; a skipped job counts as passed). Changing this file does not by
# itself run any job, so a pull request that adds an entry and its job runs that job only. Every job runs on manual
# runs (workflow_dispatch: Actions > Coq proofs > Run workflow) and in the weekly scheduled run.
#
# So after changing how a job builds without changing its entry's files (its steps, the container image, or the busycoq
# pin BUSYCOQ_COMMIT, which is set in each job below), run the workflow manually on the branch.''')
rep('''            shared:
              - '.github/**'
''', '')
BS = chr(92); NL = chr(10)
rep('          if [ "${{ github.event_name }}" = schedule ] || [ "${{ github.event_name }}" = workflow_dispatch ] ' + BS + NL +
    '             || [ "${{ steps.f.outputs.shared }}" = true ]; then',
    '          if [ "${{ github.event_name }}" = schedule ] || [ "${{ github.event_name }}" = workflow_dispatch ]; then')
rep('''Builds BB9/verify_c04 (all 55 files,''', '''Builds BB9/verify_c04 (all 56 files,''')
rep('''the BB(9)
    # entry: all 56 files from scratch, 4 coqc at a time, then the probe (about 1 h 40 min on a 4-vCPU runner; the
    # longest file, k31/K_e1.v, takes most of it).''', '''the proof
    # base of BB8/verify_m8 and of the later BB(9) proofs: all 56 files from scratch, 4 coqc at a time, then the probe
    # (about 1 h 40 min on a 4-vCPU runner; the longest file, k31/K_e1.v, takes most of it).''')
rep('''    # ZF/: the 393-, 361- and 354-state "halts iff ZF proves a contradiction" machines.''',
'''    # ZF/verify: the 393-, 361-, 354-, 336- and 335-state machines halt iff O'Rear's ZF system proves a contradiction
    # (check.py ties each literal table to its .tm file, builds the proof and checks the statement and its assumptions).''')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
