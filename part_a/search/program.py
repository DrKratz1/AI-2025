# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part A: Single Player Freckers

from .core import CellState, Coord, Direction, MoveAction
from .utils import render_board
from collections import deque

BOARD_N = 8
END_ROW = 7
directions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1)]
directionDict = {
    (0, -1): Direction.Left,
    (1, -1): Direction.DownLeft,
    (1, 0): Direction.Down,
    (1, 1): Direction.DownRight,
    (0, 1): Direction.Right,
}


def search(board: dict[Coord, CellState]) -> list[MoveAction] | None:
    """
    This is the entry point for your submission. You should modify this
    function to solve the search problem discussed in the Part A specification.
    See `core.py` for information on the types being used here.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to "player colours". The keys are `Coord` instances,
            and the values are `CellState` instances which can be one of
            `CellState.RED`, `CellState.BLUE`, or `CellState.LILY_PAD`.

    Returns:
        A list of "move actions" as MoveAction instances, or `None` if no
        solution is possible.
    """

    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    print(render_board(board, ansi=True))

    # Do some impressive AI stuff here to find the solution...
    # ...
    # ... (your solution goes here!)
    # ...

    start = findStart(board)
    moveList = bfs(board, start)

    if moveList == None:
        # if no path was found, return None
        return None

    else:
        result = []
        for i in range(len(moveList)):
            coord = moveList[i][0]
            direction = moveList[i][1]
            coord = Coord(r=coord[0], c=coord[1])

            if any(isinstance(j, list) for j in direction):
                direction = flattenList(direction)

            result.append(MoveAction(coord, direction))
    
    # python -m search < test-vis3.csv

    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    return result



def findStart(board):
    # Going through the initialisation of the board and identifying the starting state.
    for x, y in board:
        state = board.get(Coord(r=x, c=y))
        if state == CellState.RED:
            return (x, y)


def backtrace(parent, direction, start, end):
    # backtrace the path from the end to the start using the parent dictionary
    path = [(end, direction[end])]
    while path[-1][0] != start:
        path.append((parent[path[-1][0]], direction[path[-1][0]]))
    path.reverse()
    path.pop(-1)  # remove the last node
    return path

def bfs(board, start):
    parent = {}
    direction = {}
    visited = []
    queue = deque()
    queue.append(start)
    visited.append(start)

    while queue:
        r, c = queue.popleft()

        # check if we have reached the end state
        if r == END_ROW:
            return backtrace(parent, direction, start, (r, c))

        # check neighbouring positions
        for dx, dy in directions:
            newR, newC = r + dx, c + dy

            # check validity of new position
            if withinBounds(newR, newC) and ((newR, newC) not in visited):
                newState = board.get(Coord(newR, newC))
                if newState == CellState.LILY_PAD:
                    parent[newR, newC] = (r, c)
                    direction[newR, newC] = directionDict[(dx, dy)]
                    queue.append((newR, newC))
                    visited.append((newR, newC))

                elif newState == CellState.BLUE:
                    # check if we can jump over the frog
                    checkR, checkC = newR + dx, newC + dy
                    if (
                        withinBounds(checkR, checkC)
                        and board.get(Coord(checkR, checkC)) == CellState.LILY_PAD
                    ):
                        # can jump over the frog
                        jumpChain = findJumpChain(
                            newR - dx,
                            newC - dy,
                            board,
                            visited.copy(),
                            result={(newR - dx, newC - dy): []},
                        )
                        for coord in list(jumpChain.keys()):
                            if coord not in visited:
                                parent[coord] = (r, c)
                                direction[coord] = jumpChain[coord]
                                queue.append(coord)
                                visited.append(coord)

    return None


def findJumpChain(r, c, board, visited, result):
    for dx, dy in directions:
        newR, newC = r + dx, c + dy
        if withinBounds(newR, newC):
            if board.get((Coord(newR, newC))) == CellState.BLUE:
                newR, newC = newR + dx, newC + dy

                if withinBounds(newR, newC):
                    if (
                        board.get((Coord(newR, newC))) == CellState.LILY_PAD
                        and (newR, newC) not in visited
                    ):
                        visited.append((newR, newC))

                        # do direction appending here
                        result[(newR, newC)] = []
                        if result[newR - 2 * dx, newC - 2 * dy] != []:
                            result[(newR, newC)].append(
                                result[newR - 2 * dx, newC - 2 * dy]
                            )
                        result[(newR, newC)].append(directionDict[(dx, dy)])

                        findJumpChain(newR, newC, board, visited, result)

    return result


def withinBounds(r, c):
    return (r < BOARD_N) and (c < BOARD_N) and (c >= 0)


def flattenList(nestedList):
    return [
        item
        for sublist in nestedList
        for item in (flattenList(sublist) if isinstance(sublist, list) else [sublist])
    ]
