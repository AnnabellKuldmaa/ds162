import os
import time
import numpy as np

# here be networksings

# here be UI

# board values
# 0 = empty
# 1 = shot, but no ship
# 2 = ship, not shot
# 3 = ship hit by shot

# clear screen

global board_size

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

# draw boards for user
def draw_main_board(board):
    size = len(board)
    temp = []

    temp.append("\\")
    for e in range(0,size):
        temp.append(str(e))
    print "  ".join(temp)
    for y in range(0,size):
        temp = []
        temp.insert(0, str(y))
        for x in range(0,size):
            if board[y][x] == 0:
                temp.append('.')
            elif board[y][x] == 2:
                temp.append('#')
        print "  ".join(temp)
    return

def draw_tracking_board(board):
    size = len(board)
    print(size)
    temp = []

    temp.append("\\")
    for e in range(0,size):
        temp.append(str(e))
    print "  ".join(temp)
    for y in range(0,size):
        temp = []
        temp.insert(0, str(y))
        for x in range(0,size):
            if board[y][x] == 0:
                temp.append('.')
            elif board[y][x] == 1:
                temp.append('o')
            elif board[y][x] == 2:
                temp.append('.')
            elif board[y][x] == 3:
                temp.append('x')
        print "  ".join(temp)
    return

    return

# shoot
def shoot(x_coord, y_coord, board):
    if board[y_coord][x_coord] == 0:
        print("miss")
        board[y_coord][x_coord] = 1
    elif board[y_coord][x_coord] == 2:
        print("hit")
        board[y_coord][x_coord] = 3
    return board

# show timer
#TODO timer

# test boards
def test_field_array(size):
    board = np.zeros((size, size),dtype=np.uint8)
    return board

def test_ships_array():
    board = np.zeros((10, 10), dtype=np.uint8)
    # submarine
    board[4][4] = 2

    board[5][8] = 2

    # destroyer
    board[3][1] = 2
    board[2][1] = 2

    board[7][9] = 2
    board[7][8] = 2

    # cruiser
    board[9][0] = 2
    board[9][1] = 2
    board[9][2] = 2

    # battleship
    board[0][2] = 2
    board[0][3] = 2
    board[0][4] = 2
    board[0][5] = 2

    # aircraft carrier
    board[6][0] = 2
    board[6][1] = 2
    board[6][2] = 2
    board[6][3] = 2
    board[6][4] = 2

    return board

def start_loop():

    global board_size

    # TODO login

    hosting = raw_input("Are you hosting a game or joining one? [H]/[J]")

        # Commands:
        # start - host-only command to start game
        # shoot x y - shoots at the grid specified by x and y coordinates
        # join - command for joining a game, args currently unknown

        # host logic
    if hosting == 'H':
        board_size = raw_input("Set the size of the playing field: ")
        command = raw_input("What do you want to do? ")
        # TODO give host info about players joining the game

        if command == "start":
            game_loop()


        # join logic
        elif hosting == 'J':
            # TODO joining game
            command = raw_input("What do you want to do? ")


def game_loop():
    print "game started"
    return








if __name__ == "__main__":

    draw_main_board(test_ships_array())
    draw_tracking_board(shoot(3,0,test_ships_array()))
    start_loop()




