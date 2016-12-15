#!/usr/bin/env python
import pika
import uuid
import json
import thread
import sys
import readline
import string, random
from time import sleep

from IPython.lib.display import YouTubeVideo

from common import construct_message, decode_message, draw_main_board, draw_tracking_board, \
    LIST_SERVERS, LIST_GAMES, JOIN_SERVER, CREATE_GAME, JOIN_GAME, SHOOT, LEAVE_GAME, REMOVE_USER, \
    NO_SHIP, SHIP_NOT_SHOT, SHIP_SHOT, NO_SHIP_SHOT, NOT_SHOT, SHIP_SUNK, USER_JOINED, START_GAME, \
    OK, NOK, YOUR_TURN, YOUR_HITS, BOARDS, HIT, SHIP_SUNK_ANNOUNCEMENT, NEW_OWNER, GAME_OVER, \
    REFRESH_BOARD, YOU_DEAD, SPECTATOR_ANNOUNCEMENT, SPECTATOR, ONLINE
from terminal_print import join_reporter, print_message


class Client(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='127.0.0.1'))

        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='main_exch', type='direct')
        result = self.channel.queue_declare(exclusive=True)  # declare queue
        self.callback_queue = result.method.queue  # access queue declared
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)  # set listen on callback queue

        self.incoming_queue = self.channel.queue_declare()  # declare incoming message queue
        self.incoming_queue = self.incoming_queue.method.queue

        self.channel.basic_consume(self.on_info, no_ack=True,
                                   queue=self.incoming_queue)  # listener on incoming message queue
        self.current_exchange = None
        self.prev_exchange = None
        self.user_name = None
        self.current_game = None
        self.server_key = None
        self.player_turn = False
        self.mode = None
        self.reconnect = False

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
            #print('Response received', body)

    def on_info(self, ch, method, props, body):
        """
        Handles information from game.
        """
        message = decode_message(body)
        req_code = message[0]
        # print('RECEIVED CODE: ', message)
        if req_code == USER_JOINED:
            print_message('Player %s joined your game' % message[1])
        if req_code == BOARDS:
            print_message('Your Ships\n' + draw_main_board(json.loads(message[1])) +
                               'Your Shots\n' + draw_tracking_board(json.loads(message[2])))
        if req_code == YOUR_TURN:
            print_message('Your turn!')
            self.player_turn = True
        if req_code == YOUR_HITS:
            to_print = 'Your Hits:\n'
            hits = json.loads(message[1])
            if hits:
                for hit in hits:
                    to_print += hit + '\n'
                to_print += self.determine_godlikeness(hits) + '\n'
            print_message(to_print)
        if req_code == HIT:
            print('One of your ships is under attack by {}!'.format(message[1]))
        if req_code == SHIP_SUNK_ANNOUNCEMENT:
            print('Player {} sunk players {} ship!'.format(message[1], message[2]))
        if req_code == NEW_OWNER:
            print('You are the new owner of this game.')
        if req_code == NOK:
            print('You requested an invalid action.')
        if req_code == LEAVE_GAME:
            print('Leaving game {}.'.format(self.current_game))
            self.leave_game()
            self.current_game = None
        if req_code == GAME_OVER:
            print('Game over, {} won.'.format(message[1]))
            if self.mode == SPECTATOR:
                self.channel.queue_unbind(exchange=self.current_exchange,
                                        queue=self.incoming_queue,
                                        routing_key=self.user_name)
                self.current_exchange = self.prev_exchange
                self.channel.queue_bind(exchange=self.prev_exchange,
                                        queue=self.incoming_queue,
                                        routing_key=self.user_name)
                self.mode == ONLINE
        if req_code == YOU_DEAD:
            self.start_spec_mode(message[1])
            print('You dead!\nEntering spectator mode..')
        if req_code == SPECTATOR_ANNOUNCEMENT:
            print(message[1])


    def determine_godlikeness(self, hits):
        if len(hits) == 2:
            return 'DOUBLE KILL!'
        if len(hits) == 3:
            return 'DOMINATING!'
        if len(hits) > 3:
            return 'GODLIKE!'
        else:
            return ''

    def message_direct(self, key, body):
        """
        Takes a key and message and sends it to direct message exchange.
        :param key: Key of the recipient
        :param body: Message to be sent
        :return: Response sent to the callback queue
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        # print('Sending message %s to' % body, key)
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

    def message_game(self, body):
        """
        Sends message without expecting callback. Required for message protocol during game
        :param body: message you want to send
        :return: Nothing
        """
        # print('Sending message %s ' % body)
        self.channel.basic_publish(exchange='main_exch',
                                   routing_key=self.server_key,
                                   body=body)
        return

    def get_game_servers(self):
        return self.message_direct('LOGIN', LIST_SERVERS)

    def get_game_list(self):
        return self.message_direct(self.server_key, construct_message([LIST_GAMES, self.user_name]))


    def join_game_server(self, user_name, reconnect=False):
        self.user_name = user_name
        return self.message_direct(self.server_key, construct_message([JOIN_SERVER, user_name, reconnect]))

    def create_game(self, board_size):
        """
        Sends params for game creation to game server. Connects client to exchanges and stores the joined game key
        :param user_name: Necessary for server to know who's creating the game
        :param server_key: Game_server where the game is created
        :param board_size: gameboard size
        :return
        """
        response = self.message_direct(self.server_key, construct_message([CREATE_GAME, self.user_name, board_size]))
        response = decode_message(response)
        game_exchange = response[0]
        self.current_exchange = game_exchange
        game_id = response[1]
        # print(game_exchange)
        self.current_game = game_id
        self.channel.queue_bind(exchange=game_exchange,
                                queue=self.incoming_queue,
                                routing_key=self.user_name)
        self.channel.basic_consume(self.on_info, queue=self.incoming_queue)
        print('Joined to a game. Incoming queue registered to game exchange.')

    def start_spec_mode(self, spec_exchange):
        self.mode = SPECTATOR
        self.prev_exchange = self.current_exchange
        self.channel.queue_unbind(exchange=self.current_exchange,
                                    queue=self.incoming_queue,
                                    routing_key=self.user_name)
        self.current_exchange = spec_exchange
        self.channel.queue_bind(exchange=spec_exchange,
                                queue=self.incoming_queue,
                                routing_key=self.user_name)

    def join_game(self, game_id):
        """
        Sends join request to game at server. Gets exchange names, makes queues and binds to them.
        :param server_key: Game server to connect to
        :param game_id: Game name to connect to
        :return:
        """
        response = self.message_direct(self.server_key, construct_message([JOIN_GAME, self.user_name, game_id, self.reconnect]))
        response = decode_message(response)
        # print('join_game response', response)
        if response[0] != NOK:
            game_exchange = response[0]
            # print(response[1])
            if response[1] == self.user_name:
                self.player_turn = True
            # print(game_exchange)
            self.current_exchange = game_exchange
            self.current_game = game_id
            self.channel.queue_bind(exchange=game_exchange,
                                    queue=self.incoming_queue,
                                    routing_key=self.user_name)
            self.channel.basic_consume(self.on_info, queue=self.incoming_queue)
            print('Joined to gameserver. Incoming queue registered to %s' % game_exchange)
            self.message_game(construct_message([REFRESH_BOARD, self.current_game]))
            return OK
        return NOK

    def start_game(self):
        print('Starting game!')
        return self.message_game(construct_message([START_GAME, self.user_name, self.current_game]))

    def shoot(self, x, y):
        print('Shooting at %s, %s' % (x, y))
        return self.message_game(construct_message([SHOOT, self.user_name, self.current_game, x, y]))

    def leave_game(self):
        print('User {} leaving game {}'.format(self.user_name, self.current_game))
        return self.message_game(construct_message([LEAVE_GAME, self.user_name, self.current_game]))

    def remove_user(self, user_name):
        print('Removing %s from game' % user_name)
        return self.message_game(construct_message([REMOVE_USER, self.user_name, self.current_game, user_name]))


def parse_command(command, client):
    if not command:
        print('UNKNOWN COMMAND!')
        return
    cmd = command.lower().split()
    cmd_code = cmd[0]
    if cmd_code == 'start':
        client.start_game()
    elif cmd_code == 'shoot':
        if len(cmd) == 3:
            client.player_turn = False
            client.shoot(cmd[1], cmd[2])
        else:
            print('The command to shoot looks like this: "shoot x y" . Try again.')
    elif cmd_code == 'leave':
        client.leave_game()
        client.current_game = None
    elif cmd_code == 'remove':
        client.remove_user(cmd[1])
    elif cmd_code == 'restart':
        client.start_game()
    else:
        print('UNKNOWN COMMAND!')
    return

def refresh_available_games(client):
    avail_games = json.loads(client.get_game_list())
    print('Available games')
    for game_name in avail_games:
        print game_name
    return avail_games

def waiting_room(client):
    avail_games = refresh_available_games(client)
    while True:
        hosting = raw_input("Do you want to join a session or host a new session? [J]/[H] ").upper()
        if hosting == 'J' and len(response) > 0:
            while True:
                avail_games = refresh_available_games(client)
                game_id = raw_input("Which game? ").upper()
                # print()
                # print('join {}, is it in {}'.format(game_id, avail_games))
                if game_id in avail_games:
                    print('game_id in avail_games')
                    if client.join_game(game_id) == OK:
                        client.current_game = game_id
                        break
            break
        if hosting == 'H':
            board_size = raw_input('Board size?')
            client.create_game(int(board_size))
            client.player_turn = True
            break


if __name__ == "__main__":
    client = Client()

    print("Requesting game servers.")
    response = json.loads(client.get_game_servers())
    print('NAME\tKEY')
    for server, r_key in response.items():
        print('{}\t{}'.format(server, r_key))

    while True:
        srv = raw_input("Which server to join?")
        #srv = 'Server1'
        srv_key = response[srv]
        client.server_key = srv_key
        if srv_key is not None:
            break

    while True:
        user_name = raw_input('Enter user name: ')
        #user_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        if not user_name:
            continue
        client.reconnect = False
        if user_name[0] == '*':
            client.reconnect = True
            user_name = user_name[1:]

        avail_games = json.loads(client.join_game_server(user_name, client.reconnect))
        if avail_games == NOK:
            print('Username {} taken, please choose a different name.'.format(user_name))
        else:
            break
    
    #print('Your name:', user_name)
    client.user_name = user_name

    thread.start_new_thread(join_reporter, (client,))
    waiting_room(client)

    while 1:
        # print('client.current_game',client.current_game)
        # print('client.player_turn',client.player_turn)
        if client.player_turn and client.current_game:
            command = raw_input('>')
            parse_command(command, client)
        sleep(0.2)
        if client.mode == SPECTATOR:
            print('You dead! You can leave, or game owner can restart the game.')
            command = raw_input('>')
            parse_command(command, client)
        if not client.player_turn and client.current_game:
            command = raw_input('>')
            parse_command(command, client)
        if not client.current_game:
            avail_games = json.loads(client.get_game_list())
            waiting_room(client)

            # break
    print('Main loop exited. Closing main thread.')
