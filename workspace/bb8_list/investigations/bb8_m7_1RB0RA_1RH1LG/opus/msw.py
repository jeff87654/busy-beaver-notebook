"""Literal words of the milestones and reach checks."""
import sys, subprocess
def M(name, b):
    T = '111001'
    if name == 'M0': return '101' * 13 + '1010' + '101010' * b + T
    if name == 'M1': return '101' * 13 + '1' + '1010' + '10' * (6 * b) + '0' + T
    if name == 'M2': return '10' * 4 + '10' * (6 * b) + '0' + '111' + '001' * 14
    if name == 'M3': return '1010' + '111' + '001' * (12 * b + 8) + '1' * 39 + '001001'
    if name == 'M4': return '1010' + '111' + '001' * (12 * b + 7) + '0' + '1111' + '000111' * 5 + '00110' + '111111' + '001001'
def reach(a, t, maxs=10**9):
    out = subprocess.run(['./reach.exe', a, t, 'B', str(maxs)], capture_output=True, text=True).stdout.strip()
    return out
if __name__ == '__main__':
    seq = sys.argv[1].split(',')
    for b in range(int(sys.argv[2]), int(sys.argv[3])):
        print(b, [reach(M(seq[k], b), M(seq[k + 1], b)) for k in range(len(seq) - 1)])
