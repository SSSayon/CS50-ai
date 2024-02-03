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
    numX = numO = 0
    for row in board:
        for item in row:
            if item == X:
                numX += 1
            elif item == O:
                numO += 1
    if numX > numO:
        return O
    return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    ret = []
    for i in range(3):
        for j in range(3):
            if board[i][j] is EMPTY:
                ret.append((i, j))
    return set(ret)


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if board[action[0]][action[1]] is not EMPTY:
        raise Exception
    if not (action[0] in [0, 1, 2] and action[1] in [0, 1, 2]):
        raise Exception

    new_board = copy.deepcopy(board)
    new_board[action[0]][action[1]] = player(new_board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if board[1][1] is not EMPTY:
        player = board[1][1]
        if board[0][0] == player and board[2][2] == player:
            return player
        if board[0][2] == player and board[2][0] == player:
            return player
        if board[1][0] == player and board[1][2] == player:
            return player
        if board[0][1] == player and board[2][1] == player:
            return player
    if board[0][0] is not EMPTY:
        player = board[0][0]
        if board[0][1] == player and board[0][2] == player:
            return player
        if board[1][0] == player and board[2][0] == player:
            return player  
    if board[2][2] is not EMPTY:
        player = board[2][2]
        if board[0][2] == player and board[1][2] == player:
            return player
        if board[2][0] == player and board[2][1] == player:
            return player      

    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    
    num = 0
    for row in board:
        for item in row:
            if item is not EMPTY:
                num += 1
    if num == 9:
        return True
    
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win == X:
        return 1
    if win == O:
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    
    def maxValue(_board, curr_min):
        curr_max = -1
        curr_action = None
        _actions = actions(_board)
        for _action in _actions:

            __board = result(_board, _action)
            if terminal(__board):
                action_val = utility(__board)
            else:
                action_val = minValue(__board, curr_max)[0]

            if action_val > curr_min:
                return (1, None)
            if action_val > curr_max:
                curr_max = action_val
                curr_action = _action

        return (curr_max, curr_action)

    def minValue(_board, curr_max):
        curr_min = 1
        curr_action = None
        _actions = actions(_board)
        for _action in _actions:

            __board = result(_board, _action)
            if terminal(__board):
                action_val = utility(__board) 
            else:
                action_val = maxValue(__board, curr_min)[0]

            if action_val < curr_max:
                return (-1, None)
            if action_val < curr_min:
                curr_min = action_val
                curr_action = _action

        return (curr_min, curr_action)

    _player = player(board)
    if _player == X:
        return maxValue(board, 1)[1]
    return minValue(board, -1)[1]


# if __name__ == "__main__":
#     board = initial_state()
#     board = result(board, (2, 0))
#     board = result(board, (1, 1))
#     board = result(board, (2, 1))
#     board = result(board, (2, 2))
#     board = result(board, (0, 0))
#     board = result(board, (0, 1))
#     board = result(board, (0, 2))
#     board = result(board, (1, 0))
#     print(minimax(board))