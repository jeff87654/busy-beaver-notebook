from inspect_post_m5_2 import run_inspect

for name, tm, ks in [
    ("G3_0LE0LF", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_0LE0LF", [11]),
    ("G4_1LF0LI", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_1LF0LI", [8, 20]),
    ("G7_1LD0LI", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LD0LI_1LH---", [5, 6, 7, 8, 9, 10, 20]),
    ("G8_1LD1LI", "1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LD1LI_0LH---", [5, 6, 7, 8, 9, 10, 20]),
    ("G9_F2_0LH_0RE", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RI_---0RE_1RH1RB", [5, 6, 7, 8, 9, 10, 20]),
]:
    print(f"================ {name}: {tm} ================")
    for k in ks:
        run_inspect(tm, k, 2 * k + 10, CAPX=0)
