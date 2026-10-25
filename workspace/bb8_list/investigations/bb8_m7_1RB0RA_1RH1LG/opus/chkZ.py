import subprocess
def reachL(w, hp, q, t, thp, qt, N=10**8):
    return subprocess.run(['./reachL.exe', w, str(hp), q, t, str(thp), qt, str(N)], capture_output=True, text=True).stdout.strip()
def Z(x, k): return '0' + '01' * x + '00' + '101' * k + '100' * 13 + '101'
bad = 0
for x in range(0, 9):
    for k in range(0, 10):
        r = reachL(Z(x + 1, k), 0, 'B', Z(x, k + 2), 0, 'B')
        if not r.startswith('REACHED'): bad += 1; print('round', x, k, r)
print('round bad', bad)
for k in range(1, 12):
    t = '1010111' + '001' * (k - 1) + '1' * 39 + '001001'
    print('fin', k, reachL(Z(0, k), 0, 'B', t, len(t), 'B'))
