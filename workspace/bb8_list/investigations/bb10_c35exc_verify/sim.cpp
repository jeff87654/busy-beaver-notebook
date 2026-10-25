// sim.cpp -- independent literal simulator for the c35 exception check (bb10_c35exc_verify).
// Usage:
//   sim MACHINE LEFT STATE RIGHT MAXSTEPS [opts...]
//   sim batch            (one job per stdin line, same fields; each job's output ends with DONE)
//     LEFT  : cells left of the head ('-' for none), leftmost first
//     RIGHT : head cell and cells to its right ('-' = blank head cell)
//   opts:
//     stop=XY      stop BEFORE executing transition (state X, read Y), e.g. stop=E0 (repeatable)
//     snap=XY      print a snapshot each time the machine is about to execute (X,Y) AND every cell
//                  right of the head is blank (head at the right edge)   (repeatable)
//     snapL=XY     same, but every cell left of the head is blank (left edge)
//     snapany=XY   snapshot every time (X,Y) is about to execute
//     hist=XY      histogram of the 3+3 cells around the head (and right-edge flag) at each (X,Y)
//     maxsnap=N    stop after N snapshots
//     quiet        do not print the final tape
// Output lines:  SNAP step tape  /  HIST ...  /  END reason step tape
// 'tape' is printed as LEFT|STATE|RIGHT with blanks trimmed at both ends (head cell always printed).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <cstdint>
using namespace std;

static int NS;
static int wr[32][2], mv[32][2], nx[32][2];  // nx = -1 : undefined (halt)

static void parse_machine(const char* m) {
    // format 1RB0RA_1LC1LF_..., '---' undefined
    NS = 0;
    const char* p = m;
    while (*p) {
        for (int s = 0; s < 2; s++) {
            if (p[0] == '-') { wr[NS][s] = 1; mv[NS][s] = 1; nx[NS][s] = -1; }
            else {
                wr[NS][s] = p[0] - '0';
                mv[NS][s] = (p[1] == 'R') ? 1 : -1;
                nx[NS][s] = (p[2] == 'Z') ? -1 : p[2] - 'A';
            }
            p += 3;
        }
        NS++;
        if (*p == '_') p++;
    }
}

struct Tape {
    vector<uint8_t> t;
    long long off;  // index of position 0
    void ensure(long long pos) {
        long long i = pos + off;
        if (i < 0) {
            long long add = t.size() > 0 ? (long long)t.size() : 1024;
            while (i + add < 0) add *= 2;
            vector<uint8_t> n(t.size() + add, 0);
            memcpy(n.data() + add, t.data(), t.size());
            t.swap(n);
            off += add;
        } else if (i >= (long long)t.size()) {
            long long add = t.size() > 0 ? (long long)t.size() : 1024;
            while (i >= (long long)t.size() + add) add *= 2;
            t.resize(t.size() + add, 0);
        }
    }
};

static long long lo_nz, hi_nz;  // conservative bounds of nonzero region (positions)

static string dump(Tape& T, long long head, int st) {
    long long a = lo_nz, b = hi_nz;
    while (a <= b && T.t[a + T.off] == 0) a++;
    while (b >= a && T.t[b + T.off] == 0) b--;
    string L, R;
    if (a > b) { a = head; b = head - 1; }
    long long from = min(a, head), to = max(b, head);
    for (long long p = from; p < head; p++) L += char('0' + T.t[p + T.off]);
    for (long long p = head; p <= to; p++) R += char('0' + T.t[p + T.off]);
    if (L.empty()) L = "-";
    string s = L + "|" + char('A' + st) + "|" + R;
    return s;
}

static long long hcount[32][2][128];

static int run_job(int argc, char** argv) {
    if (argc < 6) { fprintf(stderr, "usage\n"); return 1; }
    parse_machine(argv[1]);
    string L = argv[2], R = argv[4];
    int st = argv[3][0] - 'A';
    long long maxsteps = atoll(argv[5]);
    vector<pair<int,int>> stops, snaps, snapsL, snapsAny, hists;
    long long maxsnap = -1; bool quiet = false, bform = false;
    for (int i = 6; i < argc; i++) {
        string o = argv[i];
        auto xy = [&](const string& v) { return make_pair(v[0] - 'A', v[1] - '0'); };
        if (o.rfind("stop=", 0) == 0) stops.push_back(xy(o.substr(5)));
        else if (o.rfind("snapL=", 0) == 0) snapsL.push_back(xy(o.substr(6)));
        else if (o.rfind("snapany=", 0) == 0) snapsAny.push_back(xy(o.substr(8)));
        else if (o.rfind("snap=", 0) == 0) snaps.push_back(xy(o.substr(5)));
        else if (o.rfind("maxsnap=", 0) == 0) maxsnap = atoll(o.substr(8).c_str());
        else if (o.rfind("hist=", 0) == 0) hists.push_back(xy(o.substr(5)));
        else if (o == "quiet") quiet = true;
        else if (o == "bform") bform = true;
        else { fprintf(stderr, "bad opt %s\n", o.c_str()); return 1; }
    }
    if (L == "-") L = "";
    if (R == "-") R = "0";
    Tape T; T.t.assign(1 << 16, 0); T.off = 1 << 15;
    long long head = 0;
    long long n = (long long)L.size();
    T.ensure(-n - 16); T.ensure((long long)R.size() + 16);
    for (long long i = 0; i < n; i++) T.t[-n + i + T.off] = L[i] - '0';
    for (size_t i = 0; i < R.size(); i++) T.t[i + T.off] = R[i] - '0';
    lo_nz = -n; hi_nz = (long long)R.size() - 1;
    if (hi_nz < 0) hi_nz = 0;
    if (lo_nz > 0) lo_nz = 0;
    bool isStop[32][2] = {}, isSnap[32][2] = {}, isSnapL[32][2] = {}, isAny[32][2] = {}, isHist[32][2] = {};
    for (auto& p : stops) isStop[p.first][p.second] = true;
    for (auto& p : snaps) isSnap[p.first][p.second] = true;
    for (auto& p : snapsL) isSnapL[p.first][p.second] = true;
    for (auto& p : snapsAny) isAny[p.first][p.second] = true;
    for (auto& p : hists) isHist[p.first][p.second] = true;
    memset(hcount, 0, sizeof(hcount));
    bool anyCheck = !stops.empty() || !snaps.empty() || !snapsL.empty() || !snapsAny.empty() || !hists.empty();
    long long step = 0, nsnap = 0, minhead = 0, minhead_at_snap = 0;
    const char* reason = "LIMIT";
    while (true) {
        if (head < lo_nz || head > hi_nz) {
            T.ensure(head - 8); T.ensure(head + 8);
            if (head < lo_nz) lo_nz = head;
            if (head < minhead) minhead = head;
            if (head > hi_nz) hi_nz = head;
        }
        int sym = T.t[head + T.off];
        if (anyCheck) {
            if (isStop[st][sym]) { reason = "STOP"; break; }
            if (isHist[st][sym]) {
                // key: cells head-3..head-1 (bits 6..4), head+1..head+3 (bits 3..1), right-edge flag (bit 0)
                int key = 0;
                for (int d = -3; d <= -1; d++) key = key * 2 + T.t[head + d + T.off];
                for (int d = 1; d <= 3; d++) key = key * 2 + T.t[head + d + T.off];
                bool edge = true;
                for (long long p = head + 1; p <= hi_nz; p++) if (T.t[p + T.off]) { edge = false; break; }
                key = key * 2 + (edge ? 1 : 0);
                hcount[st][sym][key]++;
            }
            bool doSnap = false;
            if (isAny[st][sym]) doSnap = true;
            if (isSnap[st][sym]) {
                bool ok = true;
                for (long long p = head + 1; p <= hi_nz; p++) if (T.t[p + T.off]) { ok = false; break; }
                if (ok && bform) {
                    // B-form: ... 1 (01)^y head  with the '1' a D0 token (preceded by 1 or blank)
                    long long p = head - 1;
                    while (p - 1 >= lo_nz && T.t[p + T.off] == 1 && T.t[p - 1 + T.off] == 0) p -= 2;
                    if (!(T.t[p + T.off] == 1 && T.t[p - 1 + T.off] == 1 && (T.t[p - 2 + T.off] == 1 || T.t[p - 3 + T.off] == 0))) ok = false;
                }
                if (ok) doSnap = true;
            }
            if (isSnapL[st][sym]) {
                bool ok = true;
                for (long long p = head - 1; p >= lo_nz; p--) if (T.t[p + T.off]) { ok = false; break; }
                if (ok) doSnap = true;
            }
            if (doSnap) {
                string s = dump(T, head, st);
                printf("SNAP %lld %s %lld\n", step, s.c_str(), minhead);
                nsnap++;
                if (maxsnap >= 0 && nsnap >= maxsnap) { reason = "MAXSNAP"; break; }
            }
        }
        if (nx[st][sym] < 0) { reason = "HALT"; break; }
        if (step >= maxsteps) { reason = "LIMIT"; break; }
        T.t[head + T.off] = wr[st][sym];
        head += mv[st][sym];
        st = nx[st][sym];
        step++;
    }
    for (int a = 0; a < 32; a++) for (int b = 0; b < 2; b++) if (isHist[a][b])
        for (int k = 0; k < 128; k++) if (hcount[a][b][k]) {
            printf("HIST %c%d %d%d%d_%d%d%d %s %lld\n", 'A' + a, b, (k >> 6) & 1, (k >> 5) & 1, (k >> 4) & 1,
                   (k >> 3) & 1, (k >> 2) & 1, (k >> 1) & 1, (k & 1) ? "edge" : "inner", hcount[a][b][k]);
        }
    if (!quiet) printf("END %s %lld %s\n", reason, step, dump(T, head, st).c_str());
    else printf("END %s %lld\n", reason, step);
    return 0;
}

int main(int argc, char** argv) {
    if (argc >= 2 && string(argv[1]) == "batch") {
        string line;
        int c = 0;
        while (c != EOF) {
            line.clear();
            while ((c = getchar()) != EOF && c != '\n') if (c != '\r') line += (char)c;
            if (line.empty()) continue;
            vector<string> parts; size_t i = 0;
            while (i < line.size()) {
                size_t j = line.find(' ', i);
                if (j == string::npos) j = line.size();
                if (j > i) parts.push_back(line.substr(i, j - i));
                i = j + 1;
            }
            vector<char*> av; av.push_back(argv[0]);
            for (auto& q : parts) av.push_back((char*)q.c_str());
            run_job((int)av.size(), av.data());
            printf("DONE\n");
            fflush(stdout);
        }
        return 0;
    }
    return run_job(argc, argv);
}
