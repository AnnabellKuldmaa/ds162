#!/usr/bin/env python
import pika
import json
from common import construct_message, decode_message, LIST_SERVERS, SERVER_ONLINE, UNKNOWN_REQUEST


connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='127.0.0.1'))

channel = connection.channel()

channel.exchange_declare(exchange='main_exch', type='direct')

channel.queue_declare(queue='login_queue')
channel.queue_bind(exchange='main_exch', queue='login_queue', routing_key='LOGIN')

gameservers = {}


def on_request(ch, method, props, body):
    print('Received request', body)

    if body == LIST_SERVERS:
        response = json.dumps(gameservers, ensure_ascii=False)
    elif body == SERVER_ONLINE:
        server_nr = len(gameservers) + 1
        gameservers['Server%d' % server_nr] = 'GAMESERVER%d' % server_nr
        response = server_nr
    else:
        response = UNKNOWN_REQUEST

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
