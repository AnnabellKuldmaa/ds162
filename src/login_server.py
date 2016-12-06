#!/usr/bin/env python
import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(
	host='127.0.0.1'))

channel = connection.channel()

channel.exchange_declare(exchange='main_exch', type='direct')

channel.queue_declare(queue='login_queue')
channel.queue_bind(exchange='main_exch', queue='login_queue', routing_key='LOGIN')

gameservers = {}


def on_request(ch, method, props, body):
	print('Received request')

	if body == 'list_servers':
		response = json.dumps(gameservers, ensure_ascii=False)
	elif body == 'server_online':
		server_nr = len(gameservers) + 1
		gameservers['Server%d' % server_nr] = 'GAMESERVER%d' % server_nr
		response = 'server_in_list'
	else:
		response = 'unknown_request'

	ch.basic_publish(exchange='',
					 routing_key=props.reply_to,
					 properties=pika.BasicProperties(correlation_id= \
														 props.correlation_id),
					 body=str(response))
	ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='login_queue')

print("Login server awaiting requests")
channel.start_consuming()
