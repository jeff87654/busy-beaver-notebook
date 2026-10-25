import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
import json

def main():
    # 1. Load tlist.txt and tbig.txt from bb9_fw1_hosts
    tlist = [l.strip() for l in open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_fw1_hosts\tlist.txt') if l.strip()]
    tbig = {}
    for l in open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_fw1_hosts\tbig.txt'):
        if l.strip():
            m, js = l.strip().split(' ', 1)
            tbig[m] = json.loads(js)

    fw1_pool = {}
    for l in open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_fw1_hosts\pool.tsv'):
        f = l.rstrip('\n').split('\t')
        fw1_pool[f[0]] = f

    # 2. Load reb7 final_all_verdicts.tsv, hand.tsv, run8.jsonl, mr_main.jsonl, mr_d.jsonl
    verdicts = {}
    for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\final_all_verdicts.tsv'):
        f = l.rstrip('\n').split('\t')
        if f[0] != 'machine':
            verdicts[f[0]] = f

    run8 = {}
    for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\run8.jsonl'):
        r = json.loads(l)
        run8[r['machine']] = r

    print(f"=== PART B.1: CROSS-REFERENCE OF THE 16 UNRESOLVED bb9_fw1_hosts/tlist.txt MACHINES ===")
    for i, m in enumerate(tlist, 1):
        p = fw1_pool.get(m, [])
        v = verdicts.get(m)
        r8 = run8.get(m)
        tb = tbig.get(m, {})
        print(f"\n[{i:2d}] {m}")
        if p:
            print(f"     fw1_pool : states={p[1]} grade={p[2]} src={p[3]} tmpl={p[4]}")
        print(f"     tbig(b=3): {tb.get('3')}")
        print(f"     tbig(b=4): {tb.get('4')}")
        if v:
            print(f"     reb7     : verdict={v[3]} | stage={v[4]} | note={v[5]}")
            print(f"                tmpl={v[6]} | rules={v[7]} | exh={v[8]}")
        elif r8:
            print(f"     reb7(8st): verdict={r8.get('verdict')} | tmpl={r8.get('tmpl_in')} | E_pat={r8.get('E_pat')}")
        else:
            print(f"     reb7     : NOT IN final_all_verdicts.tsv or run8.jsonl!")

if __name__ == '__main__':
    main()
