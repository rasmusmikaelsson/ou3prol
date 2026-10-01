"""Test cases for the parser

:Authors:
    Timotheus Kampik <tkampik@cs.umu.se>
    Tests based on similar ones written by Adrian Rebmann
"""

import json
from subprocess import Popen, PIPE

from conf import parser_base_command

def get_parser_output(command: list) -> list:
    """Executes a parsing command and returns the result as an
    alphanumerically sorted list.

    Args:
        command (list): list of the parsing command that is to be executed

    Returns:
        list: Parsed constraints, alphanumerically sorted
    """
    process = Popen(command, stdout=PIPE, stderr=False)
    result = json.loads(process.communicate()[0].decode('utf8').replace("'", '"'))
    result.sort()
    return result

def test_xor_branching():
    """Tests an exclusive choice: Start -> a -> {b XOR c} -> d.
    """
    expected_ltl = ["G(START -> (a))", "G(a -> N(b v c))", "G(b -> N(d))", "G(c -> N(d))", "G((d) -> END)"]
    expected_ltl.sort()
    expected_regexp = ["^(a)", "^[^a]*(a(b|c)[^a]*)*[^a]*$", "^[^b]*(b(d)[^b]*)*[^b]*$", "^[^c]*(c(d)[^c]*)*[^c]*$", "(d)$", "^(?!.*((d)(d)).*$)"]
    expected_regexp.sort()

    result_ltl = get_parser_output(parser_base_command + ["./tests/matrix_1.json", "LTL"])
    assert expected_ltl == result_ltl

    result_regexp = get_parser_output(parser_base_command + ["./tests/matrix_1.json", "RegExp"])
    assert expected_regexp == result_regexp

def test_or_branching():
    """Tests an OR flow: Start -> a -> (b || c) -> d
    """
    expected_ltl = ["G(START -> (a))", "G(a -> N(b v c))", "G(b -> N(c v d))", "G(c -> N(b v d))", "G((d) -> END)"]
    expected_ltl.sort()
    expected_regexp = ["^(a)", "^[^a]*(a(b|c)[^a]*)*[^a]*$", "^[^b]*(b(c|d)[^b]*)*[^b]*$", "^[^c]*(c(b|d)[^c]*)*[^c]*$", "(d)$", "^(?!.*((d)(d)).*$)"]
    expected_regexp.sort()

    result_ltl = get_parser_output(parser_base_command + ["./tests/matrix_2.json", "LTL"])
    assert expected_ltl == result_ltl

    result_regexp = get_parser_output(parser_base_command + ["./tests/matrix_2.json", "RegExp"])
    assert expected_regexp == result_regexp

def test_or_bypass():
    """Tests an or flow with bypass: Start -> a -> (b || c) -> d, and a -> d.
    """
    expected_ltl = ["G(START -> (a))", "G(a -> N(b v c v d))", "G(b -> N(c v d))", "G(c -> N(b v d))", "G((d) -> END)"]
    expected_ltl.sort()
    expected_regexp = ["^(a)", "^[^a]*(a(b|c|d)[^a]*)*[^a]*$", "^[^b]*(b(c|d)[^b]*)*[^b]*$", "^[^c]*(c(b|d)[^c]*)*[^c]*$", "(d)$", "^(?!.*((d)(d)).*$)"]
    expected_regexp.sort()

    result_ltl = get_parser_output(parser_base_command + ["./tests/matrix_3.json", "LTL"])
    assert expected_ltl == result_ltl

    result_regexp = get_parser_output(parser_base_command + ["./tests/matrix_3.json", "RegExp"])
    assert expected_regexp == result_regexp

def test_loop():
    """Tests a structured loop: Start -> a -> b -> c -> b ... -> d.
    """
    expected_ltl = ["G(START -> (a))", "G(a -> N(b))", "G(b -> N(c))", "G(c -> N(b v d))", "G((d) -> END)"]
    expected_ltl.sort()
    expected_regexp = ["^(a)", "^[^a]*(a(b)[^a]*)*[^a]*$", "^[^b]*(b(c)[^b]*)*[^b]*$", "^[^c]*(c(b|d)[^c]*)*[^c]*$", "(d)$", "^(?!.*((d)(d)).*$)"]
    expected_regexp.sort()

    result_ltl = get_parser_output(parser_base_command + ["./tests/matrix_4.json", "LTL"])
    assert expected_ltl == result_ltl

    result_regexp = get_parser_output(parser_base_command + ["./tests/matrix_4.json", "RegExp"])
    assert expected_regexp == result_regexp

def test_multiple_starts():
    """Tests a process that can start with either a or b.
    """
    expected_ltl = ["G(START -> (a v b))", "G(a -> N(c))", "G(b -> N(c))", "G((c) -> END)"]
    expected_ltl.sort()
    expected_regexp = ["^(a|b)", "^[^a]*(a(c)[^a]*)*[^a]*$", "^[^b]*(b(c)[^b]*)*[^b]*$", "(c)$", "^(?!.*((c)(c)).*$)"]
    expected_regexp.sort()

    result_ltl = get_parser_output(parser_base_command + ["./tests/matrix_5.json", "LTL"])
    assert expected_ltl == result_ltl

    result_regexp = get_parser_output(parser_base_command + ["./tests/matrix_5.json", "RegExp"])
    assert expected_regexp == result_regexp

def test_multiple_ends():
    """Tests a process that can end with either b or c.
    """
    expected_ltl = ["G(START -> (a))", "G(a -> N(b v c))", "G((b v c) -> END)"]
    expected_ltl.sort()
    expected_regexp = ["^(a)", "^[^a]*(a(b|c)[^a]*)*[^a]*$", "(b|c)$", "^(?!.*((b|c)(b|c)).*$)"]
    expected_regexp.sort()

    result_ltl = get_parser_output(parser_base_command + ["./tests/matrix_6.json", "LTL"])
    assert expected_ltl == result_ltl

    result_regexp = get_parser_output(parser_base_command + ["./tests/matrix_6.json", "RegExp"])
    assert expected_regexp == result_regexp