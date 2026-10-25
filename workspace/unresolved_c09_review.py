"""Independent C09 artifact audit and transcription checks for local word lemmas.

This does not search for a nonhalting classification. The finite-language closure
proof was produced by mxdys; this script checks its saved inputs and diagnostics.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
MACHINE = '1RB1LA_0LA0RC_1RA1LD_0LE1RZ_1LC1LF_0RG0LE_1RH0RG_1RA0RF'
COMMAND = 'MitM_CTL ExRWL sim 1001 maxT 300000 H 12 tH 1 bsz 8 n 2 run'
TABLE = [[(int(row[j]), 1 if row[j+1] == 'R' else -1,
           -1 if row[j+2] == 'Z' else ord(row[j+2])-65)
          for j in (0, 3)] for row in MACHINE.split('_')]

def run(word, state, head, steps, origin=0):
    tape = {origin+i for i, ch in enumerate(word) if ch == '1'}
    trace = []
    visited = []
    for _ in range(steps):
        if state == -1:
            break
        read = int(head in tape)
        trace.append(chr(65+state)+str(read))
        visited.append(head)
        write, direction, new_state = TABLE[state][read]
        if write:
            tape.add(head)
        else:
            tape.discard(head)
        head += direction
        state = new_state
    return {'tape': tape, 'state': state, 'head': head, 'trace': trace,
            'visited_min': min(visited), 'visited_max': max(visited)}

def serial(result):
    return {**result, 'tape': sorted(result['tape'])}

checks = 0
for n in range(33):
    for final, state, output in [('1', 5, '10'), ('0', 0, '11')]:
        prefix = '0'+'1'*n+'0'+final
        result = run(prefix, 5, 0, n+3)
        expected = '0'*(n+1)+output
        assert result['state'] == state and result['head'] == n+3
        assert result['tape'] == {i for i,c in enumerate(expected) if c == '1'}
        assert result['visited_max'] < len(prefix)
        checks += 1

k1 = run('01011', 5, 0, 17)
assert k1['head'] == -3 and k1['state'] == 5
assert k1['tape'] == {-2, 0, 2, 3}
assert k1['visited_max'] == 4  # No bit of arbitrary continuation W is read.
checks += 1

danger_word = '0'+'10'*2+'11'+'00010011'
danger = run(danger_word, 5, 0, 100)
assert danger['state'] == -1 and len(danger['trace']) == 21
assert danger['visited_max'] < len(danger_word)
checks += 1

local_halt = run('1101', 5, 3, 4)
assert local_halt['state'] == -1
assert local_halt['trace'] == ['F1', 'E0', 'C1', 'D1']
checks += 1

seed = run('', 0, 0, 1001)
assert seed['state'] != -1 and len(seed['trace']) == 1001
seed_summary = {k:v for k,v in serial(seed).items() if k != 'trace'}

assert ROOT.joinpath('discovery_holdouts.txt').read_text().splitlines()[8] == MACHINE
partial = MACHINE.replace('1RZ', '---')
diagnostic = 'verified: lset:116 lset_tr:118 rset:5940 rset_tr:6266 accept_set:42099 block_maxT:4'
artifact_checks = []
for name in ('c09_p09', 'c09_p09_replay'):
    folder = ROOT/'unresolved_native_runs'/name
    assert (folder/'input.txt').read_text().strip() == partial+' '+COMMAND
    assert (folder/'log.txt').read_text().strip() == partial+' N'
    assert (folder/'stderr.txt').read_text().strip() == diagnostic
    artifact_checks.append(name)

portfolio = json.loads((ROOT/'unresolved_native_portfolio.json').read_text())
record = next(r for r in portfolio['results'] if r['id'] == 9)
assert record['machine'] == MACHINE
assert record['status'] == 'verified_nonhalting_replayed'
successful = [r for r in record['attempts'] if r['portfolio_index'] == 9]
assert len(successful) == 2 and all(r['returncode'] == 0 for r in successful)
actual_hash = hashlib.sha256((ROOT/'candidate_deciders_deep_verified.cpp').read_bytes()).hexdigest()
assert actual_hash == portfolio['diagnostic_source_sha256']

result = {
    'machine': MACHINE,
    'conclusion': 'C09 nonhalting result corroborated by independent source and saved-artifact review',
    'classification_basis': 'finite-language closure plus exact block verification, not finite simulation',
    'command': COMMAND,
    'reviewed_runs': artifact_checks,
    'verifier_diagnostic': diagnostic,
    'diagnostic_source_sha256': actual_hash,
    'local_transcription_checks': checks,
    'seed_after_1001_literal_steps': seed_summary,
    'K1_universal_finite_prefix_trace': serial(k1),
    'K2_halting_neighbour_finite_prefix_trace': serial(danger),
    'local_halt_trigger': serial(local_halt),
    'limitations': 'The compact K recurrence is partial; nonhalting rests on the separately verified finite closure.'
}
(ROOT/'unresolved_c09_review.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({'checks':checks,'artifact_runs':artifact_checks,'seed_state':chr(65+seed['state']),
                  'seed_head':seed['head'],'seed_ones':len(seed['tape']),
                  'K1_trace':k1['trace'],'danger_trace':danger['trace']},indent=2))
