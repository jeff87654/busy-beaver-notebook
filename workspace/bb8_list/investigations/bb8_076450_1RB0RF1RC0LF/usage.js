// Count how often each transition is used in the first N literal steps from the blank tape.
const TM = "1RB0RF_1RC0LF_0RD0RB_1LE1LG_0LA0LC_0LD1RH_1RA1LC_1RF---";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const N = 1 << 24; const tape = new Uint8Array(N); let pos = N >> 1, st = 0;
const cnt = Array.from({ length: 8 }, () => [0, 0]);
const maxSteps = +(process.argv[2] || 1e8);
for (let s = 0; s < maxSteps; s++) {
  const r = tape[pos]; const e = T[st][r]; if (!e) { console.log('HALT'); break; }
  cnt[st][r]++; tape[pos] = e[0]; pos += e[1]; st = e[2];
}
console.log(cnt.map((c, i) => 'ABCDEFGH'[i] + '0:' + c[0] + ' ' + 'ABCDEFGH'[i] + '1:' + c[1]).join('\n'));
