# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part A: Single Player Freckers

from .core import CellState, Coord, Direction, MoveAction
from .utils import render_board
from collections import deque

BOARD_N = 8
directions = [(0,-1), (1,-1), (1,0), (1,1), (0,1)]

def search(
    board: dict[Coord, CellState]
) -> list[MoveAction] | None:
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

    #python -m search < test-vis1.csv
    visited = []
    queue = deque()

    #Going through the initialisation of the board and identifying the starting state.
    for x, y in board:
        state = board.get(Coord(r = x, c = y))
        if state == CellState.RED:
            queue.append((x,y))
            visited.append((x,y))
            break  
    
    while queue:
        print(queue)
        r, c = queue.popleft()

        #Check all neighbouring positions, it's a valid move if it is in the board dict and == 'Lilypad'
        for dx, dy in directions:
            newR, newC = r + dx, c + dy

            if ((withinBounds(newR, newC)) and ((newR, newC) not in visited)):
                newState = board.get(Coord(newR, newC))
                if (newState == CellState.LILY_PAD):
                    queue.append((newR, newC))
                    visited.append((newR, newC))

                #Check if we can jump over the frog
                elif (newState == CellState.BLUE):
                    if ((withinBounds(newR + dx, newC + dy)) and (board.get(Coord(newR + dx, newC + dy)) == CellState.LILY_PAD) and ((newR + dx, newC + dy) not in visited)):
                        queue.append((newR + dx, newC + dy))
                        visited.append((newR + dx, newC + dy))

                        #Call findJumpChain to queue the possible squares we could've jumped to from here
                        for coord in findJumpChain(newR + dx, newC + dy, board, visited, result = []):
                            queue.append(coord)
                            visited.append(coord)
                
                #Still need to make the frog stop moving once it reaches the end state
    
                    
    #python -m search < test-vis1.csv

    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    return []
    '''
        MoveAction(Coord(0, 5), [Direction.Down]),
        MoveAction(Coord(1, 5), [Direction.DownLeft]),
        MoveAction(Coord(3, 3), [Direction.Left]),
        MoveAction(Coord(3, 2), [Direction.Down, Direction.Right]),
        MoveAction(Coord(5, 4), [Direction.Down]),
        MoveAction(Coord(6, 4), [Direction.Down]),
       ''' 
    
def findJumpChain(
    r, c, board: dict[Coord, CellState], visited, result
) -> list[()] | None:
    
    for dx, dy in directions:
        newR, newC = r + dx, c + dy
        if withinBounds(newR, newC):
            if (board.get((Coord(newR, newC))) == CellState.BLUE):
                newR, newC = newR + dx, newC + dy

                if withinBounds(newR, newC):
                    if ((board.get((Coord(newR, newC))) == CellState.LILY_PAD) and (newR, newC) not in visited):
                        visited.append((newR, newC))
                        result.append((newR, newC))
                        findJumpChain(newR, newC, board, visited, result)
                
    return result

def withinBounds(r,c):
    return ((r < BOARD_N) and (c < BOARD_N) and (c >= 0))
    