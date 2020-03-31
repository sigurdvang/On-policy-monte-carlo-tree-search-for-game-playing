from boards import DiamondBoard
import random
import matplotlib.pyplot as plt

class Game:

    def __init__(self, verbose):
        self.winning_player = None
        self.verbose = verbose
        self.is_frozen = False

    def should_print_verbose(self):
        return ( (not self.is_frozen) and self.verbose)

    def has_won(self, player):
        return self.winning_player == player

    def anet_index_to_action_map(self):
        raise NotImplementedError("Subclass with game specific method")

    def get_illegal_action_pruner(self):
        raise NotImplementedError("Subclass with game specific method")

class Hex(Game):

    def __init__(self, verbose, k):
        super().__init__(verbose)
        self.board = DiamondBoard(k)

        if self.should_print_verbose():
            self.board.display_board()

    def get_state(self):
        return self.board.get_state()

    def set_state(self, state):
        self.board.set_state(state)

    def set_winning_player_if_exists(self, player):
        if player == 1:
            for i in range(self.board.size):
                if self.has_path_to_goal(i, 0, player):
                    self.winning_player = player
                    break
        else:
            for i in range(self.board.size):
                if self.has_path_to_goal(0, i, player):
                    self.winning_player = player
                    break

    
    def has_path_to_goal(self, i, j, player, current_path=None):
        #if the path ends here
        piece = self.board.board[i][j]
        if piece.has_peg != player:
            return False

        if current_path == None:
            current_path = [piece.position]
        else:
            current_path.append(piece.position)

        #if goal is reached
        if player == 1 and piece.position[1] == self.board.size - 1:
            return True
        if player == 2 and piece.position[0] == (self.board.size -1):
            return True

        #iterate over neighbours to see if they lead to goal state
        for direction in piece.neighbours:
            neigh_pos = piece.neighbours[direction].position
            if neigh_pos in current_path:
                continue
            n_i, n_j = neigh_pos
            if self.has_path_to_goal(n_i, n_j, player, current_path.copy()):
                return True

        return False


    def reset_game(self):
        self.board.reset_to_initial_state()
        self.winning_player = None
        self.is_frozen = False

    def is_game_over(self):
        return True if self.has_won(1) or self.has_won(2) else False

    def get_possible_actions(self):
        return self.board.find_possible_moves()

    def perform_action(self, action, player):
        self.board.make_move(action, player)
        self.set_winning_player_if_exists(player)

        if self.should_print_verbose():
            self.board.display_board()

    def print_start_board(self, verbose):
        if verbose:
            self.board.display_board()

    def anet_index_to_action_map(self, anet_index):
        """
        maps index in anet output to correct index 
        on board
        """
        i = 0
        j = 0
        while anet_index - self.board.size >= 0:
            anet_index -= self.board.size
            i += 1
        while anet_index - 1 >= 0:
            anet_index -= 1
            j += 1
        return (i, j)

    def get_illegal_action_pruner(self, network_output):
        """
        removes states from output that allready exists
        """
        state = self.get_state()
        for i in range(network_output.shape[1]):
            if state[i] != "0":
                network_output[0, i] = 0.0
        return network_output

if __name__ == "__main__":
    h = Hex(True, 7)

    player = 1 
    while not h.is_game_over():
        actions = h.get_possible_actions()
        action = actions[random.randint(0, len(actions)-1)]
        h.perform_action(action, player)
        player = 1 if player == 2 else 2
    
    
    plt.show()