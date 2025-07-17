# chess_gui.pyw

import tkinter as tk

# Unicode chess pieces
pieces_unicode = {
    'wp': '\u2659', 'wr': '\u2656', 'wn': '\u2658', 'wb': '\u2657', 'wq': '\u2655', 'wk': '\u2654',
    'bp': '\u265F', 'br': '\u265C', 'bn': '\u265E', 'bb': '\u265D', 'bq': '\u265B', 'bk': '\u265A'
}

# Starting board setup
def setup_board():
    board = {}
    for c in "abcdefgh":
        board[c + "2"] = 'wp'
        board[c + "7"] = 'bp'
    board.update({
        'a1': 'wr', 'b1': 'wn', 'c1': 'wb', 'd1': 'wq', 'e1': 'wk', 'f1': 'wb', 'g1': 'wn', 'h1': 'wr',
        'a8': 'br', 'b8': 'bn', 'c8': 'bb', 'd8': 'bq', 'e8': 'bk', 'f8': 'bb', 'g8': 'bn', 'h8': 'br',
    })
    return board

class ChessGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Python Chess GUI")
        self.geometry("520x520")
        self.resizable(False, False)
        self.cell_size = 60
        self.board = setup_board()
        self.selected_square = None
        self.create_widgets()
        self.draw_board()

    def create_widgets(self):
        self.canvas = tk.Canvas(self, width=8*self.cell_size, height=8*self.cell_size)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#F0D9B5", "#B58863"]  # Light and dark squares
        for rank in range(8):
            for file in range(8):
                x1 = file * self.cell_size
                y1 = (7 - rank) * self.cell_size
                color = colors[(rank + file) % 2]
                self.canvas.create_rectangle(x1, y1, x1+self.cell_size, y1+self.cell_size, fill=color, outline="")
                square = chr(ord('a') + file) + str(rank + 1)
                piece = self.board.get(square)
                if piece:
                    self.canvas.create_text(
                        x1 + self.cell_size/2,
                        y1 + self.cell_size/2,
                        text=pieces_unicode[piece],
                        font=("Arial", 36),
                        fill="black" if piece[0] == 'b' else "white"
                    )

    def on_click(self, event):
        file = event.x // self.cell_size
        rank = 7 - (event.y // self.cell_size)
        square = chr(ord('a') + file) + str(rank + 1)
        print("Clicked square:", square)  # For debugging
        # For now, just select a square and redraw
        if self.selected_square == square:
            self.selected_square = None
        else:
            self.selected_square = square
        self.draw_board()
        if self.selected_square:
            self.highlight_square(self.selected_square)

    def highlight_square(self, square):
        file = ord(square[0]) - ord('a')
        rank = int(square[1]) - 1
        x1 = file * self.cell_size
        y1 = (7 - rank) * self.cell_size
        self.canvas.create_rectangle(x1, y1, x1+self.cell_size, y1+self.cell_size, outline="red", width=3)

if __name__ == "__main__":
    app = ChessGUI()
    app.mainloop()
