import pytest
import math
from gameplay import combo_input_buffer as mod

CASES = [
    ("push", 'm.buffer_push([1, 2], 3, 2) == [2, 3]'),
    ("expire", 'm.buffer_expire(100, 120, 30) is True'),
    ("event", 'm.event_sample([(0, "a"), (1, "b")], 1) == "b"'),
    ("sort", "m.sort_inputs([(2, 'b'), (1, 'a')]) == [(1, 'a'), (2, 'b')]"),
    ("table", "m.stance_table('air', {'air': 1, 'ground': 2}) == 1"),
    ("server", 'm.server_window(100, 50) == 50'),
    ("dead", 'm.deadzone(0.1, 0.2) == 0.0'),
    ("pass", 'm.should_pass(True) is False'),
    ("prio", 'm.priority(2, 5) == 5'),
    ("fallback", "m.fallback('attack', False) == 'idle'"),
    ("step", 'm.combo_step(2, 3) == 0'),
    ("id", 'm.combo_id(3, 2) == "3:2"'),
    ("key", 'm.input_key(1.5, "light") == "1.5:light"'),
    ("window", 'm.combo_window(1, 3, 2) is True'),
    ("len", "m.chain_length(['a', 'b']) == 2")
]

@pytest.mark.parametrize("name,expr", CASES, ids=[c[0] for c in CASES])
def test_contract(name, expr):
    assert eval(expr, {"m": mod, "approx": pytest.approx, "math": math})
