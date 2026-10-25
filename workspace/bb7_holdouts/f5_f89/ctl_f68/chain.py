import subprocess, sys
subprocess.run([sys.executable, 'symsuite68.py', 'symsuite68_partB.tsv', 'red', '10,12,16,20,25,31'])
with open('hs68_out.txt', 'w') as f: subprocess.run([sys.executable, 'hs68.py'], stdout=f, stderr=subprocess.STDOUT)
