import chess
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model


def encode_position(position):
    board_representation = np.zeros(64, dtype=np.int8)
    piece_map = position.piece_map()

    for square, piece in piece_map.items():
        index = square // 8 * 8 + square % 8
        piece_type = piece.piece_type
        board_representation[index] = piece_type

    return board_representation


# Set the TensorFlow backend explicitly
tf.keras.backend.set_learning_phase(0)

# Load the trained model
model = load_model("chess_model.h5")

# Create a sample chess position
board = chess.Board()
board.set_piece_at(chess.E4, chess.Piece(chess.PAWN, chess.WHITE))
board.set_piece_at(chess.E5, chess.Piece(chess.PAWN, chess.BLACK))

# Encode the position
encoded_position = encode_position(board)

# Reshape the input for prediction
input_data = np.array([encoded_position])

# Perform prediction
prediction = model.predict(input_data)

# Print the prediction
print("Prediction:", prediction)
