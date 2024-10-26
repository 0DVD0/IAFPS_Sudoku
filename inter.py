import pygame
import sys
import random
from Backtracking import *
from Constraint_propagation import *
from Measures import *


def generate_random_sudoku():
    """Generate a random Sudoku puzzle by filling the board and removing some cells."""

    def fill_board(board):
        empty = find_empty(board)
        if not empty:
            return True
        row, col = empty

        nums = list(range(1, 10))
        random.shuffle(nums)
        for num in nums:
            if is_valid(board, num, row, col):
                board[row][col] = num
                if fill_board(board):
                    return True
                board[row][col] = 0

        return False

    def remove_numbers(board, attempts=40):
        """Remove numbers from a filled board to create a puzzle with some empty cells."""
        while attempts > 0:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            while board[row][col] == 0:
                row = random.randint(0, 8)
                col = random.randint(0, 8)
            board[row][col] = 0
            attempts -= 1

    # Generate a fully filled board
    board = [[0 for _ in range(9)] for _ in range(9)]
    fill_board(board)

    # Remove numbers to create a playable puzzle
    remove_numbers(board)

    return board


pygame.init()

screen = pygame.display.set_mode((SCREEN_SIZE, TOTAL_HEIGHT))
pygame.display.set_caption("Sudoku")
pygame.font.init()

font = pygame.font.SysFont("Arial", 24)
user_font = pygame.font.SysFont("Arial", 24, bold=True)


class Grid:
    def __init__(self, board):
        self.board = board
        self.selected_number = None
        self.user_inputs = set()
        self.algo_buttons = ["Backtracking", "Constraint Propagation", "Dancing Links (DLX)"]
        self.selected_algo = None
        self.possibilities = self.initialize_possibilities()

    def draw_grid(self):
        screen.fill(WHITE)
        for x in range(0, SCREEN_SIZE, CELL_SIZE):
            pygame.draw.line(screen, BLACK, (x, 0), (x, SCREEN_SIZE), 1)
            pygame.draw.line(screen, BLACK, (0, x), (SCREEN_SIZE, x), 1)
        for x in range(0, SCREEN_SIZE, CELL_SIZE * 3):
            pygame.draw.line(screen, BLACK, (x, 0), (x, SCREEN_SIZE), 2)
            pygame.draw.line(screen, BLACK, (0, x), (SCREEN_SIZE, x), 2)

    def reset_board(self, new_board):
        """Reset the grid with a new board layout."""
        self.board = new_board
        self.user_inputs.clear()
        self.possibilities = self.initialize_possibilities()

    def draw_numbers(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] != 0:
                    if (row, col) in self.user_inputs:
                        text = user_font.render(str(self.board[row][col]), True, USER_INPUT_COLOR)
                    else:
                        text = font.render(str(self.board[row][col]), True, BLACK)
                    screen.blit(text, (col * CELL_SIZE + CELL_SIZE // 3, row * CELL_SIZE + CELL_SIZE // 8))

    def highlight_cell(self, pos):
        if pos[0] < SCREEN_SIZE and pos[1] < SCREEN_SIZE:
            col = pos[0] // CELL_SIZE
            row = pos[1] // CELL_SIZE
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 5)
            return row, col
        return None

    def draw_number_buttons(self):
        for i in range(9):
            button_rect = pygame.Rect(i * CELL_SIZE, SCREEN_SIZE, CELL_SIZE, BUTTON_HEIGHT)
            pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
            text = font.render(str(i + 1), True, WHITE)
            screen.blit(text, (i * CELL_SIZE + CELL_SIZE // 3, SCREEN_SIZE + BUTTON_HEIGHT // 5))
            if button_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect, 2)

        if self.selected_number:
            pygame.draw.rect(screen, USER_INPUT_COLOR,
                             (self.selected_number * CELL_SIZE - CELL_SIZE, SCREEN_SIZE, CELL_SIZE, BUTTON_HEIGHT), 3)

    def select_number(self, pos):
        if SCREEN_SIZE <= pos[1] <= SCREEN_SIZE + BUTTON_HEIGHT:
            col = pos[0] // CELL_SIZE
            self.selected_number = col + 1
            return self.selected_number
        return None

    def place_number(self, pos, selected_number):
        if pos[0] < SCREEN_SIZE and pos[1] < SCREEN_SIZE and selected_number is not None:
            col = pos[0] // CELL_SIZE
            row = pos[1] // CELL_SIZE
            if (row, col) in self.user_inputs or self.board[row][col] == 0:
                # If the number is the same as the selected, clear the cell
                if self.board[row][col] == selected_number:
                    self.board[row][col] = 0
                    self.user_inputs.discard((row, col))
                else:
                    # Otherwise, place the new number
                    self.board[row][col] = selected_number
                    self.user_inputs.add((row, col))

    def draw_algo_buttons(self):
        for i, algo in enumerate(self.algo_buttons):
            button_x = i * (SCREEN_SIZE // len(self.algo_buttons))
            button_y = SCREEN_SIZE + BUTTON_HEIGHT
            button_width = SCREEN_SIZE // len(self.algo_buttons)
            button_rect = pygame.Rect(button_x, button_y, button_width, ALGO_BUTTON_HEIGHT)
            pygame.draw.rect(screen, ALGO_BUTTON_COLOR, button_rect)
            text = font.render(algo, True, WHITE)
            screen.blit(text, (button_x + 10, button_y + 5))
            if self.selected_algo is not None and self.selected_algo == i:
                pygame.draw.rect(screen, USER_INPUT_COLOR, button_rect, 3)
            if button_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, ALGO_BUTTON_HOVER_COLOR, button_rect, 2)

    def select_algo(self, pos):
        if SCREEN_SIZE + BUTTON_HEIGHT <= pos[1] <= TOTAL_HEIGHT:
            col = pos[0] // (SCREEN_SIZE // len(self.algo_buttons))
            self.selected_algo = col
            print(f"Selected Algorithm: {self.algo_buttons[col]}")
            return self.algo_buttons[col]
        return None

    def initialize_possibilities(self):
        possibilities = {}
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] == 0:
                    possibilities[(row, col)] = set(range(1, 10))  # All numbers 1-9 are possible
                else:
                    possibilities[(row, col)] = set()  # No possibilities for filled cells
        return possibilities

    def update_possibilities(self):
        # Update the possibilities for all cells
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] == 0:
                    self.possibilities[(row, col)] = self.find_possibilities(row, col)
                else:
                    self.possibilities[(row, col)] = set()

    def find_possibilities(self, row, col):
        # Find the possible values for a cell
        if self.board[row][col] != 0:
            return set()

        possible_values = set(range(1, 10))

        # Eliminate values based on the row
        for i in range(GRID_SIZE):
            if self.board[row][i] in possible_values:
                possible_values.remove(self.board[row][i])

        # Eliminate values based on the column
        for i in range(GRID_SIZE):
            if self.board[i][col] in possible_values:
                possible_values.remove(self.board[i][col])

        # Eliminate values based on the 3x3 box
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] in possible_values:
                    possible_values.remove(self.board[i][j])

        return possible_values


def main():
    # Generate an initial random board
    initial_board = generate_random_sudoku()
    grid = Grid(initial_board)
    selected = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                # Check if algorithm button is clicked
                if pos[1] > SCREEN_SIZE + BUTTON_HEIGHT:
                    selected_algo = grid.select_algo(pos)
                    if selected_algo:
                        # Generate a new random board for the new algorithm
                        new_board = generate_random_sudoku()
                        grid.reset_board(new_board)

                        if selected_algo == "Backtracking":
                            solve_with_backtracking(grid)
                        elif selected_algo == "Constraint Propagation":
                            solve_with_constraint_propagation(grid)
                        elif selected_algo == "Dancing Links (DLX)":
                            # Add the function call for Dancing Links here if implemented
                            pass

                # Check if number button is clicked
                elif SCREEN_SIZE <= pos[1] <= SCREEN_SIZE + BUTTON_HEIGHT:
                    grid.select_number(pos)

                # Otherwise, try to place the number on the grid
                else:
                    selected = grid.highlight_cell(pos)
                    if selected and grid.selected_number:
                        grid.place_number(pos, grid.selected_number)

        grid.draw_grid()
        grid.draw_numbers()
        grid.draw_number_buttons()
        grid.draw_algo_buttons()

        pygame.display.update()


if __name__ == "__main__":
    main()
