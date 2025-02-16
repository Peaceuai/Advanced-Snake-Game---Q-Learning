# import the necessary libraries
import pygame, sys, time, random
import numpy as np
from time import sleep

# initialize the pygame module
pygame.init()

# setting the screen size and some other parameters
screenSize = {'x': 500, 'y': 500}
FPS = 100
direction = 'RIGHT'
change_to = direction
# in order to use the image in our project. We need to add this line of code.
pygame.display.set_mode((500, 500))

# define some colors
colors = {
    'black': pygame.Color(0, 0, 0),
    'white': pygame.Color(255, 255, 255),
    'red': pygame.Color(255, 0, 0),
    'shallowGreen': pygame.Color(102, 255, 204),
    'darkGreen': pygame.Color(50, 200, 50),
    'darkBlue': pygame.Color(0, 102, 255),
    'blue': pygame.Color(102, 153, 255),
}

# loadind the images
try:
    food_image = pygame.image.load('image/1.png').convert_alpha()  # normal food
    special_food_image = pygame.image.load('image/2.png').convert_alpha()  # special food(eat this one will game over)
    delete_body_food_image = pygame.image.load('image/3.png').convert_alpha()  # medicine food(eat this one will decrease the score)
except Exception as e:
    print(f"Error loading images: {e}")
    sys.exit(-1)

# initializing the snake's position and body
init_pos_x = random.randrange(1, (screenSize['x'] // 10)) * 10
init_pos_y = random.randrange(1, (screenSize['y'] // 10)) * 10
snake_pos = [init_pos_x, init_pos_y]
snake_body = [[init_pos_x, init_pos_y], [init_pos_x - 10, init_pos_y], [init_pos_x - (2 * 10), init_pos_y]]

# initializing the food's position(three foods in total)
food_pos = [random.randrange(1, (screenSize['x'] // 10)) * 10, random.randrange(1, (screenSize['y'] // 10)) * 10]
food_spawn = True

# eat this one will game over, so we don't need to spawn it again
special_food_pos = [random.randrange(1, (screenSize['x'] // 10)) * 10, random.randrange(1, (screenSize['y'] // 10)) * 10]

delete_body_food_pos = [random.randrange(1, (screenSize['x'] // 10)) * 10, random.randrange(1, (screenSize['y'] // 10)) * 10]
delete_body_food_spawn = True

# initialize the game score
score = 0
# initialize the window
game_window = None

# if we game over, we need to call this function to start a new game
def newGame():
    # initialize the snake's position and body
    global snake_pos, food_pos, score, food_spawn, snake_body, special_food_pos, delete_body_food_pos, delete_body_food_spawn

    init_pos_x = random.randrange(1, (screenSize['x'] // 10)) * 10
    init_pos_y = random.randrange(1, (screenSize['y'] // 10)) * 10

    snake_pos = [init_pos_x, init_pos_y]
    snake_body = [[init_pos_x, init_pos_y], [init_pos_x - 10, init_pos_y], [init_pos_x - (2 * 10), init_pos_y]]

    # initializing the food's position(three foods in total)
    food_pos = [random.randrange(1, (screenSize['x'] // 10)) * 10, random.randrange(1, (screenSize['y'] // 10)) * 10]
    food_spawn = True

    special_food_pos = [random.randrange(1, (screenSize['x'] // 10)) * 10,
                        random.randrange(1, (screenSize['y'] // 10)) * 10]

    delete_body_food_pos = [random.randrange(1, (screenSize['x'] // 10)) * 10,
                            random.randrange(1, (screenSize['y'] // 10)) * 10]
    delete_body_food_spawn = True

    # initialize the game score
    score = 0

# this is the main game entrance, we will call this function in the Q_Learning.py
def main(emulate, onGameOver, onScore, deleteScore):
    global game_window

    # Checks for errors encountered
    check_errors = pygame.init()

    # pygame.init() example output -> (6, 0)
    # second number in tuple gives number of errors
    if check_errors[1] > 0:
        # if we have errors, we exit the program
        sys.exit(-1)

    # setting the window caption
    pygame.display.set_caption('Advanced Snake Game')
    # displaying the game window
    game_window = pygame.display.set_mode((screenSize['x'], screenSize['y']))

    # initializing the fps controller
    fps_controller = pygame.time.Clock()
    # calling the next function to start the game
    mainGame(emulate, fps_controller, onGameOver, onScore, deleteScore)

# initialize the variables for the game
moveCounter = 0
moves = []
moveSinceScore = 0

# the main game function
def mainGame(emulate, fps_controller, onGameOver, onScore, deleteScore):
    global moveCounter, moves, moveSinceScore
    global food_pos, food_spawn, special_food_pos, delete_body_food_pos, delete_body_food_spawn, snake_body, snake_pos, score, colors, screenSize, direction, change_to
    global game_window

    moveCounter = 0
    while True:
        # the next line of code is used to control the game by the user
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == ord('w'):
                    change_to = 'UP'
                if event.key == pygame.K_DOWN or event.key == ord('s'):
                    change_to = 'DOWN'
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    change_to = 'LEFT'
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    change_to = 'RIGHT'
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

        # calculating the difference between the snake's position and the normal food's position
        diff = [snake_pos[0] - food_pos[0], snake_pos[1] - food_pos[1]]
        diff = abs(diff[0] + diff[1])

        # calculating the difference between the snake's position and the special food's position
        special_food_pos_diff = [snake_pos[0] - special_food_pos[0], snake_pos[1] - special_food_pos[1]]
        special_food_pos_diff = abs(special_food_pos_diff[0] + special_food_pos_diff[1])

        # calculating the difference between the snake's position and the medicine food's position
        delete_body_food_pos_diff = [snake_pos[0] - delete_body_food_pos[0], snake_pos[1] - delete_body_food_pos[1]]
        delete_body_food_pos_diff = abs(delete_body_food_pos_diff[0] + delete_body_food_pos_diff[1])

        # combine the parameters for the calculation of the q-table
        params = {
            'food_pos': food_pos,
            'special_food_pos': special_food_pos,
            'delete_body_food_pos': delete_body_food_pos,
            'snake_pos': snake_pos,
            'snake_body': snake_body,
            'score': score,
            'diff': diff,
            'special_food_pos_diff': special_food_pos_diff,
            'delete_body_food_pos_diff': delete_body_food_pos_diff,
            'screenSizeX': screenSize['x'],
            'screenSizeY': screenSize['y'],
            'moveSinceScore': moveSinceScore
        }

        ######## emulate keyPresses ##########
        # call emulate function in Q_Learning.py, returns direction
        # if we want to control the snake manually, we can comment the following line
        choosenDirection = emulate(params)

        # calculate the next step
        if choosenDirection == 'U':
            change_to = 'UP'
            moveCounter += 1
            moves.append(moveCounter)
            moveSinceScore += 1
        if choosenDirection == 'D':
            change_to = 'DOWN'
            moveCounter += 1
            moves.append(moveCounter)
            moveSinceScore += 1
        if choosenDirection == 'L':
            change_to = 'LEFT'
            moveCounter += 1
            moves.append(moveCounter)
            moveSinceScore += 1
        if choosenDirection == 'R':
            change_to = 'RIGHT'
            moveCounter += 1
            moves.append(moveCounter)
            moveSinceScore += 1

        # Making sure the snake cannot move in the opposite direction instantaneously
        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'

        # Moving the snake
        if direction == 'UP':
            snake_pos[1] -= 10
        if direction == 'DOWN':
            snake_pos[1] += 10
        if direction == 'LEFT':
            snake_pos[0] -= 10
        if direction == 'RIGHT':
            snake_pos[0] += 10

        # Snake body growing mechanism
        snake_body.insert(0, list(snake_pos))

        # check if the snake ate the food or the special food or the medicine food
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 1
            moveSinceScore = 0
            onScore(params)
            food_spawn = False
        elif snake_pos[0] == special_food_pos[0] and snake_pos[1] == special_food_pos[1]:
            game_over(emulate, colors, score, game_window, screenSize, onGameOver)
        elif snake_pos[0] == delete_body_food_pos[0] and snake_pos[1] == delete_body_food_pos[1]:
            score -= 1
            moveSinceScore = 0
            deleteScore(params)
            delete_body_food_spawn = False

        # Snake body growing mechanism
        snake_body.pop()

        # Spawning food on the screen
        if not food_spawn:
            food_pos = [random.randrange(1, (screenSize['x'] // 10)) * 10, random.randrange(1, (screenSize['y'] // 10)) * 10]
            for x in snake_body:
                while (food_pos == x):
                    food_pos = [random.randrange(1, (screenSize['x'] // 10)) * 10, random.randrange(1, (screenSize['y'] // 10)) * 10]

        food_spawn = True

        # Spawning food on the screen
        if not delete_body_food_spawn:
            delete_body_food_pos = [random.randrange(1, (screenSize['x'] // 10)) * 10, random.randrange(1, (screenSize['y'] // 10)) * 10]
            for x in snake_body:
                while (delete_body_food_pos == x):
                    delete_body_food_pos = [random.randrange(1, (screenSize['x'] // 10)) * 10, random.randrange(1, (screenSize['y'] // 10)) * 10]

        delete_body_food_spawn = True

        game_window.fill(colors['shallowGreen'])

        for index, pos in enumerate(snake_body):
            if index > 0:
                pygame.draw.rect(game_window, colors['blue'], pygame.Rect(pos[0], pos[1], 10, 10))
            else:
                pygame.draw.rect(game_window, colors['darkBlue'], pygame.Rect(pos[0], pos[1], 10, 10))

        # drawing the food on the screen
        game_window.blit(food_image, (food_pos[0], food_pos[1]))
        game_window.blit(special_food_image, (special_food_pos[0], special_food_pos[1]))
        game_window.blit(delete_body_food_image, (delete_body_food_pos[0], delete_body_food_pos[1]))

        # showing the score on the screen
        font = pygame.font.SysFont('arial', 20)
        score_text = font.render(f'Score: {score}', True, colors['black'])
        game_window.blit(score_text, (10, 10))

        # game Over conditions
        # getting out of bounds
        if snake_pos[0] < 0 or snake_pos[0] > screenSize['x'] - 10:
            game_over(emulate, colors, score, game_window, screenSize, onGameOver)
        if snake_pos[1] < 0 or snake_pos[1] > screenSize['y'] - 10:
            game_over(emulate, colors, score, game_window, screenSize, onGameOver)

        # Touching the snake body
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                game_over(emulate, colors, score, game_window, screenSize, onGameOver)

        pygame.display.update()
        fps_controller.tick(FPS)

# game over function
def game_over(emulate, colors, score, game_window, screenSize, onGameOver):
    global moves, moveCounter
    moveCounter = 0
    # recording the state to the q-table
    onGameOver(score, moves)

    game_window.fill(colors['shallowGreen'])
    pygame.display.flip()

    newGame()