import pygame
import chess

# Define some colors
LIGHT_BROWN = (176, 142, 112)
DARK_BROWN = (232, 204, 168)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)

# Initialize Pygame
pygame.init()

# Set the width and height of the screen
board_size = 512
tile_size = board_size // 8
screen = pygame.display.set_mode((board_size, board_size))
pygame.display.set_caption("Chessboard")

# Create a chess board
board = chess.Board()

# Load piece images
piece_images = {}
for piece_type in chess.PIECE_TYPES:
    for color in (chess.WHITE, chess.BLACK):
        color_name = chess.COLOR_NAMES[color].lower()
        piece_type_name = chess.PIECE_NAMES[piece_type].lower()
        filename = f"pieces/{color_name}_{piece_type_name}.png"
        piece_image = pygame.image.load(filename).convert_alpha()
        piece_image = pygame.transform.scale(piece_image, (tile_size, tile_size))
        piece_images[(piece_type, color)] = piece_image

# Store the selected piece and its position
selected_piece = None
selected_piece_pos = None

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle mouse events
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Get the tile position where the mouse was clicked
            x, y = pygame.mouse.get_pos()
            row = 7 - y // tile_size
            col = x // tile_size

            # Get the piece on the clicked tile
            square = chess.square(col, row)
            piece = board.piece_at(square)

            if selected_piece is None:
                # If no piece is selected, check if the clicked tile contains a piece
                if piece is not None:
                    # Store the selected piece and its position
                    selected_piece = piece
                    selected_piece_pos = square
            else:
                # If a piece is already selected, try to make a move
                move = chess.Move(selected_piece_pos, square)
                if move in board.legal_moves:
                    # If the move is valid, update the board
                    board.push(move)

                # Reset the selected piece and its position
                selected_piece = None
                selected_piece_pos = None

    # Clear the screen with a gray background
    screen.fill(GRAY)

    # Draw the chessboard tiles
    for row in range(8):
        for col in range(8):
            x = col * tile_size
            y = (7 - row) * tile_size
            if (row + col) % 2 == 0:
                pygame.draw.rect(screen, LIGHT_BROWN, (x, y, tile_size, tile_size))
            else:
                pygame.draw.rect(screen, DARK_BROWN, (x, y, tile_size, tile_size))

    # Draw the chess pieces on the board
    for square in chess.SQUARES:
        rank = chess.square_rank(square)
        file = chess.square_file(square)
        x = file * tile_size
        y = (7 - rank) * tile_size

        # Draw the chess piece if it exists on the current square
        piece = board.piece_at(square)
        if piece is not None:
            piece_image = piece_images[(piece.piece_type, piece.color)]
            screen.blit(piece_image, (x, y))

    # Draw a blue border around the selected piece
    if selected_piece is not None:
        selected_x = chess.square_file(selected_piece_pos) * tile_size
        selected_y = (7 - chess.square_rank(selected_piece_pos)) * tile_size
        pygame.draw.rect(screen, BLUE, (selected_x, selected_y, tile_size, tile_size), 5)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
