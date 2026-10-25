"""Compare exact step counts and ones counts across n1 (GH), n1_GH_plus1, n1_REC_plus1, and n1_H_plus1 on startup and all macro rules."""
from test_n1_twins import MACHINES, parse_tm, Tape, from_b, bword, FARP, FARE

def main():
    rules = [
        ('R1([2,4],4)',       [2, 4], 4, ''),
        ('R2([2,4,1,1],4)',   [2, 4, 1, 1], 4, ''),
        ('H([1,1,1],6)',      [1, 1, 1], 6, ''),
        ('S0',                [2] + [1]*8 + [0, 1, 1, 1], 6, ''),
        ('P1',                [2, 5] + [1]*7 + [0, 0, 2, 1, 1], 7, ''),
        ('P2',                [2, 5] + [1]*7 + [0, 0, 0, 1, 4, 0, 1, 1], 4, ''),
        ('P3',                [2, 2, 1, 1], 6, FARP(1, 1)),
        ('P4',                [2, 5] + [1]*3 + [0, 0, 3, 0, 1, 1], 4, ''),
        ('E',                 [2]*7 + [5, 1, 0, 0, 0, 1, 4, 0, 1, 1], 4, ''),
    ]
    for nm, (m, cs) in MACHINES.items():
        tr = parse_tm(m)
        # Startup to [7, 1^35 | 4]
        T = Tape(tr, '0', 0, 'A', cs)
        while T.steps < 10000:
            T.step()
            if T.q == cs and T.t[T.h] == 0 and T.t[T.h - 1] == 1:
                bf = T.bform()
                if bf == ([], [7] + [1]*35, 4):
                    break
        st_steps = T.steps
        r_steps = {}
        for rname, L, A, far in rules:
            kind, (T_, bf) = from_b(tr, L, A, far, cs)
            assert kind == 'B'
            r_steps[rname] = T_.steps
        # HALT on bword([0, 1, 1], 4, FARE(1))
        wd = bword([0, 1, 1], 4, FARE(1))
        Th = Tape(tr, wd, len(wd), cs, cs)
        while Th.step():
            pass
        print(f"{nm:24s} | start35={st_steps} | HALT=(steps={Th.steps}, ones={Th.ones()}) | rules={r_steps}")

if __name__ == '__main__':
    main()
