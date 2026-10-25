"""Probe: start 0^inf A>0 <word>, run to the next left-edge A0 config; print result compressed."""
import sys
from nextA import from_word, word_of
from lit import rle, MAIN
def go(w, tm=MAIN, maxsteps=10**7):
    r, s = from_word(w, tm=tm, maxsteps=maxsteps)
    return r, s.steps, (rle(word_of(s)) if r == 'A0' else s.show())
if __name__ == '__main__':
    for w in sys.argv[1:]:
        print(w, *go(w))
