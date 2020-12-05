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
from abc import ABC, abstractmethod

_TTTB = namedtuple("TicTacToeBoard", "tup turn winner terminal")

# Inheriting from a namedtuple is convenient because it makes the class
# immutable and predefines __init__, __repr__, __hash__, __eq__, and others
class ReversiState(_TTTB, Node):
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
                if board.tup[i][j] is None:
                    new = board.make_move(i, j)
                    if new is not None:
                        children.add(new)
        return children

    def find_random_child(board):
        if board.terminal:
            return None  # If the game is finished then no moves can be made
        empty_spots = [i for i, value in enumerate(board.tup) if value is None]
        #return board.make_move(choice(empty_spots))
        children = board.find_children()
        if children:
            return sample(children, 1)[0]
        return ReversiState(board.tup, not board.turn, board.winner, board.terminal)
        #print('==============\n',children)
        #print('==============\n', board)
        #raise Exception("I'm s'posed to pass.")

    def reward(board):
        #if not board.terminal:
        #   raise RuntimeError(f"reward called on nonterminal board {board}")
        #if board.winner is board.turn:
        #    # It's your turn and you've already won. Should be impossible.
        #    #raise RuntimeError(f"reward called on unreachable board {board}")
        #    return 1
        #if board.turn is (not board.winner):
        #    return 0  # Your opponent has just won. Bad.
        #if board.winner is None:
        #    return 0.5  # Board is a tie
        ## The winner is neither True, False, nor None
        #raise RuntimeError(f"board has unknown winner type {board.winner}")
        count = [0, 0]
        for i in range(8):
            for j in range(8):
                #if board.tup[i][j] is None: return None  # not finished yet
                if not board.tup[i][j] is None:
                    count[board.tup[i][j]] += 1 
        return count[1] - count[0]   # True needs to get more

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
        return ReversiState(new, turn, winner, is_terminal) if valid else None

    def __str__(board):
        to_char = lambda v: ("X" if v is True else ("O" if v is False else " "))
        return (
            "\n  0 1 2 3 4 5 6 7 \n"
            + "\n".join(str(i) + " " + " ".join(map(to_char, row)) for i, row in enumerate(board.tup))
            + "\n"
        )

    def __repr__(board):
        to_char = lambda v: ("T" if v is True else ("F" if v is False else " "))
        return (
            "\n  0 1 2 3 4 5 6 7 \n"
            + "\n".join(str(i) + " " + " ".join(map(to_char, row)) for i, row in enumerate(board.tup))
            + "\n"
            + f'turn={board.turn} winner={board.winner} terminal={board.terminal}\n\n'
        )


class AI:
    def __init__(self, name:str):
        self.name:str = name

    @abstractmethod
    def play(self, board:ReversiState) -> ReversiState: pass

class MCTSAI(AI):
    tree = MCTS()
    def __init__(self, name:str, nRollout:int=5):
        self.nRollout:int = nRollout
        super().__init__(name)

    def play(self, board: ReversiState):
        for _ in range(self.nRollout): self.tree.do_rollout(board)
        return self.tree.choose(board)

class Human(AI):
    def play(self, board: ReversiState):
        invalid = True
        while invalid:
            invalid = False
            row_col = input("enter row,col: ")
            try:
                row, col = map(int, row_col.split(","))
            except ValueError:
                print('\tplease enter 2 comma-separated numbers')
                invalid = True
                continue
            if row<0 or row>=8 or col<0 or col>=8 or board.tup[row][col] is not None: 
                print('\tcell must be empty')
                invalid = True
                continue
            board_ = board.make_move(row, col)
            if board_ is None:
                print('\tsomething must flip')
                invalid = True
        return board_

class Greedy(AI):
    def play(self, board: ReversiState):
        children = list(board.find_children())
        children.sort(reverse=board.turn, key=lambda board: board.reward())
        #print(*[(child, child.reward()) for child in children])
        return children[0]

def play_game(agentX=Human("Player X"), agentO=Human("Player O"), noisy:bool=True):
    global board
    board = new_reversi_state()
    if noisy: print(board)
    passX = passO = False
    while not(passX and passO):
        # X's turn
        if board.find_children():
            passX = False
            board = agentX.play(board)
            if noisy: print(board)
        else:
            passX = True
            board = ReversiState(board.tup, not board.turn, board.winner, board.terminal)
            if noisy: print(f"{agentX.name} has to pass, it's your turn\n")
        if board.terminal:
            break

        # O's turn
        if board.find_children():
            passO = False
            board = agentO.play(board)
            if noisy: print(board)
        else:
            passO = True
            board = ReversiState(board.tup, not board.turn, board.winner, board.terminal)
            if noisy: print(f"{agentO.name} has to pass, it's your turn\n")
        if board.terminal:
            break

    O = sum(1 for row in board.tup for cell in row if cell is False)
    X = sum(1 for row in board.tup for cell in row if cell is True)
    if noisy:
        print(f"X has {X:2d} points")
        print(f"O has {O:2d} points")
        print(f"{'X' if X>O else 'O'} won by {abs(X-O)} points!")
    return X-O


def _find_winner(tup):
    count = [0, 0]
    for i in range(8):
        for j in range(8):
            if tup[i][j] is None: return None  # not finished yet
            count[tup[i][j]] += 1 
    return count[1] > count[0]   # True needs to get more


def new_reversi_state():
    tup = [[None for j in range(8)] for i in range(8)]
    tup[3][3] = tup[4][4] = True
    tup[3][4] = tup[4][3] = False
    tup = tuple(tuple(row) for row in tup)
    return ReversiState(tup=tup,
                        turn=True, winner=None, terminal=False)


if __name__ == "__main__":
    play_game(MCTSAI("Bot X"), Greedy("Bot O"))
