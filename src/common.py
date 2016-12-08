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



def construct_message(args):
	return MSG_SEP.join(args)

def decode_message(message):
	return message.split(MSG_SEP)