import os, sys, json, glob, subprocess, time

M8_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_m8sweep"
OUR_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_nontemplate_guards"
OUT_DIR = os.path.join(OUR_DIR, "scr_x33")
os.makedirs(OUT_DIR, exist_ok=True)

WF = os.path.join(M8_DIR, "wf8.exe")
CREATE_FLAGS = 0x08000000 | 0x40  # CREATE_NO_WINDOW | IDLE_PRIORITY_CLASS

TARGETS = [
    ("X33",   "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE", 470),
    ("Z16",   "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LA1LG_---0LE", 476),
    ("Y19",   "1RB1RA_0RC0RA_0LD1RC_0LE1LE_---1LF_1LA0LG_1LB1LG", 459),
    ("F70",   "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LG0LE_1RA---", 481),
    ("F279",  "1RB0LA_0RC0RG_1RD---_0LE0LF_1LE0RF_1LF1RA_0RD0RG",  84),
    ("F44a",  "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LG0LE_0RA---", 478),
    ("F44b",  "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LG0LE_1RE---", 474),
]

tc = {}
for f in glob.glob(os.path.join(M8_DIR, "towercls_*.jsonl")):
    for line in open(f):
        try:
            o = json.loads(line)
            tc[o["machine"]] = o
        except Exception:
            pass

xc = {r["m"]: r for r in json.load(open(os.path.join(M8_DIR, "xcands.json")))}

def setslot(m, X, act):
    R = m.split('_')
    st, sym = ord(X[0]) - 65, int(X[1])
    R[st] = R[st][:3 * sym] + act + R[st][3 * sym + 3:]
    return '_'.join(R)

def run_wf(cmd, out_path):
    with open(out_path, 'w') as fo:
        p = subprocess.Popen(cmd, stdout=fo, stderr=subprocess.STDOUT, creationflags=CREATE_FLAGS, cwd=OUR_DIR)
        p.wait()
    return open(out_path).read()

print("=================================================================")
print("1. RUN WF8 SCREEN ON X33, Z16, Y19, F70, F279, F44a, F44b")
print("=================================================================")

M_MOD = 60
for name, m, idx in TARGETS:
    r = xc[m]
    o = tc[m]
    tmpl = o.get("tmpl") or r["tmpl"]
    cl = sorted(set(c % M_MOD for c in o["cls"]))
    xs = [(X, None) for X in r["free"]] + [(g[:2], int(g[2])) for g in r["guards"]]
    print(f"\n[{name}] (i={idx}) m={m}")
    print(f"  tmpl={tmpl} | cl={cl} | xs={xs}")
    
    leaf_counts = {}
    notable_leaves = []
    for c in cl:
        r0 = c if c >= 4 else c + M_MOD
        common = ['--rc', '10', '--rk', '1', '--cls', str(c), str(M_MOD), '--R0', str(r0)]
        # Cache snapshot per (i, X, c) since free X and guard (X, s) share the same snapshot for X!
        for X, s in xs:
            tag = f"{idx:03d}_{X}_c{c}"
            snapf = os.path.join(OUT_DIR, tag + "_snap.txt")
            if not os.path.exists(snapf) or "SNAPPED" not in open(snapf).read():
                so = run_wf([WF, m, tmpl] + common + ['--x', X, '--snapx', '--maxt', '3e9', '--maxs', '3e9'], snapf)
            else:
                so = open(snapf).read()
            if "SNAPPED" not in so:
                print(f"  c={c} X={X} s={s}: SNAP NOT REACHED: {so.strip().splitlines()[-1] if so.strip() else 'empty'}")
                continue
            old = m.split('_')[ord(X[0]) - 65][3 * int(X[1]):3 * int(X[1]) + 3]
            if s is None:
                if old[0] == '-':
                    # Already undefined slot in 7-state base!
                    # Wait: if X is already '---' in the 7-state base, how could the base run without halting at X?!
                    # Only if X is the first slot hit at exhaustion! Redirecting X -> w d H gives 4*33*33 variants
                    variants = [(f"{w}{d}", setslot(m, X, w + d + 'H') + '_------', 'H0,H1') for w in '01' for d in 'LR']
                else:
                    variants = [(f"{w}{d}", setslot(m, X, w + d + 'H') + '_------', 'H0,H1') for w in '01' for d in 'LR']
            else:
                if old[0] == '-':
                    continue
                T = m.split('_')[ord(old[2]) - 65]
                copy = T[3 * (1 - s):3 * (1 - s) + 3]
                h = ['---', '---']
                h[1 - s] = copy
                variants = [(f"g{s}", setslot(m, X, old[:2] + 'H') + '_' + h[0] + h[1], f"H{s}")]
            for vt, child, free in variants:
                rf = os.path.join(OUT_DIR, f"{tag}_{vt}.txt")
                if not os.path.exists(rf):
                    txt = run_wf([WF, child, tmpl] + common + ['--x', X, '--from', snapf, '--free', free,
                                 '--maxt', '3e6', '--maxs', '3e6', '--loop', '--slit', '3e6',
                                 '--maxexact', '1e7', '--xmax', '20000', '--tapemax', '3e7'], rf)
                else:
                    txt = open(rf).read()
                for line in txt.splitlines():
                    if line.startswith("LEAF "):
                        parts = line.split()
                        verdict = parts[2]
                        leaf_counts[verdict] = leaf_counts.get(verdict, 0) + 1
                        if verdict not in ("HALT_E1", "LOOP", "COLLAPSED", "PERIODIC", "RUNAWAY") and not verdict.startswith("HALT_E1"):
                            notable_leaves.append((c, X, s, vt, line))
    print(f"  Leaf verdict counts: {leaf_counts}")
    print(f"  Notable leaves ({len(notable_leaves)}):")
    for nl in notable_leaves[:25]:
        print(f"    c={nl[0]} X={nl[1]} s={nl[2]} vt={nl[3]}: {nl[4]}")
