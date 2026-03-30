import pygame
import random
import asyncio

# Ініціалізація
pygame.init()
WIDTH = 400
HEIGHT = 500
timer = pygame.time.Clock()
fps = 60

# Використовуємо None для шрифтів
font = pygame.font.Font(None, 24)

colors = {0: (204, 192, 179), 2: (238, 228, 218), 4: (237, 224, 200), 8: (242, 177, 121),
          16: (245, 149, 99), 32: (246, 124, 95), 64: (246, 94, 59), 128: (237, 207, 114),
          256: (237, 204, 97), 512: (237, 200, 80), 1024: (237, 197, 62), 2048: (237, 194, 46),
          'light text': (249, 246, 242), 'dark text': (119, 110, 101),
          'other': (0, 0, 0), 'bg': (187, 173, 160)}


def draw_over(screen):
    pygame.draw.rect(screen, 'black', [50, 50, 300, 100], 0, 10)
    game_over_text1 = font.render('Game Over!', True, 'white')
    game_over_text2 = font.render('Tap to Restart', True, 'white')
    screen.blit(game_over_text1, (130, 65))
    screen.blit(game_over_text2, (110, 105))


def take_turn(direc, board, score):
    merged = [[False for _ in range(4)] for _ in range(4)]
    if direc == 'UP':
        for i in range(4):
            for j in range(4):
                shift = 0
                if i > 0:
                    for q in range(i):
                        if board[q][j] == 0: shift += 1
                    if shift > 0:
                        board[i - shift][j] = board[i][j]
                        board[i][j] = 0
                    if i - shift - 1 >= 0:
                        if board[i - shift - 1][j] == board[i - shift][j] and not merged[i - shift - 1][j] and not \
                        merged[i - shift][j]:
                            board[i - shift - 1][j] *= 2
                            score += board[i - shift - 1][j]
                            board[i - shift][j] = 0
                            merged[i - shift - 1][j] = True
    elif direc == 'DOWN':
        for i in range(3):
            for j in range(4):
                shift = 0
                for q in range(i + 1):
                    if board[3 - q][j] == 0: shift += 1
                if shift > 0:
                    board[2 - i + shift][j] = board[2 - i][j]
                    board[2 - i][j] = 0
                if 3 - i + shift <= 3:
                    if board[2 - i + shift][j] == board[3 - i + shift][j] and not merged[3 - i + shift][j] and not \
                    merged[2 - i + shift][j]:
                        board[3 - i + shift][j] *= 2
                        score += board[3 - i + shift][j]
                        board[2 - i + shift][j] = 0
                        merged[3 - i + shift][j] = True
    elif direc == 'LEFT':
        for i in range(4):
            for j in range(4):
                shift = 0
                for q in range(j):
                    if board[i][q] == 0: shift += 1
                if shift > 0:
                    board[i][j - shift] = board[i][j]
                    board[i][j] = 0
                if j - shift - 1 >= 0:
                    if board[i][j - shift] == board[i][j - shift - 1] and not merged[i][j - shift - 1] and not \
                    merged[i][j - shift]:
                        board[i][j - shift - 1] *= 2
                        score += board[i][j - shift - 1]
                        board[i][j - shift] = 0
                        merged[i][j - shift - 1] = True
    elif direc == 'RIGHT':
        for i in range(4):
            for j in range(2, -1, -1):
                if board[i][j] == 0: continue
                k = j
                while k < 3 and board[i][k + 1] == 0:
                    board[i][k + 1] = board[i][k]
                    board[i][k] = 0
                    k += 1
                if k < 3 and board[i][k + 1] == board[i][k] and not merged[i][k + 1] and not merged[i][k]:
                    board[i][k + 1] *= 2
                    score += board[i][k + 1]
                    board[i][k] = 0
                    merged[i][k + 1] = True
    return board, score


def new_pieces(board):
    count = 0
    while any(0 in row for row in board) and count < 1:
        row, col = random.randint(0, 3), random.randint(0, 3)
        if board[row][col] == 0:
            count += 1
            board[row][col] = 4 if random.randint(1, 10) == 10 else 2
    return board, not any(0 in row for row in board)


def draw_board(screen, score, high_score):
    pygame.draw.rect(screen, colors['bg'], [0, 0, 400, 400], 0, 10)
    score_text = font.render(f'Score: {score}', True, 'black')
    high_score_text = font.render(f'High Score: {high_score}', True, 'black')
    screen.blit(score_text, (10, 410))
    screen.blit(high_score_text, (10, 450))


def draw_pieces(screen, board):
    for i in range(4):
        for j in range(4):
            value = board[i][j]
            # ВИПРАВЛЕНО: тепер беремо конкретний колір зі словника
            value_color = colors if value > 8 else colors
            color = colors.get(value, colors['other'])
            pygame.draw.rect(screen, color, [j * 95 + 20, i * 95 + 20, 75, 75], 0, 5)
            if value > 0:
                val_font = pygame.font.Font(None, 35)
                value_text = val_font.render(str(value), True, value_color)
                text_rect = value_text.get_rect(center=(j * 95 + 57, i * 95 + 57))
                screen.blit(value_text, text_rect)


async def main():
    # Ініціалізація екрана всередині main для стабільності в браузері
    screen = pygame.display.set_mode([WIDTH, HEIGHT])

    board_values = [[0 for _ in range(4)] for _ in range(4)]
    game_over = False
    spawn_new = True
    init_count = 0
    direction = ''
    score = 0
    high_score = 0
    run = True

    while run:
        screen.fill('gray')
        draw_board(screen, score, high_score)
        draw_pieces(screen, board_values)

        if spawn_new or init_count < 2:
            board_values, _ = new_pieces(board_values)
            spawn_new = False
            init_count += 1

        if direction != '':
            board_values, score = take_turn(direction, board_values, score)
            direction = ''
            spawn_new = True

        if game_over:
            draw_over(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    direction = 'UP'
                elif event.key == pygame.K_DOWN:
                    direction = 'DOWN'
                elif event.key == pygame.K_LEFT:
                    direction = 'LEFT'
                elif event.key == pygame.K_RIGHT:
                    direction = 'RIGHT'
                if game_over and event.key == pygame.K_RETURN:
                    board_values, score, game_over, spawn_new, init_count = [[0 for _ in range(4)] for _ in
                                                                             range(4)], 0, False, True, 0

            if event.type == pygame.MOUSEBUTTONUP:
                x, y = event.pos
                if game_over:
                    board_values, score, game_over, spawn_new, init_count = [[0 for _ in range(4)] for _ in
                                                                             range(4)], 0, False, True, 0
                else:
                    if y < 150:
                        direction = 'UP'
                    elif y > 350:
                        direction = 'DOWN'
                    elif x < 150:
                        direction = 'LEFT'
                    elif x > 250:
                        direction = 'RIGHT'

        if score > high_score:
            high_score = score

        pygame.display.flip()
        await asyncio.sleep(0)
        timer.tick(fps)

    pygame.quit()


asyncio.run(main())
