# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Coord, Direction, Action, MoveAction, GrowAction


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
        self.game = GameState()

        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")

        # print(self.game)

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object.
        """
        redValidMoves = dict(
            sorted(
                self.game.validMoves(PlayerColor.RED).items(),
                key=lambda item: item[0][1],
            )
        )
        blueValidMoves = dict(
            sorted(
                self.game.validMoves(PlayerColor.BLUE).items(),
                key=lambda item: item[0][1],
            )
        )
        match self._color:
            case PlayerColor.RED:
                if self.game.turn < 6:
                    DEPTH = 1
                else:
                    DEPTH = 3
                frogToMove, bestAction = self.minimaxDecision(
                    self.game, DEPTH, True, redValidMoves, self._color
                )
                self.game.turn += 1

                if bestAction == "Grow":
                    return GrowAction()
                else:
                    return MoveAction(Coord(frogToMove[0], frogToMove[1]), bestAction)

            case PlayerColor.BLUE:
                if self.game.turn < 6:
                    DEPTH = 1
                else:
                    DEPTH = 3
                frogToMove, bestAction = self.minimaxDecision(
                    self.game, DEPTH, True, blueValidMoves, self._color
                )

                self.game.turn += 1
                if bestAction == "Grow":
                    return GrowAction()
                else:
                    return MoveAction(Coord(frogToMove[0], frogToMove[1]), bestAction)

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
                dirs_text = ", ".join([str(dir) for dir in dirs])
                print(f"Testing: {color} played MOVE action:")
                print(f"  Coord: {coord}")
                print(f"  Directions: {dirs_text}")

                self.game.move(color, coord, dirs)
                # print(self.game)
            case GrowAction():
                print(f"Testing: {color} played GROW action")

                self.game.grow(color)
                # print(self.game)

            case _:
                raise ValueError(f"Unknown action type: {action}")

    def minimaxDecision(
        self,
        state: "GameState",
        depth: int,
        maxToMove: bool,
        operators: list,
        color: PlayerColor,
    ):
        highestOp = float("-inf")
        frogs = state.redFrogs if color == PlayerColor.RED else state.blueFrogs
        alpha = float("-inf")
        beta = float("inf")
        gorw = False

        for r, c in frogs:
            for op in operators[(r, c)]:
                depthValue = depth
                # For each frog, we check all of the valid moves they can make
                # print(f"Testing MAX: Operator of ({r},{c}) is ", op)

                newState = state.copyState()
                if op == "Grow":
                    newState.grow(color)
                    grow = True
                else:
                    newState.move(color, Coord(r, c), op)
                # print(newState)

                opValue = self.minimaxValue(
                    newState, depthValue - 1, not maxToMove, color, alpha, beta, grow
                )
                # print(f"evaluationValue = {opValue}")

                if opValue > highestOp:
                    highestOp = opValue
                    frogToMove = (r, c)
                    bestAction = op

        print(
            f"Best move for {color} is to move frog at {frogToMove} with operator {bestAction} with value {highestOp}"
        )
        return (frogToMove, bestAction)

    def minimaxValue(
        self,
        state: "GameState",
        depth: int,
        maxToMove: bool,
        color: PlayerColor,
        alpha: float,
        beta: float,
        grow: bool,
    ):
        if depth == 0 or state.checkWinner() is not None:
            # print("terminal condition satisfied, evaluation = ", self.evaluateMove(state, color))
            return self.evaluateMove(state, color, grow)

        if maxToMove:
            return self.maxValue(state, depth, color, alpha, beta)

        else:
            return self.minValue(state, depth, color, alpha, beta)

    def maxValue(
        self,
        state: "GameState",
        depth: int,
        color: PlayerColor,
        alpha: float,
        beta: float,
    ):
        highestOp = float("-inf")
        frogs = state.redFrogs if color == PlayerColor.RED else state.blueFrogs
        operators = (
            dict(
                sorted(
                    state.validMoves(PlayerColor.RED).items(),
                    key=lambda item: item[0][1],
                )
            )
            if color == PlayerColor.RED
            else dict(
                sorted(
                    state.validMoves(PlayerColor.BLUE).items(),
                    key=lambda item: item[0][1],
                )
            )
        )

        for r, c in frogs:
            for op in operators[(r, c)]:
                # print(f"Testing MAX: Operator of ({r},{c}) is ", op, " depth = ", depth)

                newState = state.copyState()
                if op == "Grow":
                    newState.grow(color)
                    grow = True
                else:
                    newState.move(color, Coord(r, c), op)
                    grow = False

                opValue = self.minimaxValue(
                    newState, depth - 1, False, color, alpha, beta, grow
                )
                if opValue > highestOp:
                    highestOp = opValue

                if opValue > alpha:
                    alpha = opValue

                if alpha >= beta:
                    return highestOp

        return highestOp

    def minValue(
        self,
        state: "GameState",
        depth: int,
        color: PlayerColor,
        alpha: float,
        beta: float,
    ):
        opponentColor = (
            PlayerColor.RED if color == PlayerColor.BLUE else PlayerColor.BLUE
        )
        lowestOp = float("inf")
        frogs = state.redFrogs if opponentColor == PlayerColor.RED else state.blueFrogs
        operators = (
            dict(
                sorted(
                    state.validMoves(PlayerColor.RED).items(),
                    key=lambda item: item[0][1],
                )
            )
            if opponentColor == PlayerColor.RED
            else dict(
                sorted(
                    state.validMoves(PlayerColor.BLUE).items(),
                    key=lambda item: item[0][1],
                )
            )
        )

        for r, c in frogs:
            for op in operators[(r, c)]:
                # print(f"Testing MIN: Operator of ({r},{c}) is ", op ," depth = ", depth)

                newState = state.copyState()
                if op == "Grow":
                    newState.grow(opponentColor)
                    grow = True
                else:
                    newState.move(opponentColor, Coord(r, c), op)
                    grow = False

                opValue = self.minimaxValue(
                    newState, depth - 1, True, color, alpha, beta, grow
                )
                if opValue < lowestOp:
                    lowestOp = opValue

                if opValue < beta:
                    beta = opValue

                if beta <= alpha:
                    return lowestOp

        return lowestOp

    def evaluateMove(self, state: "GameState", color: PlayerColor, grow: bool):
        evaluationScore = 0
        frogs = state.redFrogs if color == PlayerColor.RED else state.blueFrogs
        opponentColor = (
            PlayerColor.BLUE if color == PlayerColor.RED else PlayerColor.RED
        )
        opponentFrogs = state.blueFrogs if color == PlayerColor.RED else state.redFrogs

        # Reward the player for setting up jump chains
        evaluationScore += 5 * (self.countJumpChains(state, color))

        # Penalise the player for setting up opponent's jump chains
        # evaluationScore -= 5 * (self.countJumpChains(state, opponentColor))

        # Reward a grow move for the amount of pads created
        if grow:
            evaluationScore += 0.5 * len(
                [cell for cell in state.board.values() if cell["state"] == "pad"]
            )
        # else:
        # Slight penalty for growing to avoid excessive stalling
        evaluationScore -= 0.5 * len(
            [cell for cell in state.board.values() if cell["state"] == "pad"]
        )

        # Reward the player for moving frogs closer to the end, while giving priority to the frogs that are already closer to the beginning

        for r, c in frogs:
            multiplier = 1
            if (color == PlayerColor.RED and r <= 2) or (
                color == PlayerColor.BLUE and r >= 5
            ):
                multiplier = 1.5

            evaluationScore += (
                (r * 12 * multiplier)
                if color == PlayerColor.RED
                else ((7 - r) * 12 * multiplier)
            )

        # Penalise opponent's progress
        for r, c in opponentFrogs:
            evaluationScore -= (r * 10) if color == PlayerColor.BLUE else ((7 - r) * 10)

        # Reward the move that leads to the winning state
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
