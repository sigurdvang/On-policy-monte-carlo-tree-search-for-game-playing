import configparser
import random
from state_manager import *
from actor import *
from tree import *
import numpy as np


class Config:
    """
    Simple class that handles that retrieves configurations
    for the system
    """

    def __init__(self, config_file_name):
        #system parameters
        config = configparser.ConfigParser()
        config.read(config_file_name)
        self.m = int(config["SYSTEM"]["m"])
        self.G = int(config["SYSTEM"]["G"])
        self.game_to_play = config["SYSTEM"]["game_to_play"]
        self.start_player = int(config["SYSTEM"]["start_player"])
        if config["SYSTEM"]["verbose"] == "True":
            self.verbose = True
        else:
            self.verbose = False

        #hex parameters
        if self.game_to_play == "hex":
            self.hex_k = int(config["HEX"]["K"])

        #ANET parameters
        self.learning_rate = float(config["ANET"]["learning_rate"])
        hidden_layers = config["ANET"]["hidden_layers"].replace(" ", "").split(",")
        self.hidden_layers = [int(layer) for layer in hidden_layers]
        self.hidden_activations = config["ANET"]["hidden_activations"].replace(" ", "").split(",")
        self.optimizer = config["ANET"]["optimizer"]
        self.anet_m = config["ANET"]["m"]
        self.anet_g = config["ANET"]["g"]
        

class ReplayBuffer:

    def __init__(self, tree_distribution_converter, max_length=2000):
        self.buffer = []
        self.labels = []
        self.max_length = max_length
        self.tree_distribution_converter = tree_distribution_converter

    def add_case(self, state, distribution):
        label = self.tree_distribution_converter(distribution)
        self.buffer.append(np.array(state))
        self.labels.append(label)
        
        if len(self.buffer) > self.max_length:
            self.buffer.pop(0)
            self.labels.pop(0)

    def generate_minibatch(self, size):
        if size >= len(self.buffer):
            return np.array(self.buffer), np.array(self.labels)
        
            

def choose_start_player(player_option):
    if player_option in [1,2]:
        return player_option
    else:
        return random.randint(1,2)

def init_state_manager(config : Config):
    if config.game_to_play == "hex":
        return StateManager_Hex(config.verbose, config.hex_k)

def init_actor(config : Config, vec_to_action_map, illegal_action_pruner):
    return Actor(
        config.learning_rate,
        config.hidden_layers, 
        config.hidden_activations, 
        config.optimizer, 
        config.anet_m, 
        config.anet_g,
        config.hex_k,
        vec_to_action_map,
        illegal_action_pruner
     )