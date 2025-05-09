# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part A: Single Player Freckers

from sys import stdin
from .core import Coord, CellState, MoveAction
from .program import search

# WARNING: Please *do not* modify any of the code in this file, as this could
#          break things in the submission environment. Failed test cases due to
#          modification of this file will not receive any marks. 
#
#          To implement your solution you should modify the `search` function
#          in `program.py` instead, as discussed in the specification.

SOLUTION_PREFIX = "$SOLUTION"


def parse_input(input: str) -> dict[Coord, CellState]:
    """
    Parse input into the required data structures.
    """
    state = {}

    try:
        for r, line in enumerate(input.strip().split("\n")):
            for c, p in enumerate(line.split(",")):
                p = p.strip()
                if line[0] != "#" and line.strip() != "" and p != "":
                    state[Coord(r, c)] = {
                        "r": CellState.RED,
                        "b": CellState.BLUE,
                        "*": CellState.LILY_PAD
                    }[p.lower()]

        return state

    except Exception as e:
        print(f"Error parsing input: {e}")
        exit(1)


def print_result(sequence: list[MoveAction] | None):
    """
    Print the given action sequence, one action per line, or "NOT_FOUND" if no
    sequence was found.
    """
    if sequence is not None:
        for action in sequence:
            print(f"{SOLUTION_PREFIX} {action}")
    else:
        print(f"{SOLUTION_PREFIX} NOT_FOUND")


def main():
    """
    Main entry point for program.
    """
    input = parse_input(stdin.read())
    sequence: list[MoveAction] | None = search(input)
    print_result(sequence)


if __name__ == "__main__":
    main()
