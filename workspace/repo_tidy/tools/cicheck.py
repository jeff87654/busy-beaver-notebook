"""Check that the GitHub workflows refer to existing paths.

usage: python cicheck.py REPO_ROOT
- every `working-directory:` exists;
- every dorny/paths-filter glob matches at least one tracked file;
- every repo path named in a `run:` script (BBn/..., PA/..., ZF/...) exists, after expanding `${{ matrix.x }}`
  over the job's matrix and `for f in a b c` loops; generated outputs (logs, .vo, _logs/) are skipped;
- every job named in `changes.outputs` has a filter, and every filter output used by a job's `if:` exists.
"""
import fnmatch, os, re, subprocess, sys
import yaml

root = os.path.abspath(sys.argv[1])
tracked = subprocess.run(['git', '-C', root, 'ls-files'], capture_output=True, text=True, check=True).stdout.split('\n')
tracked = [t for t in tracked if t]
dirs = set()
for t in tracked:
    parts = t.split('/')
    for i in range(1, len(parts)):
        dirs.add('/'.join(parts[:i]))

def expand_braces(g):
    m = re.search(r'\{([^{}]*)\}', g)
    if not m:
        return [g]
    return [x for alt in m.group(1).split(',') for x in expand_braces(g[:m.start()] + alt + g[m.end():])]

def glob_match(g):
    if g.startswith('!'):
        excl = set(glob_match(g[1:]))
        return [t for t in tracked if t not in excl]
    if '{' in g:
        out = set()
        for e in set(expand_braces(g)):
            n = glob_match_one(e)
            if not n:
                print('ERROR brace alternative', e, 'matches no tracked file')
            out |= set(n)
        return sorted(out)
    return glob_match_one(g)

def glob_match_one(g):
    # paths-filter uses picomatch; '**' spans directories
    rx = re.escape(g).replace(r'\*\*/', '(?:.*/)?').replace(r'\*\*', '.*').replace(r'\*', '[^/]*')
    r = re.compile('^' + rx + '$')
    return [t for t in tracked if r.match(t)]

def exists(p):
    p = p.rstrip('/')
    return p in dirs or p in tracked

GEN = re.compile(r'(\.log$|\.vo$|_logs|compile_ci|probe_ci|check_ci|check_\d+)')
PATH = re.compile(r'(?<![\w/.$-])((?:BB\d+|PA|ZF)/[A-Za-z0-9_./${}\- ]*?)(?=[\s"\'`;)|]|$)')
bad = 0
def err(msg):
    global bad
    bad += 1
    print('ERROR', msg)

for wf in sorted(os.listdir(os.path.join(root, '.github/workflows'))):
    path = os.path.join(root, '.github/workflows', wf)
    doc = yaml.safe_load(open(path, encoding='utf-8'))
    jobs = doc.get('jobs', {})
    filters = {}
    for jn, job in jobs.items():
        for st in job.get('steps', []):
            if 'paths-filter' in str(st.get('uses', '')):
                filters = yaml.safe_load(st['with']['filters'])
                for name, globs in filters.items():
                    for g in globs:
                        n = len(glob_match(g))
                        if g.startswith('.github') and n:
                            continue
                        if n == 0:
                            err(f'{wf}: filter {name}: glob {g!r} matches no tracked file')
                        else:
                            print(f'ok  {wf}: filter {name}: {g} ({n} files)')
        if jn == 'changes':
            for out, val in job.get('outputs', {}).items():
                m = re.search(r'steps\.f\.outputs\.([\w-]+)', val)
                if m and m.group(1) not in filters:
                    err(f'{wf}: changes.outputs.{out} refers to missing filter {m.group(1)}')
    for jn, job in jobs.items():
        cond = str(job.get('if', ''))
        for m in re.finditer(r'needs\.changes\.outputs\.([\w-]+)', cond):
            if m.group(1) != 'all' and m.group(1) not in jobs.get('changes', {}).get('outputs', {}):
                err(f'{wf}: job {jn} uses undefined output {m.group(1)}')
        matrix = (job.get('strategy') or {}).get('matrix') or {}
        def expand(s):
            outs = [s]
            for k, vals in matrix.items():
                if isinstance(vals, list):
                    outs = [o.replace('${{ matrix.%s }}' % k, str(v)) for o in outs for v in vals]
            return outs
        defaults_wd = None
        for st in job.get('steps', []):
            wd = st.get('working-directory')
            for w in expand(wd) if wd else []:
                if not exists(w):
                    err(f'{wf}: job {jn}: working-directory {w} missing')
                else:
                    print(f'ok  {wf}: job {jn}: working-directory {w}')
            run = st.get('run')
            if not run:
                continue
            # for-loops: for f in a b c; do ... $f ...
            loops = re.findall(r'for (\w+) in ([^;\n]+);', run)
            for line in run.split('\n'):
                for cand in PATH.findall(line):
                    cand = cand.strip()
                    if GEN.search(cand):
                        continue
                    variants = expand(cand)
                    for var, vals in loops:
                        if '$' + var in cand:
                            variants = [v.replace('$' + var, x) for v in variants for x in vals.split()]
                    for v in variants:
                        if '$' in v or '{' in v:
                            continue
                        base = v
                        if wd:
                            pass
                        if not exists(base):
                            err(f'{wf}: job {jn}: path {base} missing (from {cand!r})')
                        else:
                            print(f'ok  {wf}: job {jn}: path {base}')
            # relative paths of scripts run inside working-directory
            if wd:
                for w in expand(wd):
                    for m in re.finditer(r'(?:bash|python3(?: -I)?(?: -B)?)\s+(\./)?([\w./-]+\.(?:sh|py|v))', run):
                        p = w + '/' + m.group(2)
                        if not exists(p):
                            err(f'{wf}: job {jn}: script {p} missing')
                        else:
                            print(f'ok  {wf}: job {jn}: script {p}')
                    for m in re.finditer(r'coqc [^\n|]*?\s([\w./-]+\.v)\b', run):
                        p = os.path.normpath(w + '/' + m.group(1)).replace(os.sep, '/')
                        if not exists(p):
                            err(f'{wf}: job {jn}: coq file {p} missing')
                        else:
                            print(f'ok  {wf}: job {jn}: coq file {p}')
print(f'{bad} problems')
sys.exit(1 if bad else 0)
