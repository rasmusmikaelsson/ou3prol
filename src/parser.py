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

    # Sort activities and create empty sets to store their relations
    activities = sorted(matrix)
    successors = {activity: set() for activity in activities}
    predecessors = {activity: set() for activity in activities}

    # Go through the upper triangular part of the matrix
    for row_index, activity in enumerate(activities):
        for column_index in range(row_index, len(activities)):
            other_activity = activities[column_index]
            relation = matrix[activity][column_index]

            # Activity is followed by other_activity
            if relation == "->":
                successors[activity].add(other_activity)
                predecessors[other_activity].add(activity)

            # Other_activity is followed by activity
            elif relation == "<-":
                successors[other_activity].add(activity)
                predecessors[activity].add(other_activity)

            # Both activities can follow each other
            elif relation == "||":
                successors[activity].add(other_activity)
                successors[other_activity].add(activity)
                predecessors[activity].add(other_activity)
                predecessors[other_activity].add(activity)

    # Find activities without predecessors (possible starting activities)
    starts = [
        activity
        for activity in activities
        if not predecessors[activity]
    ]

    # Find activities without successors (possible ending activities)
    ends = [
        activity for activity in activities if not successors[activity]
    ]

    constraints = []

    # Create constraints for the starting activities
    if starts:
        if format == "LTL":
            constraints.append(f"G(START -> ({' v '.join(starts)}))")
        else:
            constraints.append(f"^({'|'.join(starts)})")

    # Create constraints for each activity and its possible successors
    for activity in activities:
        activity_successors = sorted(successors[activity])

        # Skip activities without successors
        if not activity_successors:
            continue

        if format == "LTL":
            # The next activity must be one of the allowed successors
            constraints.append(
                f"G({activity} -> N({' v '.join(activity_successors)}))"
            )
        else:
            # Create a RegExp pattern for the allowed successors
            successor_pattern = "|".join(activity_successors)
            constraints.append(
                f"^[^{activity}]*({activity}({successor_pattern})"
                f"[^{activity}]*)*"
                f"[^{activity}]*$"
            )

    # Create constraints for the ending activities
    if ends:
        if format == "LTL":
            constraints.append(f"G(({' v '.join(ends)}) -> END)")
        else:
            # The sequence must end with one of the ending activities
            end_pattern = "|".join(ends)
            constraints.append(f"({end_pattern})$")

            # Prevent two ending activities from appearing consecutively
            constraints.append(
                f"^(?!.*(({end_pattern})({end_pattern})).*$)"
            )

    return constraints

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
