# wraparound-reversi
The computer plays using a very naively applied MCTS (Monte Carlo Tree Search) from https://gist.github.com/qpwo/c538c6f73727e254fdc7fab81024f6e1.

Wraparound reversi is where the board sorta wraps around.

![wraps around](https://raw.githubusercontent.com/c-j-lh/wraparound-reversi/master/sample.jpg)

For example, above, X plays at (row, column) = (7,0), flipping (0,1) using the diagonal line (7,0) <--> (0,1) <--> (1,2) <--> ...

Run reversi.py to play.

