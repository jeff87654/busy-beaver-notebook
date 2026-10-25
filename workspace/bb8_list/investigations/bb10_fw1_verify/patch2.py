s=open('sim.cpp').read()
s=s.replace("""    std::vector<char> ev(2 * n, 0);
""","""    std::vector<char> ev(2 * n, 0); bool bstop = false;
""")
s=s.replace("""while (std::getline(ss, e, ',')) ev[2 * (e[0] - 'A') + (e[1] - '0')] = e.size() > 2 ? (e[2] == 'r' ? 2 : 3) : 1; }""",
"""while (std::getline(ss, e, ',')) { if (e == "Bf") { bstop = true; continue; }
        ev[2 * (e[0] - 'A') + (e[1] - '0')] = e.size() > 2 ? (e[2] == 'r' ? 2 : 3) : 1; } }""")
s=s.replace("""            const Tr &tr = t[k];
            if (!tr.def) {""","""            if (bstop && q == 6 && c == 0 && Rc == 0 && step > 0 && isB(h)) {
                dumpword(h, out, rel);
                printf("BF %s %lld %lld %s\n", lab.c_str(), step, rel, out.c_str()); fflush(stdout); done = true; break;
            }
            const Tr &tr = t[k];
            if (!tr.def) {""")
s=s.replace("""int main(int argc, char **argv) {""","""// B-form test: head on a 0 with no 1 to its right; tape = list tokens, D0, D(A), head right after.
static bool isB(long long h) {
    long long p = h - 1; if (p < lo || !tape[p]) return false;
    long long q = p - 1; while (q - 1 >= lo && tape[q] == 0 && tape[q - 1] == 1) q -= 2;
    if (q < lo || tape[q] != 1) return false;           // q = the D0 separator
    long long s = q - 1;                                  // last cell of the list (or blank)
    long long a = lo; while (a <= s && !tape[a]) ++a;     // leftmost 1
    if (a > s) return true;                               // empty list
    if (!tape[s]) return false;
    for (long long i = a; i < s; ++i) if (!tape[i] && !tape[i + 1]) return false;
    return true;
}

int main(int argc, char **argv) {""")
open('sim.cpp','w').write(s)
