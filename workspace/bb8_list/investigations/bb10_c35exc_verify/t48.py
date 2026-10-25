from tower import tower_res
N = 54305848396800
t = tower_res(2 * N)          # stable tower residue mod 2N
y = (3 * t - 8) % (2 * N)     # accumulator token after a standard (depth >= 2) clearing
R = ((y - 4) % (2 * N)) // 2
print('their universal R:', 49612750485498, ' mine (y = 2R+4, y = 3*tau-8):', R % N, R % N == 49612750485498)
