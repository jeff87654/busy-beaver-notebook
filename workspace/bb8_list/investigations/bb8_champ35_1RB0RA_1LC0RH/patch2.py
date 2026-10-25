s=open('gen35.py').read()
s=s.replace("""            else:
                out.append('do %d step.' % op[1])
            first = False""","""            else:
                if op[1] > 0:
                    out.append('do %d step.' % op[1])
            first = False""")
s=s.replace("""        else:
            stmt = 'forall %s, %s -->+ %s' % (' '.join(nm), cfg2coq(st), cfg2coq(tg))
            if len(script) == 1""","""        elif script[0] == ('steps', 0):
            stmt = 'forall %s, %s -->* %s' % (' '.join(nm), cfg2coq(st), cfg2coq(tg))
            tac = tac_of(script, False)
            body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (name, stmt) + wrap(tac) + 'Qed.\n'
        else:
            stmt = 'forall %s, %s -->+ %s' % (' '.join(nm), cfg2coq(st), cfg2coq(tg))
            if len(script) == 1""")
open('gen35.py','w').write(s)
