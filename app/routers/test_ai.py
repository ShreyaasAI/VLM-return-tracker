import os
from ai import decide, parse

def test_parse():
    assert parse('here: {"a": 1} done') == {'a': 1}

def test_hard_rule_skips_llm():
    c = dict(anomaly=1, duplicate=0, price=10, product_id='P1')
    assert decide(c)['route'] == 'human'

    