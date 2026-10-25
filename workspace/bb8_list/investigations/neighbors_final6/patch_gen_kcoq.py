"""One-off patch of neighbors_family_tools/gen_kcoq.py: halting-boundary offset h and split rebuild.
Run from neighbors_family_tools/.  Each replaced snippet must occur exactly once."""
p = 'gen_kcoq.py'
s = open(p).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, n, old)
    s = s.replace(old, new)


rep('''Compile and check with ..\\\\..\\\\proofs\\\\check.py (copy OUT.v there first).
"""''', '''Compile and check with ..\\\\..\\\\proofs\\\\check.py (copy OUT.v there first).

Two generalizations (added in ../neighbors_final6.md; with neither, the output is byte-identical to before):
 - halting-boundary offset h = (m - 3) - ch >= 0 (fit H: k = m b + ch).  h = 1 means the machine's left
   crossing needs a run of >= 4 ones (LOOP/FINAL get h extra concrete 1s, END4b starts from 1^(2+h) C>), and a
   run of exactly 3 at FINAL is the halting reset k = m b + m - 4.  R3 then needs k <= m b + m - 4 - h.
 - split rebuild: if R4 fits K(;0;b) -> K(P, 1^(m b + c4); a4; b4) only for b >= 2 (kfit reports 'no fit'),
   Top B is the raw END4b output, and TopZ splits B = 0 (the literal b = 1 rebuild, checked to have nonzero
   digits) from B = S B' (the fitted form).
"""''')

rep('''def fit_end4(tm):
    res = {}
    for i in range(3, 9):
        w = '11' + '0' + '10' * i
        s = Sim.from_word(tm, '0000' + w, 6, 'C')''', '''def fit_end4(tm, h=0):
    res = {}
    for i in range(3, 9):
        w = '1' * (2 + h) + '0' + '10' * i
        s = Sim.from_word(tm, '0000' + w, 6 + h, 'C')''')

rep('''def coq_list(ds_top_first):''', '''def fit_r4_split(tm, N=10 ** 6):
    """R4 fitted on b = 2..6 only: returns (P, m4, c4, a4, b4, (ds1, a1, b1)) where (ds1, a1, b1) is the
    literal successor of K(;0;1), or None."""
    from kfam import run_next
    from kfit import lin_fit
    o = {b: run_next(tm, (), 0, b, N=N) for b in range(1, 7)}
    if any(v[0] != 'K' for v in o.values()):
        return None
    fits = {}
    for b in range(2, 7):
        ds, a0, b0 = o[b][2]
        n = 0
        while n < len(ds) and ds[len(ds) - 1 - n] == 1:
            n += 1
        fits[b] = (tuple(ds[:len(ds) - n]), n, a0, b0)
    pref = set((x[0], x[2], x[3]) for x in fits.values())
    if len(pref) != 1:
        return None
    f = lin_fit({b: x[1] for b, x in fits.items()})
    if not f:
        return None
    P, a4, b4 = pref.pop()
    return P, f[0], f[1], a4, b4, o[1][2]


def coq_list(ds_top_first):''')

rep('''    P, raw = fit(tm)
    need = ['m1', 'c1', 'm2', 'c2', 'b2', 'm3', 'c3', 'a3', 'b3', 'mh', 'ch', 'm4', 'c4', 'P', 'a4', 'b4']
    miss = [k for k in need if k not in P]
    if miss:
        raise SystemExit('rules do not fit (missing %s)' % miss)
    m = P['m1']
    tmpl = dict(m1=m, c1=m, m2=m, c2=m - 1, b2=1, m3=m, c3=m - 1, a3=1, b3=1, mh=m, ch=m - 3, m4=m)
    bad = [(k, P[k], v) for k, v in tmpl.items() if P[k] != v]
    if bad or m < 2 or P['b4'] < 1 or any(d == 0 for d in P['P']):
        raise SystemExit('not the m-template: %r (m=%d, R4 %r)' % (bad, m, (P['P'], P['a4'], P['b4'])))
    u, s = fit_end4(tm)''', '''    P, raw = fit(tm)
    split = None
    if 'm4' not in P:
        r = fit_r4_split(tm)
        if r is not None:
            P['P'], P['m4'], P['c4'], P['a4'], P['b4'], split = r
            print('R4 fits only for b >= 2; b = 1 rebuild: K(%s; %d; %d)' % split, file=sys.stderr)
    need = ['m1', 'c1', 'm2', 'c2', 'b2', 'm3', 'c3', 'a3', 'b3', 'mh', 'ch', 'm4', 'c4', 'P', 'a4', 'b4']
    miss = [k for k in need if k not in P]
    if miss:
        raise SystemExit('rules do not fit (missing %s)' % miss)
    m = P['m1']
    h = (m - 3) - P['ch']
    tmpl = dict(m1=m, c1=m, m2=m, c2=m - 1, b2=1, m3=m, c3=m - 1, a3=1, b3=1, mh=m, m4=m)
    bad = [(k, P[k], v) for k, v in tmpl.items() if P[k] != v]
    if bad or m < 2 or P['b4'] < 1 or any(d == 0 for d in P['P']) or not 0 <= h <= 1 or 2 * m - 4 - h < 0:
        raise SystemExit('not the m-template: %r (m=%d, h=%d, R4 %r)' % (bad, m, h, (P['P'], P['a4'], P['b4'])))
    if split is not None and (P['b4'] < 1 or any(d == 0 for d in split[0]) or split[2] < 1
                              or 2 * m + P['c4'] < 0):
        raise SystemExit('split rebuild not usable: %r' % (split,))
    if h:
        print('halting boundary offset h = %d: R3 needs k <= %db%+d' % (h, m, m - 4 - h), file=sys.stderr)
    u, s = fit_end4(tm, h)''')

rep('''    ph = phases(m)
    left_end4 = [1, 0] * s + T10 + [int(c) for c in reversed(u)] + [BLANK]
    ph['END4b'] = (('C', [1, 1, 0, BLANK], [0] + T10 + [BLANK], '>'), ('B', left_end4, [BLANK], '>'))''',
    '''    ph = phases(m, h)
    left_end4 = [1, 0] * s + T10 + [int(c) for c in reversed(u)] + [BLANK]
    ph['END4b'] = (('C', [1] * (2 + h) + [0, BLANK], [0] + T10 + [BLANK], '>'), ('B', left_end4, [BLANK], '>'))''')

rep('''            stmt = ('forall i, (1 >> 1 >> 0 >> const 0) {{C}}> 0 >> [1;0]^^i *> const 0 -->+ '
                    '(%s) {{B}}> const 0' % end4_coq)
        else:
            stmt = coq_stmt(pname, m)''', '''            stmt = ('forall i, (%s0 >> const 0) {{C}}> 0 >> [1;0]^^i *> const 0 -->+ '
                    '(%s) {{B}}> const 0' % ('1 >> ' * (2 + h), end4_coq))
        else:
            stmt = coq_stmt(pname, m, h)''')

rep('''    ctop = m + P['c4']
    if ctop < 0:
        raise SystemExit('Top needs b*m + %d ones' % ctop)
    top_digits = ','.join(str(d) for d in P['P'])''', '''    ctop = m + P['c4']
    if ctop < 0 and split is None:
        raise SystemExit('Top needs b*m + %d ones' % ctop)
    top_digits = ','.join(str(d) for d in P['P'])
    hv = h_values(m, h)
    if split is None:
        hv.update(r4_end='rewrite lft_ones. finish_norm.',
                  top_def='Kc (repeat 1%%nat (B * %d + %d) ++ %s) %d %d' % (m, ctop, tail, P['a4'], P['b4']),
                  topz_proof='Proof. intros. unfold Top. apply GEN. apply Forall_top. Qed.')
    else:
        ds1, a1, b1 = split
        ctopS = 2 * m + P['c4']
        hv.update(r4_end='finish_norm.',
                  top_def='(%s) {{B}}> const 0' % end4_coq.replace('^^i ', '^^(B * %d + %d) ' % (m, hv['cl4'])),
                  topz_proof=NL.join([
                      "Proof.",
                      "  intros. destruct B as [| B].",
                      "  - assert (E : Top 0 -->* Kc %s %d %d) by (unfold Top, Kc; simpl; finish)."
                      % (coq_list(ds1), a1, b1),
                      "    destruct (GEN %s %d %d) as [k [B' H1]]." % (coq_list(ds1), a1, b1 - 1),
                      "    { repeat (apply Forall_cons; [lia |]). apply Forall_nil. }",
                      "    exists k, B'. eapply evstep_trans; [exact E | exact H1].",
                      "  - assert (E : Top (S B) -->* Kc (repeat 1%%nat (B * %d + %d) ++ %s) %d %d)"
                      % (m, ctopS, tail, P['a4'], P['b4']),
                      "      by (unfold Top, Kc; rewrite lft_ones; finish_norm).",
                      "    destruct (GEN (repeat 1%%nat (B * %d + %d) ++ %s) %d %d (Forall_top _)) as [k [B' H1]]."
                      % (m, ctopS, tail, P['a4'], P['b4'] - 1),
                      "    exists k, B'. eapply evstep_trans; [exact E | exact H1].",
                      "Qed."]))''')

rep('''        top_comment='Kc (1^(%d b0 + %d) ++ %s) %d %d (digits %s,1,...,1)' % (m, ctop, tail, P['a4'], P['b4'], top_digits),''',
    '''        top_comment=('Kc (1^(%d b0 + %d) ++ %s) %d %d (digits %s,1,...,1)' % (m, ctop, tail, P['a4'], P['b4'], top_digits)
                     if split is None else
                     'the END4b output; Top 0 = Kc %s %d %d, Top (S b0) = Kc (1^(%d b0 + %d) ++ %s) %d %d'
                     % (coq_list(split[0]), split[1], split[2], m, 2 * m + P['c4'], tail, P['a4'], P['b4'])),''')

rep('''        ds0=coq_list(ds0), a0=a0, b0=b0, b0m1=b0 - 1, nsteps=nsteps)''',
    '''        ds0=coq_list(ds0), a0=a0, b0=b0, b0m1=b0 - 1, nsteps=nsteps, **hv)''')

rep('''def gen(tm, outp, title=None, report=None):''', '''def h_values(m, h):
    """Template strings that depend on the halting-boundary offset h (h = 0 reproduces the old text)."""
    return dict(
        l2=2 + h, l3=3 + h, l4=4 + h, e4s=' '.join(['1'] * (2 + h)),
        cfin=2 * m - 3 - h, cres=2 * m - 4 - h, cl4=2 * m - 2 - h,
        extra_lemmas='' if h == 0 else (
            'Lemma ones4 : forall n r X, n = 4 + r -> [1]^^n *> X = 1 >> 1 >> 1 >> 1 >> [1]^^r *> X.' + NL
            + 'Proof. intros. subst n. reflexivity. Qed.' + NL),
        Sr='S (S r)' if h == 0 else 'S (S (S r))',
        Sjr='S (S (S (j + r)))' if h == 0 else 'S (S (S (S (j + r))))',
        loops_rw=('rewrite (ones2 (j + S (S r)) (j + r)) by lia.' if h == 0
                  else 'rewrite <- (ones3 (j + S (S (S r))) (j + r)) by lia.'),
        r1_ones='ones3' if h == 0 else 'ones4',
        S3r='S (S (S r))' if h == 0 else 'S (S (S (S r)))',
        S2z='S (S 0)' if h == 0 else 'S (S (S 0))',
        wS='S (S ' if h == 0 else 'S (S (S ', wE='))' if h == 0 else ')))')


def gen(tm, outp, title=None, report=None):''')

rep('''import os
import sys
HERE''', '''import os
import sys
NL = chr(10)
HERE''')
open(p, 'w', newline='\n').write(s)
print('gen ok')
