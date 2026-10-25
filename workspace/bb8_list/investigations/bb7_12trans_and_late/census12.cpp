// census12.cpp: 12-Transition Engine Census across all 7-state machines in reb7/pool_all.tsv (+ pool7f.tsv)
// Compiled with: g++ -O3 -static -o census12.exe census12.cpp
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>
#include <thread>
#include <mutex>
#include <atomic>

struct TM {
    int w[7][2];
    int d[7][2]; // +1 for R, -1 for L
    int nx[7][2]; // 0..6, or -1 for ---
    int halt_slot; // 0..13
};

static bool parse_tm(const std::string &s, TM &m) {
    if (s.size() < 47) return false;
    m.halt_slot = -1;
    for (int q = 0; q < 7; ++q) {
        for (int c = 0; c < 2; ++c) {
            int idx = q * 7 + c * 3;
            if (s[idx] == '-') {
                m.w[q][c] = 1;
                m.d[q][c] = 1;
                m.nx[q][c] = -1;
                m.halt_slot = q * 2 + c;
            } else {
                m.w[q][c] = s[idx] - '0';
                m.d[q][c] = (s[idx + 1] == 'R') ? 1 : -1;
                m.nx[q][c] = s[idx + 2] - 'A';
            }
        }
    }
    return true;
}

struct Template {
    bool valid = false;
    char side = 'R';
    int Q = 0;
    std::string P, u, s, S;
    long long d_al = 1, d_be = 0, b_al = 1, b_be = 0;
};

static Template parse_template(const std::string &ts) {
    Template T;
    if (ts.empty() || ts == "-") return T;
    std::vector<std::string> parts;
    std::stringstream ss(ts);
    std::string item;
    while (std::getline(ss, item, ',')) parts.push_back(item);
    if (parts.size() < 8) return T;
    T.side = parts[0][0];
    T.Q = parts[1][0] - 'A';
    for (size_t i = 2; i < parts.size(); ++i) {
        const std::string &p = parts[i];
        if (p.rfind("P=", 0) == 0) { T.P = p.substr(2); if (T.P == "-") T.P = ""; }
        else if (p.rfind("u=", 0) == 0) { T.u = p.substr(2); }
        else if (p.rfind("s=", 0) == 0) { T.s = p.substr(2); }
        else if (p.rfind("S=", 0) == 0) { T.S = p.substr(2); if (T.S == "-") T.S = ""; }
        else if (p.rfind("d=", 0) == 0) {
            sscanf(p.c_str(), "d=%lldd+%lld", &T.d_al, &T.d_be);
        } else if (p.rfind("b=", 0) == 0) {
            sscanf(p.c_str(), "b=%lldb+%lld", &T.b_al, &T.b_be);
        }
    }
    T.valid = !T.u.empty() && !T.s.empty() && T.Q >= 0 && T.Q < 7;
    return T;
}

struct Row {
    std::string machine;
    std::string grade;
    std::string sources;
    std::string verdict;
    std::string stage;
    std::string tmpl_str;
    std::string rules;
    std::string exhaustion;
};

struct CensusResult {
    long long total_steps = 0;
    bool halted = false;
    bool oob = false;
    long long span = 0;
    long long cnt_early[14] = {0};   // steps 1..5000
    long long cnt_mid[14] = {0};     // steps 5001..100000
    long long cnt_vlate[14] = {0};   // steps 100001..5000000
    long long first_step[14] = {0};
    long long last_step[14] = {0};
    long long cnt_dbk[14] = {0};     // synthetic D + Bk probe
    long long cnt_exh[14] = {0};     // synthetic E(b) probe
    int n_used_total = 0;
    int n_used_after_5k = 0;
    int n_used_after_100k = 0;
    int n_engine = 0;
    std::string slot_roles[14];
    std::string non_engine_slots;
};

static std::string slot_name(int s) {
    char buf[4];
    snprintf(buf, sizeof(buf), "%c%d", 'A' + (s / 2), s % 2);
    return std::string(buf);
}

static std::string rep_str(const std::string &x, long long k) {
    std::string o;
    if (k > 0) o.reserve(x.size() * k);
    for (long long i = 0; i < k; ++i) o += x;
    return o;
}

// Run synthetic probe on word w (placed at 0..w.size()-1, head at w.size() in state Q, mirrored if side=='L')
static void run_word_probe(const TM &m, const Template &T, const std::string &w, long long max_steps, long long cnt_out[14], bool stop_on_first_d_drop = false, long long init_d0 = -1) {
    const long long SZ = 1 << 20;
    const long long OFF = SZ / 2;
    std::vector<unsigned char> tape(SZ, 0);
    long long lo = 1, hi = 0;
    auto put = [&](long long p, int v) {
        tape[OFF + p] = v;
        if (v) {
            if (lo > hi) lo = hi = p;
            else { if (p < lo) lo = p; if (p > hi) hi = p; }
        }
    };
    for (size_t i = 0; i < w.size(); ++i) put((long long)i, w[i] == '1' ? 1 : 0);
    long long pos = (long long)w.size();
    int q = T.Q;
    int dir_mult = (T.side == 'L') ? -1 : 1;
    for (long long st = 1; st <= max_steps; ++st) {
        if (pos + OFF <= 4 || pos + OFF >= SZ - 5) break;
        int c = tape[OFF + pos];
        if (stop_on_first_d_drop && st > 10 && c == 0 && q == T.Q && lo <= hi && pos > hi) {
            // Check if K-moment reached with first digit decremented
            while (lo <= hi && !tape[OFF + hi]) --hi;
            while (lo <= hi && !tape[OFF + lo]) ++lo;
            if (pos > hi && hi - lo < 50000) {
                std::string cw;
                cw.reserve(pos - lo);
                for (long long i = lo; i < pos; ++i) cw += char('0' + tape[OFF + i]);
                if (cw.size() >= T.P.size() + T.S.size() &&
                    cw.compare(0, T.P.size(), T.P) == 0 &&
                    cw.compare(cw.size() - T.S.size(), T.S.size(), T.S) == 0) {
                    long long e = (long long)cw.size() - (long long)T.S.size();
                    std::vector<long long> rr;
                    bool ok = true;
                    while (true) {
                        long long k = 0;
                        while (e - (long long)T.u.size() >= (long long)T.P.size() &&
                               cw.compare(e - T.u.size(), T.u.size(), T.u) == 0) {
                            e -= T.u.size(); ++k;
                        }
                        rr.push_back(k);
                        if (e - (long long)T.s.size() >= (long long)T.P.size() &&
                            cw.compare(e - T.s.size(), T.s.size(), T.s) == 0) {
                            e -= T.s.size();
                        } else break;
                    }
                    if (e == (long long)T.P.size() && rr.size() >= 3) {
                        long long top_raw = rr.back();
                        long long top_d = (top_raw - T.d_be) / T.d_al;
                        if (top_d < init_d0) break;
                    }
                }
            }
        }
        int s = q * 2 + c;
        if (m.nx[q][c] < 0) break;
        cnt_out[s]++;
        int nw = m.w[q][c];
        tape[OFF + pos] = nw;
        if (nw) {
            if (lo > hi) lo = hi = pos;
            else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; }
        }
        pos += m.d[q][c] * dir_mult;
        q = m.nx[q][c];
    }
}

static CensusResult analyze_machine(const Row &row, long long max_steps) {
    CensusResult R;
    TM m;
    parse_tm(row.machine, m);
    const long long SZ = 1 << 24; // 16M cells
    const long long OFF = SZ / 2;
    std::vector<unsigned char> tape(SZ, 0);
    long long pos = 0, lo = 0, hi = 0;
    int q = 0;
    for (long long st = 1; st <= max_steps; ++st) {
        if (pos + OFF <= 4 || pos + OFF >= SZ - 5) {
            R.oob = true;
            R.total_steps = st - 1;
            break;
        }
        int c = tape[OFF + pos];
        int s = q * 2 + c;
        if (m.nx[q][c] < 0) {
            R.halted = true;
            R.total_steps = st;
            if (R.first_step[s] == 0) R.first_step[s] = st;
            R.last_step[s] = st;
            if (st <= 5000) R.cnt_early[s]++;
            else if (st <= 100000) R.cnt_mid[s]++;
            else R.cnt_vlate[s]++;
            break;
        }
        if (R.first_step[s] == 0) R.first_step[s] = st;
        R.last_step[s] = st;
        if (st <= 5000) R.cnt_early[s]++;
        else if (st <= 100000) R.cnt_mid[s]++;
        else R.cnt_vlate[s]++;

        tape[OFF + pos] = m.w[q][c];
        pos += m.d[q][c];
        q = m.nx[q][c];
        if (pos < lo) lo = pos;
        if (pos > hi) hi = pos;
    }
    if (!R.halted && !R.oob) R.total_steps = max_steps;
    R.span = hi - lo + 1;

    Template T = parse_template(row.tmpl_str);
    if (T.valid && row.verdict.find("LOW-GROWTH") == std::string::npos) {
        // Probe D + Bk on K([2, 1, 0, 0, 2]; a=2; b=24)
        auto enc_d = [&](long long d) { return rep_str(T.u, T.d_al * d + T.d_be) + T.s; };
        std::string w_dbk = T.P + enc_d(2) + enc_d(1) + enc_d(0) + enc_d(0) + enc_d(2)
                          + enc_d(2) + rep_str(T.u, T.b_al * 24 + T.b_be) + T.S;
        run_word_probe(m, T, w_dbk, 300000, R.cnt_dbk, true, 2);

        // Probe E(b) on K([0]; a=0; b=20..23)
        for (long long b = 20; b <= 23; ++b) {
            std::string w_exh = T.P + enc_d(0) + rep_str(T.u, T.b_al * b + T.b_be) + T.S;
            run_word_probe(m, T, w_exh, 50000, R.cnt_exh, false, -1);
        }
    }

    std::vector<std::string> non_eng;
    for (int s = 0; s < 14; ++s) {
        if (s == m.halt_slot) {
            R.slot_roles[s] = "HALT";
            continue;
        }
        long long tot = R.cnt_early[s] + R.cnt_mid[s] + R.cnt_vlate[s];
        long long late = R.cnt_mid[s] + R.cnt_vlate[s];
        if (tot > 0) R.n_used_total++;
        if (late > 0) R.n_used_after_5k++;
        if (R.cnt_vlate[s] > 0) R.n_used_after_100k++;

        // Is slot s part of the steady-state D + Bk engine?
        // A slot is ENGINE if it is used > 20 times after step 5000 AND used after step 100k (or if machine halted early, used in cnt_dbk)
        bool is_engine = (late > 20 && R.cnt_vlate[s] > 0) || (R.halted && R.cnt_dbk[s] > 0 && late > 20);
        if (is_engine) {
            R.n_engine++;
            R.slot_roles[s] = "ENGINE";
        } else {
            if (tot == 0) {
                R.slot_roles[s] = (R.cnt_exh[s] > 0) ? "UNUSED_BLANK(EXH_PROBE)" : "UNUSED";
            } else if (late == 0) {
                // Used only in steps 1..5000! Check if used at exhaustion (like F0 in X33) or only at startup (like G0 in champ_231)
                if (R.cnt_dbk[s] == 0 && R.cnt_exh[s] > 0 && R.last_step[s] > 20) {
                    R.slot_roles[s] = "EARLY_ONLY(EXH:" + std::to_string(R.cnt_early[s]) + "@t<=" + std::to_string(R.last_step[s]) + ")";
                } else {
                    R.slot_roles[s] = "STARTUP_ONLY(" + std::to_string(R.cnt_early[s]) + "@t<=" + std::to_string(R.last_step[s]) + ")";
                }
            } else {
                // Used after step 5000, but <= 20 times or 0 times after 100k (e.g. exhaustion in [5001, 100000])
                R.slot_roles[s] = "RARE_LATE(e=" + std::to_string(R.cnt_early[s]) + ",m=" + std::to_string(R.cnt_mid[s]) + ",vl=" + std::to_string(R.cnt_vlate[s]) + ",last=" + std::to_string(R.last_step[s]) + ")";
            }
            non_eng.push_back(slot_name(s) + ":" + R.slot_roles[s]);
        }
    }
    for (size_t i = 0; i < non_eng.size(); ++i) {
        if (i > 0) R.non_engine_slots += ";";
        R.non_engine_slots += non_eng[i];
    }
    if (R.non_engine_slots.empty()) R.non_engine_slots = "-";
    return R;
}

int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    std::string verdicts_path = (argc > 1) ? argv[1] : "C:\\Users\\jeffr\\Downloads\\bb8\\bb7_holdouts\\reb7\\final_all_verdicts.tsv";
    std::string out_path = (argc > 2) ? argv[2] : "census12_all.tsv";
    long long max_steps = (argc > 3) ? atoll(argv[3]) : 5000000LL;

    std::vector<Row> rows;
    {
        std::ifstream fin(verdicts_path);
        std::string line;
        bool header = true;
        while (std::getline(fin, line)) {
            if (header) { header = false; continue; }
            if (line.empty()) continue;
            std::vector<std::string> f;
            std::stringstream ss(line);
            std::string item;
            while (std::getline(ss, item, '\t')) f.push_back(item);
            if (f.size() >= 7) {
                Row r;
                r.machine = f[0];
                r.grade = f[1];
                r.sources = f[2];
                r.verdict = f[3];
                r.stage = f[4];
                r.tmpl_str = f[6];
                r.rules = (f.size() > 7) ? f[7] : "-";
                r.exhaustion = (f.size() > 8) ? f[8] : "-";
                rows.push_back(r);
            }
        }
    }

    fprintf(stderr, "Loaded %zu machines from %s. Running %lld steps per machine on 2 threads...\n", rows.size(), verdicts_path.c_str(), max_steps);

    std::vector<CensusResult> results(rows.size());
    std::atomic<size_t> next_idx{0};

    auto worker = [&]() {
        SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_IDLE);
        while (true) {
            size_t idx = next_idx.fetch_add(1);
            if (idx >= rows.size()) break;
            results[idx] = analyze_machine(rows[idx], max_steps);
            if ((idx + 1) % 200 == 0) {
                fprintf(stderr, "  processed %zu / %zu\n", idx + 1, rows.size());
            }
        }
    };

    std::thread t1(worker);
    std::thread t2(worker);
    t1.join();
    t2.join();

    std::ofstream fout(out_path);
    fout << "machine\tgrade\tverdict\tstage\tn_used_total\tn_used_after_5k\tn_used_after_100k\tn_engine\tnon_engine_slots\tspan\ttemplate\trules\texhaustion\n";
    for (size_t i = 0; i < rows.size(); ++i) {
        const auto &r = rows[i];
        const auto &c = results[i];
        fout << r.machine << "\t"
             << r.grade << "\t"
             << r.verdict << "\t"
             << r.stage << "\t"
             << c.n_used_total << "\t"
             << c.n_used_after_5k << "\t"
             << c.n_used_after_100k << "\t"
             << c.n_engine << "\t"
             << c.non_engine_slots << "\t"
             << c.span << "\t"
             << r.tmpl_str << "\t"
             << r.rules << "\t"
             << r.exhaustion << "\n";
    }
    fout.close();
    fprintf(stderr, "Done! Wrote %s\n", out_path.c_str());
    return 0;
}
