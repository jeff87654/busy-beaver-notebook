"""Wade's axiom-order hill climb (zf2.py __main__ loop, unchanged logic) applied to zf2s at IDLE priority.
usage: python hillclimb.py START(wade|identity) [variant-json] [maxminutes]
Logs to hc_<start>.log, writes best order to hc_<start>.json after every improvement."""
import sys, os, json, time, ctypes
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:
    pass
import zf2s
startname = sys.argv[1] if len(sys.argv) > 1 else 'wade'
variant = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
maxmin = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9
n = len(zf2s.ZF2S(variant).axioms())
axiomorder = list(zf2s.WADE_ORDER) if startname == 'wade' else list(range(n))
log = open(f'hc_{startname}.log', 'a'); t0 = time.time(); builds = 0
def total(order):
    global builds
    builds += 1
    return zf2s.count(zf2s.build(order, variant))[2]
def save(note):
    json.dump({'order': axiomorder, 'states': state_count, 'variant': variant, 'builds': builds,
               'minutes': (time.time() - t0) / 60, 'note': note}, open(f'hc_{startname}.json', 'w'))
state_count = total(axiomorder)
print('start', axiomorder, state_count, file=log, flush=True); save('start')
changed = True; timeout = False
while changed and not timeout:
    changed = False
    for mid in range(1, len(axiomorder)):
        for left in range(mid):
            for right in range(mid + 1, len(axiomorder) + 1):
                neworder = axiomorder[:left] + axiomorder[mid:right] + axiomorder[left:mid] + axiomorder[right:]
                if neworder[-1] != 0 and neworder[-1] != 1:
                    new_count = total(neworder)
                    if new_count < state_count:
                        axiomorder = neworder; state_count = new_count; changed = True
                        print(f'{(time.time()-t0)/60:7.1f} min builds {builds}: {state_count} {axiomorder}', file=log, flush=True)
                        save('improved')
            if (time.time() - t0) / 60 > maxmin:
                timeout = True; break
        if timeout: break
    print(f'{(time.time()-t0)/60:7.1f} min: pass done, changed={changed}', file=log, flush=True)
save('timeout' if timeout else 'converged')
print('optimized axiom order:', axiomorder, state_count, 'timeout' if timeout else 'converged', file=log, flush=True)
