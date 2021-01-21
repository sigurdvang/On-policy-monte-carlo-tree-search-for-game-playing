# On-policy-monte-carlo-tree-search-for-game-playing

This repository contains an implementation of the monte carlo tree search (MCTS) algorithm, most famously seen in DeepMind architectures such as AlphaZero. 
It is implemented in an object oriented manner with a clean seperation between the MCTS algorithm itself, the state manager, from which the MCTS algorithm queries game states,
and the games (currently only one game) that it can solve. This seperation makes the implementation general and allows for one to add various other two player games for the
system to solve. 
