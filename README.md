# Docs-to-Test-Case Generator

A Python CLI that converts **OpenAPI 3.x** specs into reviewable API test case specifications. It creates documented success cases, missing-required-parameter candidates, and missing-authentication candidates.

## Run

```bash
python -m unittest discover -s tests -v
python generator.py --spec examples/petstore.json
```

The bundled example is a small **synthetic OpenAPI sample** for reproducible offline tests. To use real public API documentation, download a public OpenAPI 3.x JSON/YAML spec and run:

```bash
pip install -r requirements.txt
python generator.py --spec path/to/public-openapi.yaml --output generated_test_cases.json
```

## Scope and limitations

- Produces **test specifications**, not executed API tests. No network calls are made to target APIs.
- Success codes come from the supplied OpenAPI document. Negative-test statuses are hypotheses and must be verified against the actual service.
- Supports OpenAPI 3.x and basic inline parameter definitions; does not resolve `$ref` or infer payloads.
- No Gemini API key required. Future work: `$ref` resolution, request-body test generation, FastAPI API, UI integration.
