import re, glob, sys, os
from orbit import classify
P = int(sys.argv[1]) if len(sys.argv) > 1 else 4400
rows = {}
for f in glob.glob(f"sweep/*_P{P}.txt"):
    m = re.match(r"sweep/(f3|m8)_L(\d+)_P\d+\.txt", f.replace("\\", "/"))
    name, L0 = m.group(1), int(m.group(2))
    s = open(f).read()
    h = re.search(r"HALT (\S+) step=(\d+) .*?ones=(\d+) jumps=(\d+) .*?haltTokD=(\d+) leftcell=(\d)", s)
    h0z = s.count("H0L0")
    d0 = re.findall(r"D0 step=\d+ jumps=\d+ t=\d+ L=(\d+) P=(\d+)", s)
    keyobs = None
    for L, Pp in d0:
        if int(L) - 1 < 60: keyobs = (int(L) - 1, int(Pp)); break
    rows.setdefault(L0, {})[name] = (h.groups() if h else None, h0z, keyobs)
print("L0'   pred(key,rho)  obs_key P_key rho_obs | f3: halt ones d H0L0 | m8: halt ones d H0L0 | same_ones")
for L0 in sorted(rows):
    key, rho, Pk, orb = classify((3 * L0 - 100) // 5, P)
    r = rows[L0]
    def fmt(x):
        if x is None: return "-"
        h, z, ko = x
        return f"{h[0] if h else 'RUN'} {h[2] if h else '-'} d={h[4] if h else '-'} H0L0={z}" if h else f"RUN H0L0={z}"
    ko = (r.get("f3") or r.get("m8"))[2]
    rho_obs = (ko[1] - 35) % 5 if ko and ko[0] == 31 else None
    same = (r.get("f3") and r.get("m8") and r["f3"][0] and r["m8"][0] and r["f3"][0][2] == r["m8"][0][2])
    print(f"{L0:6d} ({key},{rho})  {ko} {rho_obs} | {fmt(r.get('f3'))} | {fmt(r.get('m8'))} | {same}")
