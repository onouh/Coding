class GameState:
    ROWS = 6
    COLS = 7

    def __init__(self, board=None, turn="X"):
        if board is None:
            self.board = [["." for _ in range(self.COLS)] for _ in range(self.ROWS)]
        else:
            self.board = board
        self.active_turn = turn  # "X" for AI, "O" for Opponent

    def get_available_moves(self) -> list[int]:
        """Returns list of column indices that still have space."""
        return [col for col in range(self.COLS) if self.board[self.ROWS - 1][col] == "."]

    def get_new_state(self, move: int) -> "GameState":
        """Returns a new GameState after dropping a piece in the given column."""
        new_board = [row[:] for row in self.board]  # Deep copy

        # Find the lowest available row in the column (row 0 = bottom)
        for row in range(self.ROWS): 
            if new_board[row][move] == ".":
                new_board[row][move] = self.active_turn
                break

        next_turn = "O" if self.active_turn == "X" else "X"
        return GameState(new_board, next_turn)

    def win(self, player: str) -> bool:
        """Returns True if the given player has 4 in a row/col/diagonal."""
        b = self.board

        for r in range(self.ROWS):
            for c in range(self.COLS):
                # Horizontal
                if c + 3 < self.COLS and all(b[r][c+i] == player for i in range(4)):
                    return True
                # Vertical
                if r + 3 < self.ROWS and all(b[r+i][c] == player for i in range(4)):
                    return True
                # Diagonal down-right
                if r + 3 < self.ROWS and c + 3 < self.COLS and all(b[r+i][c+i] == player for i in range(4)):
                    return True
                # Diagonal down-left
                if r + 3 < self.ROWS and c - 3 >= 0 and all(b[r+i][c-i] == player for i in range(4)):
                    return True
        return False

    def over(self) -> bool:
        """Returns True if the game is over (win or no moves left)."""
        return self.win("X") or self.win("O") or len(self.get_available_moves()) == 0

    def print_board(self):
        """Prints the board in a human-readable format."""
        print("  " + " ".join(str(c) for c in range(self.COLS)))
        print("  " + "-" * (self.COLS * 2 - 1))
        for r in range(self.ROWS - 1, -1, -1):
            print(f"{r}| " + " ".join(self.board[r]))
        print()


# ── Scoring & Minimax ────────────────────────────────────────────────────────

def count_threats(game: GameState, player: str, length: int) -> int:
    """
    Counts the number of open-ended runs of `length` pieces for `player`.
 
    A "threat" is a window of exactly 4 cells containing:
      - exactly `length` pieces belonging to `player`
      - zero pieces belonging to the opponent (the rest are empty)
 
    This means the window is not blocked and could still become a winning 4-in-a-row.
 
    Parameters:
        game (GameState): The current game state.
        player (str): The player to count threats for ("X" or "O").
        length (int): The run length to look for (e.g. 2 or 3).
 
    Returns:
        int: The number of unblocked windows containing exactly `length` pieces.
    """
    b = game.board
    opponent = "O" if player == "X" else "X"
    threats = 0
 
    # All 4 directions represented as (row_step, col_step)
    directions = [
        (0, 1),   # horizontal
        (1, 0),   # vertical
        (1, 1),   # diagonal down-right
        (1, -1),  # diagonal down-left
    ]
 
    for r in range(GameState.ROWS):
        for c in range(GameState.COLS):
            for dr, dc in directions:
                # Collect the 4-cell window starting at (r, c)
                window = []
                for i in range(4):
                    nr, nc = r + dr * i, c + dc * i
                    if 0 <= nr < GameState.ROWS and 0 <= nc < GameState.COLS:
                        window.append(b[nr][nc])
 
                # Only score complete 4-cell windows
                if len(window) < 4:
                    continue
 
                player_count   = window.count(player)
                opponent_count = window.count(opponent)
 
                # Threat = exactly `length` of our pieces, zero opponent pieces
                if player_count == length and opponent_count == 0:
                    threats += 1
 
    return threats
 
 
def heuristic(game: GameState) -> int:
    """
    Scores a non-terminal board position by counting threats of each length.
 
    Weights:
        3-in-a-row (one away from winning): +5 per threat for X, -5 for O
        2-in-a-row (building presence):     +2 per threat for X, -2 for O
 
    Returns:
        int: A heuristic score from X's perspective (positive = X advantage).
    """
    score = 0
    # For defensive AI, we want to count all possible opponent threats including 3-in-a-row and 2-in-a-row, and subtract them from our score 

    # for player, sign in [("X", 1), ("O", -1)]:
    #     score += sign * count_threats(game, player, length=3) * 5
    #     score += sign * count_threats(game, player, length=2) * 2

    # For aggressive AI, we want to count all possible threats for X and ignore opponent threats, since we are focused on winning rather than blocking

    score += count_threats(game, "X", length=3) * 5
    score += count_threats(game, "X", length=2) * 2
    score -= count_threats(game, "O", length=3) * 4
    # score -= count_threats(game, "O", length=2) * 1 
    # We can ignore 2-in-a-row threats for O since they are less urgent than 3-in-a-row threats, and we want to focus on winning rather than blocking every single threat
    
    return score
 
 
def score(game: GameState, depth: int = 4) -> int:
    """
    Evaluates the game state and returns a numerical score based on the AI's advantage.
 
    Terminal states use fixed win/loss scores adjusted by depth.
    Non-terminal states (depth limit reached) fall back to the heuristic.
 
    Parameters:
        game (GameState): The current game state.
        depth (int): The depth of the recursion.
 
    Returns:
        int: A numerical score based on the board evaluation.
    """
    if game.win("X"):       # AI wins
        return 10 - depth   # Prefer quicker wins
    elif game.win("O"):     # Opponent wins
        return depth - 10   # Prefer delaying losses
    else:
        ## For non-terminal states, we can use a heuristic evaluation to estimate the score based on potential winning positions and threats. We don't return 0 for all non-terminal states because that would make the AI blind to the strategic value of different board positions. By using a heuristic, we can guide the AI towards moves that create more winning opportunities for itself and block the opponent's threats, even if it can't see an immediate win or loss.
        return heuristic(game)  # Use positional scoring, return positive if favorable for X, negative if favorable for O
        # return 0  # Neutral score for non-terminal states without heuristic evaluation (i.e. neither plays wins immediately, and we don't consider positional advantages)


def minimax(game: GameState, depth: int, max_depth: int = 4) -> int:
    """
    Minimax algorithm with depth limiting.
    """
    # Base case: game is over OR depth limit reached
    if game.over() or depth >= max_depth:
        return score(game, depth)

    available_moves = game.get_available_moves()
    scores = []

    for move in available_moves:
        new_state = game.get_new_state(move)
        move_score = minimax(new_state, depth + 1, max_depth)
        scores.append(move_score)

    if game.active_turn == "X":
        return max(scores)
    else:
        return min(scores)


def best_move(game: GameState, depth: int = 0, max_depth: int = 4) -> int:
    """
    Returns the column number of the best move for the AI.

    Parameters:
        game (GameState): The current game state.
        depth (int): Starting depth (default 0).
        max_depth (int): Maximum depth to search (default 7).

    Returns:
        int: The column index of the best move.
    """
    available_moves = game.get_available_moves()
    best_col = None
    best_score_val = float('-inf')

    for move in available_moves:
        new_state = game.get_new_state(move)
        move_score = minimax(new_state, depth + 1, max_depth)
        if move_score > best_score_val:
            best_score_val = move_score
            best_col = move

    print(f"Best move for AI (X): Column {best_col}")
    print(f"Predicted score: {best_score_val}")
    return best_col, best_score_val


# ── Test Case ──────────────────────────────────────────────────

if __name__ == "__main__":
    # Board state from the assignment (row 0 = bottom, row 5 = top)
    board = [
        ["X", "O", "X", "O", "X", ".", "."],  # row 0 (bottom)
        [".", "X", "O", "O", ".", ".", "."],   # row 1
        [".", "O", "X", ".", ".", ".", "."],   # row 2
        [".", ".", "X", ".", ".", ".", "."],   # row 3
        [".", ".", ".", ".", ".", ".", "."],   # row 4
        [".", ".", ".", ".", ".", ".", "."],   # row 5 (top)
    ]

    game = GameState(board=board, turn="X")
    game.print_board()

    best_move(game)
    # Expected output:
    # Best move for AI (X): Column 3
    # Predicted score: 7


    ## Note: The expected score may vary based on the depth and heuristic evaluation.
    ## The key point is that the best move should be column 3, which allows X to win immediately.
    ## 


    ## THIS PRODUCT BELONGS TO OMAR NOUH
