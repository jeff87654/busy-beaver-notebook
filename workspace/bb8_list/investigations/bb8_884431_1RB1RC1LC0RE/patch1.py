p='coqgen.py'
s=open(p).read()
old1 = """    ops, C, how = engine.run_until_stuck(step, None, target=expect)
    if how != 'target':
        raise GenFail('framed round does not return to the loop shape (%s at %s)' % (how, pl.show(C)))"""
new1 = """    ops, C, how = engine.run_until_stuck(step, None, target=expect)
    round_text = ''
    if how != 'target':
        if gen is None:
            raise GenFail('framed round does not return to the loop shape (%s at %s)' % (how, pl.show(C)))
        # the round contains inner loops: prove it as a separate lemma by the explorer (nested loops)
        tree = engine.explore(step, expect, 1, 4)
        rname = name + '_round'
        round_text = rule_lemma(rname, step, expect, tree, gen, progress=False)
        rc, rv = free_vars(step, expect)
        ops = None"""
print(old1 in s)
s = s.replace(old1, new1)
old2 = """    tac = ['induction j; intros.', '- simpl. finish_norm.', '- simpl.'] + ops_to_tactics(ops) + \
          ['try align_tape.', 'follow (IHj %s).' % ' '.join(ih_args)] + shifts + ['finish_norm.']
    text = helpers + 'Lemma %s : %s.\nProof.\n%s\nQed.\n' % (name, stmt, wrap(tac))"""
new2 = """    first = ['follow (%s %s).' % (rname, ' '.join(rc + rv))] if ops is None else ops_to_tactics(ops)
    tac = ['induction j; intros.', '- simpl. finish_norm.', '- simpl.'] + first + \
          ['try align_tape.', 'follow (IHj %s).' % ' '.join(ih_args)] + shifts + ['finish_norm.']
    text = helpers + round_text + 'Lemma %s : %s.\nProof.\n%s\nQed.\n' % (name, stmt, wrap(tac))"""
print(old2 in s)
s = s.replace(old2, new2)
s = s.replace("def loop_lemma(name, lp, engine):", "def loop_lemma(name, lp, engine, gen=None):")
s = s.replace("text, info = loop_lemma(nm, lp, self.engine)", "text, info = loop_lemma(nm, lp, self.engine, self)")
open(p,'w').write(s)
