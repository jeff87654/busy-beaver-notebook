s=open('abs35.v').read()
s=s.replace("{ rewrite rev_app_distr. simpl. rewrite rev_rep. rewrite <- !app_assoc. reflexivity. }","{ rewrite rev_app_distr, rev_rep. cbn [rev]. rewrite <- !app_assoc. reflexivity. }")
s=s.replace("{ rewrite rev_app_distr. simpl. rewrite rev_rep. rewrite <- app_assoc. reflexivity. }","{ rewrite rev_app_distr, rev_rep. cbn [rev]. rewrite <- app_assoc. reflexivity. }")
open('abs35.v','w').write(s)
