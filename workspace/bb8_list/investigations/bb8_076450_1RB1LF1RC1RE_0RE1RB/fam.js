// Literal simulation; report left-edge configs in state F on blank cell left of word, parse 1^n 0 1^m
const TM = process.env.TM || "1RB1LF_1RC1RE_1RD0LG_0RE1RB_1LA0LC_0RG1LA_---0LH_0LC1LC";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const Nn = 1 << 25; const tape = new Uint8Array(Nn);
let pos = Nn >> 1, st = 0, first1 = Nn, last1 = -1;
const maxSteps = +(process.argv[2] || 1e7);
const wantState = +(process.env.ST || 5);
function parse() {
  let i = first1;
  while (i <= last1 && tape[i] === 1) i++;
  const L = i - first1;
  if (i > last1) return [L, 0, ''];
  for (let k = i + 1; k <= last1; k++) if (tape[k] !== 1) return [L, -1, rle()];
  return [L, last1 - i, ''];
}
function rle() { let out = []; let i = first1; while (i <= last1) { let j = i; while (j <= last1 && tape[j] === tape[i]) j++; out.push(tape[i] + '^' + (j - i)); i = j; if (out.length > 30) { out.push('...'); break; } } return out.join(' '); }
let s;
for (s = 1; s <= maxSteps; s++) {
  const r = tape[pos]; const e = T[st][r];
  if (!e) { console.log('HALT at step', s - 1, 'state', String.fromCharCode(65 + st), 'pos-first1', pos - first1, rle()); break; }
  tape[pos] = e[0];
  if (e[0] === 1) { if (pos < first1) first1 = pos; if (pos > last1) last1 = pos; }
  else if (pos === first1) { while (first1 <= last1 && tape[first1] === 0) first1++; }
  else if (pos === last1) { while (last1 >= first1 && tape[last1] === 0) last1--; }
  pos += e[1]; st = e[2];
  if (pos <= 0 || pos >= Nn - 1) { console.log('tape overflow'); break; }
  if (st === wantState && pos === first1 - 1) {
    const [n, m, x] = parse();
    if (m >= 0) { if (process.env.ALL || n % 6 === 4) console.log(`step ${s}: n=${n} (n%6=${n%6}, j=${(n-4)/6}) m=${m}`); }
    else if (process.env.ALL) console.log(`step ${s}: other ${x}`);
  }
}
console.log('ran', s - 1, 'steps');
