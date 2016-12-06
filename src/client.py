#!/usr/bin/env python
import pika
import uuid
import json
from common import construct_message, decode_message

class Client(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='127.0.0.1'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)  # declare queue
        self.callback_queue = result.method.queue  # access queue declared
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue) # set listen on callback queue

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
            print('Response received.')

    def message_direct(self, key, body):
        """
        Takes a key and message and sends it to direct message exchange.
        :param key: Key of the recipient
        :param body: Message to be sent
        :return: Response sent to the callback queue
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
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
        return self.message_direct('LOGIN', 'list_servers')

    def get_game_list(self, server_key):
        return self.message_direct(server_key, 'list_games')

    def create_game(self, server_key):
        return self.message_direct(server_key, 'create_game')

    def join_game(self, server_key, game_id):
        return self.message_direct(server_key, construct_message(['join_game', game_id]))


# Code for testing the client
client = Client()

print("Requesting gameservers.")
response = json.loads(client.get_game_servers())
print('NAME\tKEY')
for server, key in response.items():
    print('{}\t{}'.format(server, key))