"""Write ../bb10_bb7_descendants.md from the result files (python gen_report.py)."""
import io
import re
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tally  # noqa: E402

buf = io.StringIO()
with redirect_stdout(buf):
    tally.main()
T = buf.getvalue()

text = Path(HERE / 'report_body.txt').read_text(encoding='utf-8')
text = text.replace('@TALLY@', T.rstrip())
(HERE.parent / 'bb10_bb7_descendants.md').write_text(text, encoding='utf-8')
print('written', len(text), 'chars')
