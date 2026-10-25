"""Concrete check of a generator item: python vcheck.py GROUP ITEM a=1,k=0,...  (uses validate.reaches on X')"""
import idle, sys, os
os.environ['ITEM'] = sys.argv[2]
import validate
mod = __import__('grp_' + sys.argv[1])
items = {it[0]: it for it in mod.ITEMS}
it = items[sys.argv[2]]
for spec in sys.argv[3:]:
    vals = {kv.split('=')[0]: int(kv.split('=')[1]) for kv in spec.split(',')}
    print(spec, validate.reaches(it[1], it[2], vals, max_steps=20_000_000))
