import tkinter as tk
from typing import Dict, List, Optional, Tuple
import os

try:
    from PIL import Image, ImageTk
except ImportError:
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageTk

# Colors exactly like Chess.com
BG_LIGHT = "#f0d9b5"   # light beige
BG_DARK = "#b58863"    # darker brown
HIGHLIGHT_LIGHT = "#fff176"  # bright yellow (full square)
HIGHLIGHT_DARK = "#a5d6a7"   # light green (full square)
SELECTED_BORDER = "#f3c623"  # gold border
SPECIAL_OVERLAY = "#80008080"  # semi-transparent purple overlay (alpha hex)
CHECK_BORDER = "#ff0000"  # red border for king in check

COLS = "abcdefgh"

PIECE_IMAGES = {}

def load_piece_images(size=64):
    base_path = os.path.join(os.path.dirname(__file__), "pieces")
    pieces = ['wp', 'wr', 'wn', 'wb', 'wq', 'wk', 'bp', 'br', 'bn', 'bb', 'bq', 'bk']
    for p in pieces:
        path = os.path.join(base_path, f"{p}.png")
        if os.path.exists(path):
            img = Image.open(path).resize((size, size), Image.ANTIALIAS)
            PIECE_IMAGES[p] = ImageTk.PhotoImage(img)
        else:
            print(f"Warning: Piece image {path} not found!")

def setup_board() -> Dict[str, str]:
    board = {}
    for col in COLS:
        board[col + "2"] = "wp"
        board[col + "7"] = "bp"
    board.update({
        'a1': 'wr', 'b1': 'wn', 'c1': 'wb', 'd1': 'wq', 'e1': 'wk', 'f1': 'wb', 'g1': 'wn', 'h1': 'wr',
        'a8': 'br', 'b8': 'bn', 'c8': 'bb', 'd8': 'bq', 'e8': 'bk', 'f8': 'bb', 'g8': 'bn', 'h8': 'br',
    })
    return board

# The chess logic functions (generate_legal_moves, is_in_check, is_checkmate, move_piece, can_promote, promote_pawn, is_special_move)
# are all the same as your previous terminal logic code. For brevity, I’ll paste them below exactly as they were before:

# -- Insert your chess logic functions here: generate_legal_moves, is_in_check, is_checkmate, move_piece, can_promote, promote_pawn --

# I will include them fully below, so the script is self-contained:

def inside_board(c: str, r: int) -> bool:
    return 'a' <= c <= 'h' and 1 <= r <= 8

def is_path_clear(board: Dict[str, str], squares: List[str]) -> bool:
    return all(sq not in board for sq in squares)

def get_king_square(board: Dict[str, str], color: str) -> Optional[str]:
    for square, piece in board.items():
        if piece == color + 'k':
            return square
    return None

def is_square_attacked(board: Dict[str, str], square: str, attacker_color: str) -> bool:
    for sq, piece in board.items():
        if piece[0] != attacker_color:
            continue
        if square in generate_legal_moves(board, sq, ignore_castling=True, ignore_check=True):
            return True
    return False

def is_in_check(board: Dict[str, str], color: str) -> bool:
    king_sq = get_king_square(board, color)
    if not king_sq:
        return False
    return is_square_attacked(board, king_sq, 'b' if color == 'w' else 'w')

def is_checkmate(board: Dict[str, str], color: str) -> bool:
    for square, piece in board.items():
        if piece[0] != color:
            continue
        legal = generate_legal_moves(board, square)
        if legal:
            return False
    return is_in_check(board, color)

def generate_legal_moves(board: Dict[str, str], square: str,
                         ignore_castling: bool = False,
                         ignore_check: bool = False,
                         last_move: Optional[Tuple[str, str]] = None) -> List[str]:
    piece = board.get(square)
    if not piece:
        return []

    color, ptype = piece[0], piece[1]
    row = int(square[1])
    col = square[0]
    directions = []
    moves = []
    enemy = 'b' if color == 'w' else 'w'

    if ptype == 'p':
        step = 1 if color == 'w' else -1
        fwd = col + str(row + step)
        # Move forward 1 square if empty
        if inside_board(col, row + step) and fwd not in board:
            moves.append(fwd)
            # Move forward 2 squares from starting position
            if (color == 'w' and row == 2) or (color == 'b' and row == 7):
                fwd2 = col + str(row + 2 * step)
                if fwd2 not in board and fwd not in board:
                    moves.append(fwd2)

        # Captures
        for dcol in [-1, 1]:
            nc = chr(ord(col) + dcol)
            target = nc + str(row + step)
            if inside_board(nc, row + step):
                # Normal capture (diagonal onto enemy piece)
                if target in board and board[target][0] == enemy:
                    moves.append(target)

                # En passant capture:
                if last_move:
                    start_sq, end_sq = last_move
                    if end_sq in board:
                        last_piece = board[end_sq]
                        if last_piece[0] == enemy and last_piece[1] == 'p':
                            start_row = int(start_sq[1])
                            end_row = int(end_sq[1])
                            # Must be a two-square pawn move adjacent horizontally
                            if abs(start_row - end_row) == 2 and end_row == row:
                                if ord(end_sq[0]) == ord(col) + dcol:
                                    en_passant_sq = end_sq[0] + str(row + step)
                                    if en_passant_sq not in board:
                                        moves.append(en_passant_sq)

    elif ptype == 'r':
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
    elif ptype == 'b':
        directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
    elif ptype == 'q':
        directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
    elif ptype == 'k':
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == dy == 0: continue
                nc = chr(ord(col) + dx)
                nr = row + dy
                target = nc + str(nr)
                if inside_board(nc, nr):
                    if target not in board or board[target][0] != color:
                        moves.append(target)
        if not ignore_castling and board.get(square) == color + 'k':
            if color == 'w' and square == 'e1':
                if 'h1' in board and board['h1'] == 'wr' and is_path_clear(board, ['f1', 'g1']):
                    if not any(is_square_attacked(board, sq, 'b') for sq in ['e1', 'f1', 'g1']):
                        moves.append('g1')
                if 'a1' in board and board['a1'] == 'wr' and is_path_clear(board, ['b1', 'c1', 'd1']):
                    if not any(is_square_attacked(board, sq, 'b') for sq in ['e1', 'd1', 'c1']):
                        moves.append('c1')
            elif color == 'b' and square == 'e8':
                if 'h8' in board and board['h8'] == 'br' and is_path_clear(board, ['f8', 'g8']):
                    if not any(is_square_attacked(board, sq, 'w') for sq in ['e8', 'f8', 'g8']):
                        moves.append('g8')
                if 'a8' in board and board['a8'] == 'br' and is_path_clear(board, ['b8', 'c8', 'd8']):
                    if not any(is_square_attacked(board, sq, 'w') for sq in ['e8', 'd8', 'c8']):
                        moves.append('c8')

    elif ptype == 'n':
        for dx, dy in [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]:
            nc = chr(ord(col) + dx)
            nr = row + dy
            target = nc + str(nr)
            if inside_board(nc, nr):
                if target not in board or board[target][0] != color:
                    moves.append(target)

    for dc, dr in directions:
        step = 1
        while True:
            nc = chr(ord(col) + dc * step)
            nr = row + dr * step
            target = nc + str(nr)
            if not inside_board(nc, nr):
                break
            if target in board:
                if board[target][0] != color:
                    moves.append(target)
                break
            moves.append(target)
            step += 1

    # Filter moves that leave king in check unless ignoring check
    if not ignore_check:
        legal = []
        for move in moves:
            temp = board.copy()
            # Handle en passant capture on temporary board
            if ptype == 'p' and last_move:
                start_sq, end_sq = last_move
                # If move is en passant capture square:
                if move not in board and abs(ord(move[0]) - ord(col)) == 1 and move[1] != square[1]:
                    # Remove captured pawn from temp board
                    temp.pop(end_sq, None)

            temp[move] = temp[square]
            del temp[square]
            if not is_in_check(temp, color):
                legal.append(move)
        return legal
    return moves

def can_promote(piece: str, square: str) -> bool:
    if piece not in ('wp', 'bp'):
        return False
    rank = int(square[1])
    return (piece == 'wp' and rank == 8) or (piece == 'bp' and rank == 1)

def promote_pawn(board: Dict[str, str], square: str, new_piece_type: str) -> None:
    color = board[square][0]
    board[square] = color + new_piece_type

def move_piece(board: Dict[str, str], start: str, end: str, last_move: Optional[Tuple[str, str]] = None) -> bool:
    piece = board.get(start)
    if not piece:
        return False

    legal = generate_legal_moves(board, start, last_move=last_move)
    if end not in legal:
        return False

    # Castling rook move
    if piece[1] == 'k' and abs(ord(end[0]) - ord(start[0])) == 2:
        if end[0] == 'g':
            rook_start, rook_end = 'h' + start[1], 'f' + start[1]
        else:
            rook_start, rook_end = 'a' + start[1], 'd' + start[1]
        board[rook_end] = board[rook_start]
        del board[rook_start]

    # En passant capture removal (only when capturing on empty square diagonally)
    if piece[1] == 'p' and last_move:
        start_sq, end_sq = last_move
        if abs(ord(end[0]) - ord(start[0])) == 1 and end[1] != start[1] and end not in board:
            ep_capture_sq = end[0] + start[1]
            if ep_capture_sq in board and board[ep_capture_sq][1] == 'p' and board[ep_capture_sq][0] != piece[0]:
                del board[ep_capture_sq]

    board[end] = piece
    del board[start]

    # Pawn promotion auto queen for simplicity (you can add a prompt)
    if can_promote(piece, end):
        promote_pawn(board, end, 'q')

    return True

def is_special_move(board: Dict[str, str], start: Optional[str], end: str, last_move: Optional[Tuple[str, str]]) -> bool:
    # Special moves: castling, en passant, promotion
    if not start:
        return False
    piece = board.get(start)
    if not piece:
        return False
    # Castling move
    if piece[1] == 'k' and abs(ord(end[0]) - ord(start[0])) == 2:
        return True
    # En passant
    if piece[1] == 'p' and last_move:
        start_sq, end_sq = last_move
        if abs(ord(end[0]) - ord(start[0])) == 1 and end[1] != start[1] and end not in board:
            ep_capture_sq = end[0] + start[1]
            if ep_capture_sq in board and board[ep_capture_sq][1] == 'p' and board[ep_capture_sq][0] != piece[0]:
                return True
    # Promotion
    if can_promote(piece, end):
        return True
    return False


class ChessGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CHESS")
        self.geometry("520x600")
        self.resizable(False, False)
        self.cell_size = 64
        self.current_screen = "welcome"
        self.player_color = 'w'
        self.board: Dict[str, str] = {}
        self.selected_square: Optional[str] = None
        self.legal_moves: List[str] = []
        self.current_turn = 'w'
        self.last_move: Optional[Tuple[str, str]] = None
        self.game_over = False

        self.canvas = tk.Canvas(self, width=8*self.cell_size, height=8*self.cell_size)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_click)

        self.status_label = tk.Label(self, text="", font=("Arial", 16))
        self.status_label.pack()

        self.start_button = tk.Button(self, text="START", font=("Arial", 20), command=self.start_game)
        self.player_buttons_frame = tk.Frame(self)
        self.white_button = tk.Button(self.player_buttons_frame, text="Play as White", font=("Arial", 16), command=lambda: self.choose_player('w'))
        self.black_button = tk.Button(self.player_buttons_frame, text="Play as Black", font=("Arial", 16), command=lambda: self.choose_player('b'))

        load_piece_images(size=self.cell_size)

        self.show_welcome_screen()

    def show_welcome_screen(self):
        self.current_screen = "welcome"
        self.canvas.delete("all")
        self.canvas.create_text(260, 240, text="CHESS", font=("Arial", 48, "bold"), fill="black")
        self.start_button.pack(pady=20)
        self.player_buttons_frame.pack_forget()
        self.status_label.config(text="")

    def start_game(self):
        self.start_button.pack_forget()
        self.show_choose_player_screen()

    def show_choose_player_screen(self):
        self.current_screen = "choose_player"
        self.canvas.delete("all")
        self.canvas.create_text(260, 180, text="Choose Your Player", font=("Arial", 32))
        self.player_buttons_frame.pack(pady=20)
        self.white_button.pack(side=tk.LEFT, padx=10)
        self.black_button.pack(side=tk.LEFT, padx=10)

    def choose_player(self, color: str):
        self.player_color = color
        self.player_buttons_frame.pack_forget()
        self.setup_new_game()

    def setup_new_game(self):
        self.current_screen = "game"
        self.board = setup_board()
        self.selected_square = None
        self.legal_moves = []
        self.current_turn = 'w'
        self.last_move = None
        self.game_over = False
        self.status_label.config(text=f"Turn: {'White' if self.current_turn == 'w' else 'Black'}")
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for rank in range(8):
            for file in range(8):
                x1 = file * self.cell_size
                y1 = (7 - rank) * self.cell_size
                square = chr(ord('a') + file) + str(rank + 1)

                # Base square color (Chess.com)
                if (rank + file) % 2 == 0:
                    bg_color = BG_LIGHT
                else:
                    bg_color = BG_DARK

                # Highlight legal moves - full square highlight with yellow or light green
                if square in self.legal_moves:
                    if is_special_move(self.board, self.selected_square, square, self.last_move):
                        # Purple overlay (semi-transparent)
                        self.canvas.create_rectangle(x1, y1, x1+self.cell_size, y1+self.cell_size,
                                                     fill="#800080", stipple="gray50", outline="")
                    else:
                        highlight_color = HIGHLIGHT_LIGHT if (rank + file) % 2 == 0 else HIGHLIGHT_DARK
                        self.canvas.create_rectangle(x1, y1, x1+self.cell_size, y1+self.cell_size,
                                                     fill=highlight_color, outline="")

                else:
                    # Normal square color
                    self.canvas.create_rectangle(x1, y1, x1+self.cell_size, y1+self.cell_size, fill=bg_color, outline="")

                # Selected square - gold border
                if square == self.selected_square:
                    self.canvas.create_rectangle(x1, y1, x1+self.cell_size, y1+self.cell_size,
                                                 outline=SELECTED_BORDER, width=4)

                # Highlight king in check with red border
                piece = self.board.get(square)
                if piece and piece[1] == 'k' and is_in_check(self.board, piece[0]):
                    self.canvas.create_rectangle(x1, y1, x1+self.cell_size, y1+self.cell_size,
                                                 outline=CHECK_BORDER, width=4)

                # Draw piece image if exists
                piece = self.board.get(square)
                if piece and piece in PIECE_IMAGES:
                    self.canvas.create_image(x1, y1, anchor=tk.NW, image=PIECE_IMAGES[piece])

    def on_click(self, event):
        if self.current_screen != "game" or self.game_over:
            return
        file = event.x // self.cell_size
        rank = 7 - (event.y // self.cell_size)
        if file < 0 or file > 7 or rank < 0 or rank > 7:
            return
        square = chr(ord('a') + file) + str(rank + 1)

        if self.selected_square is None:
            piece = self.board.get(square)
            if piece and piece[0] == self.current_turn:
                self.selected_square = square
                self.legal_moves = generate_legal_moves(self.board, square, last_move=self.last_move)
            else:
                self.selected_square = None
                self.legal_moves = []
        else:
            if square in self.legal_moves:
                moved = move_piece(self.board, self.selected_square, square, self.last_move)
                if moved:
                    self.last_move = (self.selected_square, square)
                    self.current_turn = 'b' if self.current_turn == 'w' else 'w'
                    if is_checkmate(self.board, self.current_turn):
                        self.status_label.config(text=f"Checkmate! {'White' if self.current_turn == 'b' else 'Black'} wins!")
                        self.game_over = True
                    elif is_in_check(self.board, self.current_turn):
                        self.status_label.config(text=f"Check! {'White' if self.current_turn == 'w' else 'Black'} to move!")
                    else:
                        self.status_label.config(text=f"Turn: {'White' if self.current_turn == 'w' else 'Black'}")
                else:
                    self.status_label.config(text="Illegal move")
                self.selected_square = None
                self.legal_moves = []
            else:
                piece = self.board.get(square)
                if piece and piece[0] == self.current_turn:
                    self.selected_square = square
                    self.legal_moves = generate_legal_moves(self.board, square, last_move=self.last_move)
                else:
                    self.selected_square = None
                    self.legal_moves = []

        self.draw_board()

if __name__ == "__main__":
    app = ChessGUI()
    app.mainloop()
