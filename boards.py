import networkx as nx
import math
import matplotlib.pyplot as plt
from cells import *


class Board:
    """
    Object represents a game board.
    it contains:
    -a size variable, representing number of rows
    -k_i and k_j lists representing indices of cells to be left open
    -a board variable, representing the array of cells making up the board
    -a graph variable, a datastructure containgin the graphical representation of the board
    and various auxillary variables
    """

    def __init__(self, size):
        self.size = size
        self.graph = nx.Graph()
        self.board = []
        self.free_cells = []
        self.seed = self.get_seed_for_board_size(size)

        self.create_board()
        self.add_graph_nodes_and_edges()

        self.initial_state =  self.get_state()
        self.set_free_cells()



    def add_graph_nodes_and_edges(self):
        """
        Creates the neighbourhood relationships between cells on the graph
        """
        for row in self.board:
            for cell in row:
                self.graph.add_node(cell)
                cell.add_neighbours(self.board)
                for key in cell.neighbours:
                    n = cell.neighbours[key]
                    if (cell, n) not in self.graph.edges and (n, cell) not in self.graph.edges:
                        self.graph.add_edge(cell, n)

    def set_free_cells(self):
        """
        arranges cells with pegs in them into a 1d array
        """
        self.free_cells = []
        for row in self.board:
            for cell in row:
                if cell.has_peg == 0:
                    self.free_cells.append(cell)

    def display_board(self):
        """
        Displays a graph representation of the board.
        """

        show_time = 1
        player_1_colour = "red"
        player_2_colour = "blue"

        node_colour_map = []
        #iterate over cells and set cell color
        for cell in self.graph:

            if cell.has_peg == 1:
                node_colour_map.append(player_1_colour)
            elif cell.has_peg == 2:
                node_colour_map.append(player_2_colour)
            else:
                node_colour_map.append("black")

        edge_colour_map = []
        #iterate over cells and set edge color
        for edge in self.graph.edges:

            if edge[0].has_peg != 0 and edge[0].has_peg == edge[1].has_peg:
                if edge[0].has_peg == 1:
                    edge_colour_map.append(player_1_colour)
                else:
                    edge_colour_map.append(player_2_colour)
            else:
                edge_colour_map.append("gray")


        #so that the same graph position is used each draw call
        graph_pos = nx.spring_layout(self.graph, seed=self.seed)
        nx.draw(self.graph, pos=graph_pos, node_color=node_colour_map, edge_color=edge_colour_map)
        plt.pause(show_time)

        

    def find_possible_moves(self):
        """
        get positions of all free cells
        """
        return [c.position for c in self.free_cells]


    def make_move(self, position, player):
        """
        given indice of cell to place, and which player the peg belongs to,
        it places a peg
        """
        i, j = position
        self.board[i][j].has_peg = player
        #remove cell from list of free cells
        self.free_cells.remove(self.board[i][j])

    def get_state(self):
        """
        gets string representation of board
        """
        state = []
        for row in self.board:
            for cell in row:
                state.append(cell.has_peg)
        return state

    def set_state(self, state):
        i = 0
        for row in self.board:
            for cell in row:
                cell.has_peg = state[i]
                i += 1
        self.set_free_cells()

    def reset_to_initial_state(self):
        self.set_state(self.initial_state)

    def get_lookup_action(self, action):
        """
        Gets a a representation of action to use for lookup.
        Turns cells into their string representation
        """
        cell_to_move, direction = action
        cell_to_move = cell_to_move.__repr__()
        action_lookup = (cell_to_move, direction)
        return action_lookup

    def get_seed_for_board_size(self, k):
        seed_map = {
            1 : 0,
            2 : 20,
            3 : 106,
            4 : 27,
            5 : 179,
            6 : 62,
            7 : 183,
            8 : 77,
        }
        return seed_map[k] if k in seed_map else 50

class DiamondBoard(Board):
    """
    A subclass of the Board object, representing the case of game board
    where the shape is triangular.
    """

    def __init__(self, size):
        super().__init__(size)

    def create_board(self):
        """
        Creates a triangle board as described in hex-board-games.pdf
        """
        for i in range(self.size):
            self.board.append([])
            for j in range(self.size):
                self.board[i].append(DiamondCell(i,j))
