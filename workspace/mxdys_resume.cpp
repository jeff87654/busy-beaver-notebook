// Resume only final-DFS frontier records from mxdys_pilot.cpp.
// Build with -DBB_STATES=7 or 8; the default is 8.
#define main mxdys_embedded_main
#include "mxdys_pilot.cpp"
#undef main

int main(int argc, char **argv) {
    assert(argc == 3 && !std::strcmp(argv[1], "resume"));
    // Read before opening output streams, so a mistaken repeated prefix cannot
    // truncate an input frontier that has not yet been read.
    std::ifstream input(argv[2]);
    assert(input.is_open());
    std::vector<std::tuple<int64_t,TM,int64_t,int64_t,int64_t>> work;
    for (std::string line; std::getline(input, line); ) {
        if (line.empty()) continue;
        int64_t shard, round, a, b, c;
        TM tm;
        std::stringstream row(line);
        assert(row >> shard >> round >> tm >> a >> b >> c);
        assert(round == 10);
        int64_t actual_rest = 0;
        for (int64_t s = 0; s < N_STATE; ++s)
            for (int64_t r = 0; r < N_CHAR; ++r)
                actual_rest += tm.trans[s][r].nxt == -1;
        assert(actual_rest == c && a <= N_STATE && b <= N_CHAR);
        work.emplace_back(shard,tm,a,b,c);
    }
    pilot_configure();
    if (!pilot_enabled) {
        pilot_enabled = true;
        pilot_frontier.open(pilot_prefix + "_frontier.txt");
        assert(pilot_frontier.is_open());
    }
    if (pilot_seconds == 0) pilot_seconds = 30;
    pilot_round = 10;
    log_stream = std::ofstream(pilot_prefix + "_holdouts.txt");
    assert(log_stream.is_open());
    std::signal(SIGINT, sigint_handler);
    TNF tnf;
    for (auto &[shard,tm,a,b,c] : work) {
        pilot_shard = shard;
        tnf.dfs(tm,a,b,c);
    }
    std::cout << "Resumed " << work.size() << " roots; " << tnf.n_tot
              << " nodes processed, " << tnf.n_unknown << " holdouts.\n";
    pilot_finish();
    return 0;
}
