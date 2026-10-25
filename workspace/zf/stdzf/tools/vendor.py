"""Copy the dependency closure (sources + compiled .vo/.glob) of the library files used by stdzf from
ext/undec-8.20 into vendor/theories, with the library's LICENSE and a README.
Usage: python tools/vendor.py"""
import shutil, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))
import undecbuild_lib as ub

ROOTS = ['FOL/Sets/minZF.v', 'FOL/Sets/ZF.v', 'FOL/Deduction/FullNDFacts.v', 'FOL/Syntax/Facts.v',
         'FOL/Reductions/PCPb_to_minZF.v', 'FOL/Sets/Models/ZF_conservativity.v']
files = ub.closure(ROOTS)
dst = HERE / 'vendor' / 'theories'
for f in files:
    rel = f.relative_to(ub.ROOT)
    for ext in ('.v', '.vo', '.glob'):
        src = f.with_suffix(ext)
        if src.exists():
            (dst / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, (dst / rel).with_suffix(ext))
shutil.copy2(ub.ROOT.parent / 'LICENSE', HERE / 'vendor' / 'LICENSE')
readme = [
    'Vendored subset of the Coq Library of Undecidability Proofs',
    '(https://github.com/uds-psl/coq-library-undecidability), branch coq-8.20, commit',
    '70dfc56f33a6e4835281044e68aa68279989047e (2024-09-18), license MPL-2.0 (see LICENSE).',
    'Unmodified files: the dependency closure of ' + ', '.join(ROOTS),
    f'({len(files)} files).  Compiled with Coq 8.20.1 (Coq Platform 2025.01); logical root Undecidability.',
    '',
]
(HERE / 'vendor' / 'README.md').write_text('\n'.join(readme), encoding='utf-8')
print(len(files), 'files vendored')
