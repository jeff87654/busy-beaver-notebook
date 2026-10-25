// tinf: template inference on the run that FOLLOWS a constructed configuration (post-exhaustion phase).
//   tinf MACHINE O Q P u s al be alB beB S SKIP STEPS  < "ds a b"
// Builds K_T(ds;a;b) (template T, as rk7), runs SKIP steps silently, then STEPS steps with dlscan2's end-event census
// (both tape ends), and prints every inferred template "TMPL <side> <template string> <score-free>" plus the number of
// parseable end events per template in a second pass. Machine orientation: the template's O decides mirroring of the
// construction; printed templates are in dlscan2's own orientation (R = right end of the ORIGINAL machine's tape).
#define main dlscan2_main
#include "../../bb8_list/neighbors/dlscan2.cpp"
#undef main
int main(int argc, char **argv) {
    if (argc != 14) { fprintf(stderr, "usage\n"); return 2; }
    char **a = argv + 1;
    TM m0, m; Tmpl t;
    if (!parse(a[0], m0)) return 2;
    bool mir = a[1][0] == 'L';
    m = mir ? mirrored(m0) : m0;
    t.q = a[2][0] - 'A'; t.P = strcmp(a[3], "-") ? a[3] : ""; t.u = a[4]; t.s = a[5];
    t.al = atoll(a[6]); t.be = atoll(a[7]); t.alB = atoll(a[8]); t.beB = atoll(a[9]); t.S = strcmp(a[10], "-") ? a[10] : "";
    long long SKIP = atoll(a[11]), STEPS = atoll(a[12]);
    static char ds_s[1000000]; long long aa, bb;
    if (scanf("%999999s %lld %lld", ds_s, &aa, &bb) != 3) return 2;
    std::vector<long long> ds;
    if (strcmp(ds_s, "-")) { char *x = ds_s; while (*x) { ds.push_back(strtoll(x, &x, 10)); if (*x == ',') ++x; } }
    Prober2 pr;
    std::string w = pr.word(t, ds, aa, bb);
    // tape in the (possibly mirrored) frame; we run machine m in that frame. Census sides are reported in that frame.
    long long SZ = 1LL << 26;
    std::vector<uint8_t> tape(SZ, 0);
    long long off = SZ / 2, pos = 0, loB = 1, hiB = 0;
    for (size_t i = 0; i < w.size(); ++i) {
        long long z = -(long long)w.size() + (long long)i;
        tape[off + z] = (uint8_t)(w[i] - '0');
        if (w[i] == '1') { if (loB > hiB) loB = hiB = z; else { if (z < loB) loB = z; if (z > hiB) hiB = z; } }
    }
    int q = t.q;
    End2 ends[2];
    for (long long st = 0; st < SKIP + STEPS; ++st) {
        long long idx = pos + off;
        if (idx < 8 || idx + 8 >= SZ) { printf("TAPE %lld\n", st); break; }
        uint8_t *T = tape.data() + off;
        int c = T[pos];
        if (st >= SKIP && c == 0 && loB <= hiB) {
            bool lft = T[pos - 1] | T[pos - 2] | T[pos - 3] | T[pos - 4];
            bool rgt = T[pos + 1] | T[pos + 2] | T[pos + 3] | T[pos + 4];
            if (lft && !rgt) {
                bool clear = true;
                while (hiB > pos) { if (T[hiB]) { clear = false; break; } --hiB; }
                if (clear) { while (!T[hiB]) --hiB; end_event2(ends[0], T, q, loB, pos, 1); }
            } else if (rgt && !lft) {
                bool clear = true;
                while (loB < pos) { if (T[loB]) { clear = false; break; } ++loB; }
                if (clear) { while (!T[loB]) ++loB; end_event2(ends[1], T, q, hiB, pos, -1); }
            }
        }
        if (m.nx[q][c] < 0) { printf("HALT %lld\n", st); break; }
        int wr = m.w[q][c], d = m.d[q][c], nq = m.nx[q][c];
        T[pos] = (uint8_t)wr;
        if (wr) { if (loB > hiB) loB = hiB = pos; else { if (pos < loB) loB = pos; if (pos > hiB) hiB = pos; } }
        pos += d; q = nq;
    }
    for (int side = 0; side < 2; ++side) {
        ends[side].collect();
        auto ts = infer_templates(ends[side]);
        char o = mir ? (side == 0 ? 'L' : 'R') : (side == 0 ? 'R' : 'L');
        for (auto &tt : ts) printf("TMPL %s\n", tt.str(o).c_str());
    }
    return 0;
}
