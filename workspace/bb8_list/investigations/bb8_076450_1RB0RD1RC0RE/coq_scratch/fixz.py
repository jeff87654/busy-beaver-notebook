s = open('body23p.v.in').read()
old_start = s.index('Lemma Zp')
old_end = s.index('Qed.', old_start) + 4
new = '''Lemma Zp : forall p, const 0 {{A}}> 0 >> 1 >> 1 >> 1 >> [1;1]^^p *> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 0 >> 1 >> const 0 -->+
  const 0 {{A}}> 0 >> 1 >> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> 0 >> [0;0]^^p *> 1 >> 1 >> 1 >> const 0.
Proof. intros. start_progress. follow cr_GR. execute. follow cr_DL. do 6 step. finish_norm. Qed.'''
s = s[:old_start] + new + s[old_end:]
open('body23p.v.in', 'w').write(s)
t = open('body4.v.in').read()
t = t.replace('  follow (Oiter a 1). Show. do 2 rewrite <- ones2_S.\n', '  follow (Oiter a 1).\n')
open('body4.v.in', 'w').write(t)
