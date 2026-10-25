"""Port the v354 ZFTM.v / Sim*.v (run from v336/coq, which holds copies of v354/coq) to R3s336."""
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
    ("(** * ZFTM: the 354-state machine B354.tm (zf-reduce's reduction of Wade's zf2.tm)",
     "(** * ZFTM: the 336-state machine R3s336.tm (a reduction of Wade's zf2.tm)"),
    ("literal table [zf2_table] of B354.tm", "literal table [zf2_table] of R3s336.tm"),
    ("  | QNode (n : bnat 287)", "  | QNode (n : bnat 269)"),
    ("Definition Node n := QNode (bmk 287 n).", "Definition Node n := QNode (bmk 269 n)."),
    ("map QNode (ball 287)", "map QNode (ball 269)"),
    ("List.length all_states = 355", "List.length all_states = 337"),
    ("List.length zf2_table = 707", "List.length zf2_table = 671"),
])
for p in ['SimDag.v', 'Sim.v']:
    s = open(p, encoding='utf-8').read()
    s = s.replace('288', '270').replace('bmk 287', 'bmk 269')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
edit('SimDag.v', [
    ("(lk tH 0 <=? 123)", "(lk tH 0 <=? 110)"),
    ("Some (e, d) -> d <= 123.", "Some (e, d) -> d <= 110."),
    ("Lemma need_le c : need c <= 136.", "Lemma need_le c : need c <= 123."),
    ("Definition N0 := 290.", "Definition N0 := 240."),
    ("(118 <=? ndec N0", "(105 <=? ndec N0"),
])
print('done')
