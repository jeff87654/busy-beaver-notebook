"""Print the Coq [node_name] function (node index -> zf2.tm state name) from the comments of coq/ZF2Dag.v.
The block is pasted into coq/ZFTM.v; correctness is not trusted: ZFTM.v checks the whole machine against
zf2_table by vm_compute."""
import re, sys
names = {}
for l in open(sys.argv[1] if len(sys.argv) > 1 else 'coq/ZF2Dag.v', encoding='utf-8'):
    m = re.match(r'\s*\| (\d+) => \(.*\)\s+\(\* (.*) \*\)\s*$', l)
    if m:
        names[int(m.group(1))] = m.group(2)
assert sorted(names) == list(range(len(names)))
print('Definition node_name (n : nat) : string :=')
print('  match n with')
for i in range(len(names)):
    print(f'  | {i} => "{names[i]}"')
print('  | _ => "?"')
print('  end.')
