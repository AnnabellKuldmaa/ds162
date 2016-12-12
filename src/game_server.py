import pika
import uuid
import json
from common import construct_message, decode_message, LIST_GAMES, UNKNOWN_REQUEST, CREATE_GAME, JOIN_SERVER, \
    JOIN_GAME, SERVER_ONLINE, USER_JOINED, START_GAME
from player import Player
from game import Game


class GameServer:
    def __init__(self):

        self.games = {}
        self.online_clients = {}
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='main_exch', type='direct')

        self.result = self.channel.queue_declare(exclusive=True)  # declare callback queue
        self.callback_queue = self.result.method.queue
        self.channel.basic_consume(self.on_response,
                                   no_ack=True,
                                   queue=self.callback_queue)  # listener on callback

        server_nr = self.notify_login_server()
        self.r_key = 'GAMESERVER' + str(server_nr)

        self.incoming_queue = self.channel.queue_declare(exclusive=True) # declare incoming message queue
        self.incoming_queue = self.incoming_queue.method.queue
        self.channel.queue_bind(exchange='main_exch',
                                queue=self.incoming_queue,
                                routing_key=self.r_key)  # subscribe to server key

        print('Gameserver {} created.'.format(self.r_key))

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue=self.incoming_queue) # listener on incoming message queue
        self.channel.start_consuming()

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
            print('Received response:', body)

    def on_request(self, ch, method, props, body):
        body = decode_message(body)
        print 'Received request', body
        if body[0] == LIST_GAMES:
            response = json.dumps(self.games.keys(), ensure_ascii=False)
        elif body[0] == JOIN_SERVER :
            if (body[1]) not in self.online_clients:
                # Create a player instance with the name
                player = Player(body[1])
                self.online_clients[body[1]] = player
                response = json.dumps(self.games.keys(), ensure_ascii=False)
            else:
                response = json.dumps('NOK', ensure_ascii=False)
        elif body[0] == CREATE_GAME:
            game_exchange, game_name = self.create_game(body[1], body[2])
            response = construct_message([game_exchange, game_name])
        elif body[0] == JOIN_GAME:
            game_exchange = self.join_game(body[1], body[2])
            response = game_exchange
        else:
            response = UNKNOWN_REQUEST

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id= \
                                                             props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def notify_login_server(self):
        """
        Lets login server know that it exists.
        :return: A number assigned to the game server by the login server
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='main_exch',
                                   routing_key='LOGIN',
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=SERVER_ONLINE)

        while self.response is None:
            self.connection.process_data_events()
        return self.response


    def create_game(self, owner, size):
        gamenr = len(self.games) + 1  # TODO > number may be in use if a game from the middle ands and is deleted
        game_name = '{}_{}'.format(self.r_key, gamenr)
        owner = self.online_clients[owner]
        spec_exchange, game_exchange = self.create_game_exchanges(game_name)
        game = Game(owner, size, spec_exchange, game_exchange)
        game_name = 'GAME_%d' % gamenr
        self.games[game_name] = game
        return game_exchange, game_name

    def create_game_exchanges(self, game_name):
        """
        Creates exchanges for a specific game at creation. Passes back names for binding by player.
        :param game_name: Name of the game as provided by the user
        :return: Exchange names
        """
        game_exchange = '{}_main'.format(game_name)
        self.channel.exchange_declare(exchange=game_exchange, type='direct')
        spec_exchange = '{}_spec'.format(game_name)
        self.channel.exchange_declare(exchange=spec_exchange, type='fanout')
        return spec_exchange, game_exchange

    def remove_game(self, gamenr):
        del self.games['GAME_%d' % gamenr]


    def join_game(self, user_name, game_name):
        player = self.online_clients[user_name]
        game = self.games[game_name]
        game_exchange = game.join(player)
        game_owner = game.owner.user_name
        print('Sending login user info to %s' %game_owner)
        self.channel.basic_publish(exchange=game_exchange,
                                   routing_key=game_owner,
                                   body=construct_message([USER_JOINED, user_name]))

        return game_exchange


if __name__ == "__main__":
    game_server = GameServer()
