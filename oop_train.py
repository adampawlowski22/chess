import random
from datetime import time, datetime

import chess
import numpy as np
from keras.models import Sequential, load_model
from keras.layers import Dense


class ChessAI:
    def __init__(self):
        self.model = None

    def train(self, num_samples=10, max_depth=100):
        X_train = []
        y_train = []

        for _ in range(num_samples):
            position = self.random_board(max_depth)
            encoded_position = self.encode_position(position)
            evaluation = random.random()  # Placeholder evaluation
            X_train.append(encoded_position)
            y_train.append(evaluation)

        X_train = np.array(X_train)
        y_train = np.array(y_train)

        model = Sequential()
        model.add(Dense(32, activation='relu', input_shape=(64,)))
        model.add(Dense(2064, activation='softmax'))  # Output a probability distribution over moves

        model.compile(optimizer='adam', loss='mse')
        model.fit(X_train, y_train, epochs=10)

        self.model = model

    def load_model(self, model_path):
        self.model = load_model(model_path)

    @staticmethod
    def random_board(max_depth=100):
        board = chess.Board()
        depth = random.randrange(0, max_depth)

        for _ in range(depth):
            all_moves = list(board.legal_moves)
            random_move = random.choice(all_moves)
            board.push(random_move)
            if board.is_game_over():
                break

        return board

    @staticmethod
    def encode_position(position):
        board_representation = np.zeros(64, dtype=np.int8)
        piece_map = position.piece_map()

        for square, piece in piece_map.items():
            index = square // 8 * 8 + square % 8
            piece_type = piece.piece_type
            board_representation[index] = piece_type

        return board_representation

    @staticmethod
    def decode_move(prediction, legal_moves):
        move_probs = prediction.flatten()
        legal_move_indices = [i for i, move in enumerate(legal_moves)]
        move_index = np.argmax(move_probs[np.array(legal_move_indices)])  # Select the move with the highest probability
        selected_move = legal_moves[legal_move_indices[move_index]]

        return selected_move

    def predict_move(self, board):
        encoded_position = self.encode_position(board)
        input_data = np.array([encoded_position])
        prediction = self.model.predict(input_data)
        legal_moves = list(board.legal_moves)
        if board.is_game_over():
            return None
        return self.decode_move(prediction, legal_moves)


if __name__ == '__main__':
    chess_ai = ChessAI()
    start = datetime.now()
    chess_ai.train(num_samples=1000000, max_depth=10)

    # Save the model
    chess_ai.model.save("chess_model.h5")

    # Create a sample chess position
    board = chess_ai.random_board()

    # Predict and print the move
    predicted_move = chess_ai.predict_move(board)
    print("Predicted Move:", predicted_move)

    end = datetime.now()
    print("Time taken to train: ", end - start)
