# hello-world example

Smallest runnable TDD-Loop example. Demonstrates the flow with the `null`
environment (no runtime harness — Tester verifies via code reading and
minimal Python execution through the shell tool).

## Run

From the Paper root:

```bash
python -m tdd_loop.run examples/hello_world/feature_list.json \
    --project-dir examples/hello_world \
    --spec examples/hello_world/SPEC.md \
    --model sonnet \
    --max-iter 10
```

Expected final state: both features `passed`, `src/greeter.py` created
under `examples/hello_world/`.

## Inspect results

```bash
cat examples/hello_world/.tdd_loop_temp/report.md
cat examples/hello_world/.tdd_loop_temp/sessions_log.jsonl | jq .
```

## Git init (required — the framework reads `git diff`)

If `examples/hello_world/` isn't its own git repo yet:

```bash
cd examples/hello_world
git init && git add -A && git commit -m "baseline"
```
