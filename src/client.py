import sys
sys.path.insert(0, "../")

import threading
import time
import logging

import snakemq
import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.queues
import snakemq.rpc


def call():
    time.sleep(1)
    c = None
    while True:
        if list(m._conn_by_ident.keys()):
            c = 1
        if c:
            try:
                print(proxy.dummy())
            except Exception as exc:
                print("remote traceback", str(exc.__remote_traceback__))
            s.stop()
        time.sleep(2)

snakemq.init_logging()

logger = logging.getLogger("snakemq")
logger.setLevel(logging.DEBUG)

s = snakemq.link.Link()
s.add_connector(('127.0.0.1', 7777))

tr = snakemq.packeter.Packeter(s)

m = snakemq.messaging.Messaging("client", "", tr, None)

t = threading.Thread(target=call)
t.setDaemon(1)
t.start()

rh = snakemq.messaging.ReceiveHook(m)
crpc = snakemq.rpc.RpcClient(rh)


proxy = crpc.get_proxy("srv", "game1")


s.loop()