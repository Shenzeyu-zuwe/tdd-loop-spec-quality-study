# hello-world spec

Trivial sample used to smoke-test the TDD-Loop framework end-to-end with
the Null environment.

## Capability

A `greeter` module with one public function:

```python
def greet(name: str) -> str:
    """Return 'Hello, {name}!'. Raise TypeError if name is not a string."""
```

## Expected behaviour

- `greet("Ada")` → `"Hello, Ada!"`
- `greet("")` → `"Hello, !"`  (we do not special-case empty strings)
- `greet(42)` → raises `TypeError` with a message mentioning "string"

## Non-goals

- No CLI, no I/O, no logging. Purely a library function.
