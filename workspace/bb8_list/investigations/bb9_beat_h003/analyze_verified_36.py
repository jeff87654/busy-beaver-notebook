import re

M = (2**20) * (3**20) * (5**5) * (7**5) * (11**3) * (13**3) * (17**2)
def f_mod(x):
    return ((5 * pow(3, 3 * x + 2, 2 * M) - 3) // 2) % M

x = 1
for _ in range(80):
    x = f_mod(x)
if x % 2 == 1:
    A_ODD = x
    A_EVEN = f_mod(x)
else:
    A_EVEN = x
    A_ODD = f_mod(x)

def parse_file(path):
    with open(path) as f:
        text = f.read()
    blocks = re.split(r'\n(?=\[\s*\d+\] )', text)
    results = []
    for b in blocks:
        m = re.match(r'\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+\|\s+H at k=\{(.*?)\}\s*\n(.*)', b, re.S)
        if not m:
            continue
        idx, sub, tm, h_list, detail = m.groups()
        k_map = {}
        for km in re.finditer(r'k(\d+)=(\S+)', detail):
            k = int(km.group(1))
            val = km.group(2)
            if val.startswith('k(') or val.startswith('K('):
                mm = re.match(r'([kK])\(([+-]?\d+),I(\d),d(\d+)\)', val)
                if mm:
                    k_map[k] = (mm.group(1), int(mm.group(2)), int(mm.group(3)), int(mm.group(4)))
            else:
                k_map[k] = (val, None, None, None)
        results.append((int(idx), sub, tm, h_list, k_map))
    return results

for label, p in [
    ('arch_a_d', r'C:\Users\jeffr\.gemini\antigravity-cli\brain\58eb37dc-428f-4147-abad-9bd872ad5bcb\.system_generated\steps\389\output.txt'),
    ('std9', r'C:\Users\jeffr\.gemini\antigravity-cli\brain\58eb37dc-428f-4147-abad-9bd872ad5bcb\.system_generated\steps\407\output.txt'),
]:
    res = parse_file(p)
    print(f'=== {label}: {len(res)} candidates ===')
    periodic_count = 0
    nonperiodic = []
    for idx, sub, tm, h_list, k_map in res:
        best_P = None
        for P in range(1, 16):
            ok = True
            for k in range(max(16, 37 - 2 * P), 37 - P):
                if k not in k_map or (k + P) not in k_map:
                    ok = False
                    break
                if k_map[k] != k_map[k + P]:
                    ok = False
                    break
            if ok:
                best_P = P
                break
        if best_P is not None:
            periodic_count += 1
            P_sim = best_P if best_P % 2 == 0 else 2 * best_P
            rule = {}
            for k in range(37 - P_sim, 37):
                rule[k % P_sim] = k_map[k]
            k_cur = 20 if '1RB0RG_1RC1RB_0RD' in tm else 21
            I_cur = 1 if '1RB0RG_1RC1RB_0RD' in tm else 0
            traj = []
            halted_r = None
            for r in range(1, 15):
                A_r = A_ODD if I_cur == 1 else A_EVEN
                if r == 1 and k_cur in k_map:
                    st, dL, I_ev, d0 = k_map[k_cur]
                else:
                    st, dL, I_ev, d0 = rule[k_cur % P_sim]
                traj.append(f'R{r}(k%{P_sim}={k_cur%P_sim},I={I_cur})->{st}')
                if st.startswith('H'):
                    halted_r = r
                    break
                if dL is None or d0 != 1:
                    break
                N_r = (3 * A_r + 1 - k_cur) % M
                k_next = (N_r + dL) % M
                I_next = (I_ev + N_r) % 2
                k_cur, I_cur = k_next, I_next
            if halted_r is not None or best_P >= 3:
                traj_str = " ; ".join(traj[:6])
                print(f'  [{idx:3d}] {sub:22s} | {tm} | P={best_P:2d} | H_at={{{h_list}}} | halt_R={halted_r} | {traj_str}')
        else:
            nonperiodic.append((idx, sub, tm, h_list, k_map))
    print(f'  Periodic: {periodic_count}/{len(res)}, Non-periodic (or P>=16): {len(nonperiodic)}')
    for idx, sub, tm, h_list, k_map in nonperiodic:
        h_ks = [int(x) for x in h_list.split(',') if x.strip()]
        print(f'  NON-PER [{idx:3d}] {sub:22s} | {tm} | H_at={{{h_list}}}')
        # print k=18..36 summary
        s = " ".join(f"k{k}:{k_map[k][0]}({k_map[k][1]},I{k_map[k][2]})" if k_map[k][1] is not None else f"k{k}:{k_map[k][0]}" for k in range(18, 37) if k in k_map)
        print(f'          {s}')
