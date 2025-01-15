import pygame
import random
import sys

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 540, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")

# Fonts
FONT = pygame.font.SysFont("comicsans", 40)
SMALL_FONT = pygame.font.SysFont("comicsans", 20)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHTBLUE = (96, 216, 232)
LOCKEDCELLCOLOR = (180, 180, 180)
INCORRECTCELL = (185, 121, 121)
RED = (255, 0, 0)

# Global buttons
hint_button = None
pause_button = None
restart_button = None

class Grid:
    def __init__(self, rows, cols, width, height, board):
        self.rows = rows
        self.cols = cols
        self.cubes = [[Cube(board[i][j], i, j, width, height)
                       for j in range(cols)]
                      for i in range(rows)]
        self.width = width
        self.height = height
        self.selected = None

    def draw(self):
        # Draw grid lines
        gap = self.width / 9
        for i in range(self.rows + 1):
            line_width = 4 if i % 3 == 0 else 1
            pygame.draw.line(SCREEN, BLACK, (0, i * gap), (self.width, i * gap), line_width)
            pygame.draw.line(SCREEN, BLACK, (i * gap, 0), (i * gap, self.height), line_width)

        # Draw cubes
        for row in self.cubes:
            for cube in row:
                cube.draw(SCREEN)

class Cube:
    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False
        self.locked = True if value != 0 else False
        self.incorrect = False

    def draw(self, screen):
        fnt = FONT
        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.locked:
            text = fnt.render(str(self.value), True, BLACK)
        elif self.value != 0:
            color = RED if self.incorrect else BLACK
            text = fnt.render(str(self.value), True, color)
        else:
            text = None

        if text:
            screen.blit(text, (x + (gap / 2 - text.get_width() / 2),
                               y + (gap / 2 - text.get_height() / 2)))

        if self.selected:
            pygame.draw.rect(screen, LIGHTBLUE, (x, y, gap, gap), 3)

def find_empty(board):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                return (i, j)
    return None

def valid(board, num, pos):
    # Check row
    for i in range(len(board[0])):
        if board[pos[0]][i] == num and pos[1] != i:
            return False
    # Check column
    for i in range(len(board)):
        if board[i][pos[1]] == num and pos[0] != i:
            return False
    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x *3, box_x * 3 + 3):
            if board[i][j] == num and (i,j) != pos:
                return False
    return True

def fill_board(board):
    empty = find_empty(board)
    if not empty:
        return True
    else:
        row, col = empty

    numbers = list(range(1, 10))
    random.shuffle(numbers)

    for num in numbers:
        if valid(board, num, (row, col)):
            board[row][col] = num
            if fill_board(board):
                return True
            board[row][col] = 0
    return False

def generate_puzzle(difficulty):
    board = [[0 for _ in range(9)] for _ in range(9)]
    fill_board(board)
    solution = [row[:] for row in board]

    squares = 81
    empties = {'Easy': 30, 'Medium': 40, 'Hard': 50, 'Impossible': 60}
    num_empty = empties.get(difficulty, 30)
    attempts = num_empty

    while attempts > 0:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        while board[row][col] == 0:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
        backup = board[row][col]
        board[row][col] = 0
        attempts -= 1

    return board, solution

def click(pos):
    if pos[0] < WIDTH and pos[1] < HEIGHT - 60:
        gap = WIDTH / 9
        x = pos[0] // gap
        y = pos[1] // gap
        return (int(y), int(x))
    else:
        return None

def difficulty_menu():
    run = True
    while run:
        SCREEN.fill(WHITE)
        title_text = FONT.render('Select Difficulty', True, BLACK)
        SCREEN.blit(title_text, (WIDTH / 2 - title_text.get_width() / 2, 150))

        difficulties = ['Easy', 'Medium', 'Hard', 'Impossible']
        mouse_pos = pygame.mouse.get_pos()
        for idx, diff in enumerate(difficulties):
            x = WIDTH / 2 - 100
            y = 250 + idx * 50
            width = 200
            height = 40
            rect = pygame.Rect(x, y, width, height)
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(SCREEN, LIGHTBLUE, rect)
            else:
                pygame.draw.rect(SCREEN, WHITE, rect)
            pygame.draw.rect(SCREEN, BLACK, rect, 2)
            text = FONT.render(diff, True, BLACK)
            SCREEN.blit(text, (rect.x + (rect.width - text.get_width()) // 2,
                               rect.y + (rect.height - text.get_height()) // 2))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for idx in range(len(difficulties)):
                    x = WIDTH / 2 - 100
                    y = 250 + idx * 50
                    width = 200
                    height = 40
                    rect = pygame.Rect(x, y, width, height)
                    if rect.collidepoint(event.pos):
                        return difficulties[idx]

def get_hint(grid, solution):
    for i in range(9):
        for j in range(9):
            cube = grid.cubes[i][j]
            if cube.value == 0:
                cube.value = solution[i][j]
                cube.locked = True
                return

def draw_hint_button():
    global hint_button
    hint_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 50, 100, 40)
    pygame.draw.rect(SCREEN, LIGHTBLUE, hint_button)
    text = SMALL_FONT.render("Hint", True, BLACK)
    SCREEN.blit(text, (hint_button.x + (hint_button.width - text.get_width()) // 2,
                       hint_button.y + (hint_button.height - text.get_height()) // 2))

def draw_pause_button(paused):
    global pause_button
    pause_text = "Resume" if paused else "Pause"
    pause_button = pygame.Rect(20, HEIGHT - 50, 100, 40)
    pygame.draw.rect(SCREEN, LIGHTBLUE, pause_button)
    text = SMALL_FONT.render(pause_text, True, BLACK)
    SCREEN.blit(text, (pause_button.x + (pause_button.width - text.get_width()) // 2,
                       pause_button.y + (pause_button.height - text.get_height()) // 2))

def draw_restart_button():
    global restart_button
    restart_button = pygame.Rect(WIDTH - 120, HEIGHT - 50, 100, 40)
    pygame.draw.rect(SCREEN, LIGHTBLUE, restart_button)
    text = SMALL_FONT.render("Restart", True, BLACK)
    SCREEN.blit(text, (restart_button.x + (restart_button.width - text.get_width()) // 2,
                       restart_button.y + (restart_button.height - text.get_height()) // 2))

def draw_timer(play_time):
    minutes = play_time // 60
    seconds = play_time % 60
    time_text = SMALL_FONT.render(f"Time: {minutes:02}:{seconds:02}", True, BLACK)
    SCREEN.blit(time_text, (WIDTH - 150, HEIGHT - 50))

def draw_win_message():
    text = FONT.render("You Won!", True, BLACK)
    SCREEN.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_height() / 2))

def draw_pause_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT - 60))
    overlay.set_alpha(200)
    overlay.fill(WHITE)
    SCREEN.blit(overlay, (0, 0))
    text = FONT.render("Paused", True, BLACK)
    SCREEN.blit(text, (WIDTH / 2 - text.get_width() / 2, (HEIGHT - 60) / 2 - text.get_height() / 2))

def valid_move(grid, num, pos):
    # Check row
    for i in range(len(grid.cubes[0])):
        if grid.cubes[pos[0]][i].value == num and pos[1] != i:
            return False
    # Check column
    for i in range(len(grid.cubes)):
        if grid.cubes[i][pos[1]].value == num and pos[0] != i:
            return False
    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x *3, box_x * 3 + 3):
            if grid.cubes[i][j].value == num and (i,j) != pos:
                return False
    return True

def is_full(grid):
    for row in grid.cubes:
        for cube in row:
            if cube.value == 0:
                return False
    return True

def check_win(grid):
    for i in range(9):
        for j in range(9):
            num = grid.cubes[i][j].value
            if not valid_move(grid, num, (i, j)):
                return False
    return True

def main():
    difficulty = difficulty_menu()
    board, solution = generate_puzzle(difficulty)
    grid = Grid(9, 9, WIDTH, HEIGHT - 60, board)
    key = None
    run = True
    start_time = pygame.time.get_ticks()
    paused = False
    won = False

    while run:
        if not paused:
            play_time = (pygame.time.get_ticks() - start_time) // 1000  # Timer in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run= False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if hint_button and hint_button.collidepoint(pos):
                    if not paused:
                        get_hint(grid, solution)
                elif pause_button and pause_button.collidepoint(pos):
                    paused = not paused  # Toggle pause
                elif restart_button and restart_button.collidepoint(pos):
                    main()  # Restart the game
                    return
                elif not paused:
                    clicked = click(pos)
                    if clicked:
                        grid.selected = None
                        row, col = clicked
                        grid.cubes[row][col].selected = True
                        grid.selected = (row, col)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused  # Toggle pause
                if event.key == pygame.K_r:
                    main()  # Restart the game
                    return
                if not paused:
                    if event.key == pygame.K_1:
                        key = 1
                    elif event.key == pygame.K_2:
                        key = 2
                    elif event.key == pygame.K_3:
                        key = 3
                    elif event.key == pygame.K_4:
                        key = 4
                    elif event.key == pygame.K_5:
                        key = 5
                    elif event.key == pygame.K_6:
                        key = 6
                    elif event.key == pygame.K_7:
                        key = 7
                    elif event.key == pygame.K_8:
                        key = 8
                    elif event.key == pygame.K_9:
                        key = 9
                    elif event.key == pygame.K_BACKSPACE:
                        if grid.selected:
                            row, col = grid.selected
                            cube = grid.cubes[row][col]
                            if not cube.locked:
                                cube.value = 0
                                cube.incorrect = False
                    elif event.key == pygame.K_RETURN:
                        pass

        if not paused:
            if grid.selected and key is not None:
                row, col = grid.selected
                cube = grid.cubes[row][col]
                if not cube.locked:
                    cube.value = key
                    if valid_move(grid, cube.value, (row, col)):
                        cube.incorrect = False
                        if is_full(grid):
                            if check_win(grid):
                                won = True
                    else:
                        cube.incorrect = True
                key = None

            # Update display
            SCREEN.fill(WHITE)
            grid.draw()
            draw_timer(play_time)
            draw_hint_button()
            draw_pause_button(paused)
            draw_restart_button()

            if won:
                draw_win_message()
                pygame.display.update()
                pygame.time.delay(3000)
                main()  # Restart the game after winning
                return
        else:
            draw_pause_screen()

        pygame.display.update()

if __name__ == "__main__":
    main()




