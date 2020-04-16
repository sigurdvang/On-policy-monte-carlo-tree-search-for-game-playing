import numpy as np
import math

class Node:
    """
    Object representing a tree node and its given connections.
    Any node serves as a subtree of the larger tree.
    """


    def __init__(self, state, possible_actions):
        self.state = state
        self.network_input = np.array([state])
        self.possible_actions = possible_actions
        self.children = self.build_edges_from_actions(possible_actions)
        self.visits = 0
        self.edge_visits = np.array([0 for _ in range(len(self.possible_actions))])
        self.q = np.array([0.0 for _ in range(len(self.possible_actions))])

    def build_edges_from_actions(self, actions):
        edges = {}
        for action in actions:
            edges[action] = None
        return edges
    
    def get_best_action(self, player, greedy):
        """
        tree policy. Uses U-values if used during a simulation.
        """

        if greedy:
            u_values = [0 for _ in range(len(self.possible_actions))]
        else:
            u_values = self.get_u_values()

        if player == 1:
            edge_values = self.q + u_values
            action_index = edge_values.argmax()
        else:
            edge_values = self.q - u_values
            action_index = edge_values.argmin()

        return self.possible_actions[action_index]

    def get_rollout_action(self, actor):
        return actor.default_policy(self.network_input)
        #return self.possible_actions[np.random.randint(0, len(self.possible_actions))]


    def u(self, action_index):
        num_edge_visits = self.edge_visits[action_index]
        return 1 * math.sqrt((math.log(self.visits))/(1 + num_edge_visits))

    def get_u_values(self):
        u_values = []
        for i in range(len(self.edge_visits)):
            u_values.append(self.u(i))
        return np.array(u_values)

    def update_q(self, action_index, reward):
        self.q[action_index] += (reward - self.q[action_index])/self.edge_visits[action_index]

    def increment_edge_visit(self, action_index):
        self.edge_visits[action_index] += 1

    def increment_node_visits(self):
        self.visits += 1

    def backprop(self, action, reward):
        #Updates key values of node edges
        action_index = self.possible_actions.index(action)
        self.increment_edge_visit(action_index)
        self.update_q(action_index, reward)

    def get_distribution(self):
        distribution_values = self.edge_visits / self.edge_visits.sum()
        distribution = {}
        for action in self.children:
            action_index = self.possible_actions.index(action)
            distribution[action] = distribution_values[action_index]
        return distribution