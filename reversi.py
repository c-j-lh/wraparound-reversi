"""
Wraparound reversi with MCTS.

If you run this file then you can play against the computer.

A tic-tac-toe board is represented as a tuple of 9 values, each either None,
True, or False, respectively meaning 'empty', 'X', and 'O'.

The board is indexed by row:
0 1 2
3 4 5
6 7 8

For example, this game board
O - X
O X -
X - -
corrresponds to this tuple:
(False, None, True, False, True, None, True, None, None)
"""

from collections import namedtuple
from random import choice, sample
from copy import deepcopy
from monte_carlo_tree_search import MCTS, Node

_TTTB = namedtuple("TicTacToeBoard", "tup turn winner terminal")

# Inheriting from a namedtuple is convenient because it makes the class
# immutable and predefines __init__, __repr__, __hash__, __eq__, and others
class TicTacToeBoard(_TTTB, Node):
    def find_children(board):
        #if board.terminal:  # If the game is finished then no moves can be made
        #    return set()
        ## Otherwise, you can make a move in each of the empty spots
        #return {
        #    board.make_move(i) for i, value in enumerate(board.tup) if value is None
        #}
        children = set()
        for i in range(8):
            for j in range(8):
               new = board.make_move(i, j)
               if new is not None:
                   children.add(new)
        return children

    def find_random_child(board):
        if board.terminal:
            return None  # If the game is finished then no moves can be made
        empty_spots = [i for i, value in enumerate(board.tup) if value is None]
        #return board.make_move(choice(empty_spots))
        return sample(board.find_children(), 1)[0]

    def reward(board):
        if not board.terminal:
           raise RuntimeError(f"reward called on nonterminal board {board}")
        if board.winner is board.turn:
            # It's your turn and you've already won. Should be impossible.
            #raise RuntimeError(f"reward called on unreachable board {board}")
            return 1
        if board.turn is (not board.winner):
            return 0  # Your opponent has just won. Bad.
        if board.winner is None:
            return 0.5  # Board is a tie
        # The winner is neither True, False, nor None
        raise RuntimeError(f"board has unknown winner type {board.winner}")

    def is_terminal(board):
        return board.terminal

    def make_move(board, i, j):
        new = [list(row) for row in board.tup]
        new[i][j] = board.turn
        valid = False

        for sign in (-1, 1):
            for jj in range(j+1*sign, j+9*sign, sign):
                if new[i][jj%8] != (not board.turn):
                    if new[i][jj%8] == board.turn:
                        for jjj in range(j+1*sign, jj, sign):
                            valid = True
                            new[i][jjj%8] = board.turn
                    break

        for sign in (-1, 1):
            for ii in range(i+1*sign, i+9*sign, sign):
                if new[ii%8][j] != (not board.turn):
                    if new[ii%8][j] == board.turn:
                        for iii in range(i+1*sign, ii, sign):
                            valid = True
                            new[iii%8][j] = board.turn
                    break

        for dsign in (-1, 1):
            for sign in (-1, 1):
                for h in range(1*sign, 9*sign, sign):
                    if new[(i+h)%8][(j+h*dsign)%8] != (not board.turn):
                        if new[(i+h)%8][(j+h*dsign)%8] == board.turn:
                            for hh in range(1*sign, h, sign):
                                valid = True
                                new[(i+hh)%8][(j+hh*dsign)%8] = board.turn
                        break

        turn = not board.turn
        winner = _find_winner(new)
        is_terminal = winner is not None
        new = tuple(tuple(row) for row in new)
        return TicTacToeBoard(new, turn, winner, is_terminal) if valid else None

    def __str__(board):
        to_char = lambda v: ("X" if v is True else ("O" if v is False else " "))
        return (
            "\n  0 1 2 3 4 5 6 7 \n"
            + "\n".join(str(i) + " " + " ".join(map(to_char, row)) for i, row in enumerate(board.tup))
            + "\n"
        )

    def __repr__(board):
        to_char = lambda v: ("X" if v is True else ("O" if v is False else " "))
        return (
            "\n  0 1 2 3 4 5 6 7 \n"
            + "\n".join(str(i) + " " + " ".join(map(to_char, row)) for i, row in enumerate(board.tup))
            + "\n"
            + f'turn={board.turn} winner={board.winner} terminal={board.terminal}\n\n'
        )


def play_game():
    global board
    print("(You are X)")
    tree = MCTS()
    board = new_tic_tac_toe_board()
    print(board)
    while True:
        row_col = input("enter row,col: ")
        row, col = map(int, row_col.split(","))
        if row<0 or row>=8 or col<0 or col>=8 or board.tup[row][col] is not None: raise RuntimeError("Invalid move")
        board = board.make_move(row, col)
        if board is None:
            raise RuntimeError("Nothing to flip")
        print(board)
        if board.terminal:
            break
        # You can train as you go, or only at the beginning.
        # Here, we train as we go, doing fifty rollouts each turn.
        for _ in range(5):
            tree.do_rollout(board)
        board = tree.choose(board)
        print(board)
        if board.terminal:
            break


#def _winning_combos():
#    for start in range(0, 9, 3):  # three in a row
#        yield (start, start + 1, start + 2)
#    for start in range(3):  # three in a column
#        yield (start, start + 3, start + 6)
#    yield (0, 4, 8)  # down-right diagonal
#    yield (2, 4, 6)  # down-left diagonal


def _find_winner(tup):
    count = [0, 0]
    for i in range(8):
        for j in range(8):
            if tup[i][j] is None: return None  # not finished yet
            count[tup[i][j]] += 1 
    return count[1] > count[0]   # True needs to get more


def new_tic_tac_toe_board():
    tup = [[None for j in range(8)] for i in range(8)]
    tup[3][3] = tup[4][4] = True
    tup[3][4] = tup[4][3] = False
    tup = [list(row) for row in tup]
    return TicTacToeBoard(tup=tup,
                          turn=True, winner=None, terminal=False)


if __name__ == "__main__":
    play_game()
