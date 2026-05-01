# Environments

An Environment is a pluggable adapter that gives the Tester agent runtime
probes. It lets the same orchestrator core drive very different verification
modalities without changing the loop logic.

## Interface

Subclass `tdd_loop.environment.Environment` and override what you need:

| Member | Purpose |
|---|---|
| `name` | Short identifier used in logs and prompts |
| `capabilities` | Natural-language description injected into the Tester prompt |
| `anchor_patterns` | Extra regex list for the intent linter |
| `env_vars()` | Environment variables injected into Tester/Worker subprocesses |
| `ensure()` | Bring up resources (called once) |
| `health_check()` | Probe before each Tester call; self-heal if possible |
| `shutdown()` | Tear down (called on every exit path) |
| `notify_pre_verify(fid, tid)` | Hook before each test |
| `notify_post_worker(modified)` | Hook after Worker edits; e.g. hot-reload |

## Registration

Expose a `build(**kwargs)` factory in a module under `environments/` and the
CLI can load it by name:

```bash
python -m tdd_loop.run path/to/feature_list.json --environment null
python -m tdd_loop.run path/to/feature_list.json --environment http --env-arg base_url=http://localhost:8080
```

## Shipped examples

- `null` — no runtime; Tester verifies via code reading only. Default.

## Adding a domain harness

The main reason this split exists. A harness that telnets into a live process,
spawns a container, hits a mock cluster, or drives a browser belongs here —
**not** in the core loop. Keep the core agnostic; make the adapter small.
