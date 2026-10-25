// Literal simulation from the blank tape (no acceleration) of
//   1RB0LC_0RC0RF_0RD0RH_1LE---_0LF1LG_1RD1LA_1RC1LA_0LF0LA
// At every right-edge configuration (state D on a blank cell, blank to the right, two blank cells behind it)
// the word W left of the head is parsed; W = 1 (10)^a 1^(6i+3) (blank to the left) is the family
// configuration Dc(a, i).  Predicted successors (Coq lemmas Dstep, Dtop = T1;R1^(3i+5);T2 with T2 = R2;R0o):
//   Dc(a+1, i) -> Dc(a, 3i+2)          Dc(0, i) -> Dc(9i+17, 0)   (then Dc(9i+16, 2) by the first rule)
// Each family configuration must be the predicted successor of the previous one.
// Usage: node trajectory.js maxSteps
const TM = "1RB0LC_0RC0RF_0RD0RH_1LE---_0LF1LG_1RD1LA_1RC1LA_0LF0LA";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const N = 1 << 25; const tape = new Uint8Array(N);
let pos = N >> 1, st = 0, lo = pos, hi = pos;
const maxSteps = +(process.argv[2] || 1e8);
function parse() {
  let f = lo; while (f < pos && tape[f] === 0) f++;
  if (f >= pos - 2 || tape[f] !== 1) return null;
  let j = f + 1, a = 0;
  while (j + 1 < pos - 2 && tape[j] === 1 && tape[j + 1] === 0) { a++; j += 2; }
  let c = 0; while (j < pos - 2 && tape[j] === 1) { c++; j++; }
  if (j !== pos - 2 || c % 6 !== 3) return null;
  return [a, (c - 3) / 6];
}
function succ(f) { const [a, i] = f; return a === 0 ? [9 * i + 17, 0] : [a - 1, 3 * i + 2]; }
let prev = null, found = 0, bad = 0, s, events = 0;
for (s = 1; s <= maxSteps; s++) {
  const r = tape[pos]; const e = T[st][r];
  if (!e) { console.log('HALT at step', s - 1); bad++; break; }
  tape[pos] = e[0]; pos += e[1]; st = e[2];
  if (pos < lo) lo = pos;
  if (pos >= hi) {
    hi = pos;
    if (st === 3 && tape[pos - 1] === 0 && tape[pos - 2] === 0) {
      events++;
      const f = parse();
      if (f) {
        found++;
        let ok = '';
        if (prev) { const p = succ(prev); ok = (p.join() === f.join()) ? 'ok' : ('MISMATCH expected ' + p.join()); if (ok !== 'ok') bad++; }
        console.log('step', s, 'Dc(' + f.join(',') + ')', ok);
        prev = f;
      }
    }
  }
  if (pos < 8 || pos > N - 8) { console.log('tape overflow at step', s); break; }
}
console.log('done', s - 1, 'steps;', events, 'right-edge events;', found, 'family configurations,', bad, 'mismatches; tape span', hi - lo + 1);
