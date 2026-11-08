"""Generate reviewable API test specifications from OpenAPI 3.x documents."""
import argparse
import json
import urllib.request
from pathlib import Path

DEFAULT_URL = 'https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore.yaml'

def load_spec(path):
    if str(path).startswith(('https://', 'http://')):
        with urllib.request.urlopen(path, timeout=20) as response:
            raw = response.read().decode('utf-8')
    else:
        raw = Path(path).read_text(encoding='utf-8')
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError('YAML input requires: pip install PyYAML') from exc
        return yaml.safe_load(raw)

def generate(spec):
    if not isinstance(spec, dict) or not str(spec.get('openapi', '')).startswith('3.'):
        raise ValueError('Expected an OpenAPI 3.x document')
    cases = []
    for path, path_item in spec.get('paths', {}).items():
        if not isinstance(path_item, dict):
            continue
        common_params = path_item.get('parameters', [])
        for method in ('get','post','put','patch','delete','options','head'):
            op = path_item.get(method)
            if not isinstance(op, dict):
                continue
            operation_id = op.get('operationId', f'{method}_{path}')
            responses = op.get('responses', {})
            success_codes = [str(c) for c in responses if str(c).startswith('2')]
            cases.append({'id': f'{operation_id}:success', 'method': method.upper(), 'path': path,
                          'type': 'documented_success', 'expected_status': success_codes,
                          'note': 'Specification-derived expectation; not an executed request'})
            for param in [*common_params, *op.get('parameters', [])]:
                if isinstance(param, dict) and param.get('required') is True and param.get('in') in ('query', 'header', 'path'):
                    cases.append({'id': f'{operation_id}:missing:{param.get("name")}',
                                  'method': method.upper(), 'path': path, 'type': 'missing_required_parameter',
                                  'parameter': param.get('name'), 'expected_status': ['400', '422'],
                                  'note': 'Candidate negative test; expected status must be verified against implementation'})
            if op.get('security', spec.get('security')):
                cases.append({'id': f'{operation_id}:unauthorized', 'method': method.upper(),
                              'path': path, 'type': 'missing_authentication', 'expected_status': ['401', '403'],
                              'note': 'Candidate security test; expected status must be verified'})
    return cases

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--spec', default='examples/petstore.json')
    parser.add_argument('--output', default='generated_test_cases.json')
    args = parser.parse_args()
    spec = load_spec(args.spec)
    cases = generate(spec)
    Path(args.output).write_text(json.dumps({'source': args.spec, 'generated_count': len(cases),
                                             'executed_count': 0, 'cases': cases}, indent=2), encoding='utf-8')
    print(f'Generated {len(cases)} test case specifications; 0 HTTP requests executed. Output: {args.output}')

if __name__ == '__main__':
    main()
