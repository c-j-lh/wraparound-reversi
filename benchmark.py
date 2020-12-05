from tqdm import *
import matplotlib.pyplot as plt
import pandas as pd

from reversi import *

diffs = []
for i in trange(20):
    diff = play_game(Random("Bot X"), Greedy2("Bot O"), noisy=False)
    diffs.append(diff)
print(pd.DataFrame(diffs).describe())

## benchmark
# greedy 1 move
# greedy 3 move
# random
# pseudo_greedy 2 move? (human)
# 
