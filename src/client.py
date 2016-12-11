#!/usr/bin/env python
import pika
import uuid
import json
from common import construct_message, decode_message, draw_main_board, draw_tracking_board, \
 LIST_SERVERS, LIST_GAMES, JOIN_SERVER, CREATE_GAME, JOIN_GAME, SHOOT, LEAVE_GAME, REMOVE_USER, \
 NO_SHIP, SHIP_NOT_SHOT, SHIP_SHOT, NO_SHIP_SHOT, NOT_SHOT, SHIP_SUNK

class Client(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='127.0.0.1'))

        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='main_exch', type='direct')
        result = self.channel.queue_declare(exclusive=True)  # declare queue
        self.callback_queue = result.method.queue  # access queue declared
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)  # set listen on callback queue

        self.incoming_queue = self.channel.queue_declare(exclusive=True) # declare incoming message queue
        self.incoming_queue = self.incoming_queue.method.queue

        self.channel.basic_consume(self.on_info, queue=self.incoming_queue) # listener on incoming message queue
        self.user_name = None  #TODO > Maybe we should set it at init

    def on_response(self, ch, method, props, body):
        """
        Default response callback. Checks if message id matches and stores message.
        :param ch:
        :param method:
        :param props:
        :param body:
        :return:
        """
        if self.corr_id == props.correlation_id:
            self.response = body
            print('Response received', body)

    def on_info(self, ch, method, props, body):
        """
        Handles information from game.
        :param ch:
        :param method:
        :param props:
        :param body:
        :return:
        """
        print('Message from game:', body)

    def message_direct(self, key, body):
        """
        Takes a key and message and sends it to direct message exchange.
        :param key: Key of the recipient
        :param body: Message to be sent
        :return: Response sent to the callback queue
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        print('Sending message to', key)
        self.channel.basic_publish(exchange='main_exch',
                                   routing_key=key,
                                   properties=pika.BasicProperties(
                                         reply_to=self.callback_queue,
                                         correlation_id=self.corr_id,
                                         ),
                                   body=body)
        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def get_game_servers(self):
        return self.message_direct('LOGIN', LIST_SERVERS)

    def get_game_list(self, server_key):
        return self.message_direct(server_key, LIST_GAMES)
    
    def join_game_server(self, server_key, user_name):
        self.user_name = user_name
        return self.message_direct(server_key, construct_message([JOIN_SERVER, user_name]))

    def create_game(self,server_key, board_size):
        """
        Sends params for game creation to game server
        :param user_name: Necessary for server to know who's creating the game
        :param server_key: Game_server where the game is created
        :param board_size: gameboard size
        :return
        """
        response  = self.message_direct(server_key, construct_message([CREATE_GAME, self.user_name, board_size]))
        response = decode_message(response)
        game_exchange = response[0]
        print(game_exchange)
        self.channel.queue_bind(exchange=game_exchange,
                        queue=self.incoming_queue,
                        routing_key=self.user_name)
        print('Joined to a game. Incoming queue registered to game exchange.')

    def join_game(self, server_key, game_id):
        """
        Sends join request to game at server. Gets exchange names, makes queues and binds to them.
        :param server_key: Game server to connect to
        :param user_name: Curent user's name
        :param game_id: Game name to connect to
        :return:
        """
        response = self.message_direct(server_key, construct_message([JOIN_GAME, self.user_name, game_id]))
        response = decode_message(response)
        game_exchange = response[0]
        print(game_exchange)
        self.channel.queue_bind(exchange=game_exchange,
                        queue=self.incoming_queue,
                        routing_key=self.user_name)
        print('Joined to gameserver. Incoming queue registered to game exchange.')
        return
    
    def shoot(self, game_key, x, y):
        return self.message_direct(game_key, construct_message([SHOOT, x, y]))
    
    def leave_game(self, game_key):
        return self.message_direct(game_key, LEAVE_GAME)

    def remove_user(self, game_key, user_name):
        return self.message_direct(game_key, construct_message([REMOVE_USER, user_name]))



if __name__ == "__main__":
    client = Client()
    
    print("Requesting game servers.")
    response = json.loads(client.get_game_servers())
    print('NAME\tKEY')
    for server, r_key in response.items():
        print('{}\t{}'.format(server, r_key))
    
    while True:
        srv = raw_input("Which server to join?")
        srv_key = response[srv]
        if srv_key is not None:
            break
    
    while True:
        user_name = raw_input('Enter user name')
        avail_games = json.loads(client.join_game_server(srv_key, user_name))
        if not avail_games == 'NOK':
            break
    
    client.user_name = user_name

    print('Available games')
    for game_name in avail_games:
        print game_name
    
    while True:
        hosting = raw_input("Do you want to join a session or host a new session? [J]/[H]")
        if hosting == 'J' and len(response) > 0:
             while True:
                 game_id = raw_input("Which game?")
                 if game_id in avail_games:
                      client.join_game(srv_key, game_id)
                      break
             break
        if hosting == 'H':
            board_size = raw_input('Board size?')
            client.create_game(srv_key, int(board_size))
            break



