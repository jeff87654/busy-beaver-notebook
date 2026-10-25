import os
import sys
os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ.get('PATH', '')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
import idle
import argparse
import fit7, eng7, rounds7, reb7

dummy_args = argparse.Namespace(steps=10000000, maxk=1000, rand=20)

print("=== 1. Compare champ_231 (G0=0LD), champ_232 (G0=0LC), and new 1MUT G0=1LC ===")
tmpl_c = "L,E,P=1,u=11,s=00,d=1d+0,b=1b+0,S=1"
for name, m in [
    ("champ_231 (G0=0LD)", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"),
    ("champ_232 (G0=0LC)", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LC0RB"),
    ("1MUT G0=1LC",        "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"),
]:
    P = fit7.Prober(m, tmpl_c)
    ks, end = P.trace(5000000, 50)
    res = reb7.analyse(m, tmpl_c, dummy_args, False)
    print(f"\n--- {name}: {m} ---")
    print("  First 8 K-configs:")
    for step, ds, a, b in ks[:8]:
        print(f"    step={step:8d} len={len(ds):2d} ds={ds} a={a} b={b}")
    print(f"  rules : {res.get('rules')}")
    print(f"  smallB: {res.get('smallB')}")
    print(f"  E_map : {res.get('E0') or res.get('E')}")
    print(f"  Q1    : {res.get('rounds', {}).get('80640', [None])[0]} trace={res.get('rounds', {}).get('80640', [None, []])[1]}")
