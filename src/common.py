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

#values for main board
NO_SHIP = '0'
SHIP_NOT_SHOT = '1'
SHIP_SHOT = '2'
NO_SHIP_SHOT = '3'

#extra value for tracking board plus SHIP_SHOT, NO_SHIP_SHOT
NOT_SHOT = '4'
SHIP_SUNK = '5'

def construct_message(args):
	return MSG_SEP.join(args)

def decode_message(message):
	return message.split(MSG_SEP)