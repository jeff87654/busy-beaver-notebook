s = open('body23p.v.in').read()
blocks = s.split('\nLemma ')
res = blocks[0]
for b in blocks[1:]:
    name = b.split()[0]
    if name in ('Rp', 'Zp', 'Wp'):
        stmt, proof = b.split('Proof.', 1)
        stmt = stmt.replace('-->*', '-->+')
        stmt = stmt.replace('0 >> 1 >> [0;0]^^p *> 0 >> 0 >> 0 >> 0 >> 0 >>', '0 >> 1 >> 0 >> 0 >> 0 >> 0 >> 0 >> [0;0]^^p *>')
        proof = proof.replace('intros. execute.', 'intros. start_progress.', 1)
        b = stmt + 'Proof.' + proof
    res += '\nLemma ' + b
open('body23p.v.in', 'w').write(res)
