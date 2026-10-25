// usage IN OUT MAXSTEPS: literal blank-tape run of each machine (any #states); per machine prints
// machine, status (HALT step / RUN / TAPE), number of defined slots, unused defined slots, step of the last first-use.
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <windows.h>
typedef long long ll;
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    FILE *in = fopen(argv[1], "r"), *out = fopen(argv[2], "w"); ll maxs = atoll(argv[3]);
    const ll SZ = 1LL << 27; std::vector<unsigned char> T(SZ);
    char line[512];
    while (fgets(line, sizeof line, in)) {
        std::string m = line; while (!m.empty() && (m.back() == '\n' || m.back() == '\r' || m.back() == ' ')) m.pop_back();
        size_t tab = m.find('\t'); if (tab != std::string::npos) m = m.substr(0, tab);
        int n = (m.size() + 1) / 7; if (n < 2 || (int)m.size() != 7 * n - 1) continue;
        int W[16][2], D[16][2], N[16][2];
        for (int q = 0; q < n; ++q) for (int c = 0; c < 2; ++c) { const char *t = m.c_str() + 7 * q + 3 * c;
            if (t[0] == '-' || t[2] == 'Z' || t[2] == '-') { N[q][c] = -1; continue; } W[q][c] = t[0] - '0'; D[q][c] = t[1] == 'R' ? 1 : -1; N[q][c] = t[2] - 'A'; }
        std::fill(T.begin(), T.end(), 0);
        ll first[16][2]; for (int q = 0; q < 16; ++q) first[q][0] = first[q][1] = -1;
        ll p = SZ / 2; int q = 0; ll st = 0; std::string status = "RUN";
        for (; st < maxs; ++st) {
            if (p <= 1 || p >= SZ - 2) { status = "TAPE"; break; }
            int c = T[p];
            if (N[q][c] < 0) { status = "HALT"; break; }
            if (first[q][c] < 0) first[q][c] = st;
            T[p] = W[q][c]; p += D[q][c]; q = N[q][c];
        }
        int def = 0; ll last = 0; std::string un;
        for (int a = 0; a < n; ++a) for (int c = 0; c < 2; ++c) { if (N[a][c] < 0) continue; ++def;
            if (first[a][c] < 0) { if (!un.empty()) un += ","; un += char('A' + a); un += char('0' + c); } else if (first[a][c] > last) last = first[a][c]; }
        fprintf(out, "%s\t%s\t%lld\t%d\t%s\t%lld\n", m.c_str(), status.c_str(), st, def, un.empty() ? "-" : un.c_str(), last);
        fflush(out);
    }
}
