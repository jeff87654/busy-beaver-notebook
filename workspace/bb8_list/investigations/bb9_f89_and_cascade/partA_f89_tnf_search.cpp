// partA_f89_tnf_search.cpp
// Exhaustive & execution-driven 9-state TNF search for F89 and F89-S1/S2/S3:
//   Family A1a: B0:0 once-per-round completion guard (B0 = 0RH, H1 = C1 = 0RG, C0 = 1LD; free: H0, B1, I0, I1)
//   Family A1b: B0:0 completion guard with C0 also free (B0 = 0RH, H1 = C1 = 0RG; free: H0, C0, B1, I0, I1)
//   Family A2a: C0:0 once-per-round completion guard (C0 = 1LH, H1 = D1 = 0RF; free: H0, B1, I0, I1)
//   Family A2b: C0:1 first-pass guard on S3 (C0 = 1LH, H0 = D0 = 1RA; free: H1, B1, I0, I1)
//   Family A2c: Full 6-slot (C0, B1, H0, H1, I0, I1) execution-driven TNF search
//   Family A3:  G0:0 first-pass guard (G0 = 1RH, H1 = C1 = 0RG; free: H0, B1, I0, I1)
// Includes exact macro-acceleration for:
//   - All-odd towers (D, B_k, T_k + universal residue 61 mod 65,520 for height >= 4)
//   - Even-headed & zero-digit towers (E_2: [2, 0, 1^k, ...], ZD: [a, 0, d, R], Z_2: [a, 0, 1^k, ...])
//   - Exact compression jumps [x] -> 1^(3x+5) [B0] 0, [x,0] -> 1^(3x+12) [B0] 0, [x,0,0] -> 1^(3x+8) [B0] 0,
//     [x,0,1,0] -> 1^(3x+11) [B0] 0 when C1, G0, and C0:1 are unmodified.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <tuple>
#include <algorithm>
#include <windows.h>

struct Trans {
    int w;   // 0, 1, or -1 (HALT) or -2 (UNDEF)
    int dir; // -1 (L) or +1 (R)
    int nxt; // 0..8 (A..I)
};

static const int HALT_TR = -1;
static const int UNDEF_TR = -2;

void init_f89_base(Trans* tr) {
    for (int i = 0; i < 18; ++i) tr[i] = {HALT_TR, 0, -1};
    // A: 1RB 0RE
    tr[0] = {1, +1, 1}; tr[1] = {0, +1, 4};
    // B: 0RC ---
    tr[2] = {0, +1, 2}; tr[3] = {HALT_TR, 0, -1};
    // C: 1LD 0RG
    tr[4] = {1, -1, 3}; tr[5] = {0, +1, 6};
    // D: 1RA 0RF
    tr[6] = {1, +1, 0}; tr[7] = {0, +1, 5};
    // E: 1LF 0LD
    tr[8] = {1, -1, 5}; tr[9] = {0, -1, 3};
    // F: 1LD 0LE
    tr[10] = {1, -1, 3}; tr[11] = {0, -1, 4};
    // G: 1RC 1RE
    tr[12] = {1, +1, 2}; tr[13] = {1, +1, 4};
}

std::string format_tm(const Trans* tr) {
    std::string s;
    for (int q = 0; q < 9; ++q) {
        if (q > 0) s += '_';
        for (int b = 0; b < 2; ++b) {
            const Trans& t = tr[2 * q + b];
            if (t.w < 0) s += "---";
            else {
                s += (char)('0' + t.w);
                s += (t.dir == -1) ? 'L' : 'R';
                s += (char)('A' + t.nxt);
            }
        }
    }
    return s;
}

static inline int cap_odd(long long v) {
    if (v <= 85) return (int)v;
    return (int)(25 + ((v - 25) % 60 + 60) % 60);
}

int collapse_all_odd_tower(std::vector<int> L) {
    if (L.empty()) return 0;
    if (L.size() >= 4) return 61;
    while (L.size() >= 2) {
        if (L.size() >= 4) return 61;
        int a = L[0];
        if (a > 85) return 61;
        if (L[1] >= 3) {
            int q = (L[1] - 1) / 2;
            L[0] = cap_odd((long long)a + 4LL * q);
            L[1] -= 2 * q;
            continue;
        }
        size_t k = 0;
        while (1 + k < L.size() && L[1 + k] == 1) k++;
        int na = cap_odd(a + 4);
        if (1 + k == L.size()) {
            std::vector<int> nxt(k - 1, 1);
            nxt.push_back(na);
            L.swap(nxt);
        } else {
            int d = L[1 + k];
            std::vector<int> nxt(k, 1);
            nxt.push_back(na);
            nxt.push_back(d - 2);
            for (size_t j = 2 + k; j < L.size(); ++j) nxt.push_back(L[j]);
            L.swap(nxt);
        }
    }
    return L[0] > 85 ? 61 : L[0];
}

// Exact macro-step on K-config L = [d_1, ..., d_n] using only the 12 core transitions of F89
bool step_core_tower(std::vector<int>& L) {
    if (L.size() < 2) return false;

    // 1. Leading odd digits sub-tower collapse
    size_t m_odd = 0;
    while (m_odd < L.size() && L[m_odd] > 0 && (L[m_odd] & 1) == 1) m_odd++;
    if (m_odd == L.size()) {
        int x = collapse_all_odd_tower(L);
        L.assign(1, x);
        return true;
    }
    if (m_odd >= 4 && m_odd < L.size()) {
        std::vector<int> nxt = {57, 1};
        for (size_t j = m_odd; j < L.size(); ++j) nxt.push_back(L[j]);
        L.swap(nxt);
        return true;
    }

    int a = L[0];

    // 2. Rule E_2: L starts with [2, 0, 1^k, ...] (k >= 1)
    if (a == 2 && L.size() >= 3 && L[1] == 0 && L[2] == 1) {
        size_t k = 0;
        while (2 + k < L.size() && L[2 + k] == 1) k++;
        if (2 + k == L.size()) {
            if (k == 1) {
                L = {3, 3};
            } else {
                std::vector<int> nxt = {3, 0};
                for (size_t i = 0; i < k - 2; ++i) nxt.push_back(1);
                nxt.push_back(4);
                L.swap(nxt);
            }
            return true;
        } else if (L[2 + k] >= 2) {
            int d = L[2 + k];
            std::vector<int> nxt = {3, 0};
            for (size_t i = 0; i < k - 1; ++i) nxt.push_back(1);
            nxt.push_back(4);
            nxt.push_back(d - 2);
            for (size_t j = 3 + k; j < L.size(); ++j) nxt.push_back(L[j]);
            L.swap(nxt);
            return true;
        }
    }

    if (a <= 0 || (a & 1) == 0) return false;

    // 3. Odd head a with L[1] >= 2: Rule D ([a, b, R] -> [a+4q, b-2q, R])
    if (L[1] >= 2) {
        int q = L[1] / 2;
        if (L[1] % 2 == 1) q = (L[1] - 1) / 2;
        if (q > 0) {
            L[0] = cap_odd((long long)a + 4LL * q);
            L[1] -= 2 * q;
            return true;
        }
    }

    // 4. Odd head a with L[1] == 1: Rules B_k and T_k
    if (L[1] == 1) {
        size_t k = 0;
        while (1 + k < L.size() && L[1 + k] == 1) k++;
        int na = cap_odd(a + 4);
        if (1 + k == L.size()) {
            std::vector<int> nxt(k - 1, 1);
            nxt.push_back(na);
            L.swap(nxt);
            return true;
        } else if (L[1 + k] >= 2) {
            int d = L[1 + k];
            std::vector<int> nxt(k, 1);
            nxt.push_back(na);
            nxt.push_back(d - 2);
            for (size_t j = 2 + k; j < L.size(); ++j) nxt.push_back(L[j]);
            L.swap(nxt);
            return true;
        }
    }

    // 5. Odd head a with L[1] == 0 and L.size() >= 3: Rules ZD and Z_2
    if (L[1] == 0 && L.size() >= 3) {
        size_t m2 = 0;
        while (2 + m2 < L.size() && L[2 + m2] > 0 && (L[2 + m2] & 1) == 1) m2++;
        if (m2 >= 3 || (m2 == 2 && L[3] >= 3)) {
            std::vector<int> nxt = {87, 0, 1};
            for (size_t j = 2 + m2; j < L.size(); ++j) nxt.push_back(L[j]);
            L.swap(nxt);
            return true;
        }
        if (L[2] >= 2) {
            // Rule ZD: [a, 0, d, R] -> [2^q (a+5) - 5, 0, d - 2q, R] where q = d / 2
            int d = L[2];
            int q = d / 2;
            long long cur = a;
            for (int i = 0; i < q; ++i) {
                cur = 2 * cur + 5;
                if (cur > 85) cur = cap_odd(cur);
            }
            L[0] = (int)cur;
            L[2] = d - 2 * q;
            return true;
        } else if (L[2] == 1) {
            // Rule Z_2: [a, 0, 1^k, ...]
            size_t k = 0;
            while (2 + k < L.size() && L[2 + k] == 1) k++;
            if (2 + k == L.size()) {
                if (k == 1) {
                    L = {cap_odd(2LL * a + 5), 0};
                } else {
                    std::vector<int> nxt = {3, 0};
                    for (size_t i = 0; i < k - 2; ++i) nxt.push_back(1);
                    nxt.push_back(cap_odd(a + 2));
                    L.swap(nxt);
                }
                return true;
            } else if (L[2 + k] >= 2) {
                int d = L[2 + k];
                std::vector<int> nxt = {3, 0};
                for (size_t i = 0; i < k - 1; ++i) nxt.push_back(1);
                nxt.push_back(cap_odd(a + 2));
                nxt.push_back(d - 2);
                for (size_t j = 3 + k; j < L.size(); ++j) nxt.push_back(L[j]);
                L.swap(nxt);
                return true;
            }
        }
    }

    return false;
}

static const int TAPE_SZ = 65536;
static const int TAPE_OFF = 32768;

struct SimOutcome {
    char status; // 'H' = halt, 'U' = hit UNDEF slot, 'T' = timeout/loop
    int undef_slot;
    int halt_slot;
    int rounds;     // number of completion events (or S([x]) rounds) reached
    int k_events;
    int steps;
    std::vector<int> round_ms; // M values at 1^M [B0] 0 or x values at S([x])
    std::vector<std::vector<int>> towers;
};

bool parse_k_config(const unsigned char* tape, int head, int hi, std::vector<int>& L_out) {
    while (hi >= head && tape[hi] == 0) hi--;
    if (hi < head + 3) return false;
    if (tape[head] != 0 || tape[head + 1] != 0 || tape[head + 2] != 0 || tape[head + 3] != 1) return false;
    int i = head + 3;
    L_out.clear();
    while (i <= hi) {
        if (tape[i] != 1) return false;
        i++;
        int d = 0;
        while (i + 1 <= hi && tape[i] == 0 && tape[i + 1] == 1) {
            d++;
            i += 2;
        }
        L_out.push_back(d);
    }
    return !L_out.empty();
}

void write_k_config(unsigned char* tape, int head, int& lo, int& hi, const std::vector<int>& L) {
    for (int i = lo; i <= hi; ++i) tape[i] = 0;
    int pos = head + 3;
    for (int d : L) {
        tape[pos++] = 1;
        for (int j = 0; j < d; ++j) {
            tape[pos++] = 0;
            tape[pos++] = 1;
        }
    }
    lo = head;
    hi = pos - 1;
}

void write_ones_b00(unsigned char* tape, int& head, int& lo, int& hi, int& min_vis, int& q, int M) {
    for (int i = lo; i <= hi; ++i) tape[i] = 0;
    int start = TAPE_OFF;
    for (int i = 0; i < M; ++i) tape[start + i] = 1;
    lo = start;
    hi = start + M;
    head = start + M; // on 0 right after 1^M
    min_vis = start;
    q = 1; // state B on 0 (with 0 to its right -> B0:0!)
}

SimOutcome sim_f89(
    const Trans* tr,
    int start_q,
    const std::vector<int>& init_L,
    bool allow_b00_jump, // true when C1=0RG, G0=1RC, and C0:1 -> D1=0RF are intact
    int max_steps = 12000,
    int max_rounds = 15
) {
    unsigned char tape[TAPE_SZ];
    memset(tape, 0, sizeof(tape));
    int head = TAPE_OFF;
    int lo = head, hi = head;
    int min_vis = head;
    int q = start_q;
    SimOutcome out = {'T', -1, -1, 0, 0, 0, {}, {}};

    if (!init_L.empty()) {
        write_k_config(tape, head, lo, hi, init_L);
        min_vis = head;
        q = 3; // D
        if (allow_b00_jump && init_L.size() == 1 && (init_L[0] & 1) == 1) {
            int x = cap_odd(init_L[0]);
            int M = 3 * x + 5;
            write_ones_b00(tape, head, lo, hi, min_vis, q, M);
            out.rounds = 1;
            out.round_ms.push_back(M);
        } else if (init_L.size() == 1) {
            out.rounds = 1;
            out.round_ms.push_back(init_L[0]);
        }
    }

    int steps_since_event = 0;
    std::vector<int> L;

    for (int step = 1; step <= max_steps; ++step) {
        if (head < 1024 || head >= TAPE_SZ - 1024) {
            out.status = 'T';
            out.steps = step;
            return out;
        }
        int b = tape[head];
        int slot = 2 * q + b;
        const Trans& t = tr[slot];
        if (t.w == UNDEF_TR) {
            out.status = 'U';
            out.undef_slot = slot;
            out.steps = step;
            return out;
        }
        if (t.w == HALT_TR) {
            out.status = 'H';
            out.halt_slot = slot;
            out.steps = step;
            return out;
        }
        tape[head] = (unsigned char)t.w;
        if (head < lo) lo = head;
        if (head > hi) hi = head;
        head += t.dir;
        q = t.nxt;
        steps_since_event++;

        if (steps_since_event > 3500) {
            out.status = 'T';
            out.steps = step;
            return out;
        }

        if (head < min_vis) {
            min_vis = head;
            if (q == 3 && parse_k_config(tape, head, hi, L)) {
                steps_since_event = 0;
                out.k_events++;
                if (out.towers.size() < 20) out.towers.push_back(L);
                if (out.k_events > 120) {
                    out.status = 'T';
                    out.steps = step;
                    return out;
                }
                bool changed = false;
                int macro_iters = 0;
                while (L.size() >= 2 && step_core_tower(L) && macro_iters < 200) {
                    changed = true;
                    macro_iters++;
                }
                if (changed) {
                    if (out.towers.size() < 20) out.towers.push_back(L);
                    write_k_config(tape, head, lo, hi, L);
                }

                // Check for exact B0:0 compression jump on [x], [x,0], [x,0,0], [x,0,1,0]
                if (allow_b00_jump && !L.empty() && L[0] > 0 && (L[0] & 1) == 1) {
                    int x = cap_odd(L[0]);
                    int M = -1;
                    if (L.size() == 1) M = 3 * x + 5;
                    else if (L.size() == 2 && L[1] == 0) M = 3 * x + 12;
                    else if (L.size() == 3 && L[1] == 0 && L[2] == 0) M = 3 * x + 8;
                    else if (L.size() == 4 && L[1] == 0 && L[2] == 1 && L[3] == 0) M = 3 * x + 11;

                    if (M != -1) {
                        write_ones_b00(tape, head, lo, hi, min_vis, q, M);
                        out.rounds++;
                        out.round_ms.push_back(M);
                        if (out.rounds > max_rounds) {
                            out.status = 'T';
                            out.steps = step;
                            return out;
                        }
                        int nr = (int)out.round_ms.size();
                        if (nr >= 2 && out.round_ms[nr - 1] == out.round_ms[nr - 2]) {
                            out.status = 'T';
                            out.steps = step;
                            return out;
                        }
                        if (nr >= 4 && out.round_ms[nr - 1] == out.round_ms[nr - 3] && out.round_ms[nr - 2] == out.round_ms[nr - 4]) {
                            out.status = 'T';
                            out.steps = step;
                            return out;
                        }
                        continue;
                    }
                }

                if (!allow_b00_jump && L.size() == 1 && (L[0] & 1) == 1) {
                    int x = cap_odd(L[0]);
                    if (x != L[0]) {
                        L[0] = x;
                        write_k_config(tape, head, lo, hi, L);
                    }
                    out.rounds++;
                    out.round_ms.push_back(x);
                    if (out.rounds > max_rounds) {
                        out.status = 'T';
                        out.steps = step;
                        return out;
                    }
                    int nr = (int)out.round_ms.size();
                    if (nr >= 2 && out.round_ms[nr - 1] == out.round_ms[nr - 2]) {
                        out.status = 'T';
                        out.steps = step;
                        return out;
                    }
                }
            }
        }
    }
    out.status = 'T';
    out.steps = max_steps;
    return out;
}

struct SearchStats {
    long long leaves = 0;
    long long halters_r1 = 0;
    long long halters_r2 = 0;
    long long halters_r3 = 0;
    long long halters_r4_plus = 0;
    long long multi_round_nonhalt = 0;
};

void print_halter(const char* fam_name, const char* start_name, const Trans* tr, const SimOutcome& res) {
    std::string tm = format_tm(tr);
    std::string ms;
    for (size_t i = 0; i < res.round_ms.size(); ++i) {
        if (i > 0) ms += "->";
        ms += std::to_string(res.round_ms[i]);
    }
    std::string tws;
    for (size_t i = 0; i < res.towers.size() && i < 6; ++i) {
        if (i > 0) tws += " ";
        tws += "[";
        for (size_t j = 0; j < res.towers[i].size(); ++j) {
            if (j > 0) tws += ",";
            if (j >= 5 && j + 1 < res.towers[i].size()) {
                tws += "...(len=" + std::to_string(res.towers[i].size()) + ")";
                break;
            }
            tws += std::to_string(res.towers[i][j]);
        }
        tws += "]";
    }
    printf("[HALT R=%d | %s | %s | halt=%c%d | k_ev=%d] %s | ms=%s | towers=%s\n",
           res.rounds, fam_name, start_name,
           'A' + (res.halt_slot / 2), res.halt_slot % 2,
           res.k_events, tm.c_str(), ms.c_str(), tws.c_str());
    fflush(stdout);
}

void dfs_tnf(
    const char* fam_name,
    const char* start_name,
    Trans* tr,
    int start_q,
    const std::vector<int>& init_L,
    bool allow_b00_jump,
    int max_used_state,
    int min_rounds_to_print,
    SearchStats& st
) {
    SimOutcome res = sim_f89(tr, start_q, init_L, allow_b00_jump);
    if (res.status == 'U') {
        int slot = res.undef_slot;
        // Option 0: leave slot as HALT_TR (---)
        tr[slot] = {HALT_TR, 0, -1};
        st.leaves++;
        if (res.rounds == 1) st.halters_r1++;
        else if (res.rounds == 2) st.halters_r2++;
        else if (res.rounds == 3) st.halters_r3++;
        else if (res.rounds >= 4) st.halters_r4_plus++;
        if (res.rounds >= min_rounds_to_print) {
            SimOutcome hres = res;
            hres.status = 'H';
            hres.halt_slot = slot;
            print_halter(fam_name, start_name, tr, hres);
        }

        int max_nxt = std::min(8, max_used_state + 1);
        for (int w = 0; w < 2; ++w) {
            for (int dir = -1; dir <= 1; dir += 2) {
                for (int nxt = 0; nxt <= max_nxt; ++nxt) {
                    tr[slot] = {w, dir, nxt};
                    int next_max_used = std::max(max_used_state, nxt);
                    if (slot / 2 > next_max_used) next_max_used = slot / 2;
                    dfs_tnf(fam_name, start_name, tr, start_q, init_L, allow_b00_jump, next_max_used, min_rounds_to_print, st);
                }
            }
        }
        tr[slot] = {UNDEF_TR, 0, -1};
    } else if (res.status == 'H') {
        st.leaves++;
        if (res.rounds == 1) st.halters_r1++;
        else if (res.rounds == 2) st.halters_r2++;
        else if (res.rounds == 3) st.halters_r3++;
        else if (res.rounds >= 4) st.halters_r4_plus++;
        if (res.rounds >= min_rounds_to_print) {
            print_halter(fam_name, start_name, tr, res);
        }
    } else {
        st.leaves++;
        if (res.rounds >= 2) st.multi_round_nonhalt++;
    }
}

void run_family(
    const char* fam_name,
    const char* sname,
    Trans* tr,
    int sq,
    const std::vector<int>& init_L,
    bool allow_b00_jump,
    int max_used_state,
    int min_r
) {
    SearchStats st;
    dfs_tnf(fam_name, sname, tr, sq, init_L, allow_b00_jump, max_used_state, min_r, st);
    printf("=== SUMMARY %s (%s): leaves=%lld R1=%lld R2=%lld R3=%lld R4+=%lld nonhalt_R2+=%lld ===\n",
           fam_name, sname, st.leaves, st.halters_r1, st.halters_r2, st.halters_r3, st.halters_r4_plus, st.multi_round_nonhalt);
    fflush(stdout);
}

int main() {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    Trans tr[18];

    // 1. Family A1a: B0:0 once-per-round completion guard (B0 = 0RH, H1 = C1 = 0RG, C0 = 1LD; free: H0, B1, I0, I1)
    for (auto [sname, sq, init_L, min_r] : std::vector<std::tuple<const char*, int, std::vector<int>, int>>{
        {"S([1])_S3", 3, {1}, 2},
        {"S([61])_F89", 3, {61}, 2},
        {"Blank_D(S3)", 3, {}, 2},
        {"Blank_A(F89)", 0, {}, 2},
        {"Blank_C(S1)", 2, {}, 2},
        {"Blank_F(S2)", 5, {}, 2}
    }) {
        init_f89_base(tr);
        tr[2] = {0, +1, 7};  // B0 = 0RH
        tr[15] = {0, +1, 6}; // H1 = C1 = 0RG
        tr[3] = {UNDEF_TR, 0, -1};  // B1
        tr[14] = {UNDEF_TR, 0, -1}; // H0
        tr[16] = {UNDEF_TR, 0, -1}; // I0
        tr[17] = {UNDEF_TR, 0, -1}; // I1
        run_family("FamA1a_B00_C0fixed", sname, tr, sq, init_L, true, 7, min_r);
    }

    // 2. Family A1b: B0:0 completion guard with C0 ALSO free (5 free slots: H0, C0, B1, I0, I1)
    for (auto [sname, sq, init_L, min_r] : std::vector<std::tuple<const char*, int, std::vector<int>, int>>{
        {"S([1])_S3", 3, {1}, 3},
        {"S([61])_F89", 3, {61}, 2},
        {"Blank_D(S3)", 3, {}, 3}
    }) {
        init_f89_base(tr);
        tr[2] = {0, +1, 7};  // B0 = 0RH
        tr[15] = {0, +1, 6}; // H1 = C1 = 0RG
        tr[4] = {UNDEF_TR, 0, -1};  // C0
        tr[3] = {UNDEF_TR, 0, -1};  // B1
        tr[14] = {UNDEF_TR, 0, -1}; // H0
        tr[16] = {UNDEF_TR, 0, -1}; // I0
        tr[17] = {UNDEF_TR, 0, -1}; // I1
        run_family("FamA1b_B00_C0free", sname, tr, sq, init_L, false, 7, min_r);
    }

    // 3. Family A2a: C0:0 once-per-round completion guard (C0 = 1LH, H1 = D1 = 0RF; free: H0, B1, I0, I1)
    for (auto [sname, sq, init_L, min_r] : std::vector<std::tuple<const char*, int, std::vector<int>, int>>{
        {"S([1])_S3", 3, {1}, 2},
        {"S([61])_F89", 3, {61}, 2},
        {"Blank_D(S3)", 3, {}, 2},
        {"Blank_A(F89)", 0, {}, 2},
        {"Blank_C(S1)", 2, {}, 2},
        {"Blank_F(S2)", 5, {}, 2}
    }) {
        init_f89_base(tr);
        tr[4] = {1, -1, 7};  // C0 = 1LH
        tr[15] = {0, +1, 5}; // H1 = D1 = 0RF
        tr[3] = {UNDEF_TR, 0, -1};  // B1
        tr[14] = {UNDEF_TR, 0, -1}; // H0
        tr[16] = {UNDEF_TR, 0, -1}; // I0
        tr[17] = {UNDEF_TR, 0, -1}; // I1
        run_family("FamA2a_C00_guard", sname, tr, sq, init_L, true, 7, min_r);
    }

    // 4. Family A2b: C0:1 first-pass guard on S3 (C0 = 1LH, H0 = D0 = 1RA; free: H1, B1, I0, I1)
    for (auto [sname, sq, init_L, min_r] : std::vector<std::tuple<const char*, int, std::vector<int>, int>>{
        {"Blank_D(S3)", 3, {}, 2},
        {"S([61])_F89", 3, {61}, 2}
    }) {
        init_f89_base(tr);
        tr[4] = {1, -1, 7};  // C0 = 1LH
        tr[14] = {1, +1, 0}; // H0 = D0 = 1RA
        tr[3] = {UNDEF_TR, 0, -1};  // B1
        tr[15] = {UNDEF_TR, 0, -1}; // H1
        tr[16] = {UNDEF_TR, 0, -1}; // I0
        tr[17] = {UNDEF_TR, 0, -1}; // I1
        run_family("FamA2b_C01_guard", sname, tr, sq, init_L, false, 7, min_r);
    }

    // 5. Family A3: G0:0 first-pass guard (G0 = 1RH, H1 = C1 = 0RG; free: H0, B1, I0, I1)
    for (auto [sname, sq, init_L, min_r] : std::vector<std::tuple<const char*, int, std::vector<int>, int>>{
        {"Blank_D(S3)", 3, {}, 2},
        {"S([61])_F89", 3, {61}, 2}
    }) {
        init_f89_base(tr);
        tr[12] = {1, +1, 7}; // G0 = 1RH
        tr[15] = {0, +1, 6}; // H1 = C1 = 0RG
        tr[3] = {UNDEF_TR, 0, -1};  // B1
        tr[14] = {UNDEF_TR, 0, -1}; // H0
        tr[16] = {UNDEF_TR, 0, -1}; // I0
        tr[17] = {UNDEF_TR, 0, -1}; // I1
        run_family("FamA3_G00_guard", sname, tr, sq, init_L, false, 7, min_r);
    }

    return 0;
}
