"""Group 'pfx': entry-prefix lemmas PFX<key>_<E> = D0f(key+1) -> pre-ESC Kt (class-b keys 37/43/49, E=0..5).
Loads the trees captured by try_prefix2.py (tree_pfx_<key>_<E>.pkl)."""
import pickle
ITEMS=[]
for KEY in (37,43,49):
    for E in range(6):
        S,T,tree=pickle.load(open('tree_pfx_%d_%d.pkl'%(KEY,E),'rb'))
        ITEMS.append(('PFX%d_%d'%(KEY,E), S, T, dict(splits=0), ()))
