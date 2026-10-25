"""Group 'pfx1': just PFX37_0 (for fast wiring-tactic iteration)."""
import pickle
S,T,tree=pickle.load(open('tree_pfx_37_0.pkl','rb'))
ITEMS=[('PFX37_0', S, T, dict(splits=0), ())]
