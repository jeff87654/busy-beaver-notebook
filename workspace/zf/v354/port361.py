import sys
NAMES = r'C:\Users\jeffr\.claude\jobs\dc5aea71\tmp\l3\names361.v'

def edit(p, reps):
    s = open(p, encoding='utf-8').read()
    for a, b in reps:
        if a not in s:
            raise SystemExit(f'{p}: missing {a!r}')
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

s = open('ZFTM.v', encoding='utf-8').read()
i = s.index('Definition node_name (n : nat) : string :=')
j = s.index('Definition name (q : state) : string :=')
s = s[:i] + open(NAMES, encoding='utf-8').read() + '\n' + s[j:]
open('ZFTM.v', 'w', encoding='utf-8', newline='\n').write(s)
edit('ZFTM.v', [
    ("(** * ZFTM: Wade's 393-state machine zf2.tm", "(** * ZFTM: the 361-state machine A361.tm (zf-reduce's reduction of Wade's zf2.tm)"),
    ("i < 9 (max run of car edges in zf2 = 9)", "i < 7 (max run of car edges = 7)"),
    ("[QBrk k]   = 6.break.k (k <= 2)", "[QBrk k]   = 6.break.k (k <= 1)"),
    ("literal table [zf2_table] of zf2.tm", "literal table [zf2_table] of A361.tm"),
    ("Definition max_zeros := 9.      (* dispatch states 4.dispatch.1 .. 4.dispatch.9 *)",
     "Definition max_zeros := 7.      (* dispatch states 4.dispatch.1 .. 4.dispatch.7 *)"),
    ("  | QDisp (i : bnat 8)", "  | QDisp (i : bnat 6)"),
    ("  | QBrk (k : bnat 2)", "  | QBrk (k : bnat 1)"),
    ("  | QNode (n : bnat 323)", "  | QNode (n : bnat 294)"),
    ("Definition Disp i := QDisp (bmk 8 i).", "Definition Disp i := QDisp (bmk 6 i)."),
    ("Definition Brk k := QBrk (bmk 2 k).", "Definition Brk k := QBrk (bmk 1 k)."),
    ("Definition Node n := QNode (bmk 323 n).", "Definition Node n := QNode (bmk 294 n)."),
    ("map QDisp (ball 8) ++ map QBrk (ball 2)", "map QDisp (ball 6) ++ map QBrk (ball 1)"),
    ("map QNode (ball 323)", "map QNode (ball 294)"),
    ("List.length all_states = 394 /\\ List.length zf2_table = 785",
     "List.length all_states = 362 /\\ List.length zf2_table = 721"),
])
edit('SimBase.v', [("andb (Nat.ltb c 9) (nz (S c) U)", "andb (Nat.ltb c 7) (nz (S c) U)"),
                   ("never reaches 10 consecutive zeros", "never reaches 8 consecutive zeros")])
edit('SimIP.v', [
    ("Lemma tm_cs_1 c : c <= 9 ->", "Lemma tm_cs_1 c : c <= 7 ->"),
    ("do 10 (destruct c as [|c]; [reflexivity|]). lia.", "do 8 (destruct c as [|c]; [reflexivity|]). lia."),
    ("Lemma tm_cs_0 c : c < 9 ->", "Lemma tm_cs_0 c : c < 7 ->"),
    ("do 9 (destruct c as [|c]; [reflexivity|]). lia.", "do 7 (destruct c as [|c]; [reflexivity|]). lia."),
    ("Lemma disp_gen U c Y : c <= 9 ->", "Lemma disp_gen U c Y : c <= 7 ->"),
    ("rewrite <- (zc_padl _ [true] _ 10)", "rewrite <- (zc_padl _ [true] _ 8)"),
    ("Lemma brk_ip U k Y : k <= 2 ->", "Lemma brk_ip U k Y : k <= 1 ->"),
    ("Lemma tm_brk_S k : k <= 1 -> tm (Brk (S k), false) = Some (false, L, Brk k).\nProof. intros H. do 2 (destruct k as [|k]; [reflexivity|]). lia. Qed.",
     "Lemma tm_brk_S k : k <= 0 -> tm (Brk (S k), false) = Some (false, L, Brk k).\nProof. intros H. do 1 (destruct k as [|k]; [reflexivity|]). lia. Qed."),
    ("destruct k as [|[|[|k]]]; [| | |lia]; simpl;", "destruct k as [|[|k]]; [| |lia]; simpl;"),
])
edit('SimDag.v', [
    ("| EBreak k => b && (1 <=? k) && (k <=? 2)", "| EBreak k => b && (1 <=? k) && (k <=? 1)"),
    ("| EBreak k => b = true /\\ 1 <= k <= 2", "| EBreak k => b = true /\\ 1 <= k <= 1"),
    ("andb (Nat.ltb c 9) (nzd (S c) U)", "andb (Nat.ltb c 7) (nzd (S c) U)"),
    ("(lk tZ n <=? 9)", "(lk tZ n <=? 7)"),
    ("1 <= Z n /\\ Z n <= 9 /\\", "1 <= Z n /\\ Z n <= 7 /\\"),
    ("have no 10 consecutive zeros (max car chain = 9)", "have no 8 consecutive zeros (max car chain = 7)"),
    ("(lk tH 0 <=? 136)", "(lk tH 0 <=? 125)"),
    ("Some (e, d) -> d <= 136.", "Some (e, d) -> d <= 125."),
    ("Lemma need_le c : need c <= 149.", "Lemma need_le c : need c <= 138."),
    ("Definition N0 := 347.", "Definition N0 := 300."),
    ("(131 <=? ndec N0", "(120 <=? ndec N0"),
])
for p in ['SimDag.v', 'Sim.v']:
    s = open(p, encoding='utf-8').read()
    s = s.replace('324', '295').replace('bmk 323', 'bmk 294')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
edit('Sim.v', [("assert (Hk : 1 <= k <= 2 /\\ forall m b, m < 295 -> dedge m b = EBreak k",
                 "assert (Hk : 1 <= k <= 1 /\\ forall m b, m < 295 -> dedge m b = EBreak k")])
edit('SimBoot.v', [("Definition boot_steps := 39773.", "Definition boot_steps := 39769.")])
print('done')
