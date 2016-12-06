import pika
import uuid

class GameServer:

	def __init__(self):

		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
		self.channel = self.connection.channel()
		self.channel.exchange_declare(exchange='main_exch', type='direct')
		self.channel.queue_declare(queue='login_queue')

		self.result = self.channel.queue_declare(exclusive=True)  # declare queue
		self.callback_queue = self.result.method.queue  # access queue declared
		self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

		server_nr = self.notify_login_server()

		self.channel.queue_bind(exchange='main_exch',
				   queue='incoming_queue',
				   routing_key='GAMESERVER_' + str(server_nr))

		print('Gameserver nr.{} created.'.format(server_nr))

	def on_response(self, ch, method, props, body):
		print('Received response:', body)

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