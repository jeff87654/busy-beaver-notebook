"""Check that every relative link in every .md file of a repo resolves (files, directories, #anchors).

usage: python linkcheck.py REPO_ROOT [--all]   (--all also checks vendored trees)
"""
import os, re, sys, unicodedata

root = os.path.abspath(sys.argv[1])
check_vendor = '--all' in sys.argv
LINK = re.compile(r'(?<!\!)\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)|!\[[^\]]*\]\(\s*([^)\s]+)')
REF = re.compile(r'^\s*\[[^\]]+\]:\s*(\S+)', re.M)

def slug(h):
    h = h.strip().lower()
    h = re.sub(r'[`*_]', '', h) if False else h.replace('`', '')
    out = []
    for ch in h:
        if ch.isalnum() or ch in '-_':
            out.append(ch)
        elif ch == ' ':
            out.append('-')
        elif unicodedata.category(ch).startswith(('L', 'N', 'M')):
            out.append(ch)
    return ''.join(out)

def anchors(path):
    res, seen = set(), {}
    try:
        text = open(path, encoding='utf-8').read()
    except Exception:
        return res
    infence = False
    for line in text.splitlines():
        if line.lstrip().startswith('```'):
            infence = not infence
            continue
        if infence:
            continue
        m = re.match(r'^(#{1,6})\s+(.*?)\s*#*\s*$', line)
        if m:
            s = slug(m.group(2))
            n = seen.get(s, 0)
            seen[s] = n + 1
            res.add(s if n == 0 else f'{s}-{n}')
    for m in re.finditer(r'<a\s+(?:name|id)="([^"]+)"', text):
        res.add(m.group(1))
    return res

bad = 0
nfiles = nlinks = 0
for dp, dns, fns in os.walk(root):
    dns[:] = [d for d in dns if d != '.git' and (check_vendor or d != 'vendor')]
    for fn in fns:
        if not fn.endswith('.md'):
            continue
        p = os.path.join(dp, fn)
        nfiles += 1
        text = open(p, encoding='utf-8').read()
        # drop fenced code blocks and inline code
        text2 = re.sub(r'```.*?```', '', text, flags=re.S)
        text2 = re.sub(r'`[^`\n]*`', '', text2)
        targets = [a or b for a, b in LINK.findall(text2)] + REF.findall(text2)
        for t in targets:
            if re.match(r'^[a-z][a-z0-9+.-]*:', t, re.I):
                continue
            nlinks += 1
            path, _, anchor = t.partition('#')
            tgt = p if path == '' else os.path.normpath(os.path.join(dp, path))
            rel = os.path.relpath(p, root)
            if path.startswith('/'):
                print(f'ABSOLUTE {rel}: {t}'); bad += 1; continue
            if not os.path.exists(tgt):
                print(f'MISSING  {rel}: {t}'); bad += 1; continue
            if not os.path.realpath(tgt).startswith(root):
                print(f'OUTSIDE  {rel}: {t}'); bad += 1; continue
            if anchor and tgt.endswith('.md') and anchor not in anchors(tgt):
                print(f'ANCHOR   {rel}: {t}'); bad += 1
print(f'{nfiles} .md files, {nlinks} relative links, {bad} problems')
sys.exit(1 if bad else 0)
