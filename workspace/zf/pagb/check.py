"""Top-level check of zf/pagb: the frozen 449-state machine machine/pa_wade.tm halts from the blank tape
iff PAeq ⊢TC GC_form (Goldbach's conjecture in the Coq Library of Undecidability Proofs' PA), in Coq,
with no axioms.

Steps:
  1. the frozen machine files have their recorded sha256 (INTERFACE.md "FROZEN");
  2. logic layer: coq/check.py (clean rebuild, statements, assumptions closed) -> CHECK PASS;
  3. TM layer: tm/check_tm.py (literal table = pa_wade.tm, generators reproduce, clean rebuild) -> CHECK PASS;
  4. program layer: prog/check.py (DagPA = machine, generated regions reproduce, clean rebuild) -> CHECK PASS;
  5. e2e: compile e2e/Headline.v (< 100 lines); its statements are the expected ones and both
     Print Assumptions report "Closed under the global context";
  6. coqchk (independent kernel re-check) of PAGBE.Headline and every library it loads.  coqchk lists the
     axioms present anywhere in that environment; the only ones allowed are the three that busycoq's TM.v
     brings in through its own imports (BusyCoq.LibTactics.inj_pair2, Coq.Logic.ProofIrrelevance.
     proof_irrelevance, Coq.Logic.Eqdep.Eq_rect_eq.eq_rect_eq).  Step 5's Print Assumptions (dependency-
     precise) shows that the headline theorems use none of them.
Usage: python -I zf/pagb/check.py"""
import ctypes, hashlib, re, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)  # IDLE
M = Path(__file__).resolve().parent
FROZEN = {
    'machine/pa_wade.tm': 'ed795af79b6752d72c037d7e32eca1d23efaa6a6c0f0d07fc7ba89869f2616a6',
    'machine/source_pa.py': '152d4a5f82be2f12c3823478a911c5f71fd21f78a21bca06f690030582b42587',
    'machine/spec_pa.py': '3cfdafbfe00828621ffdcddac7de09c57418a3b8eeadc08d2ee681ab9828dde4',
    'machine/design_choice_A.json': 'da10ced32774ea0ea3ea91f1d84d3fe15ef17324e760579165586b431fd7abf9',
}
COQCHK = r'C:\Coq-Platform~8.20~2025.01\bin\coqchk.exe'


def fail(msg):
    print('CHECK FAIL:', msg)
    sys.exit(1)


def run(args, cwd, tail=1500):
    print('>>', ' '.join(map(str, args)), flush=True)
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                       creationflags=0x08000000 | 0x40)
    out = r.stdout + r.stderr
    print(out[-tail:], flush=True)
    if r.returncode:
        fail(f'{args} exited with {r.returncode}')
    return out


for f, h in FROZEN.items():
    if hashlib.sha256((M / f).read_bytes()).hexdigest() != h:
        fail(f'{f} does not have the frozen sha256')
print('frozen machine files: sha256 ok')

for args, cwd in [([sys.executable, '-I', str(M / 'coq' / 'check.py')], M / 'coq'),
                  ([sys.executable, '-I', str(M / 'tm' / 'check_tm.py')], M / 'tm'),
                  ([sys.executable, '-I', str(M / 'prog' / 'check.py')], M / 'prog')]:
    if 'CHECK PASS' not in run(args, cwd):
        fail(f'{args[-1]} did not print CHECK PASS')

E2E = M / 'e2e'
for f in E2E.glob('Headline.*'):
    if f.suffix in ('.vo', '.vok', '.vos', '.glob'):
        f.unlink()
out = run([sys.executable, '-I', str(E2E / 'build.py')], E2E)
head = (E2E / 'Headline.v').read_text(encoding='utf-8')
if len(head.splitlines()) >= 100:
    fail('Headline.v has 100 lines or more')
for stmt in ['Theorem pagb_halts_iff_PA_GC :\n  PAGBT.ZFTM.ZFTM.halts PAGBT.ZFTM.tm PAGBT.ZFTM.ZFTM.c0 <-> @tprv _ _ falsity_on class PAeq GC_form.',
             'Theorem GC_adequate rho : sat interp_nat rho GC_form <-> Goldbach_nat.',
             'Definition GC_form : form :=\n  ∀ ((even $0 ∧ leq (num 4) $0) → ∃ ∃ ((Pr $1 ∧ Pr $0) ∧ ($1 ⊕ $0 == $2))).']:
    if stmt not in head:
        fail('unexpected statement in Headline.v: ' + stmt)
if out.count('Closed under the global context') != 2 or 'Axioms:' in out:
    fail('Headline assumptions are not closed')

flags = ['-Q', str(M / 'vendor' / 'theories'), 'Undecidability',
         '-Q', str((M / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()), 'BusyCoq',
         '-Q', str(M / 'coq'), 'PAGB', '-Q', str(M / 'tm' / 'coq'), 'PAGBT',
         '-Q', str(M / 'prog' / 'coq'), 'PAGBP', '-Q', str(E2E), 'PAGBE']
out = run([COQCHK, '-silent', '-o', *flags, 'PAGBE.Headline'], M, tail=800)
m = re.search(r'\* Axioms:(.*?)\n\s*\n\* Constants', out, re.S)
if not m:
    fail('coqchk summary not found')
env_axioms = set(m.group(1).split()) - {'<none>'}
ALLOWED = {'BusyCoq.LibTactics.inj_pair2', 'Coq.Logic.ProofIrrelevance.proof_irrelevance',
           'Coq.Logic.Eqdep.Eq_rect_eq.eq_rect_eq'}
if not env_axioms <= ALLOWED:
    fail(f'coqchk: unexpected axioms in the environment: {sorted(env_axioms - ALLOWED)}')
for k in ['type-in-type', 'unsafe (co)fixpoints', 'positivity is assumed']:
    if not re.search(re.escape(k) + r'[^\n]*:\s*<none>', out):
        fail(f'coqchk: {k} not <none>')
print('coqchk: kernel re-check ok; environment axioms', sorted(env_axioms),
      '(loaded by busycoq TM.v imports; Print Assumptions shows the headline theorems use none)')
print('CHECK PASS: pa_wade.tm halts iff PAeq ⊢TC GC_form (Goldbach); Print Assumptions closed for both headline theorems')
