

MSG_SEP = ';'

def construct_message(args):
	return MSG_SEP.join(args)

def decode_message(message):
	return message.split(MSG_SEP)