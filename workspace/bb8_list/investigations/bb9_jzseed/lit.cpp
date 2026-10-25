// lit.cpp: plain literal TM simulator (validation reference for symsim).  Same input format as symsim
// ("MACHINE START [TAPESPEC]", exact counts only), halting convention: an undefined/halt slot writes 1 and stops.
//   lit BUDGET < input      prints "L machine start HALT|BUDGET steps sigma" and "TAPE state headidx cells"
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
struct Tr { int w, d, nx; bool halt; };
int main(int argc, char **argv) {
    ll budget = argc > 1 ? atoll(argv[1]) : 1000000;
    string line;
    while (getline(cin, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        istringstream is(line); string m, st; if (!(is >> m >> st)) continue;
        int ns = (int)(m.size() + 1) / 7; Tr T[16][2];
        for (int q = 0; q < ns; ++q) for (int c = 0; c < 2; ++c) {
            const char *x = m.c_str() + 7 * q + 3 * c;
            if (x[0] == '-' || x[2] == '-' || x[2] == 'Z' || x[2] - 'A' >= ns) T[q][c] = Tr{1, 1, -1, true};
            else T[q][c] = Tr{x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', false};
        }
        string cells; ll head = -1; int q = st[0] - 'A'; string t;
        while (is >> t) {
            if (t.size() == 2 && t[1] == '>') { head = cells.size(); q = t[0] - 'A'; continue; }
            size_t h = t.find('^'); string w = t.substr(0, h); ll n = h == string::npos ? 1 : atoll(t.c_str() + h + 1);
            for (ll i = 0; i < n; ++i) cells += w;
        }
        if (head < 0) head = cells.size();
        ll N = 1 << 22; vector<unsigned char> tape; ll off = N / 2;
        tape.assign(N, 0);
        for (size_t i = 0; i < cells.size(); ++i) tape[off + i] = cells[i] - '0';
        ll pos = off + head, steps = 0; bool halted = false;
        while (steps < budget) {
            if (pos <= 0 || pos >= (ll)tape.size() - 1) {   // grow
                ll add = tape.size(); vector<unsigned char> nt(tape.size() + 2 * add, 0);
                memcpy(&nt[add], tape.data(), tape.size()); tape.swap(nt); pos += add; off += add;
            }
            int c = tape[pos]; const Tr &tr = T[q][c];
            if (tr.halt) { tape[pos] = 1; ++steps; halted = true; break; }
            tape[pos] = tr.w; pos += tr.d; q = tr.nx; ++steps;
        }
        ll a = -1, b = -1, sig = 0;
        for (ll i = 0; i < (ll)tape.size(); ++i) if (tape[i]) { if (a < 0) a = i; b = i; ++sig; }
        printf("L %s %s %s %lld %lld\n", m.c_str(), st.c_str(), halted ? "HALT" : "BUDGET", steps, sig);
        if (!halted) printf("TAPE notshown\n");
        else if (a < 0) printf("TAPE %c 0 -\n", 'A' + q);
        else { string s; for (ll i = a; i <= b; ++i) s += char('0' + tape[i]); printf("TAPE %c %lld %s\n", 'A' + q, pos - a, s.c_str()); }
        fflush(stdout);
    }
    return 0;
}
