import sys, zf2
ORDER=[16, 17, 3, 18, 4, 7, 8, 9, 11, 5, 12, 13, 14, 2, 15, 0, 1, 6, 10, 19]
def count(z):
    return len(set(s[0] for s in z.tm.states))
if __name__=='__main__':
    z=zf2.ZF2(); z.debug=False; z.AXIOMORDER=ORDER; z.build_machine()
    print(count(z))
    z.tm.save('rebuilt.tm') if hasattr(z.tm,'save') else None
