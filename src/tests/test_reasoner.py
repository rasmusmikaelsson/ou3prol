"""Test cases for the parser

:Authors:
    Timotheus Kampik <tkampik@cs.umu.se>
"""

import json
from subprocess import Popen, PIPE

from conf import reasoner_base_command

def get_reasoner_output(command):
    process = Popen(command, stdout=PIPE, stderr=False)
    result = json.loads(process.communicate()[0].decode('utf8').replace("'", '"'))
    return result

def test_xor_branching():
    """Tests an exclusive choice: Start -> a -> {b XOR c} -> d.
    """
    expected_results = {
        "abd": True,
        "acd": True,
        "bcd": False,
        "aba": False,
        "abda": False,
        "abcd": False
    }
    results = get_reasoner_output(reasoner_base_command + ["./tests/matrix_1.json", "./tests/traces_1.json"])
    assert results == expected_results

def test_or_branching():
    """Tests an or flow: Start -> a -> (b || c) -> d
    """
    expected_results = {
        "abd": True,
        "acd": True,
        "bcd": False,
        "aba": False,
        "abda": False,
        "abcd": True,
        "acbd": True,
        "ad": False
    }
    results = get_reasoner_output(reasoner_base_command + ["./tests/matrix_2.json", "./tests/traces_2.json"])
    assert results == expected_results

def test_or_bypass():
    """Tests an or flow with bypass: Start -> a -> (b || c) -> d, and a -> d.
    """
    expected_results = {
        "abd": True,
        "acd": True,
        "bcd": False,
        "aba": False,
        "abda": False,
        "abcd": True,
        "acbd": True,
        "ad": True
    }
    results = get_reasoner_output(reasoner_base_command + ["./tests/matrix_3.json", "./tests/traces_3.json"])
    assert results == expected_results

def test_loop():
    """Tests a structured loop: Start -> a -> b -> c -> b ... -> d.
    """
    expected_results = {
        "abd": False,
        "acd": False,
        "aacd": False,
        "abbd": False,
        "abccd": False,
        "abcbc": False,
        "abcbcd": True,
        "abcd": True
    }
    results = get_reasoner_output(reasoner_base_command + ["./tests/matrix_4.json", "./tests/traces_4.json"])
    assert results == expected_results

def test_multiple_starts():
    """Tests a process that can start with either a or b.
    """
    expected_results = {
        "ac": True,
        "bc": True,
        "ab": False,
        "bcd": False,
        "abc": False,
        "acb": False,
        "bac": False
    }
    results = get_reasoner_output(reasoner_base_command + ["./tests/matrix_5.json", "./tests/traces_5.json"])
    assert results == expected_results

def test_multiple_ends():
    """Tests a process that can end with either b or c.
    """
    expected_results = {
        "ac": True,
        "bc": False,
        "ab": True,
        "bcd": False,
        "abc": False,
        "acb": False,
        "bac": False,
        "acc": False
    }
    results = get_reasoner_output(reasoner_base_command + ["./tests/matrix_6.json", "./tests/traces_6.json"])
    assert results == expected_results



    