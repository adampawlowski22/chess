import sys

import pygame
import chess
import time

# Define some colors
LIGHT_BROWN = (176, 142, 112)
DARK_BROWN = (232, 204, 168)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize Pygame
pygame.init()

# Set the width and height of the screen
board_size = 640
tile_size = board_size // 8
sidebar_width = 200
window_width = board_size + sidebar_width
window_height = board_size
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Chess Game")

# Set the clock font and size
clock_font = pygame.font.Font(None, 36)

# Set the notation font and size
notation_font = pygame.font.Font(None, 24)

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

# Store the notation of played moves
notation = []

# Start the clock
start_time = time.time()

# Define the promotion menu pieces
promotion_menu_pieces = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]

# Store the clicked promotion menu piece
clicked_promotion_piece = None


# Function to handle pawn promotion
def handle_promotion(move):
    global clicked_promotion_piece
    if clicked_promotion_piece is not None:
        move.promotion = clicked_promotion_piece
        if move in board.legal_moves:
            # If the move is valid, update the board
            board.push(move)
            notation.append(move)
    # Reset the clicked promotion piece
    clicked_promotion_piece = None


# Create a clock object to control the frame rate
clock = pygame.time.Clock()

# Store the game state
game_state = "MainMenu"

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "MainMenu":
                # Check if the "Start Game" button was clicked
                # (50, 250, 230, 50)
                start_button_rect = pygame.Rect(50, 250, 230, 50)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if start_button_rect.collidepoint(event.pos):
                        game_state = "Chessboard"

            elif game_state == "Chessboard":
                # Handle chessboard events
                # Get the tile position where the mouse was clicked
                x, y = pygame.mouse.get_pos()
                if x > board_size:
                    # Check if the click is inside the promotion menu
                    menu_x = board_size + 10
                    menu_y = (board_size - (tile_size * len(promotion_menu_pieces))) // 2
                    menu_width = sidebar_width - 20
                    menu_height = tile_size * len(promotion_menu_pieces)
                    if menu_x <= x <= menu_x + menu_width and menu_y <= y <= menu_y + menu_height:
                        clicked_index = (y - menu_y) // tile_size
                        clicked_promotion_piece = promotion_menu_pieces[clicked_index]
                        continue
                    # Ignore clicks on the sidebar
                    continue
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

                    if selected_piece.piece_type == chess.PAWN and (
                            chess.square_rank(move.to_square) == 0 or chess.square_rank(move.to_square) == 7
                    ):
                        # Handle pawn promotion
                        handle_promotion(move)
                    elif selected_piece.piece_type == chess.PAWN and board.is_capture(move) and (
                            chess.square_rank(move.to_square) == 0 or chess.square_rank(move.to_square) == 7
                    ):
                        # Handle capture to promotion
                        handle_promotion(move)
                    else:
                        if move in board.legal_moves:
                            # If the move is valid, update the board
                            board.push(move)
                            notation.append(move)

                    # Reset the selected piece and its position
                    selected_piece = None
                    selected_piece_pos = None

    # Clear the screen
    screen.fill(LIGHT_BROWN)

    if game_state == "MainMenu":
        # Draw the main menu
        header_text = clock_font.render("Chess by Adam Pawlowski", True, BLACK)
        screen.blit(header_text, (50, 50))

        pvp = pygame.draw.rect(screen, DARK_BROWN, (50, 250, 230, 50))
        pvp_text = clock_font.render("Player vs Player", True, BLACK)
        screen.blit(pvp_text, (60, 260))
        pve = pygame.draw.rect(screen, DARK_BROWN, (50, 350, 230, 50))
        pve_text = clock_font.render("Player vs Engine", True, BLACK)
        screen.blit(pve_text, (60, 360))
        eve = pygame.draw.rect(screen, DARK_BROWN, (50, 450, 230, 50))
        eve_text = clock_font.render("Engine vs Engine", True, BLACK)
        screen.blit(eve_text, (60, 460))

    elif game_state == "Chessboard":
        # Draw the chessboard
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

        # Draw the sidebar
        pygame.draw.rect(screen, WHITE, (board_size, 0, sidebar_width, board_size))

        # Draw the promotion menu on the sidebar
        menu_x = board_size + 10
        menu_y = (board_size - (tile_size * len(promotion_menu_pieces))) // 2
        pygame.draw.rect(screen, LIGHT_BROWN,
                         (menu_x, menu_y, sidebar_width - 20, tile_size * len(promotion_menu_pieces)))
        for i, piece_type in enumerate(promotion_menu_pieces):
            piece_image = piece_images[(piece_type, chess.WHITE)]
            piece_x = menu_x + 10
            piece_y = menu_y + i * tile_size
            screen.blit(piece_image, (piece_x, piece_y))

        # Draw the notation
        notation_x = board_size + 10
        notation_y = board_size - 10
        for i, move in enumerate(notation):
            notation_text = notation_font.render(str(move), True, BLACK)
            screen.blit(notation_text, (notation_x, notation_y - (i + 1) * 30))

        # Draw the current move count
        move_count_text = clock_font.render("Move: " + str(len(notation)), True, BLACK)
        screen.blit(move_count_text, (notation_x, notation_y - (len(notation) + 1) * 30))

        # Draw the clock
        elapsed_time = time.time() - start_time
        clock_text = clock_font.render("Time: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)), True, BLACK)
        screen.blit(clock_text, (notation_x, 10))

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
