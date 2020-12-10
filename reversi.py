"""
Wraparound reversi with MCTS.

If you run this file then you can play against the computer.

A tic-tac-toe state is represented as a tuple of 9 values, each either None,
True, or False, respectively meaning 'empty', 'X', and 'O'.

The state is indexed by row:
0 1 2
3 4 5
6 7 8

For example, this game state
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

_TTTB = namedtuple("TicTacToeBoard", "board turn winner terminal")

# Inheriting from a namedtuple is convenient because it makes the class
# immutable and predefines __init__, __repr__, __hash__, __eq__, and others
class ReversiState(_TTTB, Node):
    def find_children(state):
        #if state.terminal:  # If the game is finished then no moves can be made
        #    return set()
        ## Otherwise, you can make a move in each of the empty spots
        #return {
        #    state.make_move(i) for i, value in enumerate(state.board) if value is None
        #}
        children = set()
        for i in range(8):
            for j in range(8):
                if state.board[i][j] is None:
                    new = state.make_move(i, j)
                    if new is not None:
                        children.add(new)
        return children

    def find_random_child(state):
        if state.terminal:
            return None  # If the game is finished then no moves can be made
        empty_spots = [i for i, value in enumerate(state.board) if value is None]
        #return state.make_move(choice(empty_spots))
        children = state.find_children()
        if children:
            return sample(children, 1)[0]
        return ReversiState(state.board, not state.turn, state.winner, state.terminal)
        #print('==============\n',children)
        #print('==============\n', state)
        #raise Exception("I'm s'posed to pass.")

    def reward(state):
        #if not state.terminal:
        #   raise RuntimeError(f"reward called on nonterminal state {state}")
        #if state.winner is state.turn:
        #    # It's your turn and you've already won. Should be impossible.
        #    #raise RuntimeError(f"reward called on unreachable state {state}")
        #    return 1
        #if state.turn is (not state.winner):
        #    return 0  # Your opponent has just won. Bad.
        #if state.winner is None:
        #    return 0.5  # Board is a tie
        ## The winner is neither True, False, nor None
        #raise RuntimeError(f"state has unknown winner type {state.winner}")
        count = [0, 0]
        for i in range(8):
            for j in range(8):
                #if state.board[i][j] is None: return None  # not finished yet
                if not state.board[i][j] is None:
                    count[state.board[i][j]] += 1 
        return count[1] - count[0]   # True needs to get more

    def is_terminal(state):
        return state.terminal

    def make_move(state, i, j):
        new = [list(row) for row in state.board]
        new[i][j] = state.turn
        valid = False

        for sign in (-1, 1):
            for jj in range(j+1*sign, j+9*sign, sign):
                if new[i][jj%8] != (not state.turn):
                    if new[i][jj%8] == state.turn:
                        for jjj in range(j+1*sign, jj, sign):
                            valid = True
                            new[i][jjj%8] = state.turn
                    break

        for sign in (-1, 1):
            for ii in range(i+1*sign, i+9*sign, sign):
                if new[ii%8][j] != (not state.turn):
                    if new[ii%8][j] == state.turn:
                        for iii in range(i+1*sign, ii, sign):
                            valid = True
                            new[iii%8][j] = state.turn
                    break

        for dsign in (-1, 1):
            for sign in (-1, 1):
                for h in range(1*sign, 9*sign, sign):
                    if new[(i+h)%8][(j+h*dsign)%8] != (not state.turn):
                        if new[(i+h)%8][(j+h*dsign)%8] == state.turn:
                            for hh in range(1*sign, h, sign):
                                valid = True
                                new[(i+hh)%8][(j+hh*dsign)%8] = state.turn
                        break

        turn = not state.turn
        winner = _find_winner(new)
        is_terminal = winner is not None
        new = tuple(tuple(row) for row in new)
        return ReversiState(new, turn, winner, is_terminal) if valid else None

    def __str__(state):
        to_char = lambda v: ("X" if v is True else ("O" if v is False else " "))
        return (
            "\n  0 1 2 3 4 5 6 7 \n"
            + "\n".join(str(i) + " " + " ".join(map(to_char, row)) for i, row in enumerate(state.board))
            + "\n"
        )

    def __repr__(state):
        to_char = lambda v: ("T" if v is True else ("F" if v is False else " "))
        return (
            "\n  0 1 2 3 4 5 6 7 \n"
            + "\n".join(str(i) + " " + " ".join(map(to_char, row)) for i, row in enumerate(state.board))
            + "\n"
            + f'turn={state.turn} winner={state.winner} terminal={state.terminal}\n\n'
        )


class AI:
    def __init__(self, name:str):
        self.name:str = name

    @abstractmethod
    def play(self, state:ReversiState) -> ReversiState: pass

class MCTSAI(AI):
    tree = MCTS()
    def __init__(self, name:str, nRollout:int=5):
        self.nRollout:int = nRollout
        super().__init__(name)

    def play(self, state: ReversiState):
        for _ in range(self.nRollout): self.tree.do_rollout(state)
        return self.tree.choose(state)

class Human(AI):
    def play(self, state: ReversiState):
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
            if row<0 or row>=8 or col<0 or col>=8 or state.board[row][col] is not None: 
                print('\tcell must be empty')
                invalid = True
                continue
            state_ = state.make_move(row, col)
            if state_ is None:
                print('\tsomething must flip')
                invalid = True
        return state_

class Greedy(AI):
    def play(self, state: ReversiState):
        children = list(state.find_children())
        children.sort(reverse=state.turn, key=lambda state: state.reward())
        #print(*[(child, child.reward()) for child in children])
        return children[0]

class Greedy2(AI):
    def play(self, state: ReversiState):
        children = [[[kid for kid in child.find_children()], child] for child in state.find_children()]
        for kids, child in children:
            kids.sort(reverse=not state.turn, key=lambda state: state.reward())
        children.sort(reverse=state.turn, key=lambda kids: kids[0][0].reward())
        #print(*[(child, child.reward()) for child in children])
        return children[0][1]

class Random(AI):
    def play(self, state: ReversiState):
        return state.find_random_child()

def play_game(agentX=Human("Player X"), agentO=Human("Player O"), noisy:bool=True):
    global state
    state = new_reversi_state()
    if noisy: print(state)
    passX = passO = False
<<<<<<< HEAD
=======
    history = [state]
    count = 0
>>>>>>> 4139b0540831901ee7d491c29e569419185154ca
    while not(passX and passO):
        # X's turn
        if state.find_children():
            passX = False
            state = agentX.play(state)
            if noisy: print(state)
        else:
            passX = True
            state = ReversiState(state.board, not state.turn, state.winner, state.terminal)
            if noisy: print(f"{agentX.name} has to pass, it's your turn\n")
        if state.terminal:
            break

        # O's turn
        if state.find_children():
            passO = False
            state = agentO.play(state)
            if noisy: print(state)
        else:
            passO = True
            state = ReversiState(state.board, not state.turn, state.winner, state.terminal)
            if noisy: print(f"{agentO.name} has to pass, it's your turn\n")
        if state.terminal:
            break
        count+=1

    O = sum(1 for row in state.board for cell in row if cell is False)
    X = sum(1 for row in state.board for cell in row if cell is True)
    if noisy:
        print(f"X has {X:2d} points")
        print(f"O has {O:2d} points")
        print(f"{'X' if X>O else 'O'} won by {abs(X-O)} points!")
    return X-O


def _find_winner(board):
    count = [0, 0]
    for i in range(8):
        for j in range(8):
            if board[i][j] is None: return None  # not finished yet
            count[board[i][j]] += 1 
    return count[1] > count[0]   # True needs to get more


def new_reversi_state():
    board = [[None for j in range(8)] for i in range(8)]
    board[3][3] = board[4][4] = True
    board[3][4] = board[4][3] = False
    board = tuple(tuple(row) for row in board)
    return ReversiState(board=board,
                        turn=True, winner=None, terminal=False)


if __name__ == "__main__":
    play_game(Greedy2("Bot X"), Greedy("Bot O"))
