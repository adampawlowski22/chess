import random
import chess
import numpy as np
from keras.models import Sequential
from keras.layers import Dense


def random_board(max_depth=100):
    board = chess.Board()
    depth = random.randrange(40, max_depth)

    for _ in range(depth):
        all_moves = list(board.legal_moves)
        random_move = random.choice(all_moves)
        board.push(random_move)
        if board.is_game_over():
            break
    return board


def encode_position(position):
    board_representation = np.zeros(64, dtype=np.int8)
    piece_map = position.piece_map()

    for square, piece in piece_map.items():
        index = square // 8 * 8 + square % 8
        piece_type = piece.piece_type
        board_representation[index] = piece_type

    return board_representation


def decode_move(prediction, legal_moves):
    move_probs = prediction.flatten()
    legal_move_indices = [i for i, move in enumerate(legal_moves)]
    move_index = np.argmax(move_probs[np.array(legal_move_indices)])  # Select the move with the highest probability
    selected_move = legal_moves[legal_move_indices[move_index]]

    return selected_move


# Generate training data
num_samples = 10
X_train = []
y_train = []

for _ in range(num_samples):
    position = random_board()
    encoded_position = encode_position(position)
    evaluation = random.random()  # Placeholder evaluation
    X_train.append(encoded_position)
    y_train.append(evaluation)

X_train = np.array(X_train)
y_train = np.array(y_train)

# Define the model architecture
model = Sequential()
model.add(Dense(32, activation='relu', input_shape=(64,)))
model.add(Dense(2064, activation='softmax'))  # Output a probability distribution over moves

# Compile the model
model.compile(optimizer='adam', loss='mse')

# Train the model
model.fit(X_train, y_train, epochs=10)

# Save the model
model.save("chess_model.h5")

# Create a sample chess position
board = random_board()

# Encode the position
encoded_position = encode_position(board)

# Reshape the input for prediction
input_data = np.array([encoded_position])

# Perform prediction
prediction = model.predict(input_data)

# Get legal moves from the current board position
legal_moves = list(board.legal_moves)

# Decode the predicted move
selected_move = decode_move(prediction, legal_moves)

# Print the predicted move
print("Predicted Move:", selected_move)

# Print the board
print(board)
