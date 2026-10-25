// xsim: batch literal simulator.  xsim MACHFILE CONFFILE MAXSTEPS [-u] [-s SNAPSTEPS]
//   MACHFILE: one machine per line (standard text format, up to 16 states; '---' undefined = halt)
//   CONFFILE: line 1 "STATE HEAD", line 2 the tape as 0/1 characters (cell 0 = first character)
// Output per machine:  machine H steps state read ones minpos maxpos      (halted: undefined transition reached)
//                      machine T steps state read ones minpos maxpos      (MAXSTEPS reached)
// -u: also print the used-transition mask (letters, lowercase = read 0, uppercase = read 1) and first-use steps.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

struct Tr { int w, d, nx; bool def; };

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage\n"); return 2; }
    long long maxs = atoll(argv[3]);
    bool usage = false, dumpt = false, pairs = false;
    for (int i = 4; i < argc; ++i) { if (!strcmp(argv[i], "-u")) usage = true; if (!strcmp(argv[i], "-d")) dumpt = true; if (!strcmp(argv[i], "-p")) pairs = true; }
    FILE *cf = fopen(argv[2], "r"); if (!cf) return 2;
    char st; long long head; if (fscanf(cf, " %c %lld", &st, &head) != 2) return 2;
    std::string init; { int ch; while ((ch = fgetc(cf)) != EOF) if (ch == '0' || ch == '1') init.push_back((char)ch); }
    fclose(cf);
    FILE *mf = fopen(argv[1], "r"); if (!mf) return 2;
    char line[512];
    while (fgets(line, sizeof line, mf)) {
        std::string m = line; while (!m.empty() && (m.back() == '\n' || m.back() == '\r' || m.back() == ' ')) m.pop_back();
        if (m.empty()) continue;
        std::vector<Tr> T; int ns = 0;
        {
            size_t p = 0; std::string s;
            for (size_t k = 0; k <= m.size(); ++k) if (k == m.size() || m[k] == '_') {
                s = m.substr(p, k - p); p = k + 1; ++ns;
                for (int r = 0; r < 2; ++r) {
                    std::string c = s.substr(3 * r, 3);
                    Tr t{0, 0, 0, false};
                    if (c[2] >= 'A' && c[2] <= 'Z' && c[0] != '-') { t.w = c[0] - '0'; t.d = c[1] == 'R' ? 1 : -1; t.nx = c[2] - 'A'; t.def = true; }
                    T.push_back(t);
                }
            }
        }
        long long OFF = 1 << 20;
        std::vector<unsigned char> tp(init.size() + 2 * OFF, 0);
        for (size_t i = 0; i < init.size(); ++i) tp[OFF + i] = init[i] - '0';
        long long pos = OFF + head, mn = pos, mx = pos; int q = st - 'A';
        long long ones = 0; for (char c : init) ones += c == '1';
        std::vector<long long> first(2 * ns, -1);
        long long step = 0; bool halted = false;
        // -p: number of "11" pairs on the tape (token boundaries of D-token lists), its start value and maximum
        long long np = 0, np0 = 0, npmax = 0, npmax_step = 0;
        if (pairs) { for (size_t i = 0; i + 1 < tp.size(); ++i) np += tp[i] & tp[i + 1]; np0 = npmax = np; }
        while (step < maxs) {
            if (pos <= 0 || pos >= (long long)tp.size() - 1) {
                long long grow = tp.size();
                std::vector<unsigned char> n2(tp.size() + 2 * grow, 0);
                memcpy(&n2[grow], &tp[0], tp.size()); tp.swap(n2); pos += grow; mn += grow; mx += grow; OFF += grow;
            }
            int s = tp[pos];
            const Tr &t = T[2 * q + s];
            if (usage && first[2 * q + s] < 0) first[2 * q + s] = step;
            if (!t.def) { halted = true; break; }
            if (pairs && t.w != s) {
                long long before = (tp[pos - 1] & s) + (s & tp[pos + 1]);
                long long after = (tp[pos - 1] & t.w) + (t.w & tp[pos + 1]);
                np += after - before;
                if (np > npmax) { npmax = np; npmax_step = step; }
            }
            ones += t.w - s; tp[pos] = t.w; pos += t.d; q = t.nx; ++step;
            if (pos < mn) mn = pos; if (pos > mx) mx = pos;
        }
        printf("%s %c %lld %c %d %lld %lld %lld", m.c_str(), halted ? 'H' : 'T', step, 'A' + q, (int)tp[pos], ones, mn - OFF, mx - OFF);
        if (usage) {
            printf(" used=");
            for (int k = 0; k < 2 * ns; ++k) if (first[k] >= 0) printf("%c%c:%lld,", 'A' + k / 2, k % 2 ? '1' : '0', first[k]);
        }
        if (pairs) printf(" pairs0=%lld pairs=%lld pairsmax=%lld@%lld", np0, np, npmax, npmax_step);
        if (dumpt) {
            long long a = pos, b = pos;
            for (long long i = 0; i < (long long)tp.size(); ++i) if (tp[i]) { if (i < a) a = i; break; }
            for (long long i = (long long)tp.size() - 1; i >= 0; --i) if (tp[i]) { if (i > b) b = i; break; }
            printf(" headoff=%lld tape=", pos - a);
            for (long long i = a; i <= b; ++i) putchar('0' + tp[i]);
        }
        printf("\n");
        fflush(stdout);
    }
    return 0;
}
