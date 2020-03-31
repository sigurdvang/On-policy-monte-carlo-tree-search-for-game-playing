import numpy as np
from tensorflow import keras

class Actor:

    def __init__(self, learning_rate, hidden_layers, hidden_activations, optimizer, m, g, k, vec_to_action_map, illegal_action_pruner):
        self.model = keras.models.Sequential()
        self.vec_to_action_map = vec_to_action_map
        self.illegal_action_pruner = illegal_action_pruner

        #input is board pluss given player to play
        self.nr_input_nodes = (k * k) + 1
        #possible pices to move
        self.nr_output_nodes = (k * k)

        #add hidden layers to model
        for i in range(len(hidden_layers)):
            #create first hidden layer
            if i == 0:
                self.model.add(
                    keras.layers.Dense(
                        hidden_layers[i], activation=hidden_activations[i], input_shape=(self.nr_input_nodes,))
                    )
            else:
                self.model.add(
                    keras.layers.Dense(hidden_layers[i], activation=hidden_activations[i])
                )

        #add output layer
        self.model.add(keras.layers.Dense(self.nr_output_nodes, activation="softmax"))

        self.model.compile(loss="sparse_categorical_crossentropy", 
                           optimizer=optimizer,
                           metrics = ["accuracy"]
                           )

    def default_policy(self, player, state):
        full_state = str(player) + str(state)
        network_input = np.array([int(x) for x in full_state]).reshape(1, self.nr_input_nodes)
        network_output = self.model.predict(network_input)
        network_output = self.illegal_action_pruner(network_output)
        return self.vec_to_action_map(network_output.argmax())

    def train_on_cases(x, y):
        self.model.train(x,y)
