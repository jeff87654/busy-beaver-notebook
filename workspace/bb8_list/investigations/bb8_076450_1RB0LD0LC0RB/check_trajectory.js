// Literal (unaccelerated) run of 1RB0LD_0LC0RB_1RA1LC_0LH1RE_1LF0RF_0RB0LG_0RD0LD_1LE--- from the blank tape.
// At every moment the head is in state E on a blank cell with only blank cells to its left, the tape to
// the right is parsed as P(a1,b1,a2,b2,t) = (10)^a1 11 0^b1 (10)^a2 11 0^b2 (10)^t 11.
// Checks:
//   * step 110 is the first such visit that parses, and it is P(2,1,0,1,0);
//   * every later parsed visit is the image of the previous one under the rule R1/R2/R3 that applies
//     (intermediate visits of the form 0^inf [E0] 1000 ... that do not parse are allowed and counted);
//   * no halt.
// Usage: node check_trajectory.js [maxSteps]
const TM = "1RB0LD_0LC0RB_1RA1LC_0LH1RE_1LF0RF_0RB0LG_0RD0LD_1LE---";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const maxSteps = +(process.argv[2] || 3e7);
const N = 1 << 24;
const tape = new Uint8Array(N);
let pos = N >> 1, q = 0, steps = 0, lo = pos, hi = pos;
const E = 4;
const re = /^((?:10)*)11(0*)((?:10)*)11(0*)((?:10)*)11$/;
function parseP(s) {
  const m = re.exec(s);
  if (!m) return null;
  return [m[1].length / 2, m[2].length, m[3].length / 2, m[4].length, m[5].length / 2];
}
function next(p) {
  const [a1, b1, a2, b2, t] = p;
  if (b1 >= 2) return ['R1', [a1 + 1, b1 - 1, a2, b2, t]];
  if (b1 === 1 && a1 >= 1 && b2 >= 2) return ['R2', [1, 2 * a1, a2 + 1, b2 - 1, t]];
  if (b1 === 1 && a1 >= 1 && b2 === 1) return ['R3', [1, 2, a1 - 1, 2 * a2 + 3, t + 1]];
  return [null, null];
}
let prev = null, first = null, parsed = 0, unparsed = 0, bad = 0;
const counts = { R1: 0, R2: 0, R3: 0 };
const r3log = [];
while (steps < maxSteps) {
  const s = tape[pos];
  const tr = T[q][s];
  if (!tr) { console.log("HALT at step", steps); bad++; break; }
  tape[pos] = tr[0]; pos += tr[1]; q = tr[2]; steps++;
  if (pos < lo) lo = pos; if (pos > hi) hi = pos;
  if (pos <= 0 || pos >= N - 1) { console.log("tape buffer exhausted at step", steps); break; }
  if (q === E && tape[pos] === 0 && pos === lo) {
    // all cells left of pos are blank because pos is the leftmost cell ever visited
    let e = hi; while (e > pos && tape[e] === 0) e--;
    const str = Array.from(tape.subarray(pos + 1, e + 1)).join("");
    const p = parseP(str);
    if (!p) { unparsed++; continue; }
    parsed++;
    if (prev === null) { first = [steps, p]; }
    else {
      const [rule, want] = next(prev);
      if (!rule || want.join() !== p.join()) {
        bad++;
        console.log("MISMATCH at step", steps, "prev", prev, "got", p, "expected", rule, want);
      } else {
        counts[rule]++;
        if (rule === 'R3') r3log.push([steps, p]);
      }
    }
    prev = p;
  }
}
console.log(JSON.stringify({ steps, first, parsed, unparsed_left_E_visits: unparsed, rule_counts: counts, mismatches: bad, last: prev, overflows: r3log }));
