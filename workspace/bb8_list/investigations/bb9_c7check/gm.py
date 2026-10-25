# gm.py: run c7m90 (exact block-macro simulator) from Kt starts to the first CL moment or halt; one line per start.
import idle, subprocess, sys, re
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_c7check\c7m90f.exe'
C7 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_1LC0RA'
def run(kt, machine=C7, maxs='1.8e19', nocl=0):
    p = subprocess.run([EXE, machine, '--kt', kt, '--maxs', maxs, '--nocl', str(nocl)], capture_output=True, text=True, creationflags=0x40)
    L = p.stdout.splitlines()
    if not L: return {'kind': 'ERR', 'raw': p.stderr}
    if L[0].startswith('J CL'):
        d = dict(kv.split('=') for kv in L[0].split()[2:])
        return {'kind': 'CL', 'r_in': int(d['r_in']), 't': int(d['t']), 'k': int(d['k']), 'X': int(d['X']), 'C': int(d['C']), 'step': int(d['step']),
                'ctx': L[1][4:], 'view': L[2][5:]}
    if L[0].startswith('HALT'):
        d = dict(kv.split('=') for kv in L[0].split()[2:])
        return {'kind': 'HALT', 'state': L[0].split()[1], 'step': int(d['step']), 'ones': int(d['ones']), 'tape': L[1].strip()[6:]}
    return {'kind': 'OTHER', 'raw': L[0]}
if __name__ == '__main__':
    for kt in sys.argv[1:]:
        r = run(kt)
        if r['kind'] == 'CL': print(kt, '=> CL t=%d | %s' % (r['t'], r['view']), flush=True)
        elif r['kind'] == 'HALT': print(kt, '=> HALT %s ones=%d | %s' % (r['state'], r['ones'], r['tape'][:300]), flush=True)
        else: print(kt, '=>', r, flush=True)
