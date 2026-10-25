"""Merge generated lemma files into the partial proof file: python merge.py BASE.v OUT.v GEN1.v GEN2.v ..."""
import re, sys
base = open(sys.argv[1]).read(); out = sys.argv[2]; gens = sys.argv[3:]
BLOCK = re.compile(r'^((?:Lemma|Theorem|Ltac|Definition|Fixpoint|Hint)\s+([A-Za-z0-9_\']+).*?(?:^Qed\.|\.\s*$))', re.S | re.M)
def defined(text):
    return set(re.findall(r'^(?:Lemma|Theorem|Ltac|Definition|Fixpoint)\s+([A-Za-z0-9_\']+)', text, re.M))
acc = base.rstrip() + '\n'
for g in gens:
    t = open(g).read()
    # body starts at the first generated non-crossing lemma: first 'Lemma' whose name does not start with cr_ after the crossing section
    names = [(m.start(), m.group(1)) for m in re.finditer(r'^Lemma\s+([A-Za-z0-9_\']+)', t, re.M)]
    hdr_names = defined(acc)
    first_body = next(pos for pos, n in names if not n.startswith('cr_') and n not in hdr_names)
    pre, body = t[:first_body], t[first_body:]
    # crossing lemmas in the preamble that are missing
    add = []
    for m in re.finditer(r'^Lemma\s+(cr_[A-Za-z0-9_]+).*?Qed\.', pre, re.S | re.M):
        if m.group(1) not in hdr_names: add.append(m.group(0))
    clash = defined(body) & defined(acc)
    assert not clash, f'name clash: {sorted(clash)[:5]}'
    acc += '\n(* ===== from %s ===== *)\n' % g + '\n'.join(add) + '\n' + body.strip() + '\n'
open(out, 'w', newline='\n').write(acc)
print('written', out, len(acc), 'bytes')
