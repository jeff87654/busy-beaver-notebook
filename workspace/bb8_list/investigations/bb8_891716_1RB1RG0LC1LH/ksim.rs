// Fast literal simulator for 1RB1RG_0LC1LH_1LD1RC_---0LE_0RF0LA_0RA1LH_1RA0RC_1RA1LF
// usage: ksim run N [maxprint]            from the blank tape, print every K event (head in C right of a K word)
//        ksim step CAP < lines            each line: "d1,d2,..|a|b" (or "|a|b" for empty list): print the next K event / HALT
use std::io::{self, BufRead};

const T: [[(u8, i8, u8); 2]; 8] = [
    [(1, 1, 1), (1, 1, 6)],       // A: 1RB 1RG
    [(0, -1, 2), (1, -1, 7)],     // B: 0LC 1LH
    [(1, -1, 3), (1, 1, 2)],      // C: 1LD 1RC
    [(9, 0, 0), (0, -1, 4)],      // D: --- 0LE   (9 = undefined)
    [(0, 1, 5), (0, -1, 0)],      // E: 0RF 0LA
    [(0, 1, 0), (1, -1, 7)],      // F: 0RA 1LH
    [(1, 1, 0), (0, 1, 2)],       // G: 1RA 0RC
    [(1, 1, 0), (1, -1, 5)],      // H: 1RA 1LF
];

struct Sim { tape: Vec<u8>, pos: usize, st: u8, steps: u64, hi: usize, lo: usize }

impl Sim {
    fn new(size: usize) -> Sim { Sim { tape: vec![0; size], pos: size / 2, st: 0, steps: 0, hi: 0, lo: usize::MAX } }
    fn grow(&mut self) {
        let n = self.tape.len();
        let mut t = vec![0u8; n];
        t.extend_from_slice(&self.tape);
        t.extend(vec![0u8; n]);
        self.tape = t; self.pos += n; if self.hi > 0 { self.hi += n; } if self.lo != usize::MAX { self.lo += n; }
    }
    // returns Some(false) on halt, Some(true) when K event, None if cap reached
    fn run_until_event(&mut self, cap: u64, first_ok: bool) -> Option<(bool, Option<Vec<u32>>)> {
        let mut first = first_ok;
        loop {
            if self.steps >= cap { return None; }
            if self.pos < 4 || self.pos + 4 >= self.tape.len() { self.grow(); }
            let s = self.tape[self.pos];
            if self.st == 2 && s == 0 && !first {
                // locate rightmost 1
                while self.hi > 0 && self.tape[self.hi] == 0 { self.hi -= 1; }
                if self.pos == self.hi + 1 {
                    if let Some(xs) = self.parse() { return Some((true, Some(xs))); }
                }
            }
            first = false;
            let e = T[self.st as usize][s as usize];
            if e.0 == 9 { return Some((false, None)); }
            self.tape[self.pos] = e.0;
            if e.0 == 1 { if self.pos > self.hi { self.hi = self.pos; } if self.pos < self.lo { self.lo = self.pos; } }
            self.pos = (self.pos as i64 + e.1 as i64) as usize;
            self.st = e.2;
            self.steps += 1;
        }
    }
    fn parse(&mut self) -> Option<Vec<u32>> {
        while self.lo < self.pos && self.tape[self.lo] == 0 { self.lo += 1; }
        let w = &self.tape[self.lo..self.pos];
        if w.is_empty() || w[0] != 1 { return None; }
        let n = w.len();
        let mut i = if n % 2 == 1 { 1 } else { 0 }; let mut xs = vec![];
        while i < n {
            let mut c = 0u32;
            while i + 1 < n && w[i] == 1 && w[i + 1] == 0 { c += 1; i += 2; }
            if i + 1 < n && w[i] == 1 && w[i + 1] == 1 { xs.push(c); i += 2; } else { return None; }
        }
        if xs.len() >= 2 { xs.push(if n % 2 == 1 { 1000000 } else { 2000000 }); Some(xs) } else { None }
    }
}

fn fmt(xs0: &[u32]) -> String {
    let tag = xs0[xs0.len() - 1];
    let xs = &xs0[..xs0.len() - 1];
    let m = xs.len();
    let ds: Vec<String> = xs[..m - 2].iter().map(|x| x.to_string()).collect();
    format!("K{}({}; {}; {})", if tag == 1000000 { "o" } else { "e" }, ds.join(","), xs[m - 2], xs[m - 1])
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args[1] == "run" {
        let n: u64 = args[2].parse().unwrap();
        let maxp: usize = if args.len() > 3 { args[3].parse().unwrap() } else { 100 };
        let mut s = Sim::new(1 << 16);
        let mut cnt = 0usize;
        loop {
            match s.run_until_event(n, false) {
                None => { println!("N steps={} events={}", s.steps, cnt); break; }
                Some((false, _)) => { println!("HALT steps={} events={}", s.steps, cnt); break; }
                Some((true, Some(xs))) => {
                    cnt += 1;
                    if cnt <= maxp { println!("{} {}", s.steps, fmt(&xs)); }
                    // all-zero list report
                    let m = xs.len() - 1;
                    if xs[..m - 1].iter().all(|&x| x == 0) && xs[m-2]==0 { println!("   ZERO n={} b={} at {}", m - 2, xs[m - 1], s.steps); }
                    // step past the event cell
                    let e = T[s.st as usize][0];
                    s.tape[s.pos] = e.0; if e.0 == 1 && s.pos > s.hi { s.hi = s.pos; }
                    s.pos = (s.pos as i64 + e.1 as i64) as usize; s.st = e.2; s.steps += 1;
                }
                _ => unreachable!(),
            }
        }
    } else {
        let cap: u64 = args[2].parse().unwrap();
        for line in io::stdin().lock().lines() {
            let line = line.unwrap();
            let lt = line.trim();
            let (odd, lt) = if lt.starts_with("e:") { (false, &lt[2..]) } else if lt.starts_with("o:") { (true, &lt[2..]) } else { (true, lt) };
            let parts: Vec<&str> = lt.split('|').collect();
            let mut xs: Vec<u32> = if parts[0].is_empty() { vec![] } else { parts[0].split(',').map(|x| x.parse().unwrap()).collect() };
            xs.push(parts[1].parse().unwrap()); xs.push(parts[2].parse().unwrap());
            let mut s = Sim::new(1 << 12);
            // build word
            let mut w: Vec<u8> = if odd { vec![1] } else { vec![] };
            for &x in &xs { for _ in 0..x { w.push(1); w.push(0); } w.push(1); w.push(1); }
            while s.tape.len() < 2 * (w.len() + 100) { s.grow(); }
            let base = 10; s.pos = base + w.len(); // head right of word
            for (i, &c) in w.iter().enumerate() { s.tape[base + i] = c; }
            s.hi = base + w.len() - 1; s.lo = base; s.st = 2;
            match s.run_until_event(cap, true) {
                None => println!("{} => T after {} steps", line.trim(), s.steps),
                Some((false, _)) => println!("{} => HALT after {} steps", line.trim(), s.steps),
                Some((true, Some(r))) => println!("{} => {} after {} steps", line.trim(), fmt(&r), s.steps),
                _ => unreachable!(),
            }
        }
    }
}
