MSG_SEP = ';'

LIST_SERVERS = '1'
LIST_GAMES = '2'
JOIN_SERVER = '3'
CREATE_GAME = '4'
JOIN_GAME = '5'
SERVER_ONLINE = '6'
UNKNOWN_REQUEST = '7'
SHOOT = '8'
LEAVE_GAME = '9'
REMOVE_USER = '10'
USER_JOINED = '11'
START_GAME = '12'
NOK = '13'
OK = '14'
BOARDS = '15'
YOUR_TURN = '16'
YOUR_HITS = '17'
HIT = '18'
GAME_OVER = '19'
SESSION_END = '19'

#values for main board
NO_SHIP = 0
SHIP_NOT_SHOT = 1
SHIP_SHOT = 2
NO_SHIP_SHOT = 3

#extra value for tracking board plus SHIP_SHOT, NO_SHIP_SHOT
NOT_SHOT = 4
SHIP_SUNK = 5

#values for mode
ONLINE = 'online'
SPECTATOR = 'spectator'
DISCONNECTED = 'disconnected'

def construct_message(args):
	return MSG_SEP.join(map(str,args))

def decode_message(message):
	return message.split(MSG_SEP)

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
            if board[y][x] == NO_SHIP:
                temp.append('.')
            elif board[y][x] == SHIP_NOT_SHOT:
                temp.append('#')
            elif board[y][x] == SHIP_SHOT:
                temp.append('#')
            elif board[y][x] == NO_SHIP_SHOT:
                temp.append('.')
        print "  ".join(temp)
    return

def draw_tracking_board(board):
    size = len(board)
    print(size)
    temp = []
    temp.append("\\")
    for e in range(0, size):
        temp.append(str(e))
    print "  ".join(temp)
    for y in range(0, size):
        temp = []
        temp.insert(0, str(y))
        for x in range(0, size):
            if board[y][x] == NO_SHIP:
                temp.append('.')
            elif board[y][x] == SHIP_NOT_SHOT:
                temp.append('.')
            elif board[y][x] == SHIP_SHOT:
                temp.append('x')
            elif board[y][x] == NO_SHIP_SHOT:
                temp.append('o')
            elif board[y][x] == NOT_SHOT:
                temp.append('.')
            elif board[y][x] == SHIP_SUNK:
                temp.append('x')
        print "  ".join(temp)