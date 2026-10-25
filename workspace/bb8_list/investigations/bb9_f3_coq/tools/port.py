"""Port C04 files (src/BB9/verify_c04/<rel>) into the X tree (x/<rel>) with the mechanical changes:
  the busycoq instance (Individual92 -> Individual112, logical path XL), and the halting configuration state
  H -> J (C04 halts in H after E0; X halts in J after E0), and the logical names Dev/K31/Score/Fgh -> XDev/...  python port.py rel1 rel2 ...  (refuses to overwrite
  a file that was edited by hand after porting unless -f)."""
import sys, hashlib
from pathlib import Path
W = Path(__file__).resolve().parents[1]
SRC = W / 'src' / 'BB9' / 'verify_c04'
X = W / 'x'
force = '-f' in sys.argv
for rel in [a for a in sys.argv[1:] if a != '-f']:
    s = (SRC / rel).read_text(encoding='utf-8')
    s = s.replace('From BB8 Require Import Individual92.', 'From XL Require Import Individual112.')
    s = s.replace('<{{H}}', '<{{J}}')
    import re
    s = re.sub(r'From (Dev|K31|Score|Fgh) Require', lambda m: 'From X' + m.group(1) + ' Require', s)
    out = X / rel
    stamp = W / 'logs' / ('port_' + rel.replace('/', '_') + '.sha')
    if out.exists() and not force:
        if not stamp.exists() or stamp.read_text() != hashlib.sha256(out.read_bytes()).hexdigest():
            print('SKIP (edited by hand):', rel); continue
    out.write_text(s, newline='\n', encoding='utf-8')
    stamp.write_text(hashlib.sha256(out.read_bytes()).hexdigest())
    print('ported', rel)
