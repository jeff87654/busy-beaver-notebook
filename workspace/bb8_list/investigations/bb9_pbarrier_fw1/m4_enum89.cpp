#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>

// M4 (unmirrored): 1RB---_1RC0RC_0LD0LE_1RA0LE_0RF1LC_1RG0RC_---1RE
// In mirrored coordinates (L=+1, R=-1):
// A0: 1LB(w=1,d=-1,nx=1), A1: UNASSIGNED
// B0: 1LC(w=1,d=-1,nx=2), B1: 0LC(w=0,d=-1,nx=2)
// C0: 0RD(w=0,d=+1,nx=3), C1: 0RE(w=0,d=+1,nx=4)
// D0: 1LA(w=1,d=-1,nx=0), D1: 0RE(w=0,d=+1,nx=4)
// E0: 0LF(w=0,d=-1,nx=5), E1: 1RC(w=1,d=+1,nx=2)
// F0: 1LG(w=1,d=-1,nx=6), F1: 0LC(w=0,d=-1,nx=2)
// G0: UNASSIGNED,         G1: 1LE(w=1,d=-1,nx=4)

struct Trans {
    int w, d, nx; // d in mirrored coords (-1 = R_orig, +1 = L_orig); nx = -1 HALT, -2 UNASSIGNED
};

// Compute exact N if <= 30, else -1, and set out_mod192 = N mod 192 (since 192 = 3 * 64)
int compute_next_N(const std::vector<int>& ds_in, int a_in, int& out_mod192) {
    std::vector<int> ds = ds_in;
    long long a = a_in;
    int m = (int)ds.size();

    // Try direct macro-step simulation for up to 60 steps if values stay small
    for (int step = 0; step < 60; ++step) {
        if (ds.empty()) {
            long long N = 2 * a + 4;
            out_mod192 = (int)(N % 192);
            return (N <= 30) ? (int)N : -1;
        }
        // Find last nonzero in ds
        int last_nz = -1;
        for (int i = (int)ds.size() - 1; i >= 0; --i) {
            if (ds[i] > 0) { last_nz = i; break; }
        }
        if (last_nz == -1) {
            // ds = [0^k]
            int k = (int)ds.size();
            if (k <= 20 && a <= 1000) {
                long long N = ((a + 1) << (k + 1)) + 2;
                out_mod192 = (int)(N % 192);
                return (N <= 30) ? (int)N : -1;
            } else {
                // N = 2^(k+1)*(a+1) + 2
                long long p2 = 1;
                for (int i = 0; i < k + 1; ++i) p2 = (p2 * 2) % 192;
                out_mod192 = (int)((p2 * ((a + 1) % 192) + 2) % 192);
                return -1;
            }
        }
        if (last_nz == (int)ds.size() - 1) {
            // Rule 1: ds.back() > 0: d -> d-1, a -> 2a+2
            int d = ds.back();
            if (d <= 15 && a <= 1000) {
                a = ((a + 2) << d) - 2;
                ds.back() = 0;
            } else {
                // Huge! Will finish this digit at A = (a+2)*2^d - 2.
                // Check if there are any other nonzero digits to the left
                bool other_nz = false;
                for (int i = 0; i < last_nz; ++i) if (ds[i] > 0) other_nz = true;
                if (!other_nz) {
                    // Only this digit! N = (a+2)*2^(d + m + 1) - 2^(m+1) + 2
                    long long p2_hi = 1;
                    for (int i = 0; i < d + m + 1; ++i) p2_hi = (p2_hi * 2) % 192;
                    long long p2_lo = 1;
                    for (int i = 0; i < m + 1; ++i) p2_lo = (p2_lo * 2) % 192;
                    long long mod = ((a + 2) % 192) * p2_hi - p2_lo + 2;
                    out_mod192 = (int)((mod % 192 + 192) % 192);
                    return -1;
                } else {
                    // Other nonzero digits exist to the left, so Rule 2 will fire at the end!
                    long long p2_lo = 1;
                    for (int i = 0; i < m + 1; ++i) p2_lo = (p2_lo * 2) % 192;
                    long long mod = 2 - p2_lo;
                    out_mod192 = (int)((mod % 192 + 192) % 192);
                    return -1;
                }
            }
        } else {
            // Rule 2: last_nz < ds.size() - 1
            if (a > 1000) {
                long long p2_lo = 1;
                for (int i = 0; i < m + 1; ++i) p2_lo = (p2_lo * 2) % 192;
                long long mod = 2 - p2_lo;
                out_mod192 = (int)((mod % 192 + 192) % 192);
                return -1;
            }
            ds[last_nz]--;
            ds[last_nz + 1] = (int)(2 * a + 1);
            for (size_t i = last_nz + 2; i < ds.size(); ++i) ds[i] = 1;
            a = 1;
        }
    }
    long long p2_lo = 1;
    for (int i = 0; i < m + 1; ++i) p2_lo = (p2_lo * 2) % 192;
    long long mod = 2 - p2_lo;
    out_mod192 = (int)((mod % 192 + 192) % 192);
    return -1;
}

struct RunResult {
    int status; // 0 = LOOP/BAD, 1 = HALT, 2 = C0_B1, 3 = UNASSIGNED
    int unass_slot;
    int steps;
    std::vector<int> ds;
    int a;
};

// Run from 0^inf [G0] 10 (110)^N 0^inf (mirrored) until C0 end-moment with b=1
RunResult run_g0(const Trans* tr, int N, int max_steps = 2500) {
    const int OFFSET = 512;
    const int TSIZE = 2048;
    unsigned char tape[TSIZE];
    memset(tape, 0, sizeof(tape));
    tape[OFFSET + 1] = 1;
    tape[OFFSET + 2] = 0;
    for (int j = 0; j < N; ++j) {
        tape[OFFSET + 3 + 3 * j] = 1;
        tape[OFFSET + 4 + 3 * j] = 1;
        tape[OFFSET + 5 + 3 * j] = 0;
    }
    int lo = OFFSET + 1;
    int hi = OFFSET + 2 + 3 * N;
    int pos = OFFSET;
    int q = 6; // G0
    for (int st = 1; st <= max_steps; ++st) {
        int c = tape[pos];
        int slot = 2 * q + c;
        const Trans& t = tr[slot];
        if (t.nx == -2) {
            RunResult r;
            r.status = 3;
            r.unass_slot = slot;
            return r;
        }
        if (t.nx == -1) {
            RunResult r;
            r.status = 1;
            r.steps = st;
            return r;
        }
        tape[pos] = (unsigned char)t.w;
        if (t.w) {
            if (pos < lo) lo = pos;
            if (pos > hi) hi = pos;
        }
        pos += t.d;
        if (pos <= 2 || pos >= TSIZE - 2) {
            RunResult r; r.status = 0; return r;
        }
        q = t.nx;

        // Check C0 end-moment with b=1: q == 2, pos > hi (or all cells >= pos are 0),
        // and tape ends with 0 0 1 [C0] (so b=1)
        if (q == 2 && pos >= OFFSET + 4 && tape[pos] == 0 && tape[pos - 1] == 1 && tape[pos - 2] == 0 && tape[pos - 3] == 0) {
            bool clean_right = true;
            for (int i = pos + 1; i <= hi; ++i) {
                if (tape[i]) { clean_right = false; break; }
            }
            if (clean_right) {
                int r_lo = -1;
                for (int i = lo; i <= pos - 1; ++i) {
                    if (tape[i]) { r_lo = i; break; }
                }
                if (r_lo != -1 && r_lo <= pos - 4) {
                    // Decode '1' + ''.join('01'*x + '0' for x in ds + [a]) + '01'
                    // Check from r_lo+1 to pos-3
                    std::vector<int> items;
                    int idx = r_lo + 1;
                    int end_idx = pos - 2; // since pos-2..pos-1 is '01' (b=1)
                    bool ok = true;
                    while (idx < end_idx) {
                        int x = 0;
                        while (idx + 1 < end_idx && tape[idx] == 0 && tape[idx + 1] == 1) {
                            x++;
                            idx += 2;
                        }
                        if (idx < end_idx && tape[idx] == 0) {
                            idx++;
                            items.push_back(x);
                        } else {
                            ok = false;
                            break;
                        }
                    }
                    if (ok && !items.empty()) {
                        RunResult r;
                        r.status = 2;
                        r.steps = st;
                        r.a = items.back();
                        r.ds.assign(items.begin(), items.end() - 1);
                        return r;
                    }
                }
            }
        }
    }
    RunResult r;
    r.status = 0;
    return r;
}

std::string fmt_tm_unmirrored(const Trans* tr, int n_states) {
    std::string s;
    for (int q = 0; q < n_states; ++q) {
        if (q) s += '_';
        for (int c = 0; c < 2; ++c) {
            const Trans& t = tr[2 * q + c];
            if (t.nx < 0) {
                s += "---";
            } else {
                s += (char)('0' + t.w);
                // Flip mirrored d back to original unmirrored d: d == -1 is 'R', d == +1 is 'L'
                s += (t.d == -1) ? 'R' : 'L';
                s += (char)('A' + t.nx);
            }
        }
    }
    return s;
}

long long total_hits_E2 = 0;
long long total_hits_E3 = 0;
long long total_hits_E4plus = 0;

int get_max_state(const Trans* tr, int n_states) {
    int mx = 6; // G is 6
    for (int s = 0; s < 2 * n_states; ++s) {
        if (tr[s].nx > mx) mx = tr[s].nx;
    }
    return mx;
}

void dfs(Trans* tr, int n_states) {
    int cur_exact = 2; // E0: N0 = 2
    int cur_mod192 = 2;
    bool grew_ever = false;

    for (int eb = 0; eb <= 8; ++eb) {
        if (cur_exact != -1) {
            RunResult r = run_g0(tr, cur_exact, 400);
            if (r.status == 3) {
                int sl = r.unass_slot;
                int lim = std::min(n_states - 1, get_max_state(tr, n_states) + 1);
                if (eb >= 2 && grew_ever) {
                    tr[sl] = {0, 1, -1};
                    dfs(tr, n_states);
                }
                for (int w = 0; w < 2; ++w) {
                    for (int d_idx = 0; d_idx < 2; ++d_idx) {
                        int d = d_idx ? 1 : -1;
                        for (int nx = 0; nx <= lim; ++nx) {
                            tr[sl] = {w, d, nx};
                            dfs(tr, n_states);
                        }
                    }
                }
                tr[sl] = {0, 0, -2};
                return;
            }
            if (r.status == 0) return;
            if (r.status == 1) {
                if (eb >= 2 && grew_ever) {
                    if (eb == 2) {
                        total_hits_E2++;
                        if (total_hits_E2 <= 30) {
                            printf("[E2 HALT (%d-state)] %s\n", n_states, fmt_tm_unmirrored(tr, n_states).c_str());
                            fflush(stdout);
                        }
                    } else if (eb == 3) {
                        total_hits_E3++;
                        if (total_hits_E3 <= 30) {
                            printf("[E3 HALT (%d-state)] %s\n", n_states, fmt_tm_unmirrored(tr, n_states).c_str());
                            fflush(stdout);
                        }
                    } else {
                        total_hits_E4plus++;
                        if (total_hits_E4plus <= 50) {
                            printf("[E%d HALT (%d-state) !!!] %s\n", eb, n_states, fmt_tm_unmirrored(tr, n_states).c_str());
                            fflush(stdout);
                        }
                    }
                }
                return;
            }
            int next_mod192 = 0;
            int next_exact = compute_next_N(r.ds, r.a, next_mod192);
            if (next_exact == cur_exact) return;
            if ((int)r.ds.size() >= 10) grew_ever = true;
            cur_exact = next_exact;
            cur_mod192 = next_mod192;
        } else {
            int Na = 64 + (cur_mod192 % 64);
            while (Na % 192 != cur_mod192) Na += 64;
            int Nb = Na + 192;
            RunResult ra = run_g0(tr, Na, 1200);
            if (ra.status == 3) {
                int sl = ra.unass_slot;
                int lim = std::min(n_states - 1, get_max_state(tr, n_states) + 1);
                if (eb >= 2 && grew_ever) {
                    tr[sl] = {0, 1, -1};
                    dfs(tr, n_states);
                }
                for (int w = 0; w < 2; ++w) {
                    for (int d_idx = 0; d_idx < 2; ++d_idx) {
                        int d = d_idx ? 1 : -1;
                        for (int nx = 0; nx <= lim; ++nx) {
                            tr[sl] = {w, d, nx};
                            dfs(tr, n_states);
                        }
                    }
                }
                tr[sl] = {0, 0, -2};
                return;
            }
            if (ra.status == 0) return;
            RunResult rb = run_g0(tr, Nb, 2200);
            if (rb.status == 3) {
                int sl = rb.unass_slot;
                int lim = std::min(n_states - 1, get_max_state(tr, n_states) + 1);
                if (eb >= 2 && grew_ever) {
                    tr[sl] = {0, 1, -1};
                    dfs(tr, n_states);
                }
                for (int w = 0; w < 2; ++w) {
                    for (int d_idx = 0; d_idx < 2; ++d_idx) {
                        int d = d_idx ? 1 : -1;
                        for (int nx = 0; nx <= lim; ++nx) {
                            tr[sl] = {w, d, nx};
                            dfs(tr, n_states);
                        }
                    }
                }
                tr[sl] = {0, 0, -2};
                return;
            }
            if (rb.status != ra.status) return;
            if (ra.status == 1) {
                if (eb >= 2 && grew_ever) {
                    if (eb == 2) {
                        total_hits_E2++;
                        if (total_hits_E2 <= 30) {
                            printf("[E2 HALT (%d-state)] %s\n", n_states, fmt_tm_unmirrored(tr, n_states).c_str());
                            fflush(stdout);
                        }
                    } else if (eb == 3) {
                        total_hits_E3++;
                        if (total_hits_E3 <= 30) {
                            printf("[E3 HALT (%d-state)] %s\n", n_states, fmt_tm_unmirrored(tr, n_states).c_str());
                            fflush(stdout);
                        }
                    } else {
                        total_hits_E4plus++;
                        if (total_hits_E4plus <= 50) {
                            printf("[E%d HALT (%d-state) !!!] %s\n", eb, n_states, fmt_tm_unmirrored(tr, n_states).c_str());
                            fflush(stdout);
                        }
                    }
                }
                return;
            }
            int sum_a = 0, sum_b = 0;
            for (int x : ra.ds) sum_a += x;
            for (int x : rb.ds) sum_b += x;
            if (rb.ds.size() > ra.ds.size() && sum_b > sum_a) {
                grew_ever = true;
            } else if (!grew_ever) {
                return;
            }
            int mod_a = 0, mod_b = 0;
            int ex_a = compute_next_N(ra.ds, ra.a, mod_a);
            int ex_b = compute_next_N(rb.ds, rb.a, mod_b);
            if (mod_a != mod_b) return;
            cur_exact = (ex_a == ex_b) ? ex_a : -1;
            cur_mod192 = mod_a;
        }
    }
}

void setup_m4(Trans* tr, int n_states) {
    for (int s = 0; s < 2 * n_states; ++s) tr[s] = {0, 0, -2};
    // Mirrored M4: 1LB---_1LC0LC_0RD0RE_1LA0RE_0LF1RC_1LG0LC_---1LE
    tr[0] = {1, -1, 1}; tr[1] = {0, 0, -2}; // A
    tr[2] = {1, -1, 2}; tr[3] = {0, -1, 2}; // B
    tr[4] = {0, +1, 3}; tr[5] = {0, +1, 4}; // C
    tr[6] = {1, -1, 0}; tr[7] = {0, +1, 4}; // D
    tr[8] = {0, -1, 5}; tr[9] = {1, +1, 2}; // E
    tr[10] = {1, -1, 6}; tr[11] = {0, -1, 2}; // F
    tr[12] = {0, 0, -2}; tr[13] = {1, -1, 4}; // G
}

int main(int argc, char** argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    int n_states = (argc > 1) ? atoi(argv[1]) : 8;
    Trans tr[20];
    setup_m4(tr, n_states);
    printf("Starting M4 exact symbolic fast-forward search for %d states...\n", n_states);
    fflush(stdout);
    int lim = std::min(n_states - 1, 7);
    for (int w = 0; w < 2; ++w) {
        for (int d_idx = 0; d_idx < 2; ++d_idx) {
            int d = d_idx ? 1 : -1;
            for (int nx = 0; nx <= lim; ++nx) {
                tr[12] = {w, d, nx}; // G0
                dfs(tr, n_states);
            }
        }
    }
    printf("Done M4 %d states! E2_hits=%lld, E3_hits=%lld, E4plus_hits=%lld\n",
           n_states, total_hits_E2, total_hits_E3, total_hits_E4plus);
    return 0;
}
