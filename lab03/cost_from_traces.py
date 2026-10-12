"""Cost of one eval run, read from the stand's traces (llm.call spans).

Run it right after a run, with the number of cases that run executed:

    python3 cost_from_traces.py 29

It takes the last N traces from the stand (GET /api/_test/traces?limit=N),
counts the llm.call spans and sums their input and output tokens.
Prices: app/agent/pricing.py of the stand (USD per 1M tokens).
"""
import json
import sys
import urllib.request

BASE = "http://localhost:8000"
# copied from paypilot-stand/app/agent/pricing.py (PRICES_CHECKED_ON 2026-10-08)
PRICES = {"claude-haiku-4-5": (1.0, 5.0), "claude-haiku-5-5": (0.10, 0.50)}
LONG_TIER = {"claude-haiku-5-5": (100_000, 0.50, 2.50)}  # input tokens per call, in, out


def spans(node):
    yield node
    for child in node.get("children", []):
        yield from spans(child)


def price(model, tok_in, tok_out):
    key = (model or "").strip().lower().rsplit("/", 1)[-1].replace(".", "-")
    if key not in PRICES:
        return None
    p_in, p_out = PRICES[key]
    tier = LONG_TIER.get(key)
    if tier and tok_in > tier[0]:
        p_in, p_out = tier[1], tier[2]
    return (tok_in * p_in + tok_out * p_out) / 1_000_000


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 29
    with urllib.request.urlopen(f"{BASE}/api/_test/traces?limit={n}", timeout=30) as r:
        traces = json.load(r)["traces"]
    calls = tok_in = tok_out = 0
    cost = 0.0
    unpriced = 0
    models, profiles, prompts = set(), set(), set()
    for t in traces:
        a = t.get("attributes", {})
        profiles.add(a.get("run.profile"))
        prompts.add(a.get("prompt.version"))
        for s in spans(t):
            if s.get("name") != "llm.call":
                continue
            at = s.get("attributes", {})
            i = at.get("gen_ai.usage.input_tokens", 0)
            o = at.get("gen_ai.usage.output_tokens", 0)
            m = at.get("gen_ai.request.model")
            calls += 1
            tok_in += i
            tok_out += o
            models.add(m)
            c = price(m, i, o)
            if c is None:
                unpriced += 1
            else:
                cost += c
    print(f"traces read:       {len(traces)}")
    print(f"profiles:          {sorted(map(str, profiles))}")
    print(f"prompt versions:   {sorted(map(str, prompts))}")
    print(f"models:            {sorted(map(str, models))}")
    print(f"llm.call spans:    {calls}")
    print(f"input tokens:      {tok_in}")
    print(f"output tokens:     {tok_out}")
    print(f"cost (USD):        {cost:.4f}" + (f"   ({unpriced} calls without a price)" if unpriced else ""))


if __name__ == "__main__":
    main()
