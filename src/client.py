#!/usr/bin/env python
import pika
import uuid
import json
import thread
import sys
import readline
from time import sleep
from common import construct_message, decode_message, draw_main_board, draw_tracking_board, \
 LIST_SERVERS, LIST_GAMES, JOIN_SERVER, CREATE_GAME, JOIN_GAME, SHOOT, LEAVE_GAME, REMOVE_USER, \
 NO_SHIP, SHIP_NOT_SHOT, SHIP_SHOT, NO_SHIP_SHOT, NOT_SHOT, SHIP_SUNK, USER_JOINED, START_GAME, \
OK, NOK, YOUR_TURN, YOUR_HITS, BOARDS
from terminal_print import join_reporter, blank_current_readline


class Client(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='127.0.0.1'))

        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='main_exch', type='direct')
        result = self.channel.queue_declare(exclusive=True)  # declare queue
        self.callback_queue = result.method.queue  # access queue declared
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)  # set listen on callback queue

        self.incoming_queue = self.channel.queue_declare() # declare incoming message queue
        self.incoming_queue = self.incoming_queue.method.queue

        self.channel.basic_consume(self.on_info, no_ack=True, queue=self.incoming_queue) # listener on incoming message queue
        self.user_name = None
        self.current_game = None
        self.server_key = None
        self.player_turn = False

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

    def print_message(self, message):
        blank_current_readline()
        print(message)
        sys.stdout.write(readline.get_line_buffer())
        sys.stdout.flush()

    def on_info(self, ch, method, props, body):
        """
        Handles information from game.
        """
        message = decode_message(body)
        req_code = message[0]
        print('RECEIVED: ', req_code)
        if req_code == USER_JOINED:
            self.print_message('Player %s joined your game' % message[1])
        if req_code == BOARDS:
            self.print_message('Your Ships\n' + draw_main_board(json.loads(message[1])) +
                               'Your Shots\n' + draw_tracking_board(json.loads(message[2])))
        if req_code == YOUR_TURN:
            self.print_message('Your turn!')
            self.player_turn = True
        if req_code == YOUR_HITS:
            message = 'Your Hits:\n'
            for hit in message[1:]:
                message += hit + '\n'
            self.print_message(message)
            #print(self.determine_godlikeness(message[1:]))

    def determine_godlikeness(self, hits):
        if len(hits) == 2:
            return 'DOUBLE KILL!'
        if len(hits) == 3:
            return 'DOMINATING!'
        if len(hits) > 3:
            return 'GODLIKE!'

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

    def get_game_list(self):
        return self.message_direct(self.server_key, LIST_GAMES)
    
    def join_game_server(self, user_name):
        self.user_name = user_name
        return self.message_direct(self.server_key, construct_message([JOIN_SERVER, user_name]))

    def create_game(self, board_size):
        """
        Sends params for game creation to game server. Connects client to exchanges and stores the joined game key
        :param user_name: Necessary for server to know who's creating the game
        :param server_key: Game_server where the game is created
        :param board_size: gameboard size
        :return
        """
        response  = self.message_direct(self.server_key, construct_message([CREATE_GAME, self.user_name, board_size]))
        response = decode_message(response)
        game_exchange = response[0]
        game_id = response[1]
        print(game_exchange)
        self.current_game = game_id
        self.channel.queue_bind(exchange=game_exchange,
                        queue=self.incoming_queue,
                        routing_key=self.user_name)
        self.channel.basic_consume(self.on_info, queue=self.incoming_queue)
        print('Joined to a game. Incoming queue registered to game exchange.')

    def join_game(self, game_id):
        """
        Sends join request to game at server. Gets exchange names, makes queues and binds to them.
        :param server_key: Game server to connect to
        :param game_id: Game name to connect to
        :return:
        """
        response = self.message_direct(self.server_key, construct_message([JOIN_GAME, self.user_name, game_id]))
        response = decode_message(response)
        if response[0] != NOK:
            game_exchange = response[0]
            print(game_exchange)
            self.current_game = game_id
            self.channel.queue_bind(exchange=game_exchange,
                            queue=self.incoming_queue,
                            routing_key=self.user_name)
            self.channel.basic_consume(self.on_info, queue=self.incoming_queue)
            print('Joined to gameserver. Incoming queue registered to %s' % game_exchange)
            return OK
        return NOK

    def start_game(self):
        print('Starting game!')
        return self.message_direct(self.server_key, construct_message([START_GAME, self.user_name, self.current_game]))
    
    def shoot(self, x, y):
        print('Shooting at %s, %s' % (x, y))
        return self.message_direct(self.server_key, construct_message([SHOOT, self.user_name, self.current_game, x, y]))
    
    def leave_game(self):
        print('Leaving game')
        return self.message_direct(self.server_key, construct_message([LEAVE_GAME, self.user_name, self.current_game]))

    def remove_user(self, user_name):
        print('Removing %s from game' % user_name)
        return self.message_direct(self.server_key, construct_message([REMOVE_USER, self.user_name, self.current_game, user_name]))


def parse_command(command):
    cmd = command.lower().split()
    cmd_code = cmd[0]
    if cmd_code == 'start':
        client.start_game()
    elif cmd_code == 'shoot':
        client.shoot(cmd[1], cmd[2])
    elif cmd_code == 'leave':
        client.leave_game()
        client.current_game = None
    elif cmd_code == 'remove':
        client.remove_user(cmd[1])


if __name__ == "__main__":
    client = Client()
    
    print("Requesting game servers.")
    response = json.loads(client.get_game_servers())
    print('NAME\tKEY')
    for server, r_key in response.items():
        print('{}\t{}'.format(server, r_key))
    
    while True:
        #srv = raw_input("Which server to join?")
        srv = 'Server1'
        srv_key = response[srv]
        client.server_key = srv_key
        if srv_key is not None:
            break
    
    while True:
        #user_name = raw_input('Enter user name')
        user_name = 'MMMMM'
        avail_games = json.loads(client.join_game_server(user_name))
        if not avail_games == NOK:
            break
        else:
            user_name = 'KKKKKK'
            avail_games = json.loads(client.join_game_server(user_name))
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
                      if client.join_game(game_id) == OK:
                          client.current_game = game_id
                          break
             break
        if hosting == 'H':
            board_size = 10#raw_input('Board size?')
            client.create_game(int(board_size))
            client.player_turn = True
            break

    thread.start_new_thread(join_reporter, (client, ))
    while 1:
        if client.player_turn:
            print('My turn')
            command = raw_input('>')
            client.player_turn = False
            parse_command(command)
        sleep(0.2)
        print('looping')







