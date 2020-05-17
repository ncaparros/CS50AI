"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if board == initial_state:
        return X

    countX = 0
    countO = 0

    for i in range(3):
        for j in range(3):
            if board[i][j] == X:
                countX += 1
            elif board[i][j] == O:
                countO += 1

    if countO < countX:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()

    for i in range(0, 3):
        for j in range(0, 3):
            if board[i][j] == None and (i, j) not in actions:
                actions.add((i, j))

    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    board[action[0]][action[1]] = player(board)
    return board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if board[0].count(X) == 3 or board[1].count(X) == 3 or board[2].count(X) == 3:
        return X
    elif board[0].count(O) == 3 or board[1].count(O) == 3 or board[2].count(O) == 3:
        return O
    elif board[0][0] == X and board[0][1] == X and board[0][2] == X:
        return X
    elif board[1][0] == X and board[1][1] == X and board[1][2] == X:
        return X
    elif board[2][0] == X and board[2][1] == X and board[2][2] == X:
        return X
    elif board[0][0] == O and board[0][1] == O and board[0][2] == O:
        return O
    elif board[1][0] == O and board[1][1] == O and board[1][2] == O:
        return O
    elif board[2][0] == O and board[2][1] == O and board[2][2] == O:
        return O
    elif board[0][0] == X and board[1][1] == X and board[2][2] == X:
        return X
    elif board[0][2] == X and board[1][1] == X and board[2][0] == X:
        return X
    elif board[0][0] == O and board[1][1] == O and board[2][2] == O:
        return O
    elif board[0][2] == O and board[1][1] == O and board[2][0] == O:
        return O
    else:
        return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    for i in range(3):
        for j in range(3):
            if board[i][j] == None:
                return False
    
    return True
    


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    if player(board) == X:
        get_max(board)
    else:
        get_min(board)

def get_min(board):
    if terminal(board):
        return utility(board)

    possible_actions = actions(board)
    minValue = 100

    for action in possible_actions:
        minValue = min(minValue, get_max(result(board, action)))
    return minValue

def get_max(board):
    if terminal(board):
        return utility(board)

    possible_actions = actions(board)
    maxValue = -100

    for action in possible_actions:
        maxValue = max(maxValue, get_min(result(board, action)))
    return maxValue

