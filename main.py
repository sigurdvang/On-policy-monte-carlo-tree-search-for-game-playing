from tree import Node
from state_manager import *
from mcts import Mcts
from utils import *

def main():
    config = Config("configs/config.txt")
    state_manager = init_state_manager(config)
    actor = init_actor(config, state_manager.get_vec_to_action_map(), state_manager.get_illegal_action_pruner())

    player_1_wins = 0
    #play game G times
    for game_nr in range(config.G):
        state_manager.current_player = choose_start_player(config.start_player)
        print("--> playig game nr: {} with start_player {}".format(game_nr + 1, state_manager.current_player))
        state_manager.print_start_board(config.verbose)
        mc = Mcts(state_manager, actor)
        mc.tree_search(config.m)
        if state_manager.has_won(1):
            player_1_wins += 1
            print("----> player 1 wins")
        else:
            print("----> player 2 wins")

        state_manager.reset_state()

    win_percentage = (player_1_wins / config.G) * 100
    print("player 1 wins: {} of {} games ({}%)".format(player_1_wins, config.G, win_percentage))

if __name__ == '__main__':
    main()
