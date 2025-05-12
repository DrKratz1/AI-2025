# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Coord, Direction, Action, MoveAction, GrowAction
import math
import random


class MCTSNode:
    def __init__(self, state, parent=None, action=None, player=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        self.action = action
        self.player = player

    def isFullyExpanded(self, validMoves):
        tried = [child.action for child in self.children]
        return len(tried) == len(validMoves)

    def bestChild(self, c=1.4):
        return max(
            self.children,
            key=lambda child: (child.wins / child.visits if child.visits > 0 else 0)
            + c * math.sqrt(math.log(self.visits + 1) / (child.visits + 1)),
        )


class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Freckers game events.
    """

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self._color = color
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")
        self.gameState = GameState()

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object.
        """

        # Below we have hardcoded two actions to be played depending on whether
        # the agent is playing as BLUE or RED. Obviously this won't work beyond
        # the initial moves of the game, so you should use some game playing
        # technique(s) to determine the best action to take.
        print(f"Testing: {self._color} is playing a MOVE action")
        simulations = 500
        root = MCTSNode(self.gameState.copyState(), player=self._color)

        for _ in range(simulations):
            node = self.select(root)
            if node is None:
                continue
            result = self.simulate(node.state.copyState(), node.player)
            self.backpropagate(node, result)

        bestChild = root.bestChild(c=0)
        frog, move = bestChild.action

        if self._color == PlayerColor.RED:
            print("Testing: RED is playing a MCTS action")
        else:
            print("Testing: BLUE is playing a MCTS action")

        return (
            GrowAction()
            if move == "Grow"
            else MoveAction(Coord(frog[0], frog[1]), move)
        )

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after a player has taken their
        turn. You should use it to update the agent's internal game state.
        """

        # There are two possible action types: MOVE and GROW. Below we check
        # which type of action was played and print out the details of the
        # action for demonstration purposes. You should replace this with your
        # own logic to update your agent's internal game state representation.
        match action:
            case MoveAction(coord, dirs):
                self.gameState.move(color, coord, dirs)
            case GrowAction():
                self.gameState.grow(color)
            case _:
                raise ValueError(f"Unknown action type: {action}")

    def select(self, node):
        current = node
        while current.children:
            current = current.bestChild()
        validMoves = self.getAllActions(current.state, current.player)
        if not current.isFullyExpanded(validMoves):
            return self.expand(current, validMoves)
        return current

    def expand(self, node, actions):
        tried = [child.action for child in node.children]
        untried = [action for action in actions if action not in tried]
        if not untried:
            return None
        action = random.choice(untried)
        newState = node.state.copyState()
        frog, move = action
        if move == "Grow":
            newState.grow(node.player)
        else:
            newState.move(node.player, Coord(frog[0], frog[1]), move)
        nextPlayer = (
            PlayerColor.RED if node.player == PlayerColor.BLUE else PlayerColor.BLUE
        )
        child = MCTSNode(newState, parent=node, action=action, player=nextPlayer)
        node.children.append(child)
        return child

    def simulate(self, state, player):
        return self.evaluateMove(state, player, grow=False)

    def backpropagate(self, node, result):
        while node:
            node.visits += 1
            node.wins += result
            node = node.parent

    def getAllActions(self, state, color):
        actions = []
        valids = state.validMoves(color)
        for frog, moves in valids.items():
            for move in moves:
                actions.append((frog, move))
        return actions

    def evaluateMove(self, state: "GameState", color: PlayerColor, grow: bool):
        evaluationScore = 0
        frogs = state.redFrogs if color == PlayerColor.RED else state.blueFrogs
        opponentColor = (
            PlayerColor.BLUE if color == PlayerColor.RED else PlayerColor.RED
        )
        opponentFrogs = state.blueFrogs if color == PlayerColor.RED else state.redFrogs

        evaluationScore += 5 * self.countJumpChains(state, color)

        if grow:
            evaluationScore += 0.5 * len(
                [cell for cell in state.board.values() if cell["state"] == "pad"]
            )
        evaluationScore -= 0.5 * len(
            [cell for cell in state.board.values() if cell["state"] == "pad"]
        )

        for r, c in frogs:
            multiplier = (
                1.5
                if (color == PlayerColor.RED and r <= 2)
                or (color == PlayerColor.BLUE and r >= 5)
                else 1
            )
            evaluationScore += (
                (r * 10 * multiplier)
                if color == PlayerColor.RED
                else ((7 - r) * 10 * multiplier)
            )

        for r, c in opponentFrogs:
            evaluationScore -= (r * 10) if color == PlayerColor.BLUE else ((7 - r) * 10)

        if (
            all(f[0] == 7 for f in frogs)
            if color == PlayerColor.RED
            else all(f[0] == 0 for f in frogs)
        ):
            evaluationScore += 10000

        return evaluationScore

    def countJumpChains(self, state: "GameState", color: PlayerColor):
        numChains = 0
        jumpChains = []
        frogs = state.redFrogs if color == PlayerColor.RED else state.blueFrogs

        directions = (
            [
                Direction.Down,
                Direction.DownLeft,
                Direction.DownRight,
                Direction.Left,
                Direction.Right,
            ]
            if color == PlayerColor.RED
            else [
                Direction.Up,
                Direction.UpLeft,
                Direction.UpRight,
                Direction.Left,
                Direction.Right,
            ]
        )

        for frog in frogs:
            dfsResult = state.DFS(frog, directions, result={frog: []}, visited=[])
            for nextCoord, jumpPath in dfsResult.items():
                if jumpPath:
                    jumpChains.append((frog, jumpPath))

        if len(jumpChains) > 0:
            numChains = len(jumpChains)
            # print(f"total chainJumps in this state = {numChains}")

        return numChains


class GameState:
    """
    This class represents the state of the game. It is used to keep track of
    the game state and update it as the game progresses.
    """

    def __init__(self):
        # 8x8 board
        self.board = {(r, c): {"state": None} for r in range(8) for c in range(8)}
        self.redFrogs = set()
        self.blueFrogs = set()
        self.turn = 0
        self.directionDict = {
            (0, -1): Direction.Left,
            (1, -1): Direction.DownLeft,
            (1, 0): Direction.Down,
            (1, 1): Direction.DownRight,
            (0, 1): Direction.Right,
            (-1, 0): Direction.Up,
            (-1, -1): Direction.UpLeft,
            (-1, 1): Direction.UpRight,
        }

        # initialise board with 6 frogs for each player in the middle 6 rows
        for c in range(8):
            if c in range(1, 7):
                self.board[(0, c)] = {"state": PlayerColor.RED}
                self.redFrogs.add((0, c))
                self.board[(1, c)] = {"state": "pad"}
                self.board[(7, c)] = {"state": PlayerColor.BLUE}
                self.blueFrogs.add((7, c))
                self.board[(6, c)] = {"state": "pad"}
            else:
                self.board[(0, c)] = {"state": "pad"}
                self.board[(7, c)] = {"state": "pad"}

    def grow(self, color: PlayerColor):
        # go through all frogs and add pads to the board in squares in a 3x3 around the frog
        for frog in self.redFrogs if color == PlayerColor.RED else self.blueFrogs:
            r, c = frog
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if (r + dr, c + dc) in self.board:
                        if self.board[(r + dr, c + dc)]["state"] == None:
                            self.board[(r + dr, c + dc)]["state"] = "pad"
                        else:
                            self.board[(r + dr, c + dc)]["state"]

    def move(self, color: PlayerColor, coord: Coord, directions: list[Direction]):
        # compute final coordinates
        finalCoord = (coord.r, coord.c)
        for direction in directions:
            if type(direction) == list:
                direction = direction[0]
                print(direction)
            nextCoord = (finalCoord[0] + direction.r, finalCoord[1] + direction.c)
            if self.board[nextCoord]["state"] != "pad":
                finalCoord = (nextCoord[0] + direction.r, nextCoord[1] + direction.c)
            else:
                finalCoord = nextCoord
            if finalCoord not in self.board:
                print(direction, directions, (coord.r, coord.c), finalCoord, color)
                print(self.board)
                raise ValueError("Invalid move: out of bounds")

        coord = (coord.r, coord.c)

        self.board[finalCoord]["state"] = color
        self.board[coord]["state"] = None

        # update the set of frogs for the player
        if color == PlayerColor.RED:
            self.redFrogs.remove(coord)
            self.redFrogs.add(finalCoord)
        else:
            self.blueFrogs.remove(coord)
            self.blueFrogs.add(finalCoord)

    def checkWinner(self):
        # check if all frogs in red set are in the last row
        if all(frog[0] == 7 for frog in self.redFrogs):
            return PlayerColor.RED

        # check if all frogs in blue set are in the first row
        elif all(frog[0] == 0 for frog in self.blueFrogs):
            return PlayerColor.BLUE

        else:
            return None

    def validMoves(self, color: PlayerColor):
        # get the set of frogs for the player
        frogs = self.redFrogs if color == PlayerColor.RED else self.blueFrogs

        if color == PlayerColor.RED:
            directions = [
                Direction.Down,
                Direction.DownLeft,
                Direction.DownRight,
                Direction.Left,
                Direction.Right,
            ]
        if color == PlayerColor.BLUE:
            directions = [
                Direction.Up,
                Direction.UpLeft,
                Direction.UpRight,
                Direction.Left,
                Direction.Right,
            ]

        # get the valid moves for each frog
        validMoves = {}

        for frog in frogs:

            # Frogs will always have the option to grow
            validMoves[frog] = ["Grow"]
            for direction in directions:
                newR, newC = frog[0] + direction.r, frog[1] + direction.c
                if (newR, newC) in self.board:
                    if self.board[(newR, newC)]["state"] == "pad":
                        # add the move to the list of valid moves
                        validMoves[frog].append([direction])
                    elif self.board[(newR, newC)]["state"] != None:
                        jumpResults = self.DFS(
                            (frog[0], frog[1]),
                            directions,
                            result={(frog[0], frog[1]): []},
                            visited=[],
                        )
                        for coord in list(jumpResults.keys()):
                            if (
                                jumpResults[coord] != []
                                and jumpResults[coord] not in validMoves[frog]
                            ):
                                validMoves[frog].append(jumpResults[coord])
        return validMoves

    def DFS(
        self,
        frog: tuple[int, int],
        directions: list[Direction],
        result: dict[tuple[int, int], list[Direction]],
        visited: list[tuple[int, int]],
    ):
        for dx, dy in directions:
            midR, midC = frog[0] + dx, frog[1] + dy
            midPosition = (midR, midC)

            if midPosition in self.board and self.board[midPosition]["state"] not in [
                "pad",
                None,
            ]:
                newR, newC = midR + dx, midC + dy
                newPosition = (newR, newC)

                if (
                    newPosition in self.board
                    and self.board[newPosition]["state"] == "pad"
                    and newPosition not in visited
                ):
                    visited.append(newPosition)
                    result[newPosition] = result[frog] + [self.directionDict[(dx, dy)]]
                    self.DFS(newPosition, directions, result, visited)

        return result

    def copyState(self):
        # create a deep copy of the game state
        newState = GameState()
        newState.board = {coord: cell.copy() for coord, cell in self.board.items()}
        newState.redFrogs = self.redFrogs.copy()
        newState.blueFrogs = self.blueFrogs.copy()
        newState.turn = self.turn
        newState.directionDict = self.directionDict.copy()

        return newState

    def __str__(self):
        # print the board in a readable format
        board_str = ""
        for r in range(8):
            for c in range(8):
                if (r, c) in self.board:
                    if self.board[(r, c)]["state"] == PlayerColor.RED:
                        board_str += "R "
                    elif self.board[(r, c)]["state"] == PlayerColor.BLUE:
                        board_str += "B "
                    elif self.board[(r, c)]["state"] == "pad":
                        board_str += "* "
                    else:
                        board_str += ". "
            board_str += "\n"

        return board_str
