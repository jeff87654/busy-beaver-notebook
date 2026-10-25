#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <windows.h>

struct Tr { int w, d, nx; };

int main() {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    const char *base_str = "1RB0LE_0RC1LF_1LD0RD_0LA---_1LA1RG_1RB1RF_0RH0LG_1RE1LD";
    Tr base[16];
    for (int q = 0; q < 8; ++q) {
        for (int c = 0; c < 2; ++c) {
            const char *p = base_str + 7 * q + 3 * c;
            if (p[0] == '-') {
                base[2*q+c] = {0, 0, -1};
            } else {
                base[2*q+c] = {p[0] - '0', p[1] == 'R' ? 1 : -1, p[2] - 'A'};
            }
        }
    }

    const long long MAX_STEPS = 10000000LL; // 10M steps per neighbor
    const long long TAPE_SZ = 1 << 20;
    std::vector<unsigned char> tape(TAPE_SZ, 0);

    int n_halt = 0, n_run = 0, n_ovf = 0;
    long long max_halt_steps = 0;
    std::string best_tm;
    long long best_ones = 0;
    std::vector<std::tuple<long long, long long, std::string, std::string>> late_halters;

    for (int slot = 0; slot < 16; ++slot) {
        if (slot == 7) continue; // D1 is ---
        for (int w = 0; w < 2; ++w) {
            for (int d_idx = 0; d_idx < 2; ++d_idx) {
                int d = d_idx == 0 ? -1 : 1;
                for (int nx = 0; nx < 8; ++nx) {
                    if (w == base[slot].w && d == base[slot].d && nx == base[slot].nx) continue;
                    Tr m[16];
                    memcpy(m, base, sizeof(base));
                    m[slot] = {w, d, nx};

                    long long pos = TAPE_SZ / 2;
                    long long lo = pos, hi = pos;
                    tape[pos] = 0;
                    int q = 0;
                    long long st = 0;
                    bool halted = false, ovf = false;
                    for (; st < MAX_STEPS; ++st) {
                        int c = tape[pos];
                        const Tr &tr = m[2*q + c];
                        if (tr.nx < 0) {
                            halted = true;
                            break;
                        }
                        tape[pos] = tr.w;
                        pos += tr.d;
                        q = tr.nx;
                        if (pos < lo) {
                            if (pos <= 4) { ovf = true; break; }
                            lo = pos;
                            tape[pos] = 0;
                        } else if (pos > hi) {
                            if (pos >= TAPE_SZ - 4) { ovf = true; break; }
                            hi = pos;
                            tape[pos] = 0;
                        }
                    }
                    long long ones = 0;
                    for (long long i = lo; i <= hi; ++i) {
                        ones += tape[i];
                        tape[i] = 0;
                    }
                    if (halted) {
                        n_halt++;
                        if (st > max_halt_steps) {
                            max_halt_steps = st;
                        }
                        if (st >= 100) {
                            std::string s = base_str;
                            int q_s = slot / 2, c_s = slot % 2;
                            int off = 7 * q_s + 3 * c_s;
                            s[off] = char('0' + w);
                            s[off+1] = d > 0 ? 'R' : 'L';
                            s[off+2] = char('A' + nx);
                            char mut[32];
                            snprintf(mut, sizeof(mut), "%c%d->%c%c%c", 'A'+q_s, c_s, '0'+w, d>0?'R':'L', 'A'+nx);
                            late_halters.push_back({st, ones, mut, s});
                        }
                    } else if (ovf) {
                        n_ovf++;
                    } else {
                        n_run++;
                    }
                }
            }
        }
    }
    std::sort(late_halters.rbegin(), late_halters.rend());
    printf("Total neighbors tested: 465 | Halted: %d | Running@10M: %d | TapeOvf: %d | Max halt steps: %lld\n",
           n_halt, n_run, n_ovf, max_halt_steps);
    printf("Halters with >= 100 steps (%zu):\n", late_halters.size());
    for (auto &x : late_halters) {
        printf("  steps=%lld ones=%lld mut=%s tm=%s\n",
               std::get<0>(x), std::get<1>(x), std::get<2>(x).c_str(), std::get<3>(x).c_str());
    }
    return 0;
}
