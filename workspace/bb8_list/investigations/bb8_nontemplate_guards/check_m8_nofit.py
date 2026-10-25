import json, glob, os

M8_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_m8sweep"
xc = json.load(open(os.path.join(M8_DIR, "xcands.json")))
tc = {}
for f in glob.glob(os.path.join(M8_DIR, "towercls_*.jsonl")):
    for line in open(f):
        try:
            o = json.loads(line)
            tc[o["machine"]] = o
        except Exception:
            pass

f89_list = [
    "1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE",
    "1RB0LG_1LC0LE_1LF0LD_1RE0RB_1RB0RD_0LA---_1LA1LD",
    "1RB0RD_1LC0LA_1LE0LD_1RA0RB_0LF---_1RB0LG_1LF1LD",
    "1RB0RF_1RC0RE_0RD---_1LA0RG_1LF0LA_1LA0LE_1RD1RE",
]

for r in xc:
    if r["m"] in f89_list:
        print("xcand:", r)
        o = tc.get(r["m"], {})
        print("  towercls:", o.get("tmpl"), o.get("rules"), o.get("cls"))
        sf = os.path.join(M8_DIR, "scr", f"{r['i']:03d}.json")
        if os.path.exists(sf):
            print("  scr summary:", json.load(open(sf)))
        else:
            print("  scr summary: NOT RUN")
