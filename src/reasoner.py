"""
Reasoner that takes a behavioral profile specification in JSON format,
as well as an array of event traces and returns for each trace whether
it satisfies the profile or not.

:Authors:
    Timotheus Kampik <tkampik@cs.umu.se>
"""

import json, logging, re, sys
import parser

logger = logging.getLogger(__name__)


def evaluate(matrix: dict, traces: list) -> dict:
    """Takes a behavioral profile and evaluates traces against
    its RegExp constraints.

    Args:
        matrix (dict): Matrix of the behavioral profile
        traces (list): List of traces (list of list of strings)

    Returns:
        Dictionary that labels all traces as True (satisfied) or False (violated)
    """

    # Generate RegExp constraints and compile them into patterns
    constraints = parser.parse(matrix, "RegExp")
    patterns = [re.compile(constraint) for constraint in constraints]

    results = {}

    # Evaluate each trace against all constraints
    for trace in traces:
        # Convert the trace into a single string
        trace_string = "".join(trace)

        # A trace is valid only if all constraints are satisfied
        results[trace_string] = all(
            pattern.search(trace_string) is not None for pattern in patterns
        )

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) != 3 or not sys.argv[2]:
        logger.error("Usage: python parser.py <path_to_matrix> <path_to_traces>")
        sys.exit(1)
    
    matrix_path = sys.argv[1]
    traces_path = sys.argv[2]
    logger.info(f'Reading matrix at {matrix_path}...')
    with open(matrix_path) as file: content = file.read()
    with open(matrix_path) as file: matrix = json.load(file)
    logger.info("Matrix:")
    logger.info(content)

    logger.info(f'Reading traces at {traces_path}...')
    with open(traces_path) as file: content = file.read()
    with open(traces_path) as file: traces = json.load(file)
    logger.info("Traces:")
    logger.info(content)

    logger.info(f'Evaluating traces...')
    constraints = json.dumps(evaluate(matrix, traces))

    logger.info("Evaluation complete:")
    print(constraints)
