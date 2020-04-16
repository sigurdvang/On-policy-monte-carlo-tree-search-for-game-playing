from games import Game, Hex
import numpy as np

class StateManager:
    """
    Manages states of games and moving between them.
    Can be subclassed to be adapted to any game
    """

    def __init__(self, game : Game):
        self.game = game
        self.init_state = None
        self.rollout_mode = False
        self.pre_rollout_state = None
        self.current_player = None

    def print_start_board(self, verbose):
        self.game.print_start_board(verbose)

    def produce_init_game_state(self):
        self.init_state = self.get_state()
        return self.init_state

    def has_won(self, player):
        return self.game.has_won(player)

    def game_over(self):
        if self.has_won(1) or self.has_won(2):
            return True
        return False

    def toggle_player(self):
        self.current_player = 1 if self.current_player == 2 else 2

    def toggle_simulation_mode(self):
        """
        Freezes state and returns to it after simulation has ended
        """
        if self.rollout_mode == False:
            self.pre_rollout_state = {
               "state" : self.get_state(),
               "game_winning_player" : self.game.winning_player,
               "current_player" : self.current_player
            }
            self.rollout_mode = True
            self.game.is_frozen = True
        else:
            self.set_state(self.pre_rollout_state["state"])
            self.game.winning_player = self.pre_rollout_state["game_winning_player"]
            self.current_player = self.pre_rollout_state["current_player"]
            self.rollout_mode = False
            self.game.is_frozen = False
            self.pre_rollout_state = None

    def get_state(self):
        return [self.current_player] + self.game.get_state()
    
    def set_state(self, state):
        self.game.set_state(state[1:])

    def reset_state(self):
        self.game.reset_game()
        self.rollout_mode = False
        self.pre_rollout_state = None

    def get_possible_actions(self):
        return self.game.get_possible_actions()

    def perform_action(self, action):
        self.game.perform_action(action, self.current_player)
        self.toggle_player()

    def get_vec_to_action_map(self):
        raise NotImplementedError("Subclass with game specific method")

    def get_illegal_action_pruner(self):
        raise NotImplementedError("Subclass with game specific method")

    def tree_distribution_converter(self):
        raise NotImplementedError("Subclass with game specific method")

class StateManager_Hex(StateManager):

    def __init__(self, verbose, k):
        game = Hex(verbose, k)
        super().__init__(game)

    def get_vec_to_action_map(self):
        """
        maps index in anet output to correct index 
        on board
        """
        i = 0
        map = {} 
        for row in self.game.board.board:
            for cell in row:
                map[i] = cell.position
                i += 1
        return map

    def map_action_to_vec(self, action):
        i, j = action
        return (i * self.game.board.size) + j


    def get_illegal_action_pruner(self, network_output, vec_to_action_map):
        """
        removes states from output that allready exists
        """
        max_arg = 0
        cur_max_val = float("-inf")
        abs_max_val = network_output.max()
        state = self.game.board.get_state()
        for i in range(network_output.shape[1]):
            if state[i] == 0:
               if network_output[0, i] > abs_max_val:
                   max_arg = i
                   break
               elif network_output[0, i] > cur_max_val:
                   max_arg = i
                   cur_max_val = network_output[0, i]
        return vec_to_action_map[max_arg]

    def tree_distribution_converter(self, distribution):
        k = self.game.board.size
        state_distribution = np.zeros(shape=(k*k,))
        for action in distribution:
            state_distribution[self.map_action_to_vec(action)] = distribution[action]
        return state_distribution
        