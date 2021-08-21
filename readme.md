# clue solver

I was thinking about information theory and this is what resulted. In clue, the central play is centered around information management; getting as much and concealing as much as possible. There are 1/6 * 1/6 * 1/9 options, or 1/324, and depending on the number and kind of cards you receive, your initial number of states can be as much as 200 (or as little as...?). An optimal strategy involves using every possible piece of information to win (including, if you're my sister, stealing cards that are shown to me by seeing where people mark clues on their sheet. cheater.). Many search techniques don't work because there's no ordering. I googled a bit and decided on constraint solvers.

I didn't want to deal with board movement, so I just assumed that it averages out. There are probably optimal board search strategies as well as guess strategies.

It works like this:

# TODO seed

```
>>> import clue
>>> import itertools
>>> nogoodplayer = itertools.cycle([clue.SimpleConstraintAIPlayer])
>>> clue.run_experiment(n_runs=1000, n_real_players=0, n_players=3, aiplayer=nogoodplayer)
{'n_real_players': 0, 'n_players': 3, 'aiplayer': <itertools.cycle object at 0x000001E4DB67A3B8>}
1000 runs in 8.0968759059906 average =  0.0080968759059906
Average Turns:  39.887
Wins: {'0': 318, '2': 320, '1': 362}
({'0': 318, '2': 320, '1': 362}, 39.887)

```