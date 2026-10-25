"""dscan.py OUT K:IT,IT.. [tags]: full-tape dumps; report #tokens, #big(>=30) and big values, count histogram."""
import sys, subprocess, re, collections
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
D = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
out = open(sys.argv[1], 'w'); Ks = sys.argv[2].split(';'); tags = sys.argv[3].split(',') if len(sys.argv) > 3 else None
for line in open('list.tsv'):
    tag, m = line.split('\t')[:2]
    if tags and tag not in tags: continue
    fn = f'tmpd_{tag}.txt'; open(fn, 'w').write(m + '\n')
    for kk in Ks:
        K, its = kk.split(':')
        for it in its.split(','):
            p = subprocess.Popen([D + r'\nlp7v.exe', fn, 'NUL', str(int(float(it)*1.5)), '--life', '--K=' + K, '--dumpat=' + str(int(float(it)))], stdout=subprocess.PIPE, text=True, creationflags=0x40)
            open(D + r'\pids.txt', 'a').write(f'{p.pid}\tgroupE2\tnlp7v dump {tag} K{K}\n')
            o = p.communicate()[0].splitlines()
            d = [i for i, l in enumerate(o) if l.startswith('DUMP')]
            if not d: out.write(f'{tag} K{K} it={it} nodump\n'); continue
            hdr = o[d[0]]; tape = o[d[0] + 1].split('|', 1)[1]
            toks = re.findall(r'(\S+)\^(\d+)', tape)
            cnt = [int(c) for _, c in toks]
            big = [c for c in cnt if c >= 30]
            mid = [c for c in cnt if 4 <= c < 30]
            out.write(f'{tag} K{K} {hdr.split()[1]} {float(hdr.split()[2]):.2e} ntok={len(toks)} big={len(big)} {sorted(big)[-10:]} mid={len(mid)} midvals={sorted(set(mid))[:12]}\n'); out.flush()
    import os; os.remove(fn)
