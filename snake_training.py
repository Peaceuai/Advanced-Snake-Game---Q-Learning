# import the necessary libraries
import pygame, sys, time, random
import numpy as np
from time import sleep

# this version could be used for training the agent. It can improve our efficiencies of training the agent.

# setting the screen size and some other parameters
screenSize = {'x': 500,'y':500}
FPS = 100
direction = 'RIGHT'
change_to = direction
# define some colors
colors = {
    'black': pygame.Color(0, 0, 0),
    'white': pygame.Color(255, 255, 255),
    'red': pygame.Color(255, 0, 0),
    'green':pygame.Color(0, 255, 0),
    'darkGreen':pygame.Color(50, 200, 50),
    'blue': pygame.Color(0, 0, 255)
}

# initializing the food's position(three foods in total)
init_pos_x = random.randrange(1, (screenSize['x']//10)) * 10
init_pos_y = random.randrange(1, (screenSize['y']//10)) * 10
snake_pos = [init_pos_x, init_pos_y]
snake_body = [[init_pos_x, init_pos_y], [init_pos_x-10, init_pos_y], [init_pos_x-(2*10), init_pos_y]]

food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]
food_spawn = True

# eat this one will game over, so we don't need to spawn it again
special_food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]

delete_body_food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]
delete_body_food_spawn = True

# initialize the game score
score = 0

# if we game over, we need to call this function to start a new game
def newGame():
    # initialize the snake's position and body
    global snake_pos, food_pos, score, food_spawn, snake_body, special_food_pos, delete_body_food_pos,delete_body_food_spawn

    init_pos_x = random.randrange(1, (screenSize['x']//10)) * 10
    init_pos_y = random.randrange(1, (screenSize['y']//10)) * 10

    snake_pos = [init_pos_x, init_pos_y]
    snake_body = [[init_pos_x, init_pos_y], [init_pos_x-10, init_pos_y], [init_pos_x-(2*10), init_pos_y]]

    # initializing the food's position(three foods in total)
    food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]
    food_spawn = True

    special_food_pos = [random.randrange(1, (screenSize['x'] // 10)) * 10,
                        random.randrange(1, (screenSize['y'] // 10)) * 10]

    delete_body_food_pos =  [random.randrange(1, (screenSize['x'] // 10)) * 10,
                        random.randrange(1, (screenSize['y'] // 10)) * 10]
    delete_body_food_spawn = True

    # initialize the game score
    score = 0

# this is the main game entrance, we will call this function in the Q_Learning.py
def main(emulate, onGameOver, onScore, deleteScore):
    # Checks for errors encountered
    check_errors = pygame.init()

    # pygame.init() example output -> (6, 0)
    # second number in tuple gives number of errors
    if check_errors[1] > 0:
        # if we have errors, we exit the program
        sys.exit(-1)
    else:
        pass

    # calling the next function to start the game
    mainGame(emulate, onGameOver, onScore, deleteScore)


# initialize the variables for the game
moveCounter = 0
moves = []
moveSinceScore = 0

def mainGame(emulate, onGameOver, onScore, deleteScore):
    global moveCounter, moves, moveSinceScore
    global food_pos, food_spawn, special_food_pos, delete_body_food_pos, delete_body_food_spawn, snake_body, snake_pos, score, colors, screenSize, direction, change_to

    moveCounter = 0
    while True:
        # calculating the difference between the snake's position and the normal food's position
        diff = [snake_pos[0]-food_pos[0], snake_pos[1] - food_pos[1]]
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
            'diff':diff,
            'special_food_pos_diff':special_food_pos_diff,
            'delete_body_food_pos_diff':delete_body_food_pos_diff,
            'screenSizeX': screenSize['x'],
            'screenSizeY': screenSize['y'],
            'moveSinceScore': moveSinceScore
            }

        ######## emulate keyPresses ##########
        # call emulate function in Q_Learning.py, returns direction
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
            game_over(emulate, colors, score, screenSize, onGameOver)
        elif snake_pos[0] == delete_body_food_pos[0] and snake_pos[1] == delete_body_food_pos[1]:
            score -= 1
            moveSinceScore = 0
            deleteScore(params)
            delete_body_food_spawn = False

        # Snake body growing mechanism
        snake_body.pop()

        # Spawning food on the screen
        if not food_spawn:
            food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]
            for x in snake_body:    #when food spawns in snake body --> new position
                while (food_pos  == x):
                    food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]

        food_spawn = True

        # Spawning food on the screen
        if not delete_body_food_spawn:
            delete_body_food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]
            for x in snake_body:    #when food spawns in snake body --> new position
                while (delete_body_food_pos  == x):
                    delete_body_food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]

        delete_body_food_spawn = True


        # Game Over conditions
        # Getting out of bounds
        if snake_pos[0] < 0 or snake_pos[0] > screenSize['x']-10:
            game_over(emulate, colors, score, screenSize, onGameOver)
        if snake_pos[1] < 0 or snake_pos[1] > screenSize['y']-10:
            game_over(emulate, colors, score, screenSize, onGameOver)

        # Touching the snake body
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                game_over(emulate, colors, score, screenSize, onGameOver)

# game over function
def game_over(emulate, colors, score, screenSize, onGameOver):
    global moves, moveCounter
    moveCounter = 0
    # recording the state to the q-table
    onGameOver(score, moves)

    newGame()
