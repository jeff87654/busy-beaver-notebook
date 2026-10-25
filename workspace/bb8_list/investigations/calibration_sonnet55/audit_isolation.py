"""Audit a subagent transcript for accesses outside its sandbox workspace.

  python audit_isolation.py <agent-transcript.jsonl> <workspace-dir>

Scans every tool_use input (commands, file paths, patterns) for absolute paths that are not under the workspace,
apart from the allowed executables (Coq, the base Python, msys2 g++). It also flags web and agent tools and any
mention of ~/.claude. It prints the model(s) seen, token usage totals and each flagged call.
"""
import json
import re
import sys
from collections import Counter

ALLOWED = [r'c:\coq-platform~8.20~2025.01', r'c:\msys64\ucrt64\bin', r'c:\users\jeffr\appdata\local\programs\python\python311',
           r'c:\users\jeffr\appdata\local\temp', r'c:\windows']
FORBIDDEN_TOOLS = {'WebFetch', 'WebSearch', 'Agent', 'SendMessage', 'Workflow'}
PATH_RE = re.compile(r'''(?i)(?:(?<![a-z0-9_])[cd]:[\\/]|(?<![a-z0-9_.])/[cd]/|~[\\/])[^\s"'`|;&<>*?]*''')


def norm(p):
    p = p.replace('/', '\\')
    m = re.match(r'(?i)^\\([a-z])\\(.*)$', p)
    if m:
        p = f'{m.group(1)}:\\{m.group(2)}'
    return p.lower().rstrip('\\')


def main():
    path, ws = sys.argv[1], norm(sys.argv[2])
    models, usage, flags, n_tools = Counter(), Counter(), [], 0
    for line in open(path, encoding='utf-8'):
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = rec.get('message') or {}
        if msg.get('model'):
            models[msg['model']] += 1
        for k, v in (msg.get('usage') or {}).items():
            if isinstance(v, int):
                usage[k] += v
        content = msg.get('content')
        if not isinstance(content, list):
            continue
        for c in content:
            if c.get('type') != 'tool_use':
                continue
            n_tools += 1
            name, inp = c.get('name'), json.dumps(c.get('input', {}))
            text = json.loads(json.dumps(inp)).replace('\\\\', '\\')
            why = []
            if name in FORBIDDEN_TOOLS:
                why.append(f'tool {name}')
            if re.search(r'(?i)\.claude', text):
                why.append('mentions .claude')
            for p in PATH_RE.findall(text):
                np_ = norm(p)
                if np_.startswith(ws) or any(np_.startswith(a) for a in ALLOWED) or np_ in ('c:', 'c:\\'):
                    continue
                if re.match(r'(?i)^[a-z]:\\?$', np_):
                    continue
                why.append(f'path {p}')
            if why:
                flags.append((name, sorted(set(why)), text[:300]))
    print('models:', dict(models))
    print('tool calls:', n_tools)
    print('usage totals:', dict(usage))
    print('flagged calls:', len(flags))
    for name, why, text in flags:
        print(f'- {name}: {"; ".join(why)}\n    {text}')


if __name__ == '__main__':
    main()
