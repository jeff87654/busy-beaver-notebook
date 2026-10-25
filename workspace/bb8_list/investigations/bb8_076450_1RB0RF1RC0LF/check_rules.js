// Exact literal checks (no acceleration) of the rules of
//   1RB0RF_1RC0LF_0RD0RB_1LE1LG_0LA0LC_0LD1RH_1RA1LC_1RF---
// Configurations (tape order, blank elsewhere):
//   Pc(a,n | ctx) = ctx (010)^a 0111 0111 1^n 01010 B>0      (head in state B on the blank right of the word)
//   Qc(a,n | ctx) = ctx (010)^a 0 1^n 01010 B>0
//   Y(M)          = A>0 (01)^M                               (head in state A on the blank left of the word)
// A rule instance passes if the run reaches the predicted configuration (exact tape, state, head cell) with no
// earlier halt, the head never visits a cell of ctx (general rules), and within the step limit.
// usage: node check_rules.js [maxk] [maxa] [nctx]
const TM = process.env.TM || "1RB0RF_1RC0LF_0RD0RB_1LE1LG_0LA0LC_0LD1RH_1RA1LC_1RF---";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const X = '01110111';
const Pw = (a, n) => '010'.repeat(a) + X + '1'.repeat(n) + '01010';
const Qw = (a, n) => '010'.repeat(a) + '0' + '1'.repeat(n) + '01010';
const Yw = M => '01'.repeat(M);
let seed = 12345;
function rnd() { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; }
function randWord(len) { let s = ''; for (let i = 0; i < len; i++) s += rnd() < 0.5 ? '0' : '1'; return '1' + s; }

// run: start = {ctx, word, st, head: 'R' (blank right of word) | 'L' (blank left of word)}
// target = {word (full tape word incl. ctx, from first cell of ctx), st, head:'R'|'L'}; ctx protected if wall
function run(ctx, word, st, head, tgtWord, tgtSt, tgtHead, wall, maxSteps) {
  const full = ctx + word;
  const N = 8 * full.length + 20000;
  const tape = new Uint8Array(N);
  const base = N >> 2;
  for (let i = 0; i < full.length; i++) tape[base + i] = +full[i];
  let pos = head === 'R' ? base + full.length : base - 1;
  const wallPos = base + ctx.length; // cells < wallPos belong to ctx
  let steps = 0;
  const tlen = tgtWord.length;
  // target check: word occupies [base, base+tlen) exactly (ctx is a prefix of tgtWord) and blank elsewhere
  let lo = Math.min(pos, base), hi = Math.max(pos, base + full.length);
  while (steps < maxSteps) {
    const e = T[st][tape[pos]];
    if (!e) return { ok: false, why: 'HALT', steps };
    tape[pos] = e[0]; pos += e[1]; st = e[2]; steps++;
    if (pos < lo) lo = pos; if (pos > hi) hi = pos;
    if (wall && pos < wallPos) return { ok: false, why: 'visited ctx', steps };
    if (pos < 1 || pos > N - 2) return { ok: false, why: 'overflow', steps };
    if (st === tgtSt && ((tgtHead === 'R' && pos >= hi) || (tgtHead === 'L' && pos <= lo))) {
      // position-independent: word must sit right next to the head, blank elsewhere
      const start = tgtHead === 'R' ? pos - tlen : pos + 1;
      if (tape[pos] === 0 && start >= 0) {
        let good = true;
        for (let i = lo; i <= hi && good; i++) {
          const w = (i >= start && i < start + tlen) ? +tgtWord[i - start] : 0;
          if (tape[i] !== w) good = false;
        }
        for (let i = start; i < start + tlen && good; i++) if (tape[i] !== +tgtWord[i - start]) good = false;
        if (good) return { ok: true, steps };
      }
    }
  }
  return { ok: false, why: 'limit', steps };
}

const maxk = +(process.argv[2] || 30), maxa = +(process.argv[3] || 6), nctx = +(process.argv[4] || 3);
const results = {};
function rec(name, ok, info) {
  if (!results[name]) results[name] = { pass: 0, fail: 0, steps: [], firstFail: null };
  const r = results[name];
  if (ok) r.pass++; else { r.fail++; if (!r.firstFail) r.firstFail = info; }
}
const ctxs = [''];
for (let i = 0; i < nctx; i++) ctxs.push(randWord(1 + Math.floor(rnd() * 12)));
// general rules: consumed blocks c, start/target words
const GEN = [
  // name, consumed, start(a,k) -> [word], target(a,k) -> [word], n-form
  ['P0r: Pc(a+3,3k+3) -> Pc(a,6k+28)', (a, k) => Pw(a + 3, 3 * k + 3), (a, k) => Pw(a, 6 * k + 28)],
  ['P1r: Pc(a+5,3k+4) -> Pc(a,6k+47)', (a, k) => Pw(a + 5, 3 * k + 4), (a, k) => Pw(a, 6 * k + 47)],
  ['P2r: Pc(a,3k+2) -> Qc(a,6k+16)', (a, k) => Pw(a, 3 * k + 2), (a, k) => Qw(a, 6 * k + 16)],
  ['Q0r: Qc(a+5,3k+3) -> Pc(a,6k+33)', (a, k) => Qw(a + 5, 3 * k + 3), (a, k) => Pw(a, 6 * k + 33)],
  ['Q1r: Qc(a+6,3k+4) -> Pc(a,6k+43)', (a, k) => Qw(a + 6, 3 * k + 4), (a, k) => Pw(a, 6 * k + 43)],
  ['Q2r: Qc(a+3,3k+2) -> Pc(a,6k+8)', (a, k) => Qw(a + 3, 3 * k + 2), (a, k) => Pw(a, 6 * k + 8)],
];
const stepsOut = {};
for (const [name, sw, tw] of GEN) {
  for (const ctx of ctxs) for (let a = 0; a <= maxa; a++) for (let k = 0; k <= maxk; k++) {
    const r = run(ctx, sw(a, k), 1, 'R', ctx + tw(a, k), 1, 'R', true, 1e8);
    rec(name, r.ok, { ctx, a, k, r });
    if (r.ok) { (stepsOut[name] = stepsOut[name] || {})[`${a},${k}`] = r.steps; }
  }
}
// end rules (fixed prefix, blank beyond)
const ENDS = [
  ['E_P0_p2: 11 Pc(0,3k+4) -> Y(3k+19)', k => ['11' + Pw(0, 3 * k + 4), 1, 'R', Yw(3 * k + 19), 0, 'L']],
  ['E_Q0_p1: 1 Qc(0,3k+4) -> Y(3k+9)', k => ['1' + Qw(0, 3 * k + 4), 1, 'R', Yw(3 * k + 9), 0, 'L']],
  ['E_Q1_p1: 1 Qc(1,3k+4) -> Y(3k+16)', k => ['1' + Qw(1, 3 * k + 4), 1, 'R', Yw(3 * k + 16), 0, 'L']],
  ['E_Q5_p2: 11 Qc(5,3k+4) -> 1 Pc(1,6k+41)', k => ['11' + Qw(5, 3 * k + 4), 1, 'R', '1' + Pw(1, 6 * k + 41), 1, 'R']],
  ['Y0: Y(3k+6) -> 11 Qc(2k+4,3)', k => [Yw(3 * k + 6), 0, 'L', '11' + Qw(2 * k + 4, 3), 1, 'R']],
  ['Y1: Y(3k+7) -> 1 Qc(2k+5,3)', k => [Yw(3 * k + 7), 0, 'L', '1' + Qw(2 * k + 5, 3), 1, 'R']],
];
for (const [name, f] of ENDS) {
  for (let k = 0; k <= 3 * maxk; k++) {
    const [w, st, hd, tw, tst, thd] = f(k);
    const r = run('', w, st, hd, tw, tst, thd, false, 1e8);
    rec(name, r.ok, { k, r });
    if (r.ok) { (stepsOut[name] = stepsOut[name] || {})[`${k}`] = r.steps; }
  }
}
for (const [k, v] of Object.entries(results)) console.log(`${k}: ${v.pass} pass, ${v.fail} fail` + (v.firstFail ? ' first fail ' + JSON.stringify(v.firstFail) : ''));
require('fs').writeFileSync('check_rules_steps.json', JSON.stringify(stepsOut));
