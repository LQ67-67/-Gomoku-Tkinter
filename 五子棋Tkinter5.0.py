import tkinter as tk
from tkinter import messagebox, font
import random
import os
import json
import datetime
from tkinter import ttk
import pygame
from PIL import Image, ImageDraw, ImageTk

# Simple way to represent chess pieces
BLACK = {"name": "Black Chess", "value": 1, "color": "#000000"}
WHITE = {"name": "White Chess", "value": 2, "color": "#FFFFFF"}

# Four directions for checking consecutive pieces
DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]

# Board parameters
GRID_SIZE = 30  # Grid size
BOARD_SIZE = 19  # Board size
MARGIN = 20  # Margin
BORDER = 2  # Border width
INSIDE = 4  # Inner padding
BOARD_LENGTH = GRID_SIZE * (BOARD_SIZE - 1) + INSIDE * 2 + BORDER  # Board length
START_X = MARGIN + BORDER // 2 + INSIDE  # Start X
START_Y = START_X  # Start Y
BOARD_HEIGHT = GRID_SIZE * (BOARD_SIZE - 1) + MARGIN * 2 + BORDER + INSIDE * 2
INFO_WIDTH = 250  # Info panel width
WINDOW_WIDTH = BOARD_HEIGHT + INFO_WIDTH  # Window width

# Stone size
STONE_SIZE = GRID_SIZE // 2 - 3  # Stone radius
Stone_Radius = STONE_SIZE  # Variable name to match the provided code
PREVIEW_SIZE = GRID_SIZE // 2 + 3  # Preview stone radius

# Colors
BOARD_COLOR = "#F5EFE0"  # Board color
GRID_COLOR = "#8A7A5E"  # Grid color
STAR_COLOR = "#8A7A5E"  # Star point color
BG_COLOR = "#F0F0F0"  # Background color
PANEL_BG = "#FFFFFF"  # Panel background color
PANEL_TEXT = "#1D1D1F"  # Panel text color
HIGHLIGHT = "#0071E3"  # Highlight color
BUTTON_BG = "#0071E3"  # Button background color
BUTTON_TEXT = "#FFFFFF"  # Button text color
WIN_LINE_COLOR = "#FF0000"  # Win line color


# Board class
class Board:
    def __init__(self, size):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.win_line = None  # Store the five points that form a win

    # Check if a stone can be placed
    def can_place(self, x, y):
        return self.board[y][x] == 0

    # Place a stone
    def place(self, chess, x, y):
        # Place stone and record
        self.board[y][x] = chess["value"]
        print(f'{chess["name"]} ({x}, {y})')
        if self.check_win(x, y):
            print(f'{chess["name"]} wins')
            return chess
        return None

    # Check if there's a win
    def check_win(self, x, y):
        value = self.board[y][x]
        for dx, dy in DIRECTIONS:
            win_points = self.count_line(x, y, value, dx, dy)
            if win_points:
                self.win_line = win_points
                return True
        return False

    # Count consecutive stones in a direction
    def count_line(self, x, y, value, dx, dy):
        count = 1
        win_points = [(x, y)]  # Store points that form a line

        # Check in one direction
        for step in range(1, 5):
            new_x = x + step * dx
            new_y = y + step * dy
            if 0 <= new_x < self.size and 0 <= new_y < self.size and self.board[new_y][new_x] == value:
                count += 1
                win_points.append((new_x, new_y))
            else:
                break

        # Check in the opposite direction
        for step in range(1, 5):
            new_x = x - step * dx
            new_y = y - step * dy
            if 0 <= new_x < self.size and 0 <= new_y < self.size and self.board[new_y][new_x] == value:
                count += 1
                win_points.insert(0, (new_x, new_y))  # Insert point at the beginning of the list
            else:
                break

        if count >= 5:
            return win_points
        return None


# AI class
class AI:
    def __init__(self, size, chess):
        self.size = size
        self.my_chess = chess
        self.opponent = BLACK if chess == WHITE else WHITE
        self.board = [[0] * size for _ in range(size)]

    # Record opponent's move
    def record_opponent(self, x, y):
        self.board[y][x] = self.opponent["value"]

    # AI makes a move
    def make_move(self):
        best_x = None
        best_y = None
        best_score = 0

        # Check all empty positions to find the one with the highest score
        for i in range(self.size):
            for j in range(self.size):
                if self.board[j][i] == 0:
                    score = self.evaluate_point(i, j)
                    if score > best_score:
                        best_score = score
                        best_x = i
                        best_y = j
                    elif score == best_score and score > 0:
                        # If scores are the same, choose randomly
                        if random.randint(0, 100) % 2 == 0:
                            best_x = i
                            best_y = j

        # Place stone
        self.board[best_y][best_x] = self.my_chess["value"]
        return best_x, best_y

    # Evaluate a point's score
    def evaluate_point(self, x, y):
        score = 0
        for dx, dy in DIRECTIONS:
            score += self.evaluate_direction(x, y, dx, dy)
        return score

    # Evaluate score in a direction
    def evaluate_direction(self, x, y, dx, dy):
        my_count = 0  # My consecutive stones
        opp_count = 0  # Opponent's consecutive stones
        my_space = None  # If there's a space in my consecutive stones
        opp_space = None  # If there's a space in opponent's consecutive stones
        my_block = 0  # If my consecutive stones are blocked at both ends
        opp_block = 0  # If opponent's consecutive stones are blocked at both ends

        # Check one direction
        flag = self.check_stone(x, y, dx, dy, True)
        if flag != 0:
            for step in range(1, 6):
                new_x = x + step * dx
                new_y = y + step * dy
                if 0 <= new_x < self.size and 0 <= new_y < self.size:
                    if flag == 1:  # My stone
                        if self.board[new_y][new_x] == self.my_chess["value"]:
                            my_count += 1
                            if my_space is False:
                                my_space = True
                        elif self.board[new_y][new_x] == self.opponent["value"]:
                            my_block += 1
                            break
                        else:
                            if my_space is None:
                                my_space = False
                            else:
                                break
                    elif flag == 2:  # Opponent's stone
                        if self.board[new_y][new_x] == self.my_chess["value"]:
                            my_block += 1
                            break
                        elif self.board[new_y][new_x] == self.opponent["value"]:
                            opp_count += 1
                            if opp_space is False:
                                opp_space = True
                        else:
                            if opp_space is None:
                                opp_space = False
                            else:
                                break
                else:
                    # Hit boundary
                    if flag == 1:
                        my_block += 1
                    elif flag == 2:
                        opp_block += 1

        if my_space is False:
            my_space = None
        if opp_space is False:
            opp_space = None

        # Check opposite direction
        flag = self.check_stone(x, y, -dx, -dy, True)
        if flag != 0:
            for step in range(1, 6):
                new_x = x - step * dx
                new_y = y - step * dy
                if 0 <= new_x < self.size and 0 <= new_y < self.size:
                    if flag == 1:  # My stone
                        if self.board[new_y][new_x] == self.my_chess["value"]:
                            my_count += 1
                            if my_space is False:
                                my_space = True
                        elif self.board[new_y][new_x] == self.opponent["value"]:
                            my_block += 1
                            break
                        else:
                            if my_space is None:
                                my_space = False
                            else:
                                break
                    elif flag == 2:  # Opponent's stone
                        if self.board[new_y][new_x] == self.my_chess["value"]:
                            my_block += 1
                            break
                        elif self.board[new_y][new_x] == self.opponent["value"]:
                            opp_count += 1
                            if opp_space is False:
                                opp_space = True
                        else:
                            if opp_space is None:
                                opp_space = False
                            else:
                                break
                else:
                    # Hit boundary
                    if flag == 1:
                        my_block += 1
                    elif flag == 2:
                        opp_block += 1

        # Calculate score
        score = 0
        if my_count == 4:
            score = 10000
        elif opp_count == 4:
            score = 9000
        elif my_count == 3:
            if my_block == 0:
                score = 1000
            elif my_block == 1:
                score = 100
            else:
                score = 0
        elif opp_count == 3:
            if opp_block == 0:
                score = 900
            elif opp_block == 1:
                score = 90
            else:
                score = 0
        elif my_count == 2:
            if my_block == 0:
                score = 100
            elif my_block == 1:
                score = 10
            else:
                score = 0
        elif opp_count == 2:
            if opp_block == 0:
                score = 90
            elif opp_block == 1:
                score = 9
            else:
                score = 0
        elif my_count == 1:
            score = 10
        elif opp_count == 1:
            score = 9
        else:
            score = 0

        # If there's a space, halve the score
        if my_space or opp_space:
            score /= 2

        return score

    # Check if a position in a direction is my stone, opponent's stone, or empty
    def check_stone(self, x, y, dx, dy, next):
        new_x = x + dx
        new_y = y + dy
        if 0 <= new_x < self.size and 0 <= new_y < self.size:
            if self.board[new_y][new_x] == self.my_chess["value"]:
                return 1
            elif self.board[new_y][new_x] == self.opponent["value"]:
                return 2
            else:
                if next:
                    return self.check_stone(new_x, new_y, dx, dy, False)
                else:
                    return 0
        else:
            return 0


# Main game class
class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Gomoku")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)  # Prevent window resizing

        # Initialize sound
        pygame.mixer.init()
        try:
            self.sound = pygame.mixer.Sound("music.wav")
            self.sound_loaded = True
        except Exception as e:
            self.sound_loaded = False
            print(f"Could not load sound file 'music.wav': {e}")
        
        # Sound toggle
        self.sound_on = tk.BooleanVar(value=True)

        # Create fonts
        self.title_font = font.Font(family="Arial", size=16, weight="bold")
        self.normal_font = font.Font(family="Arial", size=12)
        self.small_font = font.Font(family="Arial", size=10)

        # Game mode
        self.game_mode = tk.StringVar(value="AI Battles")  # Default to AI battle mode
        self.move_history = []  # For recording move history, supports undo

        # Win records
        self.win_records = self.load_records()

        # Create chess piece images
        self.create_chess_images()

        # Create main frame
        main_frame = tk.Frame(root, bg=BG_COLOR, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create left board area
        self.left_frame = tk.Frame(main_frame, bg=BG_COLOR)
        self.left_frame.pack(side=tk.LEFT, padx=(0, 15))

        # Board canvas
        self.canvas = tk.Canvas(
            self.left_frame,
            width=BOARD_HEIGHT,
            height=BOARD_HEIGHT,
            bg=BOARD_COLOR,
            highlightthickness=0  # Remove border
        )
        self.canvas.pack()

        # Create right info panel
        self.right_frame = tk.Frame(main_frame, width=INFO_WIDTH, bg=PANEL_BG, padx=15, pady=15, relief="flat")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        # Add title
        title_label = tk.Label(
            self.right_frame,
            text="Gomoku",
            font=self.title_font,
            bg=PANEL_BG,
            fg=PANEL_TEXT
        )
        title_label.pack(pady=(0, 15), anchor="w")

        # Game mode selection
        mode_frame = tk.Frame(self.right_frame, bg=PANEL_BG)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            mode_frame,
            text="Game Mode",
            font=self.normal_font,
            bg=PANEL_BG,
            fg=PANEL_TEXT
        ).pack(side=tk.LEFT)

        mode_menu = tk.OptionMenu(
            mode_frame,
            self.game_mode,
            "AI Battles",
            "Two-player Battles",
            command=self.change_mode
        )
        mode_menu.config(
            font=self.normal_font,
            bg=BUTTON_BG,
            fg=BUTTON_TEXT,
            activebackground=HIGHLIGHT,
            activeforeground=BUTTON_TEXT,
            relief="flat",
            width=10
        )
        mode_menu.pack(side=tk.RIGHT)

        # Info panel
        self.info_frame = tk.Frame(self.right_frame, bg=PANEL_BG)
        self.info_frame.pack(fill=tk.X, pady=(0, 20))

        # Current player info
        self.player_frame = tk.Frame(self.info_frame, bg=PANEL_BG)
        self.player_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            self.player_frame,
            text="Current player",
            font=self.normal_font,
            bg=PANEL_BG,
            fg=PANEL_TEXT
        ).pack(side=tk.LEFT)

        self.player_label = tk.Label(
            self.player_frame,
            text="Black Chess",
            font=self.normal_font,
            bg=PANEL_BG,
            fg=HIGHLIGHT
        )
        self.player_label.pack(side=tk.RIGHT)

        # Tip info
        self.tip_label = tk.Label(
            self.info_frame,
            text="Click on the board to land",
            font=self.small_font,
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            justify="left"
        )
        self.tip_label.pack(anchor="w", pady=5)

        # Win records display
        self.record_frame = tk.Frame(self.right_frame, bg=PANEL_BG)
        self.record_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            self.record_frame,
            text="Win Records",
            font=self.normal_font,
            bg=PANEL_BG,
            fg=PANEL_TEXT
        ).pack(anchor="w", pady=(0, 5))

        # Create win records table
        self.record_tree = ttk.Treeview(
            self.record_frame,
            columns=("date", "winner", "mode"),
            show="headings",
            height=5
        )
        self.record_tree.heading("date", text="Date")
        self.record_tree.heading("winner", text="Winner")
        self.record_tree.heading("mode", text="Mode")
        self.record_tree.column("date", width=70)
        self.record_tree.column("winner", width=70)
        self.record_tree.column("mode", width=70)
        self.record_tree.pack(fill=tk.X)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.record_frame, orient="vertical", command=self.record_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.record_tree.configure(yscrollcommand=scrollbar.set)

        # Update win records display
        self.update_records()

        # Button frame
        button_frame = tk.Frame(self.right_frame, bg=PANEL_BG)
        button_frame.pack(fill=tk.X, pady=5)

        # Undo button
        self.undo_button = tk.Button(
            button_frame,
            text="Undo",
            font=self.normal_font,
            bg=BUTTON_BG,
            fg=BUTTON_TEXT,
            activebackground=HIGHLIGHT,
            activeforeground=BUTTON_TEXT,
            relief="flat",
            padx=10,
            pady=5,
            command=self.undo
        )
        self.undo_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Restart button
        self.reset_button = tk.Button(
            button_frame,
            text="Restart",
            font=self.normal_font,
            bg=BUTTON_BG,
            fg=BUTTON_TEXT,
            activebackground=HIGHLIGHT,
            activeforeground=BUTTON_TEXT,
            relief="flat",
            padx=10,
            pady=5,
            command=self.reset
        )
        self.reset_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Add sound control UI
        sound_frame = tk.Frame(self.right_frame, bg=PANEL_BG)
        sound_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            sound_frame,
            text="Sound",
            font=self.normal_font,
            bg=PANEL_BG,
            fg=PANEL_TEXT
        ).pack(side=tk.LEFT)
        
        sound_check = tk.Checkbutton(
            sound_frame,
            variable=self.sound_on,
            bg=PANEL_BG
        )
        sound_check.pack(side=tk.RIGHT)

        # Initialize game
        self.reset()
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_move)
        self.last_preview = None

    def load_records(self):
        """Load win records"""
        if os.path.exists("win_records.json"):
            try:
                with open("win_records.json", "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_records(self):
        """Save win records"""
        with open("win_records.json", "w") as f:
            json.dump(self.win_records, f)

    def update_records(self):
        """Update win records display"""
        # Clear table
        for item in self.record_tree.get_children():
            self.record_tree.delete(item)

        # Add records (show at most 10 recent records)
        for record in self.win_records[-10:]:
            mode = record.get("mode", "Unknown")  # If there is no mode field, it defaults to "Unknown"
            self.record_tree.insert("", 0, values=(
                record["date"],
                record["winner"],
                mode
            ))

    def create_chess_images(self):
        """Pre-created chess piece images with shadow effects"""
        size = Stone_Radius * 2 + 10  # Add edges for shadows

        # Create an image of a black piece
        black_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(black_img)
        # Draw shadows
        shadow_radius = Stone_Radius + 2
        shadow_center = size // 2
        for i in range(3):
            alpha = 60 - i * 20  # Shadow transparency
            offset = i + 1  # Shadow Shift
            draw.ellipse(
                (shadow_center - shadow_radius + offset,
                 shadow_center - shadow_radius + offset,
                 shadow_center + shadow_radius + offset,
                 shadow_center + shadow_radius + offset),
                fill=(0, 0, 0, alpha)
            )
        # Draw black pieces
        draw.ellipse(
            (shadow_center - Stone_Radius,
             shadow_center - Stone_Radius,
             shadow_center + Stone_Radius,
             shadow_center + Stone_Radius),
            fill=BLACK["color"]
        )
        # Add a highlight effect
        highlight_radius = Stone_Radius // 3
        highlight_offset = Stone_Radius // 3
        draw.ellipse(
            (shadow_center - highlight_radius - highlight_offset,
             shadow_center - highlight_radius - highlight_offset,
             shadow_center - highlight_offset,
             shadow_center - highlight_offset),
            fill=(80, 80, 80, 150)
        )
        self.black_chess_img = ImageTk.PhotoImage(black_img)

        # Create an image of a white piece
        white_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(white_img)
        # Draw shadows
        for i in range(3):
            alpha = 60 - i * 20
            offset = i + 1
            draw.ellipse(
                (shadow_center - shadow_radius + offset,
                 shadow_center - shadow_radius + offset,
                 shadow_center + shadow_radius + offset,
                 shadow_center + shadow_radius + offset),
                fill=(0, 0, 0, alpha)
            )
        # Draw white pieces
        draw.ellipse(
            (shadow_center - Stone_Radius,
             shadow_center - Stone_Radius,
             shadow_center + Stone_Radius,
             shadow_center + Stone_Radius),
            fill=WHITE["color"],
            outline="#DDDDDD"
        )
        # Add a highlight effect
        draw.ellipse(
            (shadow_center - highlight_radius - highlight_offset,
             shadow_center - highlight_radius - highlight_offset,
             shadow_center - highlight_offset,
             shadow_center - highlight_offset),
            fill=(255, 255, 255, 200)
        )
        self.white_chess_img = ImageTk.PhotoImage(white_img)

        # Create a black chess preview image - translucent effect
        black_preview_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(black_preview_img)
        # Draw translucent black discs
        draw.ellipse(
            (shadow_center - Stone_Radius,
             shadow_center - Stone_Radius,
             shadow_center + Stone_Radius,
             shadow_center + Stone_Radius),
            fill=(0, 0, 0, 100),
            outline=(0, 0, 0, 150)
        )
        self.black_preview_chess_img = ImageTk.PhotoImage(black_preview_img)

        # Create a white chess preview image - translucent effect
        white_preview_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(white_preview_img)
        # Draw translucent white pieces
        draw.ellipse(
            (shadow_center - Stone_Radius,
             shadow_center - Stone_Radius,
             shadow_center + Stone_Radius,
             shadow_center + Stone_Radius),
            fill=(255, 255, 255, 100),
            outline=(200, 200, 200, 150)
        )
        self.white_preview_chess_img = ImageTk.PhotoImage(white_preview_img)

    def create_images(self):
        """Create stone images - this method is now replaced by create_chess_images"""
        pass

    def draw_stone(self, x, y, chess):
        """Draw a stone using pre-created images"""
        cx = START_X + GRID_SIZE * x
        cy = START_Y + GRID_SIZE * y

        # Draw stone using image
        img = self.black_chess_img if chess == BLACK else self.white_chess_img
        self.canvas.create_image(
            cx, cy,  # Position at exact grid intersection
            image=img,
            anchor="center"  # Center the image at the intersection
        )

    def draw_preview(self, x, y):
        """Draw preview stone using pre-created images"""
        if not self.is_valid_position(x, y) or not self.board.can_place(x, y):
            return

        cx = START_X + GRID_SIZE * x
        cy = START_Y + GRID_SIZE * y

        # Draw preview stone using image
        img = self.black_preview_chess_img if self.current_player == BLACK else self.white_preview_chess_img
        self.canvas.create_image(
            cx, cy,  # Position at exact grid intersection
            image=img,
            anchor="center",  # Center the image at the intersection
            tags="preview"
        )

    def change_mode(self, *args):
        """Handle game mode change"""
        self.reset()

    def undo(self):
        """Undo function"""
        if not self.move_history or self.winner is not None:
            return

        # Get the last move
        last_move = self.move_history.pop()
        # Remove this move from the board
        self.board.board[last_move[1]][last_move[0]] = 0

        # If in AI mode, also remove AI's move
        if self.game_mode.get() == "AI Battles":
            if self.move_history:
                ai_move = self.move_history.pop()
                self.board.board[ai_move[1]][ai_move[0]] = 0
                self.current_player = BLACK
            else:
                self.current_player = BLACK

        # Redraw board
        self.draw_board()
        self.update_info()

    def on_click(self, event):
        if self.winner is not None:
            return  # Already have a winner, click is无效

        x, y = self.get_point(event.x, event.y)
        if x is None or y is None:
            print("Out of the board")
            return

        if self.board.can_place(x, y):
            # Delete preview
            self.canvas.delete("preview")
            self.last_preview = None

            # Player places stone
            self.winner = self.board.place(self.current_player, x, y)
            # Play sound
            self.play_sound()
            # Record move
            self.move_history.append((x, y))
            self.draw_board()

            if self.winner:
                # Record win
                self.record_win(self.winner["name"])

                self.black_wins += 1
                messagebox.showinfo("Game Over", f"{self.winner['name']} Wins！😋")
                self.update_info()
                return

            # Switch player
            self.current_player = WHITE if self.current_player == BLACK else BLACK
            self.update_info()

            # If in AI mode, let AI make a move
            if self.game_mode.get() == "AI Battles":
                self.ai.record_opponent(x, y)
                self.root.after(300, self.ai_move)
        else:
            print("The position cannot be dropped")

    def record_win(self, winner_name):
        """Record win"""
        # Get current date and time
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M")

        # Create record
        record = {
            "date": date_str,
            "winner": winner_name,
            "mode": self.game_mode.get()
        }

        # Add to records list
        self.win_records.append(record)

        # Save records
        self.save_records()

        # Update display
        self.update_records()

    def ai_move(self):
        """AI makes a move"""
        x, y = self.ai.make_move()
        self.winner = self.board.place(self.current_player, x, y)
        # Play sound
        self.play_sound()
        # Record AI move
        self.move_history.append((x, y))
        self.draw_board()

        if self.winner:
            # Record win
            self.record_win(self.winner["name"])

            self.white_wins += 1
            messagebox.showinfo("Game Over", f"{self.winner['name']} Wins！😋")

        # Switch back to player
        self.current_player = BLACK
        self.update_info()

    def reset(self):
        """Reset game"""
        self.board = Board(BOARD_SIZE)
        self.current_player = BLACK
        self.winner = None
        self.black_wins = 0
        self.white_wins = 0
        self.move_history = []  # Clear move history
        self.ai = AI(BOARD_SIZE, WHITE)
        self.draw_board()
        self.update_info()

    def draw_board(self):
        self.canvas.delete("all")

        # Draw board background
        self.canvas.create_rectangle(
            0, 0, BOARD_HEIGHT, BOARD_HEIGHT,
            fill=BOARD_COLOR, outline=""
        )

        # Draw board border
        self.canvas.create_rectangle(
            MARGIN, MARGIN,
            MARGIN + BOARD_LENGTH,
            MARGIN + BOARD_LENGTH,
            width=BORDER, outline=GRID_COLOR,
            fill=""
        )

        # Draw grid lines
        for i in range(BOARD_SIZE):
            x0 = START_X
            y0 = START_Y + i * GRID_SIZE
            x1 = START_X + GRID_SIZE * (BOARD_SIZE - 1)
            self.canvas.create_line(x0, y0, x1, y0, fill=GRID_COLOR, width=1)

        for j in range(BOARD_SIZE):
            x0 = START_X + j * GRID_SIZE
            y0 = START_Y
            y1 = START_Y + GRID_SIZE * (BOARD_SIZE - 1)
            self.canvas.create_line(x0, y0, x0, y1, fill=GRID_COLOR, width=1)

        # Draw star points
        for i in (3, 9, 15):
            for j in (3, 9, 15):
                radius = 4 if (i == 9 and j == 9) else 3
                cx = START_X + GRID_SIZE * i
                cy = START_Y + GRID_SIZE * j
                self.canvas.create_oval(
                    cx - radius, cy - radius,
                    cx + radius, cy + radius,
                    fill=STAR_COLOR, outline=""
                )

        # Draw all stones
        for y, row in enumerate(self.board.board):
            for x, cell in enumerate(row):
                if cell == BLACK["value"]:
                    self.draw_stone(x, y, BLACK)
                elif cell == WHITE["value"]:
                    self.draw_stone(x, y, WHITE)

        # If there's a win line, draw red line
        if self.board.win_line:
            self.draw_win_line()

    def draw_win_line(self):
        """Draw winning red line"""
        if not self.board.win_line or len(self.board.win_line) < 5:
            return

        # Get start and end points of the line
        start_x, start_y = self.board.win_line[0]
        end_x, end_y = self.board.win_line[-1]

        # Calculate canvas coordinates
        canvas_start_x = START_X + GRID_SIZE * start_x
        canvas_start_y = START_Y + GRID_SIZE * start_y
        canvas_end_x = START_X + GRID_SIZE * end_x
        canvas_end_y = START_Y + GRID_SIZE * end_y

        # Draw red line
        self.canvas.create_line(
            canvas_start_x, canvas_start_y, canvas_end_x, canvas_end_y,
            fill=WIN_LINE_COLOR, width=3
        )

    def on_move(self, event):
        """Handle mouse move event, show preview stone"""
        if self.winner is not None:
            return

        # Get board coordinates for current mouse position
        x, y = self.get_point(event.x, event.y)

        # If position is valid and different from last preview
        if x is not None and y is not None and (x, y) != self.last_preview:
            # Delete previous preview stone
            self.canvas.delete("preview")

            # If position can place stone, draw preview
            if self.board.can_place(x, y):
                self.draw_preview(x, y)
                self.last_preview = (x, y)
        # If moved out of valid area, delete preview
        elif (x is None or y is None) and self.last_preview:
            self.canvas.delete("preview")
            self.last_preview = None

    def is_valid_position(self, x, y):
        """Check if position is valid"""
        return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

    def get_point(self, canvas_x, canvas_y):
        """Convert canvas coordinates to board coordinates"""
        pos_x = canvas_x - START_X + GRID_SIZE // 2
        pos_y = canvas_y - START_Y + GRID_SIZE // 2
        grid_x = pos_x // GRID_SIZE
        grid_y = pos_y // GRID_SIZE
        if self.is_valid_position(grid_x, grid_y):
            return int(grid_x), int(grid_y)
        else:
            return None, None

    def update_info(self):
        """Update info panel"""
        # Update current player info
        player_name = "Black Chess" if self.current_player == BLACK else "White Chess"
        self.player_label.config(text=player_name)

        # If there's a winner, update tip info
        if self.winner:
            self.tip_label.config(text=f"Game Over | {self.winner['name']} Wins！😋", fg=HIGHLIGHT)
        else:
            self.tip_label.config(text="Click on the board to land", fg=PANEL_TEXT)

        # Update undo button state
        self.undo_button.config(state="normal" if self.move_history and not self.winner else "disabled")

        # Keep key binding
        self.root.bind("<Return>", lambda event: self.reset())

    def play_sound(self):
        """Play stone placement sound"""
        if self.sound_on.get() and self.sound_loaded:
            self.sound.play()


# Start game
root = tk.Tk()
game = Game(root)
root.mainloop()