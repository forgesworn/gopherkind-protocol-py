# gopherkind-protocol-py

An independent Python implementation of the proposed Gopherkind document
grammar (Nostr kind `31436`). It validates document metadata and exact paths,
parses kindmaps, applies NIP-01 replacement ordering before document validation
and NIP-40 expiry, and renders RFC 1436 type `0` wire bodies.

This was implemented from `SPEC.md` and the language-neutral fixture published
by [forgesworn/gopherkind](https://github.com/forgesworn/gopherkind). It does
not import, copy or mechanically translate that repository's TypeScript
parser. The fixture is vendored unchanged at
`tests/fixtures/kind31436-v1.json` so the evidence remains reproducible.

It deliberately starts after ordinary NIP-01 event id and signature
validation. A consuming Nostr client remains responsible for that layer.

Run the complete published fixture with the Python standard library:

```sh
python3 -m unittest discover -s tests -v
```

No runtime or test dependency is required.
