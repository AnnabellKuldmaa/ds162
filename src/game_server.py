import pika
import uuid
import json


class GameServer:
    def __init__(self):

        self.games = {}
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='main_exch', type='direct')

        self.result = self.channel.queue_declare(exclusive=True)  # declare queue
        self.callback_queue = self.result.method.queue  # access queue declared
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

        server_nr = self.notify_login_server()
        self.r_key = 'GAMESERVER' + str(server_nr)

        self.channel.queue_declare(queue='incoming_queue')
        self.channel.queue_bind(exchange='main_exch',
                                queue='incoming_queue',
                                routing_key=self.r_key)

        print('Server {} created.'.format(self.r_key))

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue='incoming_queue')
        self.channel.start_consuming()

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
            print('Received response:', body)

    def on_request(self, ch, method, props, body):
        print 'Received request', body
        if body == 'list_games':
            response = json.dumps(self.games, ensure_ascii=False)
        else:
            response = 'unknown_request'

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
                                   body='server_online')

        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def create_game(self):
        pass

    def remove_game(self):
        pass


game_server = GameServer()


class Game():

    def __init__(self):
        pass