import sys
from datetime import datetime
import pygame
import chess
import time


class ChessGame:
    def __init__(self):
        # Define some colors
        self.LIGHT_BROWN = (176, 142, 112)
        self.DARK_BROWN = (232, 204, 168)
        self.GRAY = (128, 128, 128)
        self.BLUE = (0, 0, 255)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        # Define the time limit for each player
        self.time = 60 * 5
        self.black_time = self.time
        self.white_time = self.time

        # Initialize Pygame
        pygame.init()

        # Set the width and height of the screen
        self.board_size = 640
        self.tile_size = self.board_size // 8
        self.sidebar_width = 200
        self.window_width = self.board_size + self.sidebar_width
        self.window_height = self.board_size
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Chess Game")

        # Set the clock font and size
        self.clock_font = pygame.font.Font(None, 72)

        # Set the notation font and size
        self.notation_font = pygame.font.Font(None, 24)

        # Set the title font
        self.title_font = pygame.font.Font(None, 50)

        # Create a chess board
        self.board = chess.Board()

        # Load piece images
        self.piece_images = {}
        for piece_type in chess.PIECE_TYPES:
            for color in (chess.WHITE, chess.BLACK):
                color_name = chess.COLOR_NAMES[color].lower()
                piece_type_name = chess.PIECE_NAMES[piece_type].lower()
                filename = f"pieces/{color_name}_{piece_type_name}.png"
                piece_image = pygame.image.load(filename).convert_alpha()
                piece_image = pygame.transform.scale(piece_image, (self.tile_size, self.tile_size))
                self.piece_images[(piece_type, color)] = piece_image

        # Store the selected piece and its position
        self.selected_piece = None
        self.selected_piece_pos = None
        self.valid_moves = []

        # Store the notation of played moves
        self.notation = []

        # Start the clock
        self.start_time = time.time()

        # Define the promotion menu pieces
        self.promotion_menu_pieces = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]

        # Store the clicked promotion menu piece
        self.clicked_promotion_piece = None

        # Create a clock object to control the frame rate
        self.clock = pygame.time.Clock()

        # Store the game state
        self.game_state = "MainMenu"

    def run(self):
        # Main game loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == "MainMenu":
                        # Check if the "Start Game" button was clicked
                        start_button_rect = pygame.Rect(50, 250, 230, 50)
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if start_button_rect.collidepoint(event.pos):
                                self.game_state = "Chessboard"
                    elif self.game_state == "GameOver":
                        play_again_button_rect = pygame.Rect(50, 250, 230, 50)
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if play_again_button_rect.collidepoint(event.pos):
                                self.board.reset()
                                self.notation = []
                                self.game_state = "Chessboard"
                                continue
                        # Check if the "Main Menu" button was clicked
                        main_menu_button_rect = pygame.Rect(50, 350, 230, 50)
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if main_menu_button_rect.collidepoint(event.pos):
                                self.board.reset()
                                self.notation = []
                                self.game_state = "MainMenu"
                                continue

                        # Check if the "Export fen" button was clicked
                        export_fen_button_rect = pygame.Rect(50, 450, 230, 50)
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if export_fen_button_rect.collidepoint(event.pos):
                                self.export_fen()
                                continue

                    elif self.game_state == "Chessboard":
                        # Handle chessboard events
                        x, y = pygame.mouse.get_pos()
                        if x > self.board_size:
                            # Check if the click is inside the promotion menu
                            menu_x = self.board_size + 10
                            menu_y = (self.board_size - (self.tile_size * len(self.promotion_menu_pieces))) // 2
                            menu_width = self.sidebar_width - 20
                            menu_height = self.tile_size * len(self.promotion_menu_pieces)
                            if menu_x <= x <= menu_x + menu_width and menu_y <= y <= menu_y + menu_height:
                                clicked_index = (y - menu_y) // self.tile_size
                                self.clicked_promotion_piece = self.promotion_menu_pieces[clicked_index]
                                continue
                            # Ignore clicks on the sidebar
                            continue
                        row = 7 - y // self.tile_size
                        col = x // self.tile_size

                        square = chess.square(col, row)
                        piece = self.board.piece_at(square)

                        if self.selected_piece is None:
                            if piece is not None and piece.color == self.board.turn:
                                # Store the selected piece and its position
                                self.selected_piece = piece
                                self.selected_piece_pos = square
                                self.get_valid_moves()
                        else:
                            move = chess.Move(self.selected_piece_pos, square)
                            # Check if the move is a promotion move
                            # Check if it was a pawn move
                            if self.selected_piece.piece_type == chess.PAWN:
                                # Check if it was from the 2nd to the 7th rank
                                if (self.selected_piece.color == chess.WHITE and
                                    chess.square_rank(self.selected_piece_pos) == 6
                                    and chess.square_rank(square) == 7) or \
                                        (self.selected_piece.color == chess.BLACK and
                                         chess.square_rank(self.selected_piece_pos) == 1 and
                                         chess.square_rank(square) == 0):
                                    move.promotion = self.clicked_promotion_piece
                                    self.clicked_promotion_piece = None

                            if move in self.valid_moves:
                                # If the move is valid, update the board
                                self.board.push(move)
                                self.notation.append(move)
                                self.valid_moves = []
                            # Reset the selected piece and its position
                            self.selected_piece = None
                            self.selected_piece_pos = None

            # Clear the screen
            self.screen.fill(self.GRAY)

            if self.game_state == "MainMenu":
                self.draw_main_menu()
            elif self.game_state == "Chessboard":
                self.draw_chessboard()
            elif self.game_state == "GameOver":
                self.draw_game_over()

            # Update the display
            pygame.display.flip()

            # Control the frame rate
            self.clock.tick(60)

            # decrement the correct players clock
            if self.board.turn == chess.BLACK:
                self.black_time -= (time.time() - self.start_time)
            else:
                self.white_time -= (time.time() - self.start_time)
            self.start_time = time.time()

            # Check if the game is over
            if self.board.is_game_over():
                self.game_state = "GameOver"

        # Quit the game
        pygame.quit()
        sys.exit(0)

    def draw_main_menu(self):
        # Draw the title
        title_text = self.title_font.render("Chess by Adam Pawlowski", True, self.BLACK)
        title_text_rect = title_text.get_rect(center=(self.board_size // 2, 100))
        self.screen.blit(title_text, title_text_rect)

        # Draw the "Start Game" button
        start_button_rect = pygame.Rect(50, 250, 230, 50)
        pygame.draw.rect(self.screen, self.LIGHT_BROWN, start_button_rect)
        pygame.draw.rect(self.screen, self.DARK_BROWN, start_button_rect, 3)
        start_button_text = self.notation_font.render("Start Game", True, self.BLACK)
        start_button_text_rect = start_button_text.get_rect(center=start_button_rect.center)
        self.screen.blit(start_button_text, start_button_text_rect)

        # Draw the "Player vs Computer" button
        player_vs_computer_button_rect = pygame.Rect(50, 350, 230, 50)
        pygame.draw.rect(self.screen, self.LIGHT_BROWN, player_vs_computer_button_rect)
        pygame.draw.rect(self.screen, self.DARK_BROWN, player_vs_computer_button_rect, 3)
        player_vs_computer_button_text = self.notation_font.render("Player vs Computer", True, self.BLACK)
        player_vs_computer_button_text_rect = player_vs_computer_button_text.get_rect(
            center=player_vs_computer_button_rect.center)
        self.screen.blit(player_vs_computer_button_text, player_vs_computer_button_text_rect)

    def draw_chessboard(self):
        # Draw the chessboard squares
        for row in range(8):
            for col in range(8):
                square_color = self.LIGHT_BROWN if (row + col) % 2 == 0 else self.DARK_BROWN
                pygame.draw.rect(self.screen, square_color,
                                 (col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))

        # Draw the chess pieces
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)
                piece = self.board.piece_at(square)
                if piece is not None:
                    piece_image = self.piece_images[(piece.piece_type, piece.color)]
                    piece_pos = (col * self.tile_size, row * self.tile_size)
                    if square == self.selected_piece_pos:
                        pygame.draw.rect(self.screen, self.BLUE,
                                         (*piece_pos, self.tile_size, self.tile_size))
                    self.screen.blit(piece_image, piece_pos)

        # Draw the promotion menu
        menu_x = self.board_size + 10
        menu_y = (self.board_size - (self.tile_size * len(self.promotion_menu_pieces))) // 2
        menu_width = self.sidebar_width - 20
        menu_height = self.tile_size * len(self.promotion_menu_pieces)
        pygame.draw.rect(self.screen, self.LIGHT_BROWN, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, self.DARK_BROWN, (menu_x, menu_y, menu_width, menu_height), 3)
        for i, piece_type in enumerate(self.promotion_menu_pieces):
            piece_image = self.piece_images[(piece_type, self.board.turn)]
            x = menu_x + (menu_width - self.tile_size) // 2
            y = menu_y + i * self.tile_size
            self.screen.blit(piece_image, (x, y))

        # Draw black's clock
        minutes_b = self.black_time // 60
        seconds_b = self.black_time % 60 // 1
        clock_text_b = self.clock_font.render(f"{minutes_b:02.0f}:{seconds_b:02.0f}", True, self.BLACK)
        clock_text_rect_b = clock_text_b.get_rect(center=(self.window_width - self.sidebar_width // 2, 50))
        self.screen.blit(clock_text_b, clock_text_rect_b)

        # Draw white's clock
        minutes_w = self.white_time // 60
        seconds_w = self.white_time % 60 // 1
        clock_text_w = self.clock_font.render(f"{minutes_w:02.0f}:{seconds_w:02.0f}", True, self.BLACK)
        clock_text_rect_w = clock_text_w.get_rect(center=(self.window_width - self.sidebar_width // 2, 600))
        self.screen.blit(clock_text_w, clock_text_rect_w)

        # Draw the valid moves for the selected piece
        if self.selected_piece_pos is not None:
            for move in self.valid_moves:
                if move.from_square == self.selected_piece_pos:
                    dest_col, dest_row = chess.square_file(move.to_square), 7 - chess.square_rank(move.to_square)
                    pygame.draw.circle(self.screen, self.BLUE, (
                        dest_col * self.tile_size + self.tile_size // 2,
                        dest_row * self.tile_size + self.tile_size // 2),
                                       8)

    def get_valid_moves(self):
        self.valid_moves = list(
            filter(lambda move: move.from_square == self.selected_piece_pos, self.board.legal_moves))

    def draw_game_over(self):
        # Draw the "Play Again" button
        play_again_button_rect = pygame.Rect(50, 250, 230, 50)
        pygame.draw.rect(self.screen, self.LIGHT_BROWN, play_again_button_rect)
        pygame.draw.rect(self.screen, self.DARK_BROWN, play_again_button_rect, 3)
        play_again_button_text = self.notation_font.render("Play Again", True, self.BLACK)
        play_again_button_text_rect = play_again_button_text.get_rect(center=play_again_button_rect.center)
        self.screen.blit(play_again_button_text, play_again_button_text_rect)

        # Draw the "Main Menu" button
        main_menu_button_rect = pygame.Rect(50, 350, 230, 50)
        pygame.draw.rect(self.screen, self.LIGHT_BROWN, main_menu_button_rect)
        pygame.draw.rect(self.screen, self.DARK_BROWN, main_menu_button_rect, 3)
        main_menu_button_text = self.notation_font.render("Main Menu", True, self.BLACK)
        main_menu_button_text_rect = main_menu_button_text.get_rect(center=main_menu_button_rect.center)
        self.screen.blit(main_menu_button_text, main_menu_button_text_rect)

        # Draw the "Export FEN" button
        export_fen_button_rect = pygame.Rect(50, 450, 230, 50)
        pygame.draw.rect(self.screen, self.LIGHT_BROWN, export_fen_button_rect)
        pygame.draw.rect(self.screen, self.DARK_BROWN, export_fen_button_rect, 3)
        export_fen_button_text = self.notation_font.render("Export FEN", True, self.BLACK)
        export_fen_button_text_rect = export_fen_button_text.get_rect(center=export_fen_button_rect.center)
        self.screen.blit(export_fen_button_text, export_fen_button_text_rect)

        # Draw the game over text
        if self.board.is_checkmate():
            text = "Checkmate"
        elif self.board.is_stalemate():
            text = "Stalemate"
        elif self.board.is_insufficient_material():
            text = "Insufficient Material"
        elif self.board.is_seventyfive_moves():
            text = "75 Moves"
        elif self.board.is_fivefold_repetition():
            text = "5 Fold Repetition"
        elif self.board.is_check():
            text = "Check"
        else:
            text = "Game Over"
        game_over_text = self.notation_font.render(text, True, self.BLACK)
        game_over_text_rect = game_over_text.get_rect(center=(self.window_width // 2, 100))
        self.screen.blit(game_over_text, game_over_text_rect)

    def export_fen(self):
        with open(f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.fen", "w") as f:
            f.write(self.board.fen())


if __name__ == "__main__":
    chess_game = ChessGame()
    chess_game.run()
