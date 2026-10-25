"""Where is H0 read?  Literal run of the main machine.  Every H0 read must start the 5-step detour
H0 0LB, B1 0RE, E0 1LB, B0 1RC, C1 1LC whose result (tape, head position, state C) equals the
result of the variant's single step H0 1LC.  So the variant runs the same tapes, 4 steps sooner
per H0 read (checked exactly at every H0 read)."""
import sys
from lit import Sim, MAIN
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10**7
s = Sim(MAIN, size=1 << 20)
reads = bad = 0
while s.steps < N:
    if s.state == 7 and s.tape[s.pos] == 0:
        reads += 1
        t2 = bytearray(s.tape); t2[s.pos] = 1; pos2 = s.pos - 1   # variant: H0 1LC
        seq = []
        for _ in range(5):
            seq.append((s.state, s.tape[s.pos])); s.step()
        if not (seq == [(7, 0), (1, 1), (4, 0), (1, 0), (2, 1)] and s.state == 2 and s.pos == pos2
                and s.tape == t2):
            bad += 1
        continue
    if not s.step():
        break
print('steps', s.steps, 'H0 reads', reads, 'reads where the 5-step detour != the variant step', bad)
