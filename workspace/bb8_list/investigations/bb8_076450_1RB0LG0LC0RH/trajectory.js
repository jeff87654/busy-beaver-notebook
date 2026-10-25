// Exact literal simulation with family parsing.
// Usage: node trajectory.js blank MAXSTEPS        -> blank-tape run, check every consecutive family config
//        node trajectory.js ymap N1 N2 MAXSTEPS    -> for n in [N1,N2]: from Y(n) run to next Y config / halt, compare f(n)
// Families (head in A on the blank cell left of the word, blank elsewhere):
//   X(a,b,c) = A> 0 1^a 0 1^b 0 1 (011)^c ;  Y(n) = A> 0 1^n
const TM = "1RB0LG_0LC0RH_---1LD_0RD1LE_1RF0LC_1RG1LG_1LA1LF_1RA1RH";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const tr = []; for (let q = 0; q < 8; q++) for (let s = 0; s < 2; s++) tr.push(T[q][s]);

function parse(tape, p, hi) {
  // word = tape[p+1 .. last one]; returns ['X',a,b,c] | ['Y',n] | null
  let last = hi; while (last > p && tape[last] === 0) last--;
  let i = p + 1; const runs = []; // alternate: ones-run lengths and zero-run lengths
  while (i <= last) { const v = tape[i]; let j = i; while (j <= last && tape[j] === v) j++; runs.push([v, j - i]); i = j; }
  if (runs.length === 0) return ['Y', 0];
  if (runs[0][0] !== 1) return null;
  if (runs.length === 1) return ['Y', runs[0][1]];
  const a = runs[0][1];
  // after a: 0 1^b 0 1 (0 11)^c
  let k = 1; let b;
  if (runs[k][1] === 1) { if (k + 1 >= runs.length) return null; b = runs[k + 1][1]; k += 2; if (k >= runs.length || runs[k][1] !== 1) return null; k++; }
  else if (runs[k][1] === 2) { b = 0; k++; }
  else return null;
  if (k >= runs.length || runs[k][1] !== 1) return null; k++;   // the lone 1
  let c = 0;
  while (k < runs.length) { if (runs[k][1] !== 1 || k + 1 >= runs.length || runs[k + 1][1] !== 2) return null; c++; k += 2; }
  return ['X', a, b, c];
}
function pred(f) {
  if (f[0] === 'X') { const [, a, b, c] = f; if (b > 0) return ['X', a + 4, b - 1, c]; if (c > 0) return ['X', 1, a + 4, c - 1]; return ['Y', a + 8]; }
  const n = f[1], k = Math.floor(n / 3), r = n % 3;
  if (n === 0) return ['Y', 4];
  if (r === 2) return ['HALT'];
  if (r === 0) return ['X', 1, 5, k - 1];
  if (k === 0) return ['Y', 5]; if (k === 1) return ['Y', 13]; if (k === 2) return ['HALT'];
  return ['X', 17, 3, k - 3];
}
function fY(n) { // exact Y-map for small n (BigInt); Y(0) is the blank tape
  if (n === 0) return 4n;
  const k = BigInt(Math.floor(n / 3)), r = n % 3;
  if (r === 2) return 'HALT';
  if (r === 0) return ((20n * 4n ** k + 7n) / 3n);
  if (k === 0n) return 5n; if (k === 1n) return 13n; if (k === 2n) return 'HALT';
  return ((104n * 4n ** (k - 3n) + 7n) / 3n);
}
function run(word, maxSteps, onFamily) {
  let N = 1 << 20; while (N < 4 * word.length + 1000) N <<= 1;
  let tape = new Uint8Array(N); let off = N >> 1;
  for (let i = 0; i < word.length; i++) tape[off + i] = word.charCodeAt(i) - 48;
  let pos = off - 1, st = 0, steps = 0, lo = pos, hi = off + word.length;
  let first = word.indexOf('1') >= 0 ? off + word.indexOf('1') : Infinity;
  while (steps < maxSteps) {
    const s = tape[pos]; const e = tr[2 * st + s];
    if (!e) return { status: 'halt', steps, state: st, sym: s, tape, pos, lo, hi };
    tape[pos] = e[0];
    if (e[0] === 1 && pos < first) first = pos;
    else if (e[0] === 0 && pos === first) { let j = pos + 1; while (j <= hi && tape[j] === 0) j++; first = j <= hi ? j : Infinity; }
    pos += e[1]; st = e[2]; steps++;
    if (pos < lo) lo = pos; if (pos > hi) hi = pos;
    if (pos <= 2 || pos >= N - 3) {  // grow
      const nt = new Uint8Array(2 * N); nt.set(tape, N >> 1); tape = nt; const d = N >> 1; pos += d; lo += d; hi += d; off += d; if (first !== Infinity) first += d; N *= 2;
    }
    if (st === 0 && tape[pos] === 0 && pos < first) {
      const f = parse(tape, pos, hi);
      if (f && onFamily(f, steps) === 'stop') return { status: 'family', steps, fam: f };
    }
  }
  return { status: 'limit', steps };
}
const key = f => JSON.stringify(f);
const mode = process.argv[2];
if (mode === 'blank') {
  const maxSteps = +process.argv[3];
  let prev = ['Y', 0], nfam = 0, bad = 0; const log = [];
  const r = run('', maxSteps, (f, steps) => {
    nfam++;
    const p = pred(prev);
    if (key(p) !== key(f)) { bad++; console.log('MISMATCH at step', steps, 'prev', key(prev), 'pred', key(p), 'got', key(f)); }
    if (f[0] === 'Y' || (f[0] === 'X' && f[2] === 0) || nfam <= 3) log.push(steps + ' ' + key(f));
    prev = f;
  });
  console.log(log.join('\n'));
  console.log('last family config:', key(prev), '; status', r.status, 'steps', r.steps, '; family configs', nfam, 'mismatches', bad);
} else if (mode === 'ymap') {
  const n1 = +process.argv[3], n2 = +process.argv[4], maxSteps = +process.argv[5];
  let bad = 0;
  for (let n = n1; n <= n2; n++) {
    const want = fY(n);
    const r = run('1'.repeat(n), maxSteps, (f) => f[0] === 'Y' ? 'stop' : null);
    let got;
    if (r.status === 'halt') got = 'HALT'; else if (r.status === 'family') got = BigInt(r.fam[1]); else got = 'LIMIT';
    const ok = (got === want) || (typeof got === 'bigint' && got === want);
    if (!ok) bad++;
    let extra = '';
    if (r.status === 'halt') { let ones = 0; for (let i = r.lo; i <= r.hi; i++) ones += r.tape[i]; extra = ' halt in state ' + 'ABCDEFGH'[r.state] + r.sym + ', ones ' + ones; }
    console.log('Y(' + n + ') -> ' + got + ' (predicted ' + want + ') steps ' + r.steps + extra + (ok ? '' : '  MISMATCH'));
  }
  console.log('mismatches', bad);
}
