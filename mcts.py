from state_manager import *
from tree import Node
from state_manager import StateManager
from actor import Actor
from tqdm import trange
from utils import ReplayBuffer

class Mcts:
    """
    Handles the monte-carlo tree search
    """

    def __init__(self, state_manager : StateManager, actor : Actor):
        self.state_manager = state_manager
        #pool of active nodes
        self.node_pool = None
        #ANET
        self.actor = actor
        #buffer
        self.replay_buffer = ReplayBuffer(self.state_manager.tree_distribution_converter)


    def get_lookup_state(self, state):
        """
        Transfomrms a state into a tuple that can be used 
        to look up in the node pool
        """
        return "".join(map(str, state))

    def add_to_pool(self, node : Node):
        lookup_state = self.get_lookup_state(node.state)
        self.node_pool[lookup_state] = node

    def pool_contains(self, state):
        return state in self.node_pool

    def store_case(self,lookup_state):
        distribution = self.node_pool[lookup_state].get_distribution()
        self.replay_buffer.add_case(self.node_pool[lookup_state].state, distribution)

    def train_anet(self):
        mini_batch = self.replay_buffer.generate_minibatch(500)
        x, y = mini_batch
        self.actor.train(x, y)

    def tree_search(self, m):
        current_state = self.state_manager.produce_init_game_state()
        possible_actions = self.state_manager.get_possible_actions()
        #creates the root node
        self.node_pool = {}
        self.add_to_pool(Node(state=current_state, possible_actions=possible_actions))
        #play game until finished
        while not self.state_manager.game_over():
            lookup_state = self.get_lookup_state(current_state)
            self.simulate(lookup_state, m)
            performed_action = self.make_move(lookup_state, is_rollout=False,greedy=True)
            #store case to later train default policy
            self.store_case(lookup_state)
            current_state = self.node_pool[lookup_state].children[performed_action].state
        #train default policy after game
        self.train_anet()
    
    
    def simulate(self, start_state, m):
        for _ in trange(m, desc="tree simulation"):
            self.state_manager.toggle_simulation_mode()
            trace, post_sim_state = self.simulate_tree(start_state)
            z = self.rollout(post_sim_state)
            self.backpropegate(trace, z)
            self.state_manager.toggle_simulation_mode()
            
    def simulate_tree(self, current_state):
        """
        Simulate game with tree policy until reaching a leaf node
        """
        sim_trace = [(current_state, None)]
        while not self.state_manager.game_over():
            performed_action = self.make_move(current_state, is_rollout=False)
            current_state, subtree_existed_prev = self.get_child(current_state, performed_action)
            sim_trace.append((current_state, performed_action))
            #the case where one has reached a leaf node
            if subtree_existed_prev == False:
                break
        return sim_trace, current_state

    def rollout(self, current_state):
        """
        rollout from leaf node to evaluate its value.
        return result of game
        """
        while not self.state_manager.game_over():
            performed_action = self.make_move(current_state, is_rollout=True)
            current_state, _ = self.get_child(current_state, performed_action)
        reward = self.get_reward()
        return reward

    def make_move(self, current_state, is_rollout, greedy=False):
        #first, increment visit count of current node
        self.node_pool[current_state].increment_node_visits()

        if is_rollout:
            action = self.node_pool[current_state].get_rollout_action(self.actor)
        else:
            action = self.node_pool[current_state].get_best_action(self.state_manager.current_player, greedy)
    
        self.state_manager.perform_action(action)
        return action

    def get_child(self, state, action):
        #if node is not in child dictionary...
        if self.node_pool[state].children[action] == None:
            new_state = self.state_manager.get_state()
            new_state_lookup = self.get_lookup_state(new_state)
            #...retrieve node from node pool if it exists...
            if self.pool_contains(new_state_lookup):
                self.node_pool[state].children[action] = self.node_pool[new_state_lookup]
            #...if not create the node 
            else:
                possible_actions_from_new_state = self.state_manager.get_possible_actions()
                self.add_to_pool(Node(new_state, possible_actions_from_new_state))
                self.node_pool[state].children[action] = self.node_pool[new_state_lookup]

            return new_state_lookup, False

        lookup_state = self.get_lookup_state(self.node_pool[state].children[action].state)
        return lookup_state, True
    
    def get_reward(self):
        if self.state_manager.has_won(1):
            return 1
        return -1

    def backpropegate(self, trace, reward):
        """
        Backpropegate through the nodes and edges traversed 
        on a given simulation
        """
        for i in range(len(trace)-1, 0, -1):
            action = trace[i][1]
            state = trace[i-1][0]
            self.node_pool[state].backprop(action, reward)