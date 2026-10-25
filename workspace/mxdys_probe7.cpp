// Single-table calibration wrapper; does not alter the upstream or pilot source.
#define BB_STATES 7
#define main mxdys_embedded_main
#include "mxdys_pilot.cpp"
#undef main

int main(int argc, char **argv) {
    pilot_configure();
    pilot_enabled = true;
    pilot_seconds = 30;
    pilot_shard = -1;
    pilot_round = 10;
    log_stream = std::ofstream("mxdys_probe7_holdouts.txt");
    std::vector<std::tuple<std::string,std::string,std::string>> cases;
    if (argc == 2) {
        cases.emplace_back("custom", argv[1], "");
    } else {
        assert(argc == 1);
        cases = {
            {"BB7 champion", "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF", "holdout"},
            {"right-moving loop", "1RA1RA_1RA1RA_1RA1RA_1RA1RA_1RA1RA_1RA1RA_1RA1RZ", "nonhalting"},
            {"BB4 champion padded to seven states", "1RB1LB_1LA0LC_1RZ1LD_1RD0RA_0RA0RA_0RA0RA_0RA0RA", "halting"}
        };
    }
    std::ofstream out("mxdys_probe7_calibration.json");
    out << "{\n  \"cases\": [\n";
    bool all_passed = true, first = true;
    for (const auto &[name, text, expected] : cases) {
        std::string encoded = text;
        for (size_t at = 0; (at = encoded.find("1RZ", at)) != std::string::npos; ) {
            encoded.replace(at, 3, "---");
            at += 3;
        }
        TM tm;
        std::stringstream input(encoded);
        input >> tm;
        int64_t rest = 0, a = 1, b = 1;
        for (int64_t s = 0; s < N_STATE; ++s) {
            for (int64_t r = 0; r < N_CHAR; ++r) {
                const auto &tr = tm.trans[s][r];
                if (tr.nxt == -1) ++rest;
                else {
                    a = std::max(a, std::max(s, tr.nxt) + 1);
                    b = std::max(b, std::max(r, tr.out) + 1);
                }
            }
        }
        // With zero or one undefined edge, TNF::dfs cannot enumerate children.
        assert(rest <= 1);
        const auto halts_before = pilot_halting_hits;
        const auto t0 = std::chrono::steady_clock::now();
        TNF tnf;
        tnf.dfs(tm, a, b, rest);
        double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
        std::string result = tnf.n_unknown ? "holdout" :
            pilot_halting_hits > halts_before ? "halting" :
            tnf.n_decided ? "nonhalting" : "unvisited";
        bool passed = (expected.empty() || result == expected) && tnf.n_tot == 1;
        all_passed &= passed;
        if (!first) out << ",\n";
        first = false;
        out << "    {\"name\": \"" << name << "\", \"tm\": \"" << text
            << "\", \"result\": \"" << result << "\", \"expected\": \"" << expected
            << "\", \"nodes_processed\": " << tnf.n_tot << ", \"elapsed_seconds\": "
            << elapsed << ", \"passed\": " << (passed ? "true" : "false") << "}";
        std::cout << name << ": " << result << " in " << elapsed << " seconds\n";
    }
    out << "\n  ],\n  \"all_passed\": " << (all_passed ? "true" : "false")
        << ",\n  \"note\": \"The BB7 champion surviving the filters is a calibration result, not a new halting proof.\"\n}\n";
    merr.flush();
    return all_passed ? 0 : 1;
}
