from absim import *
k = new_atom('k', 5, MB, rank=0); n = new_atom('n', 7, MB, rank=1); a = new_atom('a', 40, MB, rank=2)
m = Val(10)
runs = norm([('t', Val(2), k), ('t', Val(5), Val(1)), ('t', Val(1), m + 6), ('t', Val(0), Val(2)), ('t', Val(2), Val(1)), ('t', Val(1), n), ('t', Val(0), Val(1)), ('t', a, Val(1))])
print(show(runs))
kind, out, info = literal_stage(runs)
print(kind, info['steps'], show(out))
print('expect [2^(k+2),5,1^m,0,0,0,1,a+3,1^n|6]')
# CLR macro check on a concrete example vs literal: [.., 7, 1^2 | 4]
runs2 = norm([('t', Val(2), Val(1)), ('t', Val(7), Val(1)), ('t', Val(1), Val(1)), ('t', Val(0), Val(1)), ('t', Val(4), Val(1))])
print(clr(runs2)[1:])
import sim
w = render(runs2, {})
print(sim.fmt(sim.tokens(w)))
