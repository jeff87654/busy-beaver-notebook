"""Port the v336 ZFTM.v / Sim*.v (run from v335/coq, which holds copies of v336/coq) to R3Y1_335."""
import subprocess, sys

def edit(p, reps):
    s = open(p, encoding='utf-8').read()
    for a, b in reps:
        if a not in s:
            raise SystemExit(f'{p}: missing {a!r}')
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

names = subprocess.run([sys.executable, '../../tools/gen_zftm_names.py', 'ZF2Dag.v'],
                       capture_output=True, text=True, check=True).stdout
s = open('ZFTM.v', encoding='utf-8').read()
i = s.index('Definition node_name (n : nat) : string :=')
j = s.index('Definition name (q : state) : string :=')
s = s[:i] + names + '\n' + s[j:]
open('ZFTM.v', 'w', encoding='utf-8', newline='\n').write(s)
edit('ZFTM.v', [
    ("(** * ZFTM: the 336-state machine R3s336.tm (a reduction of Wade's zf2.tm)",
     "(** * ZFTM: the 335-state machine R3Y1_335.tm (a reduction of Wade's zf2.tm)"),
    ("literal table [zf2_table] of R3s336.tm", "literal table [zf2_table] of R3Y1_335.tm"),
    ("  | QNode (n : bnat 269)", "  | QNode (n : bnat 268)"),
    ("Definition Node n := QNode (bmk 269 n).", "Definition Node n := QNode (bmk 268 n)."),
    ("map QNode (ball 269)", "map QNode (ball 268)"),
    ("List.length all_states = 337", "List.length all_states = 336"),
    ("List.length zf2_table = 671", "List.length zf2_table = 669"),
])
for p in ['SimDag.v', 'Sim.v']:
    s = open(p, encoding='utf-8').read()
    s = s.replace('270', '269').replace('bmk 269', 'bmk 268')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
edit('SimDag.v', [
    ("(lk tH 0 <=? 110)", "(lk tH 0 <=? 109)"),
    ("Some (e, d) -> d <= 110.", "Some (e, d) -> d <= 109."),
    ("Lemma need_le c : need c <= 123.", "Lemma need_le c : need c <= 122."),
    ("(105 <=? ndec N0", "(104 <=? ndec N0"),
])
print('done')
