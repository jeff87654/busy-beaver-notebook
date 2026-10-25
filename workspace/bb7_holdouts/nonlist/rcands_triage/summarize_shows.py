import os, glob

TRIAGE = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist\rcands_triage'
sub = os.path.join(TRIAGE, 'deep_shows')
digest = os.path.join(TRIAGE, 'shows_digest.txt')

with open(digest, 'w', encoding='utf-8') as o:
    for fn in sorted(glob.glob(os.path.join(sub, '*.show.txt'))):
        name = os.path.basename(fn)[:-9]
        m = open(fn[:-9] + '.in').read().strip()
        lines = [l.rstrip('\n') for l in open(fn, 'r', encoding='utf-8', errors='replace') if l.strip()]
        o.write(f"=== {name} : {m} ({len(lines)} lines) ===\n")
        # Keep first 6 and last 16 lines
        if len(lines) <= 24:
            for l in lines:
                o.write("  " + l[:180] + "\n")
        else:
            for l in lines[:6]:
                o.write("  " + l[:180] + "\n")
            o.write(f"  ... ({len(lines) - 22} middle lines omitted) ...\n")
            for l in lines[-16:]:
                o.write("  " + l[:180] + "\n")
        o.write("\n")

print("Wrote shows_digest.txt:", os.path.getsize(digest), "bytes")
