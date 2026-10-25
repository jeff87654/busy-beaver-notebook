// pbarrier_scan.cpp: Fast analyzer for 7-state P-barrier f_{w+1} loopers (MULTI, MULTI?, REBUILD, R4-SOME).
// Parses from right end to find true irreducible prefix P_true, checks blank-tape K-trace, D/Bk/E rules,
// and finds exact slot masks: mask_D, mask_B (b >> k), mask_E (empty list rebuild), and E-only slots!
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>

#ifdef _WIN32
#include <windows.h>
#endif

struct Tr { int w, d, nx; bool def; };

struct Tmpl {
    bool mirror;
    int TQ;
    std::string P, u, s, S;
    long long al, be, alB, beB;
};

// Parse tape word w from the right using u, s, al, be, alB, beB, S, and a fixed prefix P_fixed
static bool kparse_fixed(const std::string &w, const Tmpl &tm, const std::string &P_use, long long B0,
                         std::vector<long long> &ds_out, long long &a_out, long long &b_out) {
    if (w.size() < P_use.size() + tm.S.size()) return false;
    if (w.compare(0, P_use.size(), P_use) != 0) return false;
    if (w.compare(w.size() - tm.S.size(), tm.S.size(), tm.S) != 0) return false;
    std::vector<long long> runs;
    size_t i = P_use.size(), e = w.size() - tm.S.size();
    const std::string &u = tm.u, &s = tm.s;
    while (true) {
        long long k = 0; size_t i0 = i;
        while (i + u.size() <= e && w.compare(i, u.size(), u) == 0) { i += u.size(); ++k; }
        if (i == e) { runs.push_back(k); break; }
        bool fs = false;
        for (long long kk = k; kk >= 0; --kk) {
            size_t j = i0 + kk * u.size();
            if (j + s.size() <= e && w.compare(j, s.size(), s) == 0) {
                runs.push_back(kk); i = j + s.size(); fs = true; break;
            }
        }
        if (!fs) return false;
    }
    if (runs.size() < 2) return false;
    long long bl = runs.back();
    if (bl < tm.beB || (bl - tm.beB) % tm.alB != 0) return false;
    long long b = (bl - tm.beB) / tm.alB;
    if (B0 >= 0 && b != B0) return false;
    for (size_t j = 0; j + 1 < runs.size(); ++j) {
        if (runs[j] < tm.be || (runs[j] - tm.be) % tm.al != 0) return false;
    }
    ds_out.clear();
    for (size_t j = 0; j + 2 < runs.size(); ++j) {
        ds_out.push_back((runs[j] - tm.be) / tm.al);
    }
    a_out = (runs[runs.size() - 2] - tm.be) / tm.al;
    b_out = b;
    return true;
}

static std::string fmt_ds(const std::vector<long long> &ds) {
    std::string out;
    for (size_t j = 0; j < ds.size();) {
        long long v = ds[j]; size_t r = j;
        while (r < ds.size() && ds[r] == v) ++r;
        out += std::to_string(v);
        if (r - j > 1) out += "^" + std::to_string(r - j);
        if (r < ds.size()) out += ",";
        j = r;
    }
    return out;
}

static std::string make_word(const Tmpl &tm, const std::string &P_use, const std::vector<long long> &ds, long long a, long long b) {
    std::string w = P_use;
    std::vector<long long> all = ds;
    all.push_back(a);
    for (long long x : all) {
        long long cnt = tm.al * x + tm.be;
        for (long long i = 0; i < cnt; ++i) w += tm.u;
        w += tm.s;
    }
    long long bcnt = tm.alB * b + tm.beB;
    for (long long i = 0; i < bcnt; ++i) w += tm.u;
    w += tm.S;
    return w;
}

struct RunRes {
    char kind; // 'K', 'H', 'T', 'W'
    long long steps;
    int mask;
    std::vector<long long> ds;
    long long a, b;
    int hslot;
};

static RunRes run_config(const Tr t[14], const Tmpl &tm, const std::string &P_use,
                         const std::string &w_init, long long head_init, int q_init,
                         long long bud, long long B0, int target_k_events = 1) {
    long long size = 1 << 16;
    while (size < 4 * (long long)w_init.size() + 4096) size *= 2;
    std::vector<unsigned char> tp(size, 0);
    long long off = size / 2;
    long long lo = 1, hi = 0;
    for (size_t z = 0; z < w_init.size(); ++z) {
        if (w_init[z] == '1') {
            tp[off + z] = 1;
            if (lo > hi) lo = hi = (long long)z; else hi = (long long)z;
        }
    }
    long long pos = head_init;
    int q = q_init;
    int mask = 0;
    int k_seen = 0;
    std::vector<long long> ds; long long a = 0, b = 0;
    for (long long st = 0; st < bud; ++st) {
        if (pos + off < 4 || pos + off + 4 >= size) {
            if (size >= (1LL << 24)) return {'W', st, mask, {}, 0, 0, -1};
            std::vector<unsigned char> nt(size * 2, 0);
            memcpy(nt.data() + size / 2, tp.data(), size);
            off += size / 2; size *= 2; tp.swap(nt);
        }
        unsigned char *T = tp.data() + off;
        int c = T[pos];
        if (st > 0 && c == 0 && q == tm.TQ && lo <= hi) {
            while (lo <= hi && !T[hi]) --hi;
            while (lo <= hi && !T[lo]) ++lo;
            if (pos > hi && lo <= hi && pos - lo < 50000) {
                std::string ww; ww.reserve(pos - lo);
                for (long long i = lo; i < pos; ++i) ww += char('0' + T[i]);
                if (kparse_fixed(ww, tm, P_use, B0, ds, a, b)) {
                    ++k_seen;
                    if (k_seen >= target_k_events) {
                        return {'K', st, mask, ds, a, b, -1};
                    }
                }
            }
        }
        int sl = 2 * q + c;
        if (!t[sl].def) return {'H', st, mask, {}, 0, 0, sl};
        mask |= (1 << sl);
        T[pos] = t[sl].w;
        if (t[sl].w) {
            if (lo > hi) lo = hi = pos;
            else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; }
        }
        pos += t[sl].d;
        q = t[sl].nx;
    }
    return {'T', bud, mask, {}, 0, 0, -1};
}

static std::string mask_str(int mask) {
    std::string s;
    for (int i = 0; i < 14; ++i) {
        if (mask & (1 << i)) {
            if (!s.empty()) s += ",";
            s += char('A' + i / 2);
            s += char('0' + i % 2);
        }
    }
    return s.empty() ? "-" : s;
}

int main(int argc, char **argv) {
#ifdef _WIN32
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
#endif
    if (argc < 2) {
        fprintf(stderr, "Usage: pbarrier_scan <tsv_file> [max_blank_steps]\n");
        return 1;
    }
    long long max_blank = argc > 2 ? atoll(argv[2]) : 1000000;
    std::ifstream f(argv[1]);
    std::string line;
    printf("machine\tgrade\ttmpl\tP_true\tB0\tblank_trace\tE_map\tmask_D\tmask_B\tmask_E\tE_only\tB_only\tundef\n");
    while (std::getline(f, line)) {
        if (line.empty() || line[0] == '#' || line.substr(0, 7) == "machine") continue;
        std::vector<std::string> cols;
        std::stringstream ss(line);
        std::string item;
        while (std::getline(ss, item, '\t')) cols.push_back(item);
        if (cols.size() < 5) continue;
        std::string m = cols[0];
        std::string grade = cols[3];
        std::string tstr = cols[4];

        // Parse template string: e.g. L,C,P=1010,u=01,s=0,d=1d+0,b=1b+0,S=-
        Tmpl tm;
        std::stringstream ts(tstr);
        std::string tok;
        std::vector<std::string> tparts;
        while (std::getline(ts, tok, ',')) tparts.push_back(tok);
        if (tparts.size() < 8) continue;
        tm.mirror = (tparts[0] == "L");
        tm.TQ = tparts[1][0] - 'A';
        for (size_t i = 2; i < tparts.size(); ++i) {
            size_t eq = tparts[i].find('=');
            if (eq == std::string::npos) continue;
            std::string k = tparts[i].substr(0, eq), v = tparts[i].substr(eq + 1);
            if (k == "P") tm.P = (v == "-" ? "" : v);
            else if (k == "u") tm.u = v;
            else if (k == "s") tm.s = v;
            else if (k == "S") tm.S = (v == "-" ? "" : v);
            else if (k == "d") sscanf(v.c_str(), "%lldd+%lld", &tm.al, &tm.be);
            else if (k == "b") sscanf(v.c_str(), "%lldb+%lld", &tm.alB, &tm.beB);
        }

        // Strip leading digits from tm.P if tm.P starts with something + u^(al*d+be) s
        std::string P_true = tm.P;
        while (true) {
            bool stripped = false;
            std::string unit_s = tm.s;
            if (P_true.size() > unit_s.size() && P_true.compare(P_true.size() - unit_s.size(), unit_s.size(), unit_s) == 0) {
                size_t rem = P_true.size() - unit_s.size();
                long long k = 0;
                while (rem >= tm.u.size() && P_true.compare(rem - tm.u.size(), tm.u.size(), tm.u) == 0) {
                    rem -= tm.u.size(); ++k;
                }
                if (rem > 0 && k >= tm.be && (k - tm.be) % tm.al == 0) {
                    P_true = P_true.substr(0, rem);
                    stripped = true;
                }
            }
            if (!stripped) break;
        }

        Tr t[14];
        int undef_slot = -1;
        for (int q = 0; q < 7; ++q) {
            for (int c = 0; c < 2; ++c) {
                const char *x = m.c_str() + 7 * q + 3 * c;
                if (x[0] == '-') { t[2 * q + c] = {0, 0, -1, false}; undef_slot = 2 * q + c; }
                else {
                    int d = (x[1] == 'R' ? 1 : -1) * (tm.mirror ? -1 : 1);
                    t[2 * q + c] = {x[0] - '0', d, x[2] - 'A', true};
                }
            }
        }

        // Run from blank tape to find B0 and blank K-trace
        long long size = 1 << 16, off = size / 2;
        std::vector<unsigned char> tp(size, 0);
        long long lo = 1, hi = 0, pos = 0; int q = 0;
        std::string last_ds_str = "#";
        long long B0 = -1;
        std::vector<std::string> btrace;
        for (long long st = 0; st < max_blank; ++st) {
            if (pos + off < 4 || pos + off + 4 >= size) {
                if (size >= (1LL << 24)) break;
                std::vector<unsigned char> nt(size * 2, 0);
                memcpy(nt.data() + size / 2, tp.data(), size);
                off += size / 2; size *= 2; tp.swap(nt);
            }
            unsigned char *T = tp.data() + off;
            int c = T[pos];
            if (st > 0 && c == 0 && q == tm.TQ && lo <= hi) {
                while (lo <= hi && !T[hi]) --hi;
                while (lo <= hi && !T[lo]) ++lo;
                if (pos > hi && lo <= hi && pos - lo < 50000) {
                    std::string ww; ww.reserve(pos - lo);
                    for (long long i = lo; i < pos; ++i) ww += char('0' + T[i]);
                    std::vector<long long> ds; long long a, b;
                    if (kparse_fixed(ww, tm, P_true, -1, ds, a, b)) {
                        std::string dstr = fmt_ds(ds);
                        if (dstr != last_ds_str) {
                            last_ds_str = dstr;
                            B0 = b;
                            if (btrace.size() < 8) {
                                btrace.push_back(std::to_string(st) + ":[" + dstr + ";" + std::to_string(a) + ";" + std::to_string(b) + "](L" + std::to_string(ds.size()) + ")");
                            }
                        }
                    }
                }
            }
            int sl = 2 * q + c;
            if (!t[sl].def) { btrace.push_back("HALT@" + std::to_string(st)); break; }
            T[pos] = t[sl].w;
            if (t[sl].w) { if (lo > hi) lo = hi = pos; else { if (pos < lo) lo = pos; if (pos > hi) hi = pos; } }
            pos += t[sl].d; q = t[sl].nx;
        }
        if (B0 < 0) B0 = 0;

        // Test D configs: [1, 2; 3; B0], [2, 1; 4; B0] (1 K-step with B0 fixed -> wait: in M4, [1,2;3;1] takes 3 R1 steps + 1 R2 step to reach next B0!)
        // Wait: in M4, during R1, b increases (b=1 -> 3 -> 5 -> 7), and only after R2 does b return to B0!
        // So if we fix B0 in kparse_fixed, target_k_events = 1 stops at the NEXT moment where b == B0, which is a full D step (decrementing the last digit by 1, or reducing a by 1 if B0 is reset every D step)!
        int mask_D = 0;
        for (int a_test : {2, 3}) {
            std::string w = make_word(tm, P_true, {1, 2}, a_test, B0);
            RunRes r = run_config(t, tm, P_true, w, w.size(), tm.TQ, 50000, B0, 1);
            if (r.kind == 'K') mask_D |= r.mask;
        }

        // Test Bk configs: [1, 0; 5; B0], [1, 0, 0; 6; B0], [1, 0, 0, 0; 7; B0]
        // Stop when ds changes (or after 2 K-events with B0)
        int mask_B = 0;
        for (int k_z = 1; k_z <= 3; ++k_z) {
            std::vector<long long> ds_init = {2};
            for (int z = 0; z < k_z; ++z) ds_init.push_back(0);
            std::string w = make_word(tm, P_true, ds_init, k_z + 4, B0);
            RunRes r = run_config(t, tm, P_true, w, w.size(), tm.TQ, 100000, B0, 1);
            if (r.kind == 'K' && r.ds == ds_init) {
                // B0 was preserved by D, so we need to run until a=0 and borrow happens!
                r = run_config(t, tm, P_true, w, w.size(), tm.TQ, 200000, B0, k_z + 5);
            }
            if (r.kind == 'K') mask_B |= r.mask;
        }

        // Test E configs: K(; a; B0) for a = 1, 2, 3, 4
        int mask_E = 0;
        std::string emap_str;
        for (int a_e = 1; a_e <= 4; ++a_e) {
            std::string w = make_word(tm, P_true, {}, a_e, B0);
            // Run until ds is non-empty or halt
            long long sz2 = 1 << 16, off2 = sz2 / 2;
            std::vector<unsigned char> tp2(sz2, 0);
            long long lo2 = 1, hi2 = 0;
            for (size_t z = 0; z < w.size(); ++z) if (w[z] == '1') { tp2[off2 + z] = 1; if (lo2 > hi2) lo2 = hi2 = z; else hi2 = z; }
            long long pos2 = w.size(); int q2 = tm.TQ; int m_e = 0;
            std::string out_e = "T";
            for (long long st = 0; st < 200000; ++st) {
                if (pos2 + off2 < 4 || pos2 + off2 + 4 >= sz2) {
                    if (sz2 >= (1LL << 24)) { out_e = "W"; break; }
                    std::vector<unsigned char> nt(sz2 * 2, 0);
                    memcpy(nt.data() + sz2 / 2, tp2.data(), sz2);
                    off2 += sz2 / 2; sz2 *= 2; tp2.swap(nt);
                }
                unsigned char *T2 = tp2.data() + off2; int c2 = T2[pos2];
                if (st > 0 && c2 == 0 && q2 == tm.TQ && lo2 <= hi2) {
                    while (lo2 <= hi2 && !T2[hi2]) --hi2;
                    while (lo2 <= hi2 && !T2[lo2]) ++lo2;
                    if (pos2 > hi2 && lo2 <= hi2 && pos2 - lo2 < 50000) {
                        std::string ww; ww.reserve(pos2 - lo2);
                        for (long long i = lo2; i < pos2; ++i) ww += char('0' + T2[i]);
                        std::vector<long long> ds; long long a, b;
                        if (kparse_fixed(ww, tm, P_true, B0, ds, a, b) && !ds.empty()) {
                            out_e = "[" + fmt_ds(ds) + ";" + std::to_string(a) + "](L" + std::to_string(ds.size()) + ")";
                            mask_E |= m_e;
                            break;
                        }
                    }
                }
                int sl = 2 * q2 + c2;
                if (!t[sl].def) { out_e = "H"; mask_E |= m_e; break; }
                m_e |= (1 << sl);
                T2[pos2] = t[sl].w;
                if (t[sl].w) { if (lo2 > hi2) lo2 = hi2 = pos2; else { if (pos2 < lo2) lo2 = pos2; if (pos2 > hi2) hi2 = pos2; } }
                pos2 += t[sl].d; q2 = t[sl].nx;
            }
            if (!emap_str.empty()) emap_str += " ";
            emap_str += "a=" + std::to_string(a_e) + "->" + out_e;
        }

        int e_only = mask_E & ~(mask_D | mask_B);
        int b_only = (mask_B & ~mask_D);
        std::string bt_s;
        for (size_t i = 0; i < btrace.size(); ++i) { if (i) bt_s += " "; bt_s += btrace[i]; }
        std::string u_s = undef_slot >= 0 ? (std::string(1, char('A' + undef_slot / 2)) + char('0' + undef_slot % 2)) : "-";
        printf("%s\t%s\t%s\t%s\t%lld\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n",
               m.c_str(), grade.c_str(), tstr.c_str(), (P_true.empty() ? "-" : P_true.c_str()), B0,
               bt_s.c_str(), emap_str.c_str(),
               mask_str(mask_D).c_str(), mask_str(mask_B).c_str(), mask_str(mask_E).c_str(),
               mask_str(e_only).c_str(), mask_str(b_only).c_str(), u_s.c_str());
    }
    return 0;
}
