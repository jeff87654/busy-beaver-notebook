# Modular-stack abstraction: bounded result

The new push abstraction records the binary value of the entire normalized stack modulo m, the exact k bits nearest the head, and an optional significant-length modulus. Leading blank padding leaves the initial abstract state unchanged. Ordinary symbol-bit order was checked using the actual upstream Word and DFA push_all implementations for block lengths 1, 2, and 3. Character-history decoration is disabled and asserted absent.

The finite-automata closure verifier is byte-for-byte identical to the vetted base. The only C++ changes are a new search-summary type and CLI dispatch. An infinite rightward writer passed the unchanged verifier; an immediate halter was not classified nonhalting. The source, binary, build command, hashes, calibration logs, and all command inputs/outputs are preserved.

The portfolio tested C13 and C15 across all m in {3,5,7,9,15,31}, k=2 through8, and block lengths1 through3, using length modulus1, the exact1001-step prefix, and abstract-work limit300000. All 252 attempts were inconclusive: {'unresolved': 252}. There were no new proofs. Search wall time was 40.35s across two workers, and summed per-process wall times were 69.49s.

Reproduction artifacts: lastfive_modular_build.py/json, lastfive_modular_native.cpp/exe, lastfive_modular_unit.cpp/log, lastfive_modular_calibration.json, lastfive_modular_portfolio.py, lastfive_modular_odd.py, and the two result JSON/log directories. No classification is inferred from resource-limited failure to prove closure.
