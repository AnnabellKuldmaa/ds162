import sys
sys.path.insert(0, "../")

import logging
import time

import snakemq
import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.rpc

class Game(object):
    def dummy(self):
        return "Have fun!"

    @snakemq.rpc.as_signal
    def mysignal(self):
        print "Mysignal"

snakemq.init_logging()
logger = logging.getLogger("snakemq")
logger.setLevel(logging.DEBUG)

s = snakemq.link.Link()

s.add_listener(('127.0.0.1', 7777))

tr = snakemq.packeter.Packeter(s)
m = snakemq.messaging.Messaging("srv", "", tr)
rh = snakemq.messaging.ReceiveHook(m)
srpc = snakemq.rpc.RpcServer(rh)
srpc.register_object(Game(), "game1")

s.loop()