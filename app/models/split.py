import requests
for m in requests.get('https://openrouter.ai/api/v1/models').json()['data']:
    if m['id'].endswith(':free') and 'reasoning' in m.get('supported_parameters', []):
        print(m['id'])