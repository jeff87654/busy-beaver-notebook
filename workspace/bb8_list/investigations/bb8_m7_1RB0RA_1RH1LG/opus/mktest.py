import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'gen'))
from common import header
hdr = header('glue test')
ax = Path('ax.v').read_text()
glue = Path('glue.v.in').read_text()
extra = Path(sys.argv[2]).read_text() if len(sys.argv) > 2 else ''
Path(sys.argv[1]).write_text(hdr + '\n' + ax + '\n' + glue + '\n' + extra, newline='\n')
