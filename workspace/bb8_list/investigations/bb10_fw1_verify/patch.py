s=open('sim.cpp').read()
s=s.replace("""while (std::getline(ss, e, ',')) ev[2 * (e[0] - 'A') + (e[1] - '0')] = 1; }""",
"""while (std::getline(ss, e, ',')) ev[2 * (e[0] - 'A') + (e[1] - '0')] = e.size() > 2 ? (e[2] == 'r' ? 2 : 3) : 1; }""")
s=s.replace("""        long long step = 0, nrep = 0; bool done = false; std::string out; long long rel;
""","""        long long step = 0, nrep = 0; bool done = false; std::string out; long long rel;
        long long Rc = 0, Lc = 0;  // ones strictly right / left of the head
        for (long long i = lo; i <= hi; ++i) { if (i > h) Rc += tape[i]; if (i < h) Lc += tape[i]; }
""")
s=s.replace("""            if (ev[k]) {""","""            if (ev[k] && (ev[k] == 1 || (ev[k] == 2 && Rc == 0) || (ev[k] == 3 && Lc == 0))) {""")
s=s.replace("""            tape[h] = tr.w; h += tr.d; q = tr.nx; ++step;""","""            tape[h] = tr.w;
            if (tr.d > 0) { Lc += tr.w; ++h; Rc -= tape[h]; } else { Rc += tr.w; --h; Lc -= tape[h]; }
            q = tr.nx; ++step;""")
s=s.replace("// EVENTS: comma list of StateSymbol pairs (e.g. E0,I1,J0) or '-' for none.","// EVENTS: comma list of StateSymbol pairs (e.g. E0,I1,J0; suffix r/l = only with no 1 right/left of the head) or '-'.")
open('sim.cpp','w').write(s)
