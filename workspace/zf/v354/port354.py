"""Port the v361 ZFTM.v / Sim*.v (run from v354/coq, which holds copies of v361/coq) to B354."""
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
    ("(** * ZFTM: the 361-state machine A361.tm (zf-reduce's reduction of Wade's zf2.tm)",
     "(** * ZFTM: the 354-state machine B354.tm (zf-reduce's reduction of Wade's zf2.tm)"),
    ("literal table [zf2_table] of A361.tm", "literal table [zf2_table] of B354.tm"),
    ("  | QNode (n : bnat 294)", "  | QNode (n : bnat 287)"),
    ("Definition Node n := QNode (bmk 294 n).", "Definition Node n := QNode (bmk 287 n)."),
    ("map QNode (ball 294)", "map QNode (ball 287)"),
    ("List.length all_states = 362 /\\ List.length zf2_table = 721",
     "List.length all_states = 355 /\\ List.length zf2_table = 707"),
])
for p in ['SimDag.v', 'Sim.v']:
    s = open(p, encoding='utf-8').read()
    s = s.replace('295', '288').replace('bmk 294', 'bmk 287')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
edit('SimDag.v', [
    ("(lk tH 0 <=? 125)", "(lk tH 0 <=? 123)"),
    ("Some (e, d) -> d <= 125.", "Some (e, d) -> d <= 123."),
    ("Lemma need_le c : need c <= 138.", "Lemma need_le c : need c <= 136."),
    ("Definition N0 := 300.", "Definition N0 := 290."),
    ("(120 <=? ndec N0", "(118 <=? ndec N0"),
])
print('done')
