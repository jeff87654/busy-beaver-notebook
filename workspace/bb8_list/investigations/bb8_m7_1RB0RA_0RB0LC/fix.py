p='../bb8_m7_1RB0RA_0RB0LC.md'
s=open(p,encoding='utf-8').read()
old='the a-token is now 1 ("1 0") with the first token 6 = (01)^6 to its left, i.e. the next event is the champion R2/R3 borrow (6 -> 3, a-token about 2r+3 with r about 2e5), after which\nthe chain is about 6e4 phases long. So the n = 1 run is a faithful second copy of the champion recursion on the degraded list; its end is not reachable.'
new='the a-token seems to have reached 1 ("1 0") with the first token 6 = (01)^6 to its left; the expected next event (not yet seen: the snapshots up to 1.9e10 still show inner rounds) is the champion\nR2/R3 borrow (6 -> 3, a-token about 2r+3 with r about 2e5), after which the chain is about 6e4 phases long. So the n = 1 run looks like a second copy of the champion recursion on the degraded list; its end is not reachable.'
assert old in s
s=s.replace(old,new)
s+='''
## End note: the M2 -> M3 exploration (gen/x3.py) FAILED, and why

mexp.explore(M2, M3) stops, after the nine crossing loops, at  0^inf 1 1 (10)^(6b) <C (110)^k 0 0 1 0 0 1 0 (010)^n 1  with "stuck without loop" (same as x2.py).
The literal M2 -> M3 stage (turns.py n b thr prints the tape at every sweep reversal) is a left-end bounce loop exactly like the sibling Z-stage: for n = 0, b = 1 the reversals at the
left end are at steps 506, 600, 684, 770, ... (about 80 steps each) with tapes

    11 (01)^x 00 1 0 11 (0 11)^k 00 1 00 1 0 1  (state D)   /   111 (01)^x 00 1 0 11 (0 11)^k 00 1 00 1 0 1  (state A)       x = 10, 9, 8, ..., 4 (x starts at 6b+4), k grows by 1 per round

(the run (10)^(6b+4) of M2 is eaten one unit per bounce and a block 0 11 is appended on the right), then a long sweep (step 1334 -> 2038) rebuilds the (001) list and ends at M3
(step 1774 is the B-frontier snapshot M3 for b = 1). So the missing machine-level piece is, as in the sibling proof (opus/gen_tr.py, ZR + hand induction ZIT), one round lemma
Z(x+1,k) -->* Z(x,k+1) for general x,k plus the hand induction and the exit sweep; the waypoints above are literal and exact for the n = 0, b = 1 orbit (check the other (n,b) with turns.py first).
'''
open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')
