from pathlib import Path
import json
from collections import Counter
for name in ('lastfive_decider_cps.json','lastfive_decider_cps_deep.json'):
 j=json.loads(Path(name).read_text());print(name,Counter(r['status']for r in j['results']))
 print('conditions',Counter(k for r in j['results']for k in r.get('abstract_transition_conditions',{})if k!='Running'))
