"""python wrapper for lsim.exe (verifier's literal simulator)."""
import subprocess, os
HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, 'lsim.exe')
TAIL44 = '10110101010101010010000010111100100100100100'
SUF = '1010'
def D(m): return '10' * m + '1'
def word_of(toks): return ''.join(D(m) for m in toks)
def rle(v):
    out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]: j += 1
        out.append(f'{v[i]}^{j-i}' if j - i > 1 else str(v[i])); i = j
    return ' '.join(out)
def parse_k(word):
    """word ends with ...1 + '101' (SUF minus last 0).  returns (far, tokens farthest-first incl. a, r)"""
    assert word.endswith('1101'), word[-10:]
    p = len(word) - 4       # the 1 before the suffix 1010
    toks = []
    while p >= 0 and word[p] == '1':
        mm = 0; p -= 1
        while p >= 1 and word[p] == '0' and word[p - 1] == '1':
            mm += 1; p -= 2
        toks.append(mm)
    return word[:p + 1].rstrip('0') if False else word[:p + 1], toks[::-1]
def run(M, word, maxs=10**10, kmode=0, head=None, state='G', target=None):
    head = len(word) if head is None else head
    job = f'{M} {state} {head} {int(maxs)} {kmode}\n{word}\n'
    if kmode == -1:
        job += f'{len(target)} ' + ' '.join(map(str, target)) + '\n'
    p = subprocess.run([EXE], input=job, capture_output=True, text=True, creationflags=0x40)
    l1, l2 = p.stdout.strip().split('\n')[:2]
    f = l1.split()
    info = {'res': f[0], 'steps': int(f[1]), 'qs': f[2], 'line': l1}
    for x in f[3:]:
        if x.startswith('lo='): info['lo'] = int(x[3:])
        if x.startswith('wordstart='): info['ws'] = int(x[10:])
        if x.startswith('head='): info['head'] = int(x[5:])
        if x.startswith('ones='): info['ones'] = int(x[5:])
    info['word'] = l2
    if f[0] == 'K':
        info['far'], info['toks'] = parse_k(l2)
    return info
