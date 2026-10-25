import pickle
import planner9 as P
out = pickle.load(open('endings.pkl', 'rb'))
start, script, got, exp = out['C']
envs = [{'x': 1000, 'y': 1037}, {'x': 2003, 'y': 2104}]
print('got L', got[1][:60])
print('exp L', exp[1][:60])
for side_name, a, b in (('L', got[1], exp[1]), ('R', got[2], exp[2])):
    print(side_name, P._run_positions(a, envs[0]), P._run_positions(b, envs[0]))
import planner9 as P2
side = list(got[1]); target = exp[1]
envs = [{'x': 1000, 'y': 1037}, {'x': 2003, 'y': 2104}]
# instrument
orig = P2.normalize_side_to
r = orig(side, target, envs)
print('result', r)
# manual trace
side2 = list(side)
for it in range(10):
    rs = P2._run_positions(side2, envs[0]); rt = P2._run_positions(target, envs[0])
    print(it, rs, rt)
    r = orig(side2, target, envs)
    break
