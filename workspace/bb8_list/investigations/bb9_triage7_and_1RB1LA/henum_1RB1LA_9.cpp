// henum_1RB1LA_9.cpp: Exhaustive 9-state redirect enumerator for the 8-state 1RB1LA f_{w+1} rebuilder family.
// Redirects one defined transition T in {A0..G1, H1} to state I (or H on read 0), and TNF-branches {H0, I0, I1}.
// For each leaf:
//  1. Simulates from blank tape for BUD_BLANK steps, recording F(P'; W; b) moments (especially re-entry after R4!).
//  2. Simulates from R1, R3A, and R4(b) (b=1..8).
//  3. If R4(b) produces a non-empty left marker P' and non-empty list W, simulates Round-2 R4: P' + F([], b2) for b2=1..6!

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <string>
#include <vector>
#include <algorithm>

struct Tr { int w, d, nx; bool def; };
static const int NS = 9;
static const int H_ST = 7, I_ST = 8;
static Tr t[18];

static std::string fmt_tm() {
    std::string s;
    for (int q = 0; q < NS; ++q) {
        if (q) s += '_';
        for (int c = 0; c < 2; ++c) {
            const Tr &x = t[2*q + c];
            if (!x.def) s += "---";
            else {
                s += char('0' + x.w);
                s += (x.d > 0 ? 'R' : 'L');
                s += char('A' + x.nx);
            }
        }
    }
    return s;
}

static std::string slot_name(int sl) {
    std::string r;
    r += char('A' + sl / 2);
    r += char('0' + sl % 2);
    return r;
}

// Encode F(P_prefix, W, b):
// Tape left-to-right: P_prefix, then for d in reversed(W): (10)^d 00, then (10)^(2b+2), head D on 0 at right end.
static std::string make_F_word(const std::string &P, const std::vector<int> &W, int b) {
    std::string w = P;
    for (int i = (int)W.size() - 1; i >= 0; --i) {
        for (int k = 0; k < W[i]; ++k) w += "10";
        w += "00";
    }
    for (int k = 0; k < 2 * b + 2; ++k) w += "10";
    return w;
}

// Parse right-end D> configuration into (P_prefix, W, b)
// Returns true if right end has at least (10)^2 (even number of 10s, so b >= 0) and at least one 00-separated digit or empty list.
static bool parse_F(const unsigned char *T, long long lo, long long pos, std::string &P_out, std::vector<int> &W_out, int &b_out) {
    // Strip leading zeros at lo
    while (lo < pos && T[lo] == 0) ++lo;
    if (lo >= pos) return false;
    long long p = pos - 1;
    int b_units = 0;
    while (p - 1 >= lo && T[p] == 0 && T[p-1] == 1) {
        ++b_units;
        p -= 2;
    }
    if (b_units < 2 || (b_units % 2) != 0) return false;
    b_out = (b_units - 2) / 2;
    W_out.clear();
    while (p - 1 >= lo && T[p] == 0 && T[p-1] == 0) {
        p -= 2;
        int d = 0;
        while (p - 1 >= lo && T[p] == 0 && T[p-1] == 1) {
            ++d;
            p -= 2;
        }
        W_out.push_back(d);
    }
    // Strip trailing zeros of W_out ONLY if p < lo (no prefix P_out)
    P_out.clear();
    if (p >= lo) {
        for (long long i = lo; i <= p; ++i) P_out += char('0' + T[i]);
    } else {
        while (!W_out.empty() && W_out.back() == 0) W_out.pop_back();
    }
    return true;
}

static std::string fmt_W(const std::vector<int> &W) {
    std::string out;
    for (size_t i = 0; i < W.size();) {
        int v = W[i];
        size_t r = i;
        while (r < W.size() && W[r] == v) ++r;
        if (!out.empty()) out += ",";
        out += std::to_string(v);
        if (r - i > 1) out += "^" + std::to_string(r - i);
        i = r;
    }
    return out;
}

struct SimRes {
    char kind; // 'H' halt, 'K' F-config, 'T' budget, 'X' runaway, 'C' cycler
    long long steps, ones;
    int slot;
    std::string P;
    std::vector<int> W;
    int b;
    long long hi_uses;
    int max_W_len;
    long long r4_count;
};

static std::vector<unsigned char> tp;

static SimRes sim(const std::string *start_w, int start_q, long long bud, bool stop_on_K) {
    long long size = 1 << 16;
    if (start_w) {
        while (size < 4 * (long long)start_w->size() + 4096) size *= 2;
    }
    tp.assign(size, 0);
    long long off = size / 2;
    long long lo = 1, hi = 0, pos = 0;
    int q = start_q;
    if (start_w) {
        for (size_t i = 0; i < start_w->size(); ++i) {
            if ((*start_w)[i] == '1') {
                tp[off + i] = 1;
                if (lo > hi) lo = hi = (long long)i;
                else hi = (long long)i;
            }
        }
        pos = (long long)start_w->size();
    }
    long long hi_uses = 0, mn = 0, mx = pos, ckp = 8192, lastsp = -1;
    int max_W_len = 0;
    long long r4_count = 0;
    bool prev_was_empty = false;

    for (long long st = 0; st < bud; ++st) {
        if (pos + off < 4 || pos + off + 4 >= size) {
            if (size >= (1LL << 24)) return {'W', st, 0, -1, "", {}, 0, hi_uses, max_W_len, r4_count};
            std::vector<unsigned char> nt(size * 2, 0);
            memcpy(nt.data() + size / 2, tp.data(), size);
            off += size / 2;
            size *= 2;
            tp.swap(nt);
        }
        unsigned char *T = tp.data() + off;
        int c = T[pos];

        if (st > 0 && q == 3 && c == 0 && lo <= hi) { // State D = 3
            while (lo <= hi && !T[hi]) --hi;
            while (lo <= hi && !T[lo]) ++lo;
            if (pos > hi && lo <= hi && pos - lo < 16384) {
                std::string P;
                std::vector<int> W;
                int b;
                if (parse_F(T, lo, pos, P, W, b)) {
                    if (stop_on_K) {
                        return {'K', st, 0, -1, P, W, b, hi_uses, (int)W.size(), r4_count};
                    } else {
                        if ((int)W.size() > max_W_len) max_W_len = (int)W.size();
                        bool is_empty = W.empty();
                        if (prev_was_empty && (int)W.size() >= 5) {
                            ++r4_count;
                        }
                        prev_was_empty = is_empty;
                    }
                }
            }
        }

        const Tr &tr = t[2*q + c];
        if (!tr.def) {
            long long ones = 0;
            for (auto v : tp) ones += v;
            return {'H', st, ones, 2*q + c, "", {}, 0, hi_uses, max_W_len, r4_count};
        }
        if (q == H_ST || q == I_ST) ++hi_uses;
        T[pos] = tr.w;
        if (tr.w) {
            if (lo > hi) lo = hi = pos;
            else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; }
        }
        pos += tr.d;
        q = tr.nx;
        if (pos < mn) mn = pos;
        if (pos > mx) mx = pos;

        if (st == ckp) {
            long long sp = mx - mn;
            double lim = 10.0 * std::sqrt((double)st) + 300 + (start_w ? 2.0 * start_w->size() : 0);
            if (st >= 32768 && sp > lim) return {'X', st, 0, -1, "", {}, 0, hi_uses, max_W_len, r4_count};
            if (!start_w && st >= 131072 && sp == lastsp) return {'C', st, 0, -1, "", {}, 0, hi_uses, max_W_len, r4_count};
            lastsp = sp;
            ckp *= 2;
        }
    }
    return {'T', bud, 0, -1, "", {}, 0, hi_uses, max_W_len, r4_count};
}

static long long total_nodes = 0, quiet_halts = 0, interesting_leaves = 0;
static std::string cur_tag;
static long long BUD_BLANK = 150000, BUD_PROBE = 100000;

static bool is_undef_HI(int sl) {
    return (sl == 14 || sl == 16 || sl == 17) && !t[sl].def;
}

static void dfs(int used_states, int defs_made) {
    ++total_nodes;
    int undef_hi = (!t[14].def) + (!t[16].def) + (!t[17].def);

    SimRes bres = sim(nullptr, 0, BUD_BLANK, false);
    int branch_slot = -1;
    if (bres.kind == 'H' && is_undef_HI(bres.slot)) {
        branch_slot = bres.slot;
    }

    // Also run R1, R3A, and R4(b=1..6) probes if blank didn't halt early (< 11000 steps)
    bool survive_early = !(bres.kind == 'H' && bres.steps < 11000);
    std::vector<SimRes> r4_res;
    SimRes r1_res = {'-', 0, 0, -1, "", {}, 0, 0, 0, 0};
    SimRes r3a_res = {'-', 0, 0, -1, "", {}, 0, 0, 0, 0};

    if (survive_early) {
        std::string w_r1 = make_F_word("", {2, 2}, 0);
        r1_res = sim(&w_r1, 3, BUD_PROBE, true);
        if (branch_slot < 0 && r1_res.kind == 'H' && is_undef_HI(r1_res.slot)) branch_slot = r1_res.slot;

        std::string w_r3a = make_F_word("", {0, 2}, 2);
        r3a_res = sim(&w_r3a, 3, BUD_PROBE, true);
        if (branch_slot < 0 && r3a_res.kind == 'H' && is_undef_HI(r3a_res.slot)) branch_slot = r3a_res.slot;

        for (int b = 1; b <= 6; ++b) {
            std::string w_r4 = make_F_word("", {}, b);
            SimRes rr = sim(&w_r4, 3, BUD_PROBE, true);
            if (branch_slot < 0 && rr.kind == 'H' && is_undef_HI(rr.slot)) branch_slot = rr.slot;
            r4_res.push_back(rr);
        }
    }

    if (!survive_early) {
        ++quiet_halts;
    } else {
        // Check if this leaf is interesting:
        // 1. Halts from blank at >= 11,000 steps (after reaching first R4!)
        // 2. Or R1 and R3A return 'K', and at least one R4(b) halts or returns 'K' with non-empty W!
        bool r4_has_H = false, r4_has_K = false, r4_has_P = false;
        for (auto &rr : r4_res) {
            if (rr.kind == 'H') r4_has_H = true;
            if (rr.kind == 'K' && (int)rr.W.size() >= 2) {
                r4_has_K = true;
                if (!rr.P.empty()) r4_has_P = true;
            }
        }
        bool is_int = (bres.kind == 'H' && bres.steps >= 11000) ||
                      (bres.r4_count >= 1) ||
                      (r1_res.kind == 'K' && r3a_res.kind == 'K' && (r4_has_H || r4_has_K));
        if (is_int) {
            ++interesting_leaves;
            printf("%s\t%s\tblank=%c:%lld:ones=%lld:maxW=%d:r4s=%lld",
                   cur_tag.c_str(), fmt_tm().c_str(), bres.kind, bres.steps, bres.ones, bres.max_W_len, bres.r4_count);
            if (bres.kind == 'H') printf(":%s", slot_name(bres.slot).c_str());
            printf("\tR1=%c", r1_res.kind);
            if (r1_res.kind == 'K') printf(":(%s)[%s];%d", r1_res.P.c_str(), fmt_W(r1_res.W).c_str(), r1_res.b);
            printf("\tR3A=%c", r3a_res.kind);
            if (r3a_res.kind == 'K') printf(":(%s)[%s];%d", r3a_res.P.c_str(), fmt_W(r3a_res.W).c_str(), r3a_res.b);
            for (int b = 1; b <= 6; ++b) {
                auto &rr = r4_res[b-1];
                printf("\tR4(%d)=%c", b, rr.kind);
                if (rr.kind == 'H') printf(":%lld:%s", rr.steps, slot_name(rr.slot).c_str());
                else if (rr.kind == 'K') printf(":(%s)[%s];%d", rr.P.c_str(), fmt_W(rr.W).c_str(), rr.b);
            }
            // If r4_has_P, test Round-2 R4 with that P!
            if (r4_has_P) {
                std::string P1;
                for (auto &rr : r4_res) if (rr.kind == 'K' && !rr.P.empty()) { P1 = rr.P; break; }
                printf("\tR4_round2(P=%s):", P1.c_str());
                for (int b2 = 1; b2 <= 4; ++b2) {
                    std::string w2 = make_F_word(P1, {}, b2);
                    SimRes rr2 = sim(&w2, 3, BUD_PROBE, true);
                    printf(" b%d=%c", b2, rr2.kind);
                    if (rr2.kind == 'H') printf(":%s", slot_name(rr2.slot).c_str());
                    else if (rr2.kind == 'K') printf(":(%s)[%s];%d", rr2.P.c_str(), fmt_W(rr2.W).c_str(), rr2.b);
                }
            }
            printf("\n");
            fflush(stdout);
        }
    }

    if (branch_slot < 0 || undef_hi <= 1 || defs_made >= 2) return;
    int lim = used_states < NS ? used_states + 1 : NS;
    for (int nx = 0; nx < lim; ++nx) {
        for (int w = 0; w < 2; ++w) {
            for (int d = -1; d <= 1; d += 2) {
                t[branch_slot] = {w, d, nx, true};
                dfs(nx + 1 > used_states ? nx + 1 : used_states, defs_made + 1);
                t[branch_slot].def = false;
            }
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) return 1;
    std::string base = argv[1];
    if (argc > 2) BUD_BLANK = atoll(argv[2]);
    if (argc > 3) BUD_PROBE = atoll(argv[3]);

    for (int q = 0; q < 8; ++q) {
        for (int c = 0; c < 2; ++c) {
            const char *x = base.c_str() + 7*q + 3*c;
            if (x[0] == '-') t[2*q + c] = {0, 0, 0, false};
            else t[2*q + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true};
        }
    }
    t[16] = {0, 0, 0, false};
    t[17] = {0, 0, 0, false};

    for (int T = 0; T < 16; ++T) {
        if (!t[T].def) continue;
        Tr save = t[T];
        // Redirect T to state I (8), or to state H (7) if not already going to H
        int targets[2] = {I_ST, H_ST};
        for (int ti = 0; ti < 2; ++ti) {
            int tgt = targets[ti];
            if (tgt == H_ST && save.nx == H_ST) continue;
            for (int w = 0; w < 2; ++w) {
                for (int d = -1; d <= 1; d += 2) {
                    t[T] = {w, d, tgt, true};
                    cur_tag = slot_name(T) + "->" + std::string(1, char('0'+w)) + (d > 0 ? "R" : "L") + char('A'+tgt);
                    dfs(tgt == I_ST ? 9 : 8, 0);
                }
            }
        }
        t[T] = save;
    }
    printf("#summary total_nodes=%lld interesting=%lld quiet_halts=%lld\n", total_nodes, interesting_leaves, quiet_halts);
    return 0;
}
