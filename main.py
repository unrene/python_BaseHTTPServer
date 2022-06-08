from assists.universal_http_server import UniversalHTTPServer
#from assists.request_handler import RequestHandler

import threading
import signal
import time

def start_as_thread ( universal_server ) :
    
    t =threading.Thread( target = universal_server.start )

    try :
        t.start()
        signal.pause() # perfect, but not supported by Windows
    except ( KeyboardInterrupt, SystemExit ) :
        print( '...wait...' )
        universal_server.stop()

    if 1 :
        # test shutdown, doesn't work with signal.pause (obviously)
        time.sleep( 5 )
        universal_server.stop()

    t.join()

if '__main__' == __name__ :

    server_host = '0.0.0.0'
    server_port = 8080

    request_handler = {} #RequestHandler()

    universal_server = UniversalHTTPServer( ( server_host, server_port ), request_handler )

    if 1 :
        universal_server.start()
    else :
        start_as_thread( universal_server )


