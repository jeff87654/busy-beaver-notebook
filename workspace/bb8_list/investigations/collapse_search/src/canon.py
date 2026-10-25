"""canon.py: BFS relabelling from A (order of first reference A0,A1,...); prints canonical strings.  usage: canon.py M..."""
import sys
def canon(m):
    rows = m.split('_'); order = [0]; i = 0
    while i < len(order):
        r = rows[order[i]]
        for c in range(2):
            t = r[3*c:3*c+3]
            if t[0] != '-' and t[2] != 'Z' and ord(t[2]) - 65 < len(rows) and ord(t[2]) - 65 not in order: order.append(ord(t[2]) - 65)
        i += 1
    ren = {o: k for k, o in enumerate(order)}
    out = []
    for o in order:
        r = rows[o]; s = ''
        for c in range(2):
            t = r[3*c:3*c+3]
            s += '---' if t[0] == '-' else t[:2] + chr(65 + ren[ord(t[2]) - 65])
        out.append(s)
    return '_'.join(out)
if __name__ == '__main__':
    for m in sys.argv[1:]: print(canon(m))
