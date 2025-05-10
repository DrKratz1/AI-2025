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

    
        #print(self.game)

    
    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object.
        """
        print("Testing: Action has been called")        
        #print(self.game)

        redValidMoves = dict(sorted(self.game.validMoves(PlayerColor.RED).items(), key=lambda item: item[0][1]))
        blueValidMoves = dict(sorted(self.game.validMoves(PlayerColor.BLUE).items(), key=lambda item: item[0][1]))

        #print(redValidMoves[(0, 2)])

        
        if self._color == PlayerColor.RED:
            frogTomove, bestAction = self.minimaxDecision(self.game, 4, True, redValidMoves, self._color)
            print("time to move frog at ", frogTomove, " with operator ", bestAction)
        else:
            frogTomove, bestAction = self.minimaxDecision(self.game, 4, True, blueValidMoves, self._color)


        match self._color:
            case PlayerColor.RED:
                frogToMove, bestAction = self.minimaxDecision(self.game, 4, True, redValidMoves, self._color)
                print("time to move frog at ", frogToMove, " with operator ", bestAction)

                if bestAction == "Grow":
                    return GrowAction()
                else:
                    return MoveAction(Coord(frogToMove[0], frogToMove[1]), bestAction)

            case PlayerColor.BLUE:
                frogToMove, bestAction = self.minimaxDecision(self.game, 4, True, blueValidMoves, self._color)
                print("time to move frog at ", frogToMove, " with operator ", bestAction)

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
            case GrowAction():
                print(f"Testing: {color} played GROW action")

                self.game.grow(color)

            case _:
                raise ValueError(f"Unknown action type: {action}")
    
    def minimaxDecision(self, state: 'GameState', depth: int, maxToMove: bool, operators: list, color: PlayerColor):
        highestOp = float('-inf')
        frogs = state.redFrogs if color == PlayerColor.RED else state.blueFrogs
        alpha = float('-inf')
        beta = float('inf')

        for (r, c) in frogs:
            for op in operators[(r, c)]:
                depthValue = depth
                # For each frog, we check all of the valid moves they can make
                #print(f"Testing MAX: Operator of ({r},{c}) is ", op)
                
                newState = state.copyState()
                if op == "Grow":
                    newState.grow(color)
                else:
                    newState.move(color, Coord(r, c), op)
                #print(newState)

                opValue = self.minimaxValue(newState, depthValue - 1, not maxToMove, color, alpha, beta)
                #print(f"evaluationValue = {opValue}")

                if opValue > highestOp:
                    highestOp = opValue
                    frogToMove = (r, c)
                    bestAction = op

        print(f"Best move for {color} is to move frog at {frogToMove} with operator {bestAction} with value {highestOp}")
        return (frogToMove, bestAction)
    
    def minimaxValue(self, state: 'GameState', depth: int, maxToMove: bool, color: PlayerColor, alpha: float, beta: float):
        #print("depth = ", depth)
        if depth == 0 or state.checkWinner() is not None:
            #print("terminal condition satisfied, evaluation = ", self.evaluateMove(state, color))
            return self.evaluateMove(state, color)

        if maxToMove:
            return self.maxValue(state, depth, color, alpha, beta)
        
        else:
            return self.minValue(state, depth, color, alpha, beta)
        
    def maxValue(self, state: 'GameState', depth: int, color: PlayerColor, alpha: float, beta: float):
        highestOp = float('-inf')
        frogs = state.redFrogs if color == PlayerColor.RED else state.blueFrogs
        operators = dict(sorted(state.validMoves(PlayerColor.RED).items(), key=lambda item: item[0][1])) if color == PlayerColor.RED else dict(sorted(state.validMoves(PlayerColor.BLUE).items(), key=lambda item: item[0][1]))

        for (r, c) in frogs:
            for op in operators[(r, c)]:
                #print(f"Testing MAX: Operator of ({r},{c}) is ", op, " depth = ", depth)
                
                newState = state.copyState()
                if op == "Grow":
                    newState.grow(color)
                else:
                    newState.move(color, Coord(r, c), op)
                
                opValue = self.minimaxValue(newState, depth - 1, False, color, alpha, beta)
                if opValue > highestOp:
                    highestOp = opValue

                if opValue > alpha:
                    alpha = opValue
                
                if alpha >= beta:
                    return highestOp

        return highestOp
    
    def minValue(self, state: 'GameState', depth: int, color: PlayerColor, alpha: float, beta: float):
        opponentColor = PlayerColor.RED if color == PlayerColor.BLUE else PlayerColor.BLUE
        lowestOp = float('inf')
        frogs = state.redFrogs if opponentColor == PlayerColor.RED else state.blueFrogs
        operators = dict(sorted(state.validMoves(PlayerColor.RED).items(), key=lambda item: item[0][1])) if opponentColor == PlayerColor.RED else dict(sorted(state.validMoves(PlayerColor.BLUE).items(), key=lambda item: item[0][1]))

        for (r, c) in frogs:
            for op in operators[(r, c)]:
                #print(f"Testing MIN: Operator of ({r},{c}) is ", op ," depth = ", depth)
                
                newState = state.copyState()
                if op == "Grow":
                    newState.grow(opponentColor)
                else:
                    newState.move(opponentColor, Coord(r, c), op)
                
                opValue = self.minimaxValue(newState, depth - 1, True, color, alpha, beta)
                if opValue < lowestOp:
                    lowestOp = opValue

                if opValue < beta:
                    beta = opValue
                
                if beta <= alpha:
                    return lowestOp
                
        return lowestOp

    def evaluateMove(self, state: 'GameState', color: PlayerColor):
        evaluationScore = 0

        if color == PlayerColor.RED:
            for (r, c) in state.redFrogs:
                evaluationScore += r

            for (r, c) in state.blueFrogs:
                evaluationScore -= 7 - r

        if color == PlayerColor.BLUE:     
            for (r, c) in state.blueFrogs:
                evaluationScore += 7 - r

            for (r, c) in state.redFrogs:
                evaluationScore -= r

        #print("Evaluating move: ", evaluationScore)

        return evaluationScore


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
        finalCoord = Coord(coord.r, coord.c)
        for direction in directions:
            if (finalCoord.r + direction.r, finalCoord.c + direction.c) in self.board:
                finalCoord = Coord(finalCoord.r + direction.r, finalCoord.c + direction.c)
            else:
                raise ValueError(f"Invalid move: {finalCoord} + {direction}")
        
        coord = (coord.r, coord.c)
        finalCoord = (finalCoord.r, finalCoord.c)

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
                                #print("testing jump: ", jumpResults[coord])
                                validMoves[frog].append(jumpResults[coord])
        return validMoves

    def DFS(
        self,
        frog: tuple[int, int],
        directions: list[Direction],
        result: list[list[Direction]],
        visited: list[tuple[int, int]],
    ):
        for dx, dy in directions:
            newR, newC = frog[0] + dx, frog[1] + dy
            if (newR, newC) in self.board:
                if self.board[(newR, newC)]["state"] not in [None, "pad"]:
                    newR, newC = newR + dx, newC + dy

                    if (newR, newC) in self.board:
                        if (
                            self.board[(newR, newC)]["state"] == "pad"
                            and (newR, newC) not in visited
                        ):
                            visited.append((newR, newC))

                            # do direction appending here
                            result[(newR, newC)] = []
                            if result[newR - 2 * dx, newC - 2 * dy] != []:
                                result[(newR, newC)] = result[
                                    newR - 2 * dx, newC - 2 * dy
                                ]
                            result[(newR, newC)].append(self.directionDict[(dx, dy)])
                            result[(newR, newC)].append(self.directionDict[(dx, dy)])
                            self.DFS((newR, newC), directions, result, visited)
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
