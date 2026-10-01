"""
Parser that takes a behavioral profile specification in JSON format
And returns constraints in either LTL or RegExp format.

:Authors:
    Timotheus Kampik <tkampik@cs.umu.se>
"""

import json, logging, sys

logger = logging.getLogger(__name__)

def parse(matrix: dict, format: str) -> list:
    """Takes a behavioral profile and turns it into a list of
    LTL or RegExp constraints.

    Args:
        matrix (dict): Matrix of the behavioral profile
        format (str): Output format: either `LTL` or `RegExp`

    Returns:
        List: list of LTL or RegExp constraints
    """
    # TODO You need to implement this. Remove the TODO afterwards.

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) != 3 or not sys.argv[2] in ["LTL", "RegExp"]:
        logger.error("Usage: python parser.py <path_to_json> <format>")
        logger.error("Format is either LTL or RegExp")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_format = sys.argv[2]
    logger.info(f'Reading file at {file_path}...')
    with open(file_path) as file: content = file.read()
    with open(file_path) as file: matrix = json.load(file)
    logger.info("Matrix:")
    logger.info(content)
   
    logger.info(f'Generating constraints as {output_format}...')
    constraints = parse(matrix, output_format)
    logger.info("Constraints generated:")
    print(constraints)
    

