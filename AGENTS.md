# gopherkind-protocol-py

An independent Python implementation of the Gopherkind kind 31436 document
grammar (see `README.md`). It validates document metadata and exact paths,
parses kindmaps, applies NIP-01 replacement ordering and NIP-40 expiry, and
renders RFC 1436 type `0` wire bodies. It was built from `SPEC.md` and the
published language-neutral fixture, not by translating the TypeScript
reference implementation at `forgesworn/gopherkind`. Requires Python 3.11+.
No runtime or test dependency.

## Build & Test

| Command | Purpose |
|---------|---------|
| `pip install -e .` | Install the package in editable mode |
| `python3 -m unittest discover -s tests -v` | Run the conformance test suite |

There is no separate lint, typecheck or build step configured.

## Structure

```
src/gopherkind_protocol/__init__.py  - public exports
src/gopherkind_protocol/core.py      - parsing, validation and rendering logic
tests/test_conformance.py            - conformance tests against the fixture
tests/fixtures/kind31436-v3.json     - vendored, unchanged published fixture
```

## Conventions

- Dataclasses (`Document`, `KindmapLine`) are frozen.
- No runtime dependencies; keep it that way.
- The fixture in `tests/fixtures/` is vendored unchanged from
  `forgesworn/gopherkind`; do not hand-edit it.
- The library starts after ordinary NIP-01 event id and signature
  validation; that stays the caller's responsibility, not this library's.

## Key Files

| File | Purpose |
|------|---------|
| `src/gopherkind_protocol/core.py` | All parsing, validation and rendering |
| `tests/fixtures/kind31436-v3.json` | Published, language-neutral conformance fixture |
| `pyproject.toml` | Package metadata, no runtime dependencies |

## Common Pitfalls

- Tests assert against the vendored fixture; do not change expected values
  there to make a test pass.
- `parse_kindmap` and `_clean_display` preserve SGR colour sequences
  (`ESC [ ... m`) but replace every other control character with a space;
  do not remove the sequence itself.
- This library does not verify Nostr event ids or signatures; callers must
  do that before passing an event in.
