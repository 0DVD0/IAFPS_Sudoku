from solver import *
from grid import *
from measures import *
import sys


def display_message(screen, font, message, color=(255, 255, 255), duration=2000):
    message_area = pygame.Rect(0, SCREEN_HEIGHT - 120, SCREEN_WIDTH, 120)
    pygame.draw.rect(screen, (0, 0, 0), message_area)

    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
    screen.blit(text, text_rect)
    pygame.display.update(message_area)
    pygame.time.wait(duration)
    pygame.draw.rect(screen, (0, 0, 0), message_area)
    pygame.display.update(message_area)


def select_difficulty(screen, font):
    running = True
    selected = 0
    text_color = (255, 255, 255)
    highlight_color = (0, 128, 255)
    messages = ['Press 1 for Easy', 'Press 2 for Medium', 'Press 3 for Hard']

    while running:
        screen.fill((0, 0, 0))

        for i, message in enumerate(messages):
            option_color = text_color if i != selected else highlight_color
            text = font.render(message, True, option_color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 150 + i * 50))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(messages)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(messages)
                elif event.key == pygame.K_RETURN:
                    return ['Easy', 'Medium', 'Hard'][selected]
                elif event.key == pygame.K_1:
                    return 'Easy'
                elif event.key == pygame.K_2:
                    return 'Medium'
                elif event.key == pygame.K_3:
                    return 'Hard'


def draw_grid(screen, font, board, selected, initial_positions):
    for row in range(9):
        for col in range(9):
            cell_x = col * BLOCK_SIZE
            cell_y = row * BLOCK_SIZE
            rect = pygame.Rect(cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE)

            if selected == (row, col):
                pygame.draw.rect(screen, (50, 50, 200), rect)
            else:
                pygame.draw.rect(screen, (0, 0, 0), rect)

            val = board[row][col]
            if val != 0:
                text_color = (255, 255, 255) if (row, col) in initial_positions else (0, 128, 255)
                text = font.render(str(val), True, text_color)
                text_rect = text.get_rect(center=(cell_x + BLOCK_SIZE // 2, cell_y + BLOCK_SIZE // 2))
                screen.blit(text, text_rect)

            pygame.draw.rect(screen, (255, 255, 255), rect, 1)

    for x in range(0, GRID_SIZE + 1, BLOCK_SIZE * 3):
        pygame.draw.line(screen, (255, 255, 255), (x, 0), (x, GRID_SIZE), 3)
        pygame.draw.line(screen, (255, 255, 255), (0, x), (GRID_SIZE, x), 3)

    pygame.display.update()


def draw_number_buttons(screen, font, selected_number):
    x = GRID_SIZE + 10
    y_start = 10
    for number in range(1, 10):
        rect = pygame.Rect(x, y_start + (number - 1) * (BUTTON_HEIGHT + 10), BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(screen, (50, 50, 50), rect)
        if number == selected_number:
            pygame.draw.rect(screen, (0, 128, 255), rect, 2)
        text = font.render(str(number), True, (255, 255, 255))
        screen.blit(text, (rect.x + 30, rect.y + 5))


def draw_algorithm_buttons(screen, font, algo_buttons):
    start_x = (SCREEN_WIDTH - (3 * BUTTON_WIDTH + 2 * BUTTON_GAP)) // 2
    start_y = SCREEN_HEIGHT - BUTTON_AREA_HEIGHT + 10
    for idx, button in enumerate(algo_buttons):
        rect = pygame.Rect(start_x + idx * (BUTTON_WIDTH + BUTTON_GAP), start_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(screen, (50, 50, 50), rect)
        text = font.render(button, True, (255, 255, 255))
        screen.blit(text, (rect.x + 10, rect.y + 5))


def handle_mouse_events(event, board, selected, selected_number, font, screen, algo_funcs, initial_positions):
    pos = pygame.mouse.get_pos()

    if pos[0] < GRID_SIZE and pos[1] < GRID_SIZE:
        if event.type == pygame.MOUSEBUTTONDOWN:
            selected = (pos[1] // BLOCK_SIZE, pos[0] // BLOCK_SIZE)
            if selected_number and board[selected[0]][selected[1]] == 0:
                if is_valid(board, selected_number, selected[0], selected[1]):
                    board[selected[0]][selected[1]] = selected_number
                    draw_grid(screen, font, board, selected, initial_positions)
                    pygame.display.update()
                else:
                    display_message(screen, font, "Invalid move!", color=(255, 0, 0), duration=500)
            elif event.button == 3:
                if selected not in initial_positions:
                    board[selected[0]][selected[1]] = 0
                    draw_grid(screen, font, board, selected, initial_positions)
                    pygame.display.update()

    elif event.type == pygame.KEYDOWN:
        if selected is None:
            selected = (0, 0)

        row, col = selected
        if event.key == pygame.K_UP:
            row = (row - 1) % 9
        elif event.key == pygame.K_DOWN:
            row = (row + 1) % 9
        elif event.key == pygame.K_LEFT:
            col = (col - 1) % 9
        elif event.key == pygame.K_RIGHT:
            col = (col + 1) % 9

        selected = (row, col)
        draw_grid(screen, font, board, selected, initial_positions)
        pygame.display.update()

        if event.key in [pygame.K_BACKSPACE, pygame.K_DELETE]:
            if selected and selected not in initial_positions:
                board[selected[0]][selected[1]] = 0
                draw_grid(screen, font, board, selected, initial_positions)
                pygame.display.update()

    elif pos[0] > GRID_SIZE and pos[1] < SCREEN_HEIGHT - BUTTON_AREA_HEIGHT:
        number_idx = (pos[1] - 10) // (BUTTON_HEIGHT + 10)
        if 0 <= number_idx < 9:
            selected_number = number_idx + 1

    elif SCREEN_HEIGHT - BUTTON_AREA_HEIGHT <= pos[1] <= SCREEN_HEIGHT:
        button_idx = (pos[0] - ((SCREEN_WIDTH - (3 * BUTTON_WIDTH + 2 * BUTTON_GAP)) // 2)) // (
                BUTTON_WIDTH + BUTTON_GAP)
        if 0 <= button_idx < len(algo_funcs):
            algo_func = algo_funcs[button_idx]
            if algo_func:
                algo_func(board, screen, lambda s, f, b, sel: draw_grid(s, f, b, sel, initial_positions), font, 100)
                pygame.display.update()
                display_message(screen, font, "Puzzle Solved!", duration=500)
    return selected, selected_number


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sudoku Solver")
    font = pygame.font.Font(None, 40)
    algo_buttons = ["Backtracking", "Constraint", "Rule-based"]
    algo_funcs = [solve_with_backtracking, solve_with_constraint_propagation, solve_with_rule_based]

    while True:
        difficulty = select_difficulty(screen, font)
        board, initial_positions = generate_board(difficulty)
        selected = (0, 0)
        selected_number = None
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        board, initial_positions = generate_board(difficulty)
                        selected = (0, 0)
                        selected_number = None
                        display_message(screen, font, "New puzzle generated", duration=500)
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        selected, selected_number = handle_mouse_events(
                            event, board, selected, selected_number, font, screen, algo_funcs, initial_positions
                        )
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    selected, selected_number = handle_mouse_events(
                        event, board, selected, selected_number, font, screen, algo_funcs, initial_positions
                    )

            draw_grid(screen, font, board, selected, initial_positions)
            draw_number_buttons(screen, font, selected_number)
            draw_algorithm_buttons(screen, font, algo_buttons)
            pygame.display.update()


if __name__ == "__main__":
    main()
