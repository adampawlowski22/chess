import sys
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
        self.clock_font = pygame.font.Font(None, 36)

        # Set the notation font and size
        self.notation_font = pygame.font.Font(None, 24)

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

                    elif self.game_state == "Chessboard":
                        # Handle chessboard events
                        # Get the tile position where the mouse was clicked
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

                        # Get the piece on the clicked tile
                        square = chess.square(col, row)
                        piece = self.board.piece_at(square)

                        if self.selected_piece is None:
                            # If no piece is selected, check if the clicked tile contains a piece
                            if piece is not None:
                                # Store the selected piece and its position
                                self.selected_piece = piece
                                self.selected_piece_pos = square
                        else:
                            # If a piece is already selected, try to make a move
                            move = chess.Move(self.selected_piece_pos, square)

                            if (
                                self.selected_piece.piece_type == chess.PAWN
                                and (
                                    chess.square_rank(move.to_square) == 0
                                    or chess.square_rank(move.to_square) == 7
                                )
                            ):
                                # Handle pawn promotion
                                self.handle_promotion(move)
                            elif (
                                self.selected_piece.piece_type == chess.PAWN
                                and self.board.is_capture(move)
                                and (
                                    chess.square_rank(move.to_square) == 0
                                    or chess.square_rank(move.to_square) == 7
                                )
                            ):
                                # Handle capture to promotion
                                self.handle_promotion(move)
                            else:
                                if move in self.board.legal_moves:
                                    # If the move is valid, update the board
                                    self.board.push(move)
                                    self.notation.append(move)

                            # Reset the selected piece and its position
                            self.selected_piece = None
                            self.selected_piece_pos = None

            # Clear the screen
            self.screen.fill(self.LIGHT_BROWN)

            if self.game_state == "MainMenu":
                self.draw_main_menu()
            elif self.game_state == "Chessboard":
                self.draw_chessboard()

            # Update the display
            pygame.display.flip()

            # Control the frame rate
            self.clock.tick(60)

        # Quit Pygame
        pygame.quit()
        sys.exit()

    def handle_promotion(self, move):
        if self.clicked_promotion_piece is not None:
            move.promotion = self.clicked_promotion_piece
            if move in self.board.legal_moves:
                # If the move is valid, update the board
                self.board.push(move)
                self.notation.append(move)
        # Reset the clicked promotion piece
        self.clicked_promotion_piece = None

    def draw_main_menu(self):
        # Draw the main menu
        header_text = self.clock_font.render("Chess by Adam Pawlowski", True, self.BLACK)
        self.screen.blit(header_text, (50, 50))

        pvp = pygame.draw.rect(self.screen, self.DARK_BROWN, (50, 250, 230, 50))
        pvp_text = self.clock_font.render("Player vs Player", True, self.BLACK)
        self.screen.blit(pvp_text, (60, 260))
        pve = pygame.draw.rect(self.screen, self.DARK_BROWN, (50, 350, 230, 50))
        pve_text = self.clock_font.render("Player vs Engine", True, self.BLACK)
        self.screen.blit(pve_text, (60, 360))
        eve = pygame.draw.rect(self.screen, self.DARK_BROWN, (50, 450, 230, 50))
        eve_text = self.clock_font.render("Engine vs Engine", True, self.BLACK)
        self.screen.blit(eve_text, (60, 460))

    def draw_chessboard(self):
        # Draw the chessboard
        for row in range(8):
            for col in range(8):
                x = col * self.tile_size
                y = (7 - row) * self.tile_size
                if (row + col) % 2 == 0:
                    pygame.draw.rect(self.screen, self.LIGHT_BROWN, (x, y, self.tile_size, self.tile_size))
                else:
                    pygame.draw.rect(self.screen, self.DARK_BROWN, (x, y, self.tile_size, self.tile_size))

        # Draw the chess pieces on the board
        for square in chess.SQUARES:
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            x = file * self.tile_size
            y = (7 - rank) * self.tile_size

            # Draw the chess piece if it exists on the current square
            piece = self.board.piece_at(square)
            if piece is not None:
                piece_image = self.piece_images[(piece.piece_type, piece.color)]
                self.screen.blit(piece_image, (x, y))

        # Draw a blue border around the selected piece
        if self.selected_piece is not None:
            selected_x = chess.square_file(self.selected_piece_pos) * self.tile_size
            selected_y = (7 - chess.square_rank(self.selected_piece_pos)) * self.tile_size
            pygame.draw.rect(self.screen, self.BLUE, (selected_x, selected_y, self.tile_size, self.tile_size), 5)

        # Draw the sidebar
        pygame.draw.rect(self.screen, self.WHITE, (self.board_size, 0, self.sidebar_width, self.board_size))

        # Draw the promotion menu on the sidebar
        menu_x = self.board_size + 10
        menu_y = (self.board_size - (self.tile_size * len(self.promotion_menu_pieces))) // 2
        pygame.draw.rect(
            self.screen,
            self.LIGHT_BROWN,
            (menu_x, menu_y, self.sidebar_width - 20, self.tile_size * len(self.promotion_menu_pieces)),
        )
        for i, piece_type in enumerate(self.promotion_menu_pieces):
            piece_image = self.piece_images[(piece_type, chess.WHITE)]
            piece_x = menu_x + 10
            piece_y = menu_y + i * self.tile_size
            self.screen.blit(piece_image, (piece_x, piece_y))

        # Draw the notation
        notation_x = self.board_size + 10
        notation_y = self.board_size - 10
        for i, move in enumerate(self.notation):
            notation_text = self.notation_font.render(str(move), True, self.BLACK)
            self.screen.blit(notation_text, (notation_x, notation_y - (i + 1) * 30))

        # Draw the current move count
        move_count_text = self.clock_font.render("Move: " + str(len(self.notation)), True, self.BLACK)
        self.screen.blit(move_count_text, (notation_x, notation_y - (len(self.notation) + 1) * 30))

        # Draw the clock
        elapsed_time = time.time() - self.start_time
        clock_text = self.clock_font.render(
            "Time: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)), True, self.BLACK
        )
        self.screen.blit(clock_text, (notation_x, notation_y - (len(self.notation) + 2) * 30))


# Create and run the chess game
chess_game = ChessGame()
chess_game.run()
