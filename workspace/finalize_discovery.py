from collections import Counter
import json
from pathlib import Path

initial=json.loads(Path('discovery_triage.json').read_text())
deep=json.loads(Path('discovery_deep.json').read_text())
assert len(initial['results'])==21 and len(deep['results'])==17
latest={r['machine']:r for r in initial['results']}
latest.update({r['machine']:r for r in deep['results']})
counts=dict(Counter(r['status'] for r in latest.values()))
assert counts=={'halt':3,'infinite':2,'cutoff':16},counts
out={'new_champion_established':False,'counts':counts,'record_status_note':'Cutoffs are unresolved. Upstream nonhalting classifications are not new independently checked proof certificates. Three halters were independently checked by literal simulation.','results':list(latest.values())}
Path('discovery_final.json').write_text(json.dumps(out,indent=2))
Path('discovery_holdouts.txt').write_text(''.join(r['machine']+'\n' for r in latest.values() if r['status']=='cutoff'))
p=Path('hunt_20260926.md')
s=p.read_text()
s=s.replace('isolated under `third_party/python_deps`. Source provenance and measured pilot\noutcomes will be recorded after compilation and validation.', 'isolated under `third_party/runtime_deps` (the first elevated installation\nunder `python_deps` is unused). SHA-256 hashes of the enumerator source and\nbinaries, plus measured run counts, are in `discovery_pilot_summary.json`.')
s+='''

## Measured discovery pilot outcomes

| Run | Partial search nodes started | Initial holdouts | Unvisited frontier nodes |
| --- | ---: | ---: | ---: |
| BB(7), shard 243308, 175 s | 3,662,039 | 15 | 86,475 |
| BB(8), shard 243308, 175 s | 4,275,667 | 6 | 156,119 |
| BB(8), shard 202609, 175 s | 2,514,045 | 15 | 92,936 |

These are incomplete slices, not completed shards, and nodes are partial
transition tables rather than a count of distinct complete machines.
Numeric shard identifiers do not describe identical regions for seven and
eight states. The short BB(7) shard run did not reach its champion.

A separate single-machine calibration did pass the actual BB(7) champion
through the entire original filter pipeline: it survived as a holdout in
0.095 seconds. An obvious loop was rejected and the BB(4) champion was
recognized as halting. See `mxdys_probe_calibration/`. This validates a key
regression condition without claiming a new proof of the BB(7) runtime.

Each of the 21 BB(8) holdouts has exactly one undefined transition. We
completed it with 1RZ and ran unmodified Ligocki Quick_Sim, first with a
10-second / 10,000-loop cap, then on the 17 remaining cutoffs with recursive
proofs and a 15-second / 100,000-loop cap. Automatic block selection was
used. No simulator errors were observed.

Final combined outcomes (`discovery_final.json`):

- Three halters: 2,002,855 steps / 1,862 ones; 871,820 / 271;
  and 21,136,127 / 6,846. All three were independently checked by literal
  JavaScript simulation (`audit_triage_halters.json`). None beats the
  existing 131,112,087-step local record, much less the BB(7) champion.
- Two machines classified nonhalting by the upstream automatic proof
  system. Their proof certificates were not independently audited here.
- Sixteen unresolved candidates, retained in `discovery_holdouts.txt`.
  Some accelerate to very large counts, but no halting conclusion follows
  from those counts. They are not established championship contenders.

The prover also reproduced BB(5)'s exact 47,176,870 steps and 4,098 ones in
334 simulator loops (`audit_ligocki_bb5.json`). Wrapper tests distinguish
halting, infinite, loop cutoff, wall timeout, and errors.

## Continuing the search

`mxdys_resume8.exe` resumes saved final-DFS frontier files without repeating
the completed prefix. It validates transition counts and preserves metadata.
Run from a fresh output directory with the compiler runtime on PATH, e.g.:

```powershell
$env:PATH = 'C:\\msys64\\ucrt64\\bin;' + $env:PATH
$env:BB_PILOT_SECONDS = '175'
$env:BB_PILOT_PREFIX = 'next8'
& '..\\mxdys_resume8.exe' resume '..\\pilot8_243308\\pilot8a_frontier.txt'
```

The interpreter used here is the bundled Python 3.12 executable reported by
workspace dependencies. With that interpreter:

```text
python ligocki_runner.py --input discovery_holdouts.txt --recursive --workers 2 --timeout 30 --max-loops 100000 --output next_triage.json
```

Results remain an exploratory search, not a BB(8) record. The important
change is that hard machines survive the discovery stage and are analyzed
afterward, rather than being discarded because direct simulation did not
reach a halt.
'''
p.write_text(s)
print(json.dumps({'counts':counts,'unresolved_saved':16,'report':str(p.resolve())}))
