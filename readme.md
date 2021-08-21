# clue solver

I was thinking about information theory and this is what resulted. In clue, the central play is centered around information management; getting as much and concealing as much as possible. There are 1/6 * 1/6 * 1/9 options, or 1/324, and depending on the number and kind of cards you receive, your initial number of states can be as much as 200 (or as little as...?). An optimal strategy involves using every possible piece of information to win (including, if you're my sister, stealing cards that are shown to me by seeing where people mark clues on their sheet. cheater.). Many search techniques don't work because there's no ordering. I googled a bit and decided on constraint solvers.

I didn't want to deal with board movement, so I just assumed that it averages out. There are probably optimal board search strategies as well as guess strategies.

It works like this:

```
>>> import clue
>>> import itertools
>>> nogoodplayer = itertools.cycle([clue.SimpleConstraintAIPlayer])
>>> onegoodplayer = itertools.cycle(
        [BetterConstraintAIPlayer, SimpleConstraintAIPlayer, SimpleConstraintAIPlayer])
>>> twogoodplayer = itertools.cycle([BetterConstraintAIPlayer, BetterConstraintAIPlayer, SimpleConstraintAIPlayer])
>>> clue.run_experiment(n_runs=1000, n_real_players=0, n_players=3, aiplayer=nogoodplayer, seed=0)
{'kwargs': {'n_real_players': 0, 'n_players': 3, 'aiplayer': <itertools.cycle object at 0x...>, 'seed': 0, 'n_runs': 1000}, 'avg_turns': 40.0, 'wins': {'0': 325, '1': 352, '2': 323}}
>>> clue.run_experiment(n_runs=1000, n_real_players=0, n_players=3, aiplayer=onegoodplayer, seed=0)
{'kwargs': {'n_real_players': 0, 'n_players': 3, 'aiplayer': <itertools.cycle object at 0x...>, 'seed': 0, 'n_runs': 1000}, 'avg_turns': 38.8, 'wins': {'1': 234, '2': 247, '0': 519}}
>>> run_experiment(n_runs=1000, n_real_players=0, n_players=3, aiplayer=twogoodplayer, seed=0)
{'kwargs': {'n_real_players': 0, 'n_players': 3, 'aiplayer': <itertools.cycle object at 0x...>, 'seed': 0, 'n_runs': 1000}, 'avg_turns': 38.1, 'wins': {'0': 421, '2': 188, '1': 391}}

```

Generally, it looks like having more "good" players shortens the game by a few turns, and confers approximately a 2:1 advantage to a good player.

I'm not sure what other strategies I can code. I think the next one would be to keep track of what cards have been shown to other players, then choose from those before showing a new card. That would reduce the amount of information being leaked. Another one might be to introduce probabilistic accusations, if there's ever a way to get more than 50% certainty. Another might be to start modeling not just the envelope, but the other players hands, although I'm not sure that actually adds information to the simulation. It might be able to tell you a better choice to guess at though, because you can guess solutions that other players haven't yet. 

Some things I'm not sure make sense here, but might if I were playing with human players, like paying attention to guessing patterns. Cards that humans use over and over might be cards in hand or cards in the envelope. Other human strategies that I've used include constructing suggestions where only 1 piece of information is being tested at a time, but I'm not sure of the efficacy of that strategy. Being shown a card is worth less than not being shown a card. Another human strategy might include 2nd-level deception, intentionally crafting suggestions to deceive other players.

Naively, if you test 1 card at a time, it would take you 6 + 6 + 9 = 21 turns, minus whatever cards you hold in your hand, which is (21 - 3) / n_players. Testing more than 1 card at a time tends to improve that, but it demands increased mental capability to keep track of things.

|                              |   BetterConstraintAIPlayerp1 |   RevealLessInfoAIPlayerp1 |   RevealLessInfoBetterAIPlayerp1 |   SimpleConstraintAIPlayerp1 |
|:-----------------------------|-----------------------------:|---------------------------:|---------------------------------:|-----------------------------:|
| BetterConstraintAIPlayer     |                   nan        |                   0.282051 |                          1.04082 |                     0.369863 |
| RevealLessInfoAIPlayer       |                     2.7037   |                 nan        |                          5.66667 |                     0.785714 |
| RevealLessInfoBetterAIPlayer |                     0.960784 |                   0.204819 |                        nan       |                     0.190476 |
| SimpleConstraintAIPlayer     |                     3.16667  |                   0.923077 |                          4.26316 |                   nan        |