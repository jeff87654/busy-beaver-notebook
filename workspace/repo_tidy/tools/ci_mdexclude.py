"""Rewrite coq.yml's paths filters for predicate-quantifier 'every' with a '!**/*.md' exclusion.

usage: python ci_mdexclude.py path/to/coq.yml
Each filter's list of globs (a union under the default 'some') becomes one brace pattern '{g1,g2,...}' (picomatch
brace expansion: the same union) followed by '!**/*.md'.
"""
import re, sys, yaml
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
m = re.search(r"( +)filters: \|\n((?:\1  .*\n|\n)+)", s)
ind = m.group(1)
block = m.group(2)
filters = yaml.safe_load(block)
out = []
for name, globs in filters.items():
    union = globs[0] if len(globs) == 1 else '{' + ','.join(globs) + '}'
    out.append(f"{ind}  {name}:\n{ind}    - '{union}'\n{ind}    - '!**/*.md'\n")
new_block = ''.join(out)
head = (f"{ind}predicate-quantifier: 'every'\n"
        f"{ind}# With 'every', a file selects a filter only if it matches every line of it: the first line is the\n"
        f"{ind}# entry's paths (a {{a,b,...}} brace pattern is their union) and '!**/*.md' leaves out documentation, so a\n"
        f"{ind}# change to .md files alone selects no job (no step a job runs reads a .md file).\n")
s = s[:m.start()] + head + f"{ind}filters: |\n" + new_block + s[m.end():]
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
