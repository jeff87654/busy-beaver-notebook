import idle, sys, re
# filter ms output: print a line only when its shape (block symbols, no counts, no head) differs from the last printed
last = None; n = 0
for ln in sys.stdin:
    if not ln.startswith('T '): print(ln.rstrip()); continue
    body = ln[ln.index('|') + 1:]
    shape = re.sub(r'\^\d+', '', body).replace('[', '').replace(']', '')
    shape = re.sub(r'(\b[01]+\b)( \1\b)+', r'\1', shape)
    if shape != last:
        print(ln.rstrip()[:int(sys.argv[1]) if len(sys.argv) > 1 else 250]); n += 1
    last = shape
