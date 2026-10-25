// rounds MACHINE RUNSPEC NSTEPS [maxprint]: run from a B-frontier word; at each B-frontier (head on blank right of
// tape, state B) compare with the previous B-frontier tape: print steps, unchanged-prefix length, turning depth
// (cells from the right end to the first changed cell), and the changed suffixes in run notation.
#include <bits/stdc++.h>
using namespace std;
#include "../bb8_m7_0RB0LC_opus/runs.h"
struct T2 { int w, d, q; bool ok; };
static string runs_of(const string& s) {
  // run notation of a 0/1 string (no compression)
  string o; size_t i = 0;
  while (i < s.size() && s[i] == '0') { o += "0"; i++; }
  if (!o.empty()) o += " ";
  while (i < s.size()) {
    size_t j = i; while (j < s.size() && s[j] == '1') j++;
    size_t k = j; while (k < s.size() && s[k] == '0') k++;
    long long ones = j - i, z = k - j;
    o += to_string(ones) + (z == 0 ? "." : z == 1 ? "" : z == 2 ? "|" : "|" + to_string(z) + "|") + " ";
    i = k;
  }
  return o;
}
static string spec2word(const string& spec);
int main(int argc, char** argv) {
  string ms = argv[1]; string spec = argv[2]; long long N = atoll(argv[3]); long long maxp = argc > 4 ? atoll(argv[4]) : 1000000;
  T2 tm[8][2]; int ns = 0; { stringstream ss(ms); string r; while (getline(ss, r, '_')) { for (int c = 0; c < 2; c++) { string t = r.substr(3 * c, 3); if (t[0] == '-') tm[ns][c] = {0, 0, 0, false}; else tm[ns][c] = {t[0] - '0', t[1] == 'R' ? 1 : -1, t[2] - 'A', true}; } ns++; } }
  string w = spec2word(spec);
  long long SZ = 1LL << 24; vector<uint8_t> tape(SZ, 0); long long off = SZ / 4;
  for (size_t i = 0; i < w.size(); i++) tape[off + i] = w[i] - '0';
  long long p = off + w.size(); int q = 1; long long mx = p;
  string prev; long long prevStep = 0; long long printed = 0;
  auto snap = [&](long long a, long long b) { string s; for (long long k = a; k <= b; k++) s += char('0' + tape[k]); return s; };
  for (long long st = 0; st < N; st++) {
    if (q == 1 && tape[p] == 0 && p >= mx) {
      long long b = p - 1; while (b > off && !tape[b]) b--;
      string cur = snap(off, b);
      if (!prev.empty()) {
        size_t l = 0; while (l < prev.size() && l < cur.size() && prev[l] == cur[l]) l++;
        // back up to a run boundary (start of the run containing the first difference)
        size_t l2 = l; while (l2 > 0 && !(prev[l2 - 1] == '0' && l2 < prev.size() && prev[l2] == '1')) l2--;
        string ps = prev.substr(l2), cs = cur.substr(l2);
        printf("%lld +%lld depth %zu | %s=> %s\n", st, st - prevStep, prev.size() - l, runs_of(ps).c_str(), runs_of(cs).c_str());
        if (++printed >= maxp) return 0;
      }
      prev = cur; prevStep = st;
    }
    int c = tape[p]; T2 t = tm[q][c];
    if (!t.ok) { printf("HALT %lld\n", st); return 0; }
    tape[p] = t.w; p += t.d; q = t.q; if (p > mx) mx = p;
    if (p < 2 || p > SZ - 2) { printf("EDGE\n"); return 0; }
  }
}
// minimal run-spec parser (same syntax as fsnap)
static string parse_tok(const string& t) { size_t bar = t.find('|'); string o = t, z = "1"; bool dot = false;
  if (!t.empty() && t.back() == '.') { o = t.substr(0, t.size() - 1); dot = true; }
  else if (bar != string::npos) { o = t.substr(0, bar); string rest = t.substr(bar + 1); if (rest.empty()) z = "2"; else z = rest.substr(0, rest.size() - 1); }
  string r(atoll(o.c_str()), '1'); if (!dot) r += string(atoll(z.c_str()), '0'); return r; }
static void skipws(const string& s, size_t& i) { while (i < s.size() && s[i] == ' ') ++i; }
static string parse_seq(const string& s, size_t& i) { string out; skipws(s, i);
  while (i < s.size() && s[i] != ')') { string unit;
    if (s[i] == '(') { ++i; unit = parse_seq(s, i); ++i; }
    else { size_t j = i; while (j < s.size() && s[j] != ' ' && s[j] != '^' && s[j] != ')') ++j; unit = parse_tok(s.substr(i, j - i)); i = j; }
    long long k = 1; if (i < s.size() && s[i] == '^') { ++i; size_t j = i; while (j < s.size() && isdigit(s[j])) ++j; k = atoll(s.substr(i, j - i).c_str()); i = j; }
    for (long long c = 0; c < k; c++) out += unit; skipws(s, i); }
  return out; }
static string spec2word(const string& spec) { size_t i = 0; string w = parse_seq(spec, i); while (!w.empty() && w.back() == '0') w.pop_back(); return w; }
