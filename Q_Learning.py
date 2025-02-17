# import the necessary modules
import numpy as np
import sys
from collections import defaultdict
import pickle
from time import sleep, time

# we can input different modes behind our demand: "play" or "train"
# for here we catch the first argument of the command line
if sys.argv[1] == "p":
    mode = "play"
if sys.argv[1] == "t":
    mode = "train"

# if we are in training mode, we need to import the snake_training module
# otherwise, we import the snake module
# in order to improve the training speed, we can use the snake_training
if mode == "play":
    import snake_show
else:
    import snake_training

# setting the reward and penalty values
# if we eat the food, we get a reward of 50000000
# if we get over the game, we get a penalty of -10000
# if we eat a medicine, we get a penalty of -10
rewardKill =  -10000
rewardScore = 50000000
rewardDeleteBodyScore = -100

# alpha is the learning rate
# alphaD is the decay factor of the learning rate
alpha = 0.1
alphaD = 1
# discount factor
gamma = 0.9

# e is the randomness
# ed is the decay factor of e
if mode == "play":
    e = 0.0001
    ed = 1
    emin = 0.0001
else:
    e = 0.9
    ed = 1.3
    emin = 0.0001

# open the old file if we have one
# otherwise, create a new file
try:
    with open("Q\Q.pickle", "rb") as file:
        Q = defaultdict(lambda: [0,0,0,0], pickle.load(file))
except:
    Q = defaultdict(lambda: [0,0,0,0])  #(UP,LEFT,DOWN,RIGHT)

lastMoves = ""
# we need this file to let the params become state. In order to save state to the q-table
def paramsToState(params):
    global lastMoves

    ################# relativeFoodPosition (where is the food relative to the body) ###################
    relativeFoodPostion = [0,0,0,0,0,0]

    if (params["food_pos"][0] - params["snake_pos"][0]) > 0:        #foodRight
        relativeFoodPostion[0] = 1
    if (params["food_pos"][0] - params["snake_pos"][0]) < 0 :       #foodLeft
        relativeFoodPostion[1] = 1
    if ((params["food_pos"][0] - params["snake_pos"][0]) == 0):     #foodXMiddle
        relativeFoodPostion[2] = 1

    if (params["food_pos"][1] - params["snake_pos"][1]) > 0:        #foodDown
        relativeFoodPostion[3] = 1
    if (params["food_pos"][1] - params["snake_pos"][1]) < 0 :       #foodTop
       relativeFoodPostion[4] = 1
    if ((params["food_pos"][1] - params["snake_pos"][1]) == 0):     #foodYMiddle
        relativeFoodPostion[5] = 1

    rFP = ""
    for x in relativeFoodPostion:
        rFP += str(x)

    ################# relativeSpecialFoodPostion (where is the special food relative to the body) ###################
    relativeSpecialFoodPostion = [0, 0, 0, 0, 0, 0]

    if (params["special_food_pos"][0] - params["snake_pos"][0]) > 0:  # foodRight
        relativeSpecialFoodPostion[0] = 1
    if (params["special_food_pos"][0] - params["snake_pos"][0]) < 0:  # foodLeft
        relativeSpecialFoodPostion[1] = 1
    if ((params["special_food_pos"][0] - params["snake_pos"][0]) == 0):  # foodXMiddle
        relativeSpecialFoodPostion[2] = 1

    if (params["special_food_pos"][1] - params["snake_pos"][1]) > 0:  # foodDown
        relativeSpecialFoodPostion[3] = 1
    if (params["special_food_pos"][1] - params["snake_pos"][1]) < 0:  # foodTop
        relativeSpecialFoodPostion[4] = 1
    if ((params["special_food_pos"][1] - params["snake_pos"][1]) == 0):  # foodYMiddle
        relativeSpecialFoodPostion[5] = 1

    rSFP = ""
    for x in relativeSpecialFoodPostion:
        rSFP += str(x)

    ################# relativeDeletedBodyFoodPostion (where is the deleted body food relative to the body) ###################
    relativeDeletedBodyFoodPostion = [0, 0, 0, 0, 0, 0]

    if (params["delete_body_food_pos"][0] - params["snake_pos"][0]) > 0:  # foodRight
        relativeDeletedBodyFoodPostion[0] = 1
    if (params["delete_body_food_pos"][0] - params["snake_pos"][0]) < 0:  # foodLeft
        relativeDeletedBodyFoodPostion[1] = 1
    if ((params["delete_body_food_pos"][0] - params["snake_pos"][0]) == 0):  # foodXMiddle
        relativeDeletedBodyFoodPostion[2] = 1

    if (params["delete_body_food_pos"][1] - params["snake_pos"][1]) > 0:  # foodDown
        relativeDeletedBodyFoodPostion[3] = 1
    if (params["delete_body_food_pos"][1] - params["snake_pos"][1]) < 0:  # foodTop
        relativeDeletedBodyFoodPostion[4] = 1
    if ((params["delete_body_food_pos"][1] - params["snake_pos"][1]) == 0):  # foodYMiddle
        relativeDeletedBodyFoodPostion[5] = 1

    rDBFP = ""
    for x in relativeDeletedBodyFoodPostion:
        rDBFP += str(x)

    ################# ScreenDanger (at the edge of the screen?) ###################

    screenDanger = [0,0,0,0]
    if(params["screenSizeX"] - params["snake_pos"][0] == 10):                               #dangerRight
        screenDanger[0] = 1
    if(params["screenSizeX"] - params["snake_pos"][0] == params["screenSizeX"]):            #dangerLeft
        screenDanger[1] = 1
    if(params["screenSizeY"] - params["snake_pos"][1] == 10):                               #dangerBottom
        screenDanger[2] = 1
    if(params["screenSizeY"] - params["snake_pos"][1] == params["screenSizeY"]):            #dangerTop
        screenDanger[3] = 1

    sD = ""
    for x in screenDanger:
        sD += str(x)

    ################# Danger Body (is body reachable to bite?) ###################

    snake_body = []
    skip = 0
    for pos in params["snake_body"]:                # ignore the first 4 body parts
        if (skip > 3):
             snake_body.append(pos)
        skip+=1

    bodyDanger = [0,0,0,0]
    for bodyPart in snake_body:
        # print bodyPart
        if(params["snake_pos"][0] - bodyPart[0] == 0 and params["snake_pos"][1] - bodyPart[1] == 10 ):  #BodyPartUp
            bodyDanger[0] = 1
        if(params["snake_pos"][0] - bodyPart[0] == 0 and params["snake_pos"][1] - bodyPart[1] == -10 ): #BodypartDown
            bodyDanger[1] = 1
        if(params["snake_pos"][0] - bodyPart[0] == 10 and params["snake_pos"][1] - bodyPart[1] == 0 ):  #BodyPartLeft
            bodyDanger[2] = 1
        if(params["snake_pos"][0] - bodyPart[0] == -10 and params["snake_pos"][1] - bodyPart[1] == 0 ): #BodypartRight
            bodyDanger[3] = 1


    bD = ""
    for x in bodyDanger:
        bD += str(x)

    direction = ""
    dx = params["snake_body"][1][0] - params["snake_body"][0][0]
    dy = params["snake_body"][1][1] - params["snake_body"][0][1]

    if dx == -10 and dy == 0:
        # Moving right
        direction="0"
    if dx == 10 and dy == 0:
        # Moving left
        direction="1"
    if dx == 0 and dy == 10:
        # Moving up
        direction="2"
    if dx == 0 and dy == -10:
        # Moving down
        direction="3"


    # we save the state as a string, which consists of the relativeFoodPosition, ScreenDanger, DangerBody, direction, relativeSpecialFoodPosition, relativeDeletedBodyFoodPosition
    # state can save the current situation of the game
    # with the q-table, we can predict the best action for the current situation
    state = rFP + "_" + sD + "_" + bD + "_" + direction + "_" + rSFP + "_" + rDBFP
    return state

# initialize variables
oldState = None
oldAction = None
gameCounter = 0
gameScores = []

# emulate function is called by the snake module to get the next action
def emulate(params):
    # record the last moves
    global oldState
    global oldAction

    state = paramsToState(params)
    estReward = Q[state]

    prevReward = Q[oldState]

    index = 0
    if oldAction == 'U':
        index = 0
    if oldAction == 'L':
        index = 1
    if oldAction == 'D':
        index = 2
    if oldAction == 'R':
        index = 3

    # if we don't eat the food, we will get more penalty
    reward = (0 -params["moveSinceScore"]) / 50

    prevReward[index] = (1 - alpha) * prevReward[index] + \
                      alpha * (reward + gamma * max(estReward) )

    Q[oldState] = prevReward

    oldState = state
    # basedOnQ choice based on Q-table
    # basedOnQ equals false means that random choice based on e
    basedOnQ = np.random.choice([True, False], p=[1-e,e])

    if basedOnQ == False:
        choice = np.random.choice(['U','L','D','R'], p=[0.25, 0.25,0.25,0.25])
        oldAction = choice
        return choice
    else:
        if estReward[0] > estReward[1] and estReward[0] > estReward[2] and estReward[0] > estReward[3]:
            oldAction = 'U'
            return 'U'
        if estReward[1] > estReward[0] and estReward[1] > estReward[2] and estReward[1] > estReward[3]:
            oldAction = 'L'
            return 'L'
        if estReward[2] > estReward[0] and estReward[2] > estReward[1] and estReward[2] > estReward[3]:
            oldAction = 'D'
            return 'D'
        if estReward[3] > estReward[0] and estReward[3] > estReward[1] and estReward[3] > estReward[2]:
            oldAction = 'R'
            return 'R'
        else:
            choice = np.random.choice(['U','L','D','R'], p=[0.25, 0.25,0.25,0.25])
            oldAction = choice
            return choice

# initialize variables
start = 0
end = 0

# onGameOver function is called by the snake module when the game is over
# we will update the Q-table and save it as a pickle file
def onGameOver(score, moves):
    global oldState
    global oldAction
    global gameCounter
    global alpha, e, ed
    global start, end

    gameScores.append(score)

    # update Q of previous state
    prevReward = Q[oldState]

    if oldAction == None:
        index = 0
    if oldAction == 'U':
        index = 0
    if oldAction == 'L':
        index = 1
    if oldAction == 'D':
        index = 2
    if oldAction == 'R':
        index = 3

    prevReward[index] = (1 - alpha) * prevReward[index] + \
                        alpha * rewardKill

    Q[oldState] = prevReward

    oldState = None
    oldAction = None

    # save Q as pickle file
    if gameCounter % 200 == 0:
        with open("Q/" + "Q" + ".pickle","wb" ) as file:
            pickle.dump(dict(Q), file)
        print("+++++++++ Pickle saved +++++++++")

    # print some stats
    if gameCounter % 100 == 1:
        end = time()
        timeD = end - start
        print (str(gameCounter)+ " : " + "\t" + 'meanScore: ' +  str(np.mean(gameScores[-100:])) + "| HighScore: " + str(np.max(gameScores)) + \
              '| moves: ' + str(np.mean(moves[-100:])) + "| time for 10 games: " + str(round(timeD*10)/100))
        start = time()

    # print hyperparameters
    if gameCounter % 100 == 0:
        print ("a:", alpha)
        print ("e:", e)
        print ("g:", gamma)

    # decrease alpha / e over time (moves)
    if gameCounter % 100 == 0:
        alpha = alpha * alphaD
        if e > emin:
            e = e / ed

    gameCounter += 1

# onScore function is called by the snake module when the snake eats the food
# update the Q-table
def onScore(params):
    global oldState
    global oldAction
    global gameCounter

    state = paramsToState(params)

    estReward = Q[state]

    prevReward = Q[oldState]

    if oldAction == 'U':
        index = 0
    if oldAction == 'L':
        index = 1
    if oldAction == 'D':
        index = 2
    if oldAction == 'R':
        index = 3

    prevReward[index] = (1 - alpha) * prevReward[index] + \
                      alpha * (rewardScore + gamma * max(estReward) )

    Q[oldState] = prevReward

# deleteScore function is called by the snake module when the snake eats the medicine
# update the Q-table
def deleteScore(params):
    global oldState
    global oldAction
    global gameCounter

    state = paramsToState(params)

    estReward = Q[state]

    prevReward = Q[oldState]

    if oldAction == 'U':
        index = 0
    if oldAction == 'L':
        index = 1
    if oldAction == 'D':
        index = 2
    if oldAction == 'R':
        index = 3

    prevReward[index] = (1 - alpha) * prevReward[index] + \
                        alpha * (rewardDeleteBodyScore + gamma * max(estReward))

    Q[oldState] = prevReward

# if our mode is "play", we call the main function of the snake_show module(showcase function)
# otherwise, we call the main function of the snake_training module(train function)
if mode == "play":
    snake_show.main(emulate, onGameOver, onScore, deleteScore)
else:
    snake_training.main(emulate, onGameOver, onScore, deleteScore)

