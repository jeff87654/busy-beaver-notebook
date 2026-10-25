// h14verify literal stage runner. Reads jobs from stdin, one per line:
//   TM STATE HEAD MAXSTEPS TAPE      (TAPE = bit string; HEAD = index into TAPE, may equal len)
// Runs until the next B-form (state H, head on the cell right of the last 1, word ends in D0 D(A) as a token
// suffix '1' + '(10)^A 1' preceded by a '1' or '0' or nothing), or an undefined slot, or MAXSTEPS.
// Prints: KIND STEPS STATE HEADREL TAPE  (TAPE = trimmed word from first 1 to last 1, HEADREL = head - first1)
// KIND: B (B-form), H (halt: STATE = state, extra field = symbol read), T (timeout)
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
#include <cstdlib>
using namespace std;
int main(){
    ios::sync_with_stdio(false);
    string tm, st, tape; long long head, maxs;
    while (cin >> tm >> st >> head >> maxs >> tape){
        if (tape == "-") tape = "";
        int nq = 0; int W[32][2], Mv[32][2], NQ[32][2]; bool def[32][2];
        size_t p = 0;
        for (int q = 0;; q++){
            for (int s = 0; s < 2; s++){
                const char* e = tm.c_str() + p + 3*s;
                if (e[0] == '-'){ def[q][s] = false; }
                else { def[q][s] = true; W[q][s] = e[0]-'0'; Mv[q][s] = e[1]=='R' ? 1 : -1; NQ[q][s] = e[2]-'A'; }
            }
            nq++; p += 6; if (p >= tm.size()) break; p++; // skip '_'
        }
        long long PAD = 1<<20;
        long long n = tape.size();
        vector<unsigned char> t(n + 2*PAD + 16, 0);
        for (long long i = 0; i < n; i++) t[PAD+i] = tape[i]-'0';
        long long h = PAD + head; int q = st[0]-'A';
        long long r1 = PAD + n + 2; // upper bound of rightmost 1
        long long lo = PAD, hi = PAD + n; // visited range
        long long steps = 0; char kind = 'T'; int hsym = -1;
        const int RING = 64; const int PMAX = 30; int hq[64], hr[64], hw[64], hd[64]; int hp = 0, nh = 0; long long accn = 0;
        static int ACC = getenv("USEACC") ? 1 : 0;
        const int QH = 'H' - 'A';
        while (steps < maxs){
            if (h <= 2 || h >= (long long)t.size()-3){
                if ((long long)t.size() > 400000000LL){ kind = 'X'; break; }
                // grow
                long long add = t.size();
                vector<unsigned char> t2(t.size() + 2*add, 0);
                memcpy(&t2[add], &t[0], t.size());
                t.swap(t2); h += add; r1 += add; lo += add; hi += add; PAD += add;
            }
            int s = t[h];
            if (q == QH && s == 0 && t[h-1] == 1){
                // is everything right of h zero?
                bool z = true;
                if (h <= r1){ for (long long i = h; i <= r1; i++) if (t[i]){ z = false; break; } if (z) r1 = h-1; }
                if (z && steps > 0){
                    long long j = h-1;
                    while (t[j-1] == 0 && t[j-2] == 1) j -= 2;
                    bool ok = (t[j-1] == 1) && !(t[j-2] == 0 && t[j-3] == 1);
                    if (ok){ kind = 'B'; break; }
                }
            }
            if (!def[q][s]){ kind = 'H'; hsym = s; break; }
            if (ACC && nh >= 2){
                int d = Mv[q][s];
                // try periods p = 1..PMAX: history entries 0..p-1 (most recent first) all moved d, state p ago == q
                for (int p = 1; p <= PMAX && p <= nh; p++){
                    int e = (hp - p + RING) % RING;           // entry p steps ago
                    if (hq[e] != q) continue;
                    bool mono = true; bool r1s = false, w1s = false;
                    for (int i = 1; i <= p; i++){ int f = (hp - i + RING) % RING; if (hd[f] != d){ mono = false; break; } if (hr[f]) r1s = true; if (hw[f]) w1s = true; }
                    if (!mono) break;   // a longer period would include this non-monotone step too
                    if (d == 1 ? !r1s : !w1s) continue;
                    // reads of the last period, oldest first: entry (hp-p .. hp-1)
                    unsigned char rb[64], wb[64];
                    for (int i = 0; i < p; i++){ int f = (hp - p + i + RING) % RING; rb[i] = hr[f]; wb[i] = hw[f]; }
                    // count full repetitions ahead
                    long long need = 0; long long pos = h;
                    long long maxrep = (maxs - steps) / p - 1;
                    while (need < maxrep){
                        long long endpos = pos + (long long)d * (p - 1);
                        if (endpos < 4 || endpos >= (long long)t.size() - 4) break;
                        bool ok = true;
                        for (int i = 0; i < p; i++) if (t[pos + (long long)d * i] != rb[i]){ ok = false; break; }
                        if (!ok) break;
                        need++; pos += (long long)d * p;
                    }
                    if (need >= 2){
                        long long pos2 = h;
                        for (long long j = 0; j < need; j++){ for (int i = 0; i < p; i++){ t[pos2 + (long long)d * i] = wb[i]; if (wb[i] && pos2 + (long long)d*i > r1) r1 = pos2 + (long long)d*i; } pos2 += (long long)d * p; }
                        h = pos2; steps += need * p; accn++;
                        if (h < lo) lo = h; if (h > hi) hi = h;
                        goto next;   // state unchanged (q), history still valid (same periodic entries)
                    }
                    break;
                }
            }
            {
            int e = hp; hq[e] = q; hr[e] = s; hw[e] = W[q][s]; hd[e] = Mv[q][s]; hp = (hp + 1) % RING; if (nh < RING) nh++;
            }
            t[h] = W[q][s]; if (W[q][s] && h > r1) r1 = h;
            h += Mv[q][s]; q = NQ[q][s]; steps++;
            next: ;
            if (h < lo) lo = h; if (h > hi) hi = h;
        }
        // output trimmed word
        long long a = -1, b = -1;
        for (long long i = 0; i < (long long)t.size(); i++) if (t[i]){ a = i; break; }
        for (long long i = t.size()-1; i >= 0; i--) if (t[i]){ b = i; break; }
        string out;
        if (a >= 0){ out.resize(b-a+1); for (long long i = a; i <= b; i++) out[i-a] = '0'+t[i]; }
        else { out = "-"; a = h; }
        printf("%c %lld %c %lld %d %lld %s\n", kind, steps, 'A'+q, h - a, hsym, (lo - PAD) , out.c_str());
        fflush(stdout);
    }
}
