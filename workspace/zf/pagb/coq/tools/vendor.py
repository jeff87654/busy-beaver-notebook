"""Copy the dependency closure (sources only) of the library files used by zf/pagb/coq from the clone
zf/stdzf/ext/undec-8.20 (branch coq-8.20, commit 70dfc56) into zf/pagb/coq/vendor/theories, unmodified.
build.py compiles them.  Usage: python tools/vendor.py"""
import shutil, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE.parent.parent / 'stdzf' / 'tools'))
import undecbuild_lib as ub

ROOTS = ['FOL/PA.v', 'FOL/Arithmetics/NatModel.v', 'FOL/Arithmetics/DeductionFacts.v',
         'FOL/Arithmetics/TarskiFacts.v', 'FOL/Deduction/FullNDFacts.v', 'FOL/Syntax/Facts.v',
         'FOL/Semantics/Tarski/FullSoundness.v']
files = ub.closure(ROOTS)
dst = HERE.parent / 'vendor' / 'theories'
for f in files:
    rel = f.relative_to(ub.ROOT)
    (dst / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, dst / rel)
shutil.copy2(ub.ROOT.parent / 'LICENSE', HERE.parent / 'vendor' / 'LICENSE')
(HERE.parent / 'vendor' / 'ORDER.txt').write_text('\n'.join(f.relative_to(ub.ROOT).as_posix() for f in files) + '\n',
                                           encoding='utf-8')
readme = [
    'Vendored subset of the Coq Library of Undecidability Proofs',
    '(https://github.com/uds-psl/coq-library-undecidability), branch coq-8.20, commit',
    '70dfc56f33a6e4835281044e68aa68279989047e (2024-09-18), license MPL-2.0 (see LICENSE).',
    'Unmodified source files: the dependency closure of ' + ', '.join(ROOTS),
    f'({len(files)} files, compile order in ORDER.txt).  Logical root Undecidability; compiled by ../build.py.',
    '',
]
(HERE.parent / 'vendor' / 'README.md').write_text('\n'.join(readme), encoding='utf-8')
print(len(files), 'files vendored')
