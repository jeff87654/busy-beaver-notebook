// Literal run from the blank tape (no acceleration).  Every canonical configuration
//   p P(a,n) = 0^inf p (010)^a 0111 0111 1^n 01010 B>0 0^inf      (p = 1 or 11)
//   p Q(a,n) = 0^inf p (010)^a 0 1^n 01010 B>0 0^inf
//   Y(M)     = 0^inf A>0 (01)^M 0^inf
// is checked to be the predicted successor (rule table of the report) of the previous one, reached after
// exactly the predicted number of steps.  usage: node trajectory.js maxSteps
const TM = "1RB0RF_1RC0LF_0RD0RB_1LE1LG_0LA0LC_0LD1RH_1RA1LC_1RF---";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const sq = k => 9 * k * k;
// successor: returns [config, steps] or null (no rule)
function succ(c) {
  const [kind, p, a, n] = c;
  if (kind === 'Y') {
    const M = a;
    if (M >= 6 && M % 3 === 0) { const k = (M - 6) / 3; return [['Q', '11', 2 * k + 4, 3], 56 * k + 202]; }
    if (M >= 7 && M % 3 === 1) { const k = (M - 7) / 3; return [['Q', '1', 2 * k + 5, 3], 56 * k + 222]; }
    return null;
  }
  const r = n % 3;
  if (kind === 'P') {
    if (r === 0 && n >= 3 && a >= 3) { const k = (n - 3) / 3; return [['P', p, a - 3, 6 * k + 28], sq(k) + 196 * k + 748]; }
    if (r === 1 && n >= 4 && a >= 5) { const k = (n - 4) / 3; return [['P', p, a - 5, 6 * k + 47], sq(k) + 268 * k + 1644]; }
    if (r === 2) { const k = (n - 2) / 3; return [['Q', p, a, 6 * k + 16], sq(k) + 142 * k + 315]; }
    if (r === 1 && n >= 4 && a === 0 && p === '11') { const k = (n - 4) / 3; return [['Y', '', 3 * k + 19, 0], sq(k) + 124 * k + 411]; }
    return null;
  }
  if (r === 0 && n >= 3 && a >= 5) { const k = (n - 3) / 3; return [['P', p, a - 5, 6 * k + 33], sq(k) + 232 * k + 1074]; }
  if (r === 1 && n >= 4 && a >= 6) { const k = (n - 4) / 3; return [['P', p, a - 6, 6 * k + 43], sq(k) + 268 * k + 1504]; }
  if (r === 2 && a >= 3) { const k = (n - 2) / 3; return [['P', p, a - 3, 6 * k + 8], sq(k) + 124 * k + 194]; }
  if (r === 1 && n >= 4 && p === '1' && a === 0) { const k = (n - 4) / 3; return [['Y', '', 3 * k + 9, 0], sq(k) + 52 * k + 67]; }
  if (r === 1 && n >= 4 && p === '1' && a === 1) { const k = (n - 4) / 3; return [['Y', '', 3 * k + 16, 0], sq(k) + 124 * k + 363]; }
  if (r === 1 && n >= 4 && p === '11' && a === 5) { const k = (n - 4) / 3; return [['P', '1', 1, 6 * k + 41], sq(k) + 268 * k + 1576]; }
  return null;
}
const N = 1 << 26; const tape = new Uint8Array(N);
let pos = N >> 1, st = 0, lo = pos, hi = pos;
const maxSteps = +(process.argv[2] || 1e8);
const R = /^(1|11)((?:010)*)(01110111|0)(1+)01010$/;
function str(a, b) { let s = ''; for (let i = a; i < b; i++) s += tape[i] ? '1' : '0'; return s; }
let prev = null, prevStep = 0, found = 0, bad = 0, s;
function report(c, step) {
  let tag = '';
  if (prev) {
    const nx = succ(prev);
    if (!nx) tag = ' (no rule for previous)';
    else if (JSON.stringify(nx[0]) !== JSON.stringify(c) || nx[1] !== step - prevStep) { tag = ' MISMATCH predicted ' + JSON.stringify(nx[0]) + ' after ' + nx[1]; bad++; }
  }
  found++;
  console.log(`step ${step}: ${c[0] === 'Y' ? 'Y(' + c[2] + ')' : c[1] + ' ' + c[0] + '(' + c[2] + ',' + c[3] + ')'}${tag}`);
  prev = c; prevStep = step;
}
for (s = 1; s <= maxSteps; s++) {
  const e = T[st][tape[pos]];
  if (!e) { console.log('HALT at step', s - 1); bad++; break; }
  tape[pos] = e[0]; pos += e[1]; st = e[2];
  if (pos < lo) {
    lo = pos;
  }
  if (st === 0 && pos === lo && tape[pos] === 0) {
    let j = hi; while (j > pos && tape[j] === 0) j--;
    if ((j - pos) % 2 === 0 && j > pos) { const w = str(pos + 1, j + 1); if (/^(01)+$/.test(w)) report(['Y', '', w.length / 2, 0], s); }
  }
  if (pos > hi) {
    hi = pos;
    if (st === 1) {
      let i = lo; while (tape[i] === 0) i++;
      const m = R.exec(str(i, pos));
      if (m) report([m[3] === '0' ? 'Q' : 'P', m[1], m[2].length / 3, m[4].length], s);
    }
  }
  if (pos < 2 || pos > N - 3) { console.log('tape overflow'); break; }
}
console.log(`ran ${s - 1} steps; ${found} configurations, ${bad} mismatches`);
