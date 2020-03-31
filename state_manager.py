from games import Game, Hex

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
               "state" : self.game.get_state(),
               "game_winning_player" : self.game.winning_player,
               "current_player" : self.current_player
            }
            self.rollout_mode = True
            self.game.is_frozen = True
        else:
            self.game.set_state(self.pre_rollout_state["state"])
            self.game.winning_player = self.pre_rollout_state["game_winning_player"]
            self.current_player = self.pre_rollout_state["current_player"]
            self.rollout_mode = False
            self.game.is_frozen = False
            self.pre_rollout_state = None

    def get_state(self):
        return self.game.get_state()

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
        return self.game.anet_index_to_action_map

    def get_illegal_action_pruner(self):
        return self.game.get_illegal_action_pruner

class StateManager_Hex(StateManager):

    def __init__(self, verbose, k):
        game = Hex(verbose, k)
        super().__init__(game)
        self.init_state = game.get_state()
