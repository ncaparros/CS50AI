"""
Tic Tac Toe Player
"""

import math
import copy

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
    copied_board = copy.deepcopy(board)
    if board[action[0]][action[1]] != None:
        raise NameError('This cell has already been played !')

    copied_board[action[0]][action[1]] = player(copied_board)
    return copied_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check for winning row
    if board[0].count(X) == 3 or board[1].count(X) == 3 or board[2].count(X) == 3:
        return X
    elif board[0].count(O) == 3 or board[1].count(O) == 3 or board[2].count(O) == 3:
        return O

    # check for winning column
    for i in range(3):
        if board[0][i] == X and board[1][i] == X and board[2][i] == X:
            return X
        elif board[0][i] == O and board[1][i] == O and board[2][i] == O:
            return O

    # check for winning diagonal
    if board[0][0] == X and board[1][1] == X and board[2][2] == X:
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
    if winner(board) != None:
        return True

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

    possible_actions = actions(board)
    if player(board) == X:
        maxValue = -200
        for action in possible_actions:
            # move to be analyzed
            move = result(board, action)
            score = get_min(move)
            # if X winner, return that move
            if score == 1:
                return (action[0], action[1])
            # else, will return a move to tie
            if maxValue < score:
                best_move = (action[0], action[1])
                maxValue = score
    else:
        minValue = 200
        for action in possible_actions:
            move = result(board, action)
            score = get_max(move)
            # if O winner, return that move
            if score == -1:
                return (action[0], action[1])
            # else, will return a move to tie
            if minValue > score:
                best_move = (action[0], action[1])
                minValue = score

    return best_move

# recursively get the minimized score


def get_min(board):
    if terminal(board):
        return utility(board)

    possible_actions = actions(board)
    minValue = 100

    for action in possible_actions:
        minValue = min(minValue, get_max(result(board, action)))
    return minValue

# recursively get the maximized score


def get_max(board):
    if terminal(board):
        return utility(board)

    possible_actions = actions(board)
    maxValue = -100

    for action in possible_actions:
        maxValue = max(maxValue, get_min(result(board, action)))
    return maxValue

