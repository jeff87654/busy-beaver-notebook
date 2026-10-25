import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short
from analyze_rebE2_and_contexts import trace_k_event, trace_blank

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

tm_rebE2 = "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC"
t_rebE2 = "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0"

print("=== reb_E2: Tracing K(1, 0^k; a; 1) and K(0^k; a; 1) for k=0..6, a=3,5 ===")
for prefix in [[], [1]]:
    for k in range(7):
        for a in [3, 5]:
            ds = prefix + [0]*k
            ev, ctxs, hits = trace_k_event(tm_rebE2, t_rebE2, 1, ds, a, target_slot="A0")
            slots_used = sorted({sl for sl, _ in ctxs})
            print(f"  K({short(ds):6s}; a={a}; 1) -> {ev[0]}({short(ev[2]) if ev[0]=='K' else ''}; {ev[3] if ev[0]=='K' else ''}){'@'+str(ev[1]) if len(ev)>1 else ''} | A0 hits={len(hits)} | used={slots_used}")
            for step, slot, win_str, full_str in hits:
                print(f"      A0 hit @ {step}: win={win_str} | full={full_str}")

print("\n=== multi_1: Why did K(0^2; a; 1) return empty in check_exact_macro_rules? Let's trace with pall=1 ===")
tm_m1 = "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF"
t_m1 = "R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1"
T_m1 = kl.tmpl(tm_m1, t_m1)
for ds in [[2, 0, 0], [1, 0, 0], [0, 0], [0], []]:
    for a in [1, 4]:
        evs = kl.run(tm_m1, ds, a, 1, steps=50000, nchg=0, maxl=50000, T=T_m1, pall=1)
        k_evs = [f"K({short(e[2])};{e[3]};{e[4]})@{e[1]}" for e in evs[1:] if e[0] == 'K'][:4]
        print(f"  multi_1 K({short(ds):6s}; a={a}; 1) -> {k_evs}")

print("\n=== w1loop_1: Let's trace K(ds; a; 1) with pall=1 ===")
tm_w1 = "1RB0RE_1RC1RA_0LD0LE_1RE0LE_0RF1LC_1LC1RG_0RB---"
t_w1 = "L,F,P=1,u=10,s=0,d=2d+0,b=2b+1,S=-"
T_w1 = kl.tmpl(tm_w1, t_w1)
for ds in [[2, 0, 0], [1, 0, 0], [0, 0], [0], []]:
    for a in [1, 4]:
        evs = kl.run(tm_w1, ds, a, 1, steps=50000, nchg=0, maxl=50000, T=T_w1, pall=1)
        k_evs = [f"K({short(e[2])};{e[3]};{e[4]})@{e[1]}" for e in evs[1:] if e[0] == 'K'][:4]
        print(f"  w1loop_1 K({short(ds):6s}; a={a}; 1) -> {k_evs}")
