s=open('planner8.py').read()
old="""            cfg = step(cfg)
            n += 1; total += 1"""
new="""            try:
                cfg = step(cfg)
            except Halted:
                script.append(('halt', n))
                return script, cfg
            n += 1; total += 1"""
assert old in s
open('planner8.py','w').write(s.replace(old,new))
