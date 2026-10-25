"""Expand a run-length tape description into a 0/1 word.
  python rle.py "111 (01)^7 1 0 11 1^5 0^3"   -> word
Tokens: literal 0/1 strings, (w)^k, c^k, and [Q] marking the head before the next cell (printed with --head)."""
import re
import sys


def expand(desc):
    word = ''
    head = None
    state = None
    for tok in desc.split():
        m = re.fullmatch(r'\[([A-Z])\](.*)', tok)
        if m:
            head = len(word)
            state = m.group(1)
            tok = m.group(2)
            if not tok:
                continue
        m = re.fullmatch(r'\(([01]+)\)\^(\d+)', tok)
        if m:
            word += m.group(1) * int(m.group(2))
            continue
        m = re.fullmatch(r'([01])\^(\d+)', tok)
        if m:
            word += m.group(1) * int(m.group(2))
            continue
        assert re.fullmatch(r'[01]+', tok), tok
        word += tok
    return word, head, state


if __name__ == '__main__':
    w, h, q = expand(sys.argv[1])
    print(w, h if h is not None else len(w), q or 'B')
