"""assemble the report: python assemble.py COQ_TEXT_FILE COST_TEXT"""
import sys
from pathlib import Path
rep = Path(__file__).resolve().parents[2] / 'bb8_m7_1RB0RA_0RB0LC.md'
old = Path(__file__).with_name('sonnet_original.md')
if not old.exists():
    old.write_text(rep.read_text(encoding='utf-8'), encoding='utf-8')
sec = Path(__file__).with_name('opus_section.txt').read_text(encoding='utf-8')
sec = sec.replace('@COQ@', Path(sys.argv[1]).read_text(encoding='utf-8').strip()).replace('@COST@', sys.argv[2])
sonnet = old.read_text(encoding='utf-8').split('\n')
sonnet[0] = '# Appendix: the earlier Sonnet report (unchanged; superseded where the Opus section above disagrees)'
sonnet = [('#' + l if l.startswith('## ') else l) for l in sonnet]
rep.write_text(sec.rstrip() + '\n\n---\n\n' + '\n'.join(sonnet), encoding='utf-8', newline='\n')
print('written', rep)
