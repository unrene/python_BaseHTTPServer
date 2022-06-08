from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import time
from datetime import datetime
import urllib
import json

# https://www.w3schools.com/tags/ref_httpmethods.asp
# https://en.wikipedia.org/wiki/List_of_HTTP_header_fields
# https://www.w3schools.com/tags/ref_httpmessages.asp
# https://www.w3schools.com/tags/ref_urlencode.asp

class UniversalHTTPRequestHandler ( BaseHTTPRequestHandler ) :
    # overwrite Server Entry in Response Header
    server_version = 'universal HTTP Server'
    sys_version    = '1.0'

    def __init__( self, request_handler_instance, *args) :
        self._clear_headers_information()
        # final init of python's BaseHTTP module with included request handler
        self.request_handler = request_handler_instance
        BaseHTTPRequestHandler.__init__( self, *args )

    def log_request ( self, format, *args ) :
        # ignores console prints for each request
        return

    def _clear_headers_information ( self ) :
        self.response_headers_information = {}

    def _update_headers_information ( self, key, val ) :
        self.response_headers_information[ key ] = val

    def _send_headers_information ( self ) :
        # equal for all
        # tell partial content range types this server supports via byte serving
        self._update_headers_information( 'Accept-Ranges', 'bytes' )
        # tell all caching mechanisms from server to client whether they may cache this object (in seconds)
        self._update_headers_information( 'Cache-Control', 'max-age=60' )
        # specifying which web sites can participate in cross-origin resource sharing (* = all)
        #self._update_headers_information( 'Access-Control-Allow-Origin', '*' )

        # loop through all given information and send it
        for key, val in self.response_headers_information.items() :
            self.send_header( key, val )
        self._clear_headers_information()
        self.end_headers()

    def _set_headers_html ( self, status = 200 ) :
        self.send_response( status )
        self._update_headers_information( 'Content-Type', 'text/html; charset=utf-8' )
        self._send_headers_information()

    def _set_headers_json ( self, status = 200 ) :
        self.send_response( status )
        self._update_headers_information( 'Content-Type', 'application/json; charset=utf-8' )
        self._send_headers_information()

    def _set_headers_file ( self, file_extension, file_length, status = 200 ) :
        self.send_response( status )
        # set content type based on file extension
        content_type_map = {
            'default' : 'text/html',
            '.html'   : 'text/html; charset=utf-8',
            '.css'    : 'text/css; charset=utf-8',
            '.js'     : 'application/javascript; charset=utf-8',
            '.jpeg'   : 'image/jpeg',
            '.jpg'    : 'image/jpeg',
            '.png'    : 'image/png',
            '.gif'    : 'image/gif',
            '.webp'   : 'image/webp',
            '.svg'    : 'image/svg+xml',
            '.pdf'    : 'application/pdf',
            '.zip'    : 'application/zip',
        }
        if file_extension not in content_type_map :
            file_extension = 'default'
        content_type = content_type_map[ file_extension ]
        self._update_headers_information( 'Content-Type', content_type )
        self._update_headers_information( 'Content-Length', str( file_length ) )
        self._send_headers_information()

    def _get_request_headers ( self ) :
        '''
        https://en.wikipedia.org/wiki/List_of_HTTP_header_fields
        possible header fields
        {
            Host: developer.mozilla.org
            User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0) Gecko/20100101 Firefox/50.0
            Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
            Accept-Language: en-US,en;q=0.5
            Accept-Encoding: gzip, deflate, br
            Referer: https://developer.mozilla.org/testpage.html
            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==
            Cookie: namen1=value1; name2=value2
            Connection: keep-alive
            Upgrade-Insecure-Requests: 1
            If-Modified-Since: Mon, 18 Jul 2016 02:36:04 GMT
            If-None-Match: "c561c68d0ba92bbeb8b0fff2a9199f722e3a621a"
            Cache-Control: max-age=0
        }
        '''
        return dict( self.headers.items() )

    def _get_request_data ( self, uri = '', print_en = False ) :
        if '' == uri :
            # fetch from parent
            uri = self.path
        uri       = urllib.parse.quote( uri, safe = '/?=_-&%' )
        uri_split = uri.split( '?' )
        # URI path
        uri_path = uri_split[ 0 ].split( '/' )
        uri_path_cleaned = []
        # delete empty Stuff
        for path_elem in uri_path :
            if len( path_elem ) :
                uri_path_cleaned.append( path_elem )
        uri_path = '/'.join( uri_path_cleaned )
        #queries
        uri_queries  = {}
        if len( uri_split ) > 1 and len( uri_split[ 1 ] ) > 0 :
            queries_split = uri_split[ 1 ].split( '&' )
            for q in queries_split :
                try :
                    [ k, v ] = q.split( '=' )
                    uri_queries[ k ] = v
                except ValueError :
                    pass
        request_data = {
            'client_ip'   : self.client_address[ 0 ],
            'client_port' : self.client_address[ 1 ],
            'uri'         : uri,
            'method'      : self.command,
            'headers'     : self._get_request_headers(),
            'path'        : uri_path,
            'queries'     : uri_queries,
            'body_json'   : {},
            'unixtime'    : round( time.time(), 3 ),
        }
        return request_data

    def do_GET ( self ) :
        request_data = self._get_request_data()
        self.handle_get_request( request_data )
    
    def do_POST( self ) :
        request_data = self._get_request_data()

        body_len = int( request_data[ 'headers' ][ 'Content-Length' ] )
        body     = json.loads( self.rfile.read( body_len ).decode() )
        request_data.update( {
            'body_json': body
        } )
        self.handle_post_request( request_data )

    def handle_get_request ( self, request_data ) :
        print( request_data )
        if not hasattr( self.request_handler, 'handle_get_request' ) :
            self.respond_default( request_data )
            return
        response_data = self.request_handler.handle_get_request( request_data )
        self.respond_by_handler( response_data )

    def handle_post_request ( self, request_data ) :
        print( request_data )
        if not hasattr( self.request_handler, 'handle_post_request' ) :
            self.respond_default( request_data )
            return
        response_data = self.request_handler.handle_post_request( request_data )
        self.respond_by_handler( response_data )

    def respond_default ( self, request_data ) :
        if not hasattr( self.request_handler, 'handle_request_fallback' ) :
            json_msg = {
                'msg' : 'default response, request handler does not provide any fallback for given request'
            }
            self.respond_json( json_msg, 501 )
            return
        response_data = self.request_handler.handle_request_fallback( request_data )
        self.respond_by_handler( response_data )

    def respond_by_handler ( self, response_data ) :
        # ... do some stuff here ...
        # response_data.type: json or file
        #                     dict
        #                     file_extension ,file_length, file_data
        # response_data.add_headers: ...
        # response_data.status: ...
        json_msg = {
                'msg' : 'default response, request handler failed on data/method for given request'
            }
        self.respond_json( json_msg, 501 )

    def respond_file ( self, file_extension ,file_length, file_data, status = 200 ) :
        self._set_headers_file( file_extension, file_length, status )
        self.wfile.write( file_data )

    def respond_json ( self, response, status = 200 ) :
        try :
            response_json = bytes( json.dumps( response ), 'utf-8' )
        except TypeError as e :
            status        = 500
            response      = { 'msg' : 'Error during JSON Conversion' }
            response_json = bytes( json.dumps( response ), 'utf-8' )
        self._update_headers_information( 'Content-Length', str( len( response_json ) ) )
        self._set_headers_json( status )
        self.wfile.write( response_json )

    def respond_file ( self, html_content, status = 200 ) :
        response = bytes( html_content, 'utf-8' )
        self._update_headers_information( 'Content-Length', str( len( response ) ) )
        self._set_headers_html( status )
        self.wfile.write( response )

class HTTPServerThreaded ( ThreadingMixIn, HTTPServer ) :
    # handles each request in a separate thread
    pass

class UniversalHTTPServer :
    def __init__( self, server_addr, request_handler_instance ) :

        def handler ( *args ) :
            UniversalHTTPRequestHandler( request_handler_instance, *args )
        
        if not self.is_valid_ip_v4( server_addr[ 0 ] ) :
            raise ValueError( 'Given IP does not match v4 format. Use string with "xxx.xxx.xxx.xxx".' )
        
        if not self.is_valid_port_number( server_addr[ 1 ] ) :
            raise ValueError( 'Given PORT does not match accepted format. Use int with xxxxx (1 .. 65_535).' )
        
        self.server_addr = server_addr
        self.server      = HTTPServerThreaded( server_addr, handler )
    
    @staticmethod
    def get_time_local_str () :
        dateTime = datetime.now()
        return dateTime.strftime( '%d-%b-%Y %H:%M:%S' )
    
    @staticmethod
    def is_valid_ip_v4 ( ip_str : str ) :
        # is it passed as string (str format needed for all other methods)
        if not isinstance( ip_str, str ) :
            return False
        # split up to octets
        octets = ip_str.split( '.' )
        # check for correct octet number
        if len( octets ) != 4 :
            return False
        # loop through octets
        for octet in octets :
            # check if only numbers (0-9) are present
            # no separators, no decimal allowed
            # leading 0 is ok
            if not octet.isdigit() :
                return False
            # check for correct range
            if int( octet ) < 0 or 255 < int( octet ) :
                return False
        # all tests were passed
        return True
    
    @staticmethod
    def is_valid_port_number ( port : int ) :
        # is it passed as int (int format needed for all other methods)
        if not isinstance( port, int ) :
            return False
        # check for correct range
        if port < 1 or 65_535 < port :
            return False
        # all tests were passed
        return True

    def start( self ) :
        try :
            print( '{} - Rest Server started for {}:{}'.format( self.get_time_local_str(), self.server_addr[ 0 ], self.server_addr[ 1 ] ) )
            self.server.serve_forever()
        except ( KeyboardInterrupt, SystemExit ) :
            print( '...wait...' )
            pass

        self.server_close()
        
    def server_close ( self ) :
        self.server.server_close()
        print( '{} - Rest Server stopped for {}:{}'.format( self.get_time_local_str(), self.server_addr[ 0 ], self.server_addr[ 1 ] ) )
    
    def stop ( self ) :
        self.server.shutdown()
