"""Token usage and API-price-equivalent cost of subagent transcripts.

  python token_cost.py <agent.jsonl> [...]

For each transcript it reports:
- final context: the size of the last request plus its output. This matches the harness's "subagent_tokens" figure.
- the sum over unique API calls of fresh input, cache writes, cache reads and output.
- the cost in dollars at list prices (per MTok, input / output):
  - Sonnet 5.5: $2 / $10; Opus 5.5: $4 / $20.
  - Cache writes cost 2x input (1-hour TTL); cache reads cost 0.1x input.
The first 200 characters of the prompt identify the run.
"""
import json
import sys

PRICE = {'claude-sonnet-5-5': (2.0, 10.0), 'claude-opus-5-5': (4.0, 20.0), 'claude-sonnet-5': (2.0, 10.0)}


def cost(path):
    seen, tot, last, model, prompt = set(), dict.fromkeys(('in', 'cw', 'cr', 'out'), 0), None, None, None
    for line in open(path, encoding='utf-8'):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        m = r.get('message') or {}
        if prompt is None and m.get('role') == 'user':
            c = m.get('content')
            prompt = c if isinstance(c, str) else ' '.join(x.get('text', '') for x in c if isinstance(x, dict))
        u = m.get('usage')
        if not u or m.get('id') in seen:
            continue
        seen.add(m.get('id'))
        model = m.get('model', model)
        last = u
        tot['in'] += u.get('input_tokens', 0)
        tot['cw'] += u.get('cache_creation_input_tokens', 0)
        tot['cr'] += u.get('cache_read_input_tokens', 0)
        tot['out'] += u.get('output_tokens', 0)
    pin, pout = PRICE.get(model, (0, 0))
    usd = (tot['in'] * pin + tot['cw'] * 2 * pin + tot['cr'] * 0.1 * pin + tot['out'] * pout) / 1e6
    final = sum(last.get(k, 0) for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens',
                                          'output_tokens')) if last else 0
    return dict(model=model, calls=len(seen), final_ctx=final, usd=round(usd, 2), **tot,
                prompt=(prompt or '')[:200].replace('\n', ' '))


if __name__ == '__main__':
    for p in sys.argv[1:]:
        d = cost(p)
        print(f"{p.split('/')[-1].split(chr(92))[-1]}\n  {d['model']} calls={d['calls']} final_ctx={d['final_ctx']:,} "
              f"in={d['in']:,} cache_write={d['cw']:,} cache_read={d['cr']:,} out={d['out']:,} -> ${d['usd']}\n"
              f"  prompt: {d['prompt']}")
