#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>

// M39 6-state core: 1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_---0LE
// Free slots in 8 states (n_states=8): F0(10), G0(12), G1(13), H0(14), H1(15)
// Free slots in 9 states (n_states=9): F0(10), G0(12), G1(13), H0(14), H1(15), I0(16), I1(17)

struct Trans {
    int w, d, nx; // nx = -1 for HALT, -2 for UNASSIGNED
};

int phi_tab[250][64];
int psi_tab[250][64];
int c_tab[250];

void init_tables() {
    for (int a = 0; a < 64; ++a) {
        phi_tab[0][a] = (3 * a + 3) & 63;
        psi_tab[0][a] = (3 * a + 3) & 63;
    }
    c_tab[0] = 1;
    for (int k = 1; k < 250; ++k) {
        for (int a = 0; a < 64; ++a) {
            int d = (3 * a + 3 - k) & 63;
            int x = c_tab[k - 1];
            for (int i = 0; i < d; ++i) x = phi_tab[k - 1][x];
            phi_tab[k][a] = x;
        }
        c_tab[k] = phi_tab[k][c_tab[k - 1]];
        for (int a = 0; a < 64; ++a) {
            int d = (3 * a + 2 - k) & 63;
            int x = c_tab[k - 1];
            for (int i = 0; i < d; ++i) x = phi_tab[k - 1][x];
            psi_tab[k][a] = psi_tab[k - 1][x];
        }
    }
}

// Compute exact N if small (< 1000), else return -1 and set mod64
int compute_next_N(const std::vector<int>& L_in, int a, int& out_mod64) {
    std::vector<int> L = L_in;
    size_t idx = 0;
    while (idx < L.size() && L[idx] == 0) idx++;
    L.erase(L.begin(), L.begin() + idx);

    if (L.empty()) {
        long long N = 3LL * a + 3;
        out_mod64 = (int)(N & 63);
        return (N <= 15) ? (int)N : -1;
    }
    int m = (int)L.size();
    int cur = a & 63;
    for (int i = m - 1; i >= 1; --i) {
        int k = m - 1 - i;
        if (k >= 250) k = 249;
        int d = L[i] & 63;
        for (int j = 0; j < d; ++j) cur = phi_tab[k][cur];
    }
    int k_top = m - 1;
    if (k_top >= 250) k_top = 249;
    int d_top = (L[0] - 1) & 63;
    for (int j = 0; j < d_top; ++j) cur = phi_tab[k_top][cur];
    int AE = psi_tab[k_top][cur];
    out_mod64 = (3 * AE + 3) & 63;
    return -1;
}

struct RunResult {
    int status; // 0 = LOOP/BAD, 1 = HALT, 2 = C0_B1, 3 = UNASSIGNED
    int unass_slot;
    int steps;
    std::vector<int> L;
    int a;
};

// Run from 0^inf [F0] (10)^N 0^inf until C0 end-moment with b=1 (and no state >=6 on tape/active)
RunResult run_f0(const Trans* tr, int N, int max_steps = 2500) {
    const int OFFSET = 512;
    const int TSIZE = 2048;
    unsigned char tape[TSIZE];
    memset(tape, 0, sizeof(tape));
    int lo = OFFSET + 1;
    int hi = OFFSET + 2 * N;
    for (int j = 0; j < N; ++j) {
        tape[OFFSET + 1 + 2 * j] = 1;
    }
    int pos = OFFSET;
    int q = 5; // F
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

        // Check C0 end-moment with b=1: ends with 010[C0] and all cells >= pos are 0
        if (q == 2 && pos >= OFFSET + 3 && tape[pos] == 0 && tape[pos - 1] == 0 && tape[pos - 2] == 1 && tape[pos - 3] == 0) {
            bool clean_right = true;
            for (int i = pos + 1; i <= hi; ++i) {
                if (tape[i]) { clean_right = false; break; }
            }
            if (clean_right) {
                int r_lo = -1;
                for (int i = lo; i <= pos - 2; ++i) {
                    if (tape[i]) { r_lo = i; break; }
                }
                if (r_lo != -1) {
                    std::vector<int> parts;
                    int cur_ones = 0;
                    for (int i = r_lo; i <= pos - 1; ++i) {
                        if (tape[i]) {
                            cur_ones++;
                        } else {
                            parts.push_back(cur_ones);
                            cur_ones = 0;
                        }
                    }
                    if (parts.size() >= 2 && parts.back() == 1) {
                        RunResult r;
                        r.status = 2;
                        r.steps = st;
                        r.a = parts[parts.size() - 2];
                        r.L.assign(parts.begin(), parts.end() - 2);
                        size_t idx = 0;
                        while (idx < r.L.size() && r.L[idx] == 0) idx++;
                        r.L.erase(r.L.begin(), r.L.begin() + idx);
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

std::string fmt_tm(const Trans* tr, int n_states) {
    std::string s;
    for (int q = 0; q < n_states; ++q) {
        if (q) s += '_';
        for (int c = 0; c < 2; ++c) {
            const Trans& t = tr[2 * q + c];
            if (t.nx < 0) {
                s += "---";
            } else {
                s += (char)('0' + t.w);
                s += (t.d == 1) ? 'R' : 'L';
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
    int mx = 5; // F is 5
    for (int s = 10; s < 2 * n_states; ++s) {
        if (tr[s].nx > mx) mx = tr[s].nx;
    }
    return mx;
}

void dfs(Trans* tr, int n_states) {
    // Trace orbit starting from E0: N0 = 3
    int cur_exact = 3;
    int cur_mod64 = 3;
    bool grew_ever = false;

    for (int eb = 0; eb <= 8; ++eb) {
        if (cur_exact != -1) {
            RunResult r = run_f0(tr, cur_exact, 400);
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
                    if (eb == 2) total_hits_E2++;
                    else if (eb == 3) {
                        total_hits_E3++;
                        if (total_hits_E3 <= 30) {
                            printf("[E%d HALT (%d-state)] %s\n", eb, n_states, fmt_tm(tr, n_states).c_str());
                            fflush(stdout);
                        }
                    } else {
                        total_hits_E4plus++;
                        if (total_hits_E4plus <= 50) {
                            printf("[E%d HALT (%d-state) !!!] %s\n", eb, n_states, fmt_tm(tr, n_states).c_str());
                            fflush(stdout);
                        }
                    }
                }
                return;
            }
            // status == 2 (rebuilt)
            int next_mod64 = 0;
            int next_exact = compute_next_N(r.L, r.a, next_mod64);
            if (next_exact == cur_exact) return; // trivial fixed point
            cur_exact = next_exact;
            cur_mod64 = next_mod64;
        } else {
            // Large N with residue cur_mod64: test on N_a and N_b = N_a + 64
            int Na = 64 + cur_mod64;
            int Nb = 128 + cur_mod64;
            RunResult ra = run_f0(tr, Na, 800);
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
            RunResult rb = run_f0(tr, Nb, 1500);
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
            if (rb.status != ra.status) return; // period doesn't divide 64
            if (ra.status == 1) {
                if (eb >= 2 && grew_ever) {
                    if (eb == 2) {
                        total_hits_E2++;
                        if (n_states == 8 && total_hits_E2 <= 30) {
                            printf("[E2 HALT (8-state)] %s\n", fmt_tm(tr, n_states).c_str());
                            fflush(stdout);
                        }
                    } else if (eb == 3) {
                        total_hits_E3++;
                        if (total_hits_E3 <= 30) {
                            printf("[E3 HALT (%d-state)] %s\n", n_states, fmt_tm(tr, n_states).c_str());
                            fflush(stdout);
                        }
                    } else {
                        total_hits_E4plus++;
                        if (total_hits_E4plus <= 50) {
                            printf("[E%d HALT (%d-state) !!!] %s\n", eb, n_states, fmt_tm(tr, n_states).c_str());
                            fflush(stdout);
                        }
                    }
                }
                return;
            }
            // Both rebuilt: check if L grows with N!
            int sum_a = 0, sum_b = 0;
            for (int x : ra.L) sum_a += x;
            for (int x : rb.L) sum_b += x;
            if (rb.L.size() > ra.L.size() && sum_b > sum_a) {
                grew_ever = true;
            } else if (!grew_ever) {
                return;
            }
            int mod_a = 0, mod_b = 0;
            int ex_a = compute_next_N(ra.L, ra.a, mod_a);
            int ex_b = compute_next_N(rb.L, rb.a, mod_b);
            if (mod_a != mod_b) return;
            cur_exact = (ex_a == ex_b) ? ex_a : -1;
            cur_mod64 = mod_a;
        }
    }
}

void setup_m39(Trans* tr, int n_states) {
    // 1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_---0LE
    tr[0] = {1, 1, 1};  tr[1] = {1, 1, 0};  // A: 1RB 1RA
    tr[2] = {0, 1, 2};  tr[3] = {0, 1, 0};  // B: 0RC 0RA
    tr[4] = {0, -1, 3}; tr[5] = {1, 1, 2};  // C: 0LD 1RC
    tr[6] = {1, -1, 4}; tr[7] = {1, -1, 5}; // D: 1LE 1LF
    tr[8] = {1, -1, 1}; tr[9] = {1, -1, 4}; // E: 1LB 1LE
    tr[10] = {0, 0, -2}; tr[11] = {0, -1, 4}; // F: --- 0LE
    for (int s = 12; s < 2 * n_states; ++s) {
        tr[s] = {0, 0, -2};
    }
}

int main(int argc, char** argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    init_tables();
    int n_states = (argc > 1) ? atoi(argv[1]) : 8;
    Trans tr[20];
    setup_m39(tr, n_states);
    printf("Starting M39 exact symbolic fast-forward search for %d states...\n", n_states);
    fflush(stdout);
    // Symmetry breaking: when F0(10) goes to a new state >= 6, it must be G(6)
    for (int w = 0; w < 2; ++w) {
        for (int d_idx = 0; d_idx < 2; ++d_idx) {
            int d = d_idx ? 1 : -1;
            for (int nx = 0; nx <= 6; ++nx) {
                tr[10] = {w, d, nx};
                dfs(tr, n_states);
            }
        }
    }
    printf("Done %d states! E2_hits=%lld, E3_hits=%lld, E4plus_hits=%lld\n",
           n_states, total_hits_E2, total_hits_E3, total_hits_E4plus);
    return 0;
}
