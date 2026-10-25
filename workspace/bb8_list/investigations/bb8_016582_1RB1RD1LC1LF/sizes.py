# Z n has tail 4(n+1); Z n -->+ Z (10*4^n - 3)
n=1
for i in range(3):
    print(i, 'n =', n if n<10**40 else 'huge', 'tail', 4*(n+1) if n<10**40 else '')
    if n>200: break
    n=10*4**n-3
