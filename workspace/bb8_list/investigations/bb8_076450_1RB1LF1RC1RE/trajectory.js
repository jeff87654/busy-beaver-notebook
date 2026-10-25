// Literal simulation from the blank tape (no acceleration) of
//   1RB1LF_1RC1RE_1RD0LG_0RE1LD_1LA0LC_0RG1LA_---0LH_1RA1LC
// Reports every configuration  W(j,m) = 0^inf A>0 1^(6j+5) 0 1^m 0^inf  and checks that each one is the
// predicted successor of the previous one, reached after exactly the predicted number of steps:
//   W(j,m+1) -> W(2j+2,m)   in (24j+67) + (2j+2)(24j+65) steps
//   W(j,0)   -> W(0,6j+7)   in 24j+76 steps
// Usage: node trajectory.js maxSteps [printEvery]
const TM = process.env.TM || "1RB1LF_1RC1RE_1RD0LG_0RE1LD_1LA0LC_0RG1LA_---0LH_1RA1LC";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const Nn = 1 << 24; const tape = new Uint8Array(Nn);
let pos = Nn >> 1, st = 0, first1 = Nn, last1 = -1;
const maxSteps = +(process.argv[2] || 1e7);
const printEvery = +(process.argv[3] || 1);
function succ(f) {
  const [j, m] = f;
  if (m >= 1) return [[2 * j + 2, m - 1], (24 * j + 67) + (2 * j + 2) * (24 * j + 65)];
  return [[0, 6 * j + 7], 24 * j + 76];
}
function parseW() { // returns [j,m] if tape[first1..last1] = 1^(6j+5) 0 1^m, else null
  let i = first1;
  while (i <= last1 && tape[i] === 1) i++;
  const L = i - first1;
  if (L % 6 !== 5) return null;
  if (i > last1) return [(L - 5) / 6, 0];
  // tape[i] === 0 here; the rest must be all ones
  for (let k = i + 1; k <= last1; k++) if (tape[k] !== 1) return null;
  return [(L - 5) / 6, last1 - i];
}
let prev = null, prevStep = 0, found = 0, bad = 0, s = 0;
for (s = 1; s <= maxSteps; s++) {
  const r = tape[pos]; const e = T[st][r];
  if (!e) { console.log('HALT at step', s - 1, 'state', String.fromCharCode(65 + st)); bad++; break; }
  tape[pos] = e[0];
  if (e[0] === 1) { if (pos < first1) first1 = pos; if (pos > last1) last1 = pos; }
  else if (pos === first1) { while (first1 <= last1 && tape[first1] === 0) first1++; }
  else if (pos === last1) { while (last1 >= first1 && tape[last1] === 0) last1--; }
  pos += e[1]; st = e[2];
  if (pos <= 0 || pos >= Nn - 1) { console.log('tape overflow'); break; }
  if (st === 0 && pos === first1 - 1) {
    const f = parseW();
    if (!f) continue;
    let tag = '';
    if (prev) {
      const [p, ds] = succ(prev);
      if (p[0] !== f[0] || p[1] !== f[1] || s - prevStep !== ds) { tag = ' MISMATCH predicted W(' + p + ') after ' + ds; bad++; }
    }
    found++;
    if (tag || found <= 12 || found % printEvery === 0 || f[1] === 0) console.log(`step ${s}: W(${f[0]},${f[1]})${tag}`);
    prev = f; prevStep = s;
  }
}
console.log(`ran ${s - 1} steps; last: W(${prev}) at step ${prevStep}; found ${found} W-configurations, ${bad} mismatches`);
