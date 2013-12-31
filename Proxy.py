#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:sts=4:ai:et:fileencoding=utf-8:number

#from __future__ import unicode_literals
import sys
if sys.version_info < (3, 0):
    python_OldVersion = True
else:
    python_OldVersion = False

if python_OldVersion:       # Python version 2.7
    import urlparse, BaseHTTPServer
    from BaseHTTPServer import BaseHTTPRequestHandler
    from SocketServer import BaseRequestHandler
else:                       # Python version 3.x
    import urllib, http.server
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from socketserver import BaseRequestHandler

import base64, binascii, re, string
import socket, select, os
import cgi,  requests
import Headers, Cache
from db_mapper import db_handler
from db_layer import Database
from Log import Log
from Config import Config
import unicodedata
import html.parser


DEBUG = Config.DEBUG['Proxy.DEBUG']
DEBUG_BEFORE_HANDLING = Config.DEBUG['Proxy.DEBUG_BEFORE_HANDLING']

class Proxy(BaseHTTPRequestHandler):
    theDB = Database()
    threadServer = None
    __version__ = '0.1'
    server_version = "HTTP_Proxy/" + __version__
    proxy_user = 'xxxxxxxxx'
    proxy_password = ''
    http_user = 'xxxxxxxxx'
    http_password = ''
    bodySize = None
    Allowed = 0
    parsed_path =''
    content = b''
    content_lenght = 0
    processed_headers = []
    code = 0
    content_cached=False
    myServerAddress =  (socket.gethostname()+':'+ str(Config.PORT)).lower()

    logger = Log()

    #http.client.HTTPConnection.debuglevel = 1

    #logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
    #logging.getLogger().setLevel(logging.DEBUG)
    #requests_log = logging.getLogger("requests.packages.urllib3")
    #requests_log.setLevel(logging.DEBUG)
    #requests_log.propagate = True


    __verbs_supported ='GET, HEAD, POST, PUT, TRACE, OPTIONS, CONNECT'
    __verbs_unsupported = 'PATCH, DELETE'
    __verbs_safe = 'GET, HEAD, OPTIONS, TRACE'


    def __init__(self, request, client_address, server):
        if not python_OldVersion:
            super().__init__(request, client_address, server)
            #BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        else:
            BaseHTTPRequestHandler.__init__(self, request, client_address, server)

        self.content = b''
        self.content_lenght = 0
        self.code = 0
        self.processed_headers [:] = []
        self.content_cached=False
        self.Allowed = 0

    def log_message(self, format, *args):
        return
    '''
        def pdebug(self,message):
            if TRACE:
                if len(message) > MAX_CON_MSG:
                    sys.stderr.write('%s - %s\n' % (self.get_timestamp(), message[0:MAX_CON_MSG-3]+'..'))
                else:
                    sys.stderr.write('%s - %s\n' % (self.get_timestamp(), message))
            return
    '''

    def svc_hndl_FILE(self,parms,query, Verb=''):
        if DEBUG: self.logger.pdebug("svc_hndl_FILE called with parms: >%s, %s<" % (Verb, parms))

        if Verb=='HEAD':
            mensaje=''
        else:
            if DEBUG: self.logger.pdebug("url parms = %s, %s" % (parms,query))
            filename=re.sub(r'[^a-zA-Z0-9]', "", parms).lower()

            if (filename == ""):
                filename = "index"

            if os.path.exists('./static/'+filename+'.static'):
                source = open('./static/'+filename+'.static', 'r')
                mensaje = source.read()
                self.int_send_HEADERS(200,mensaje)

            else:
                mensaje=self.int_get_html_message('File "<font color="red">'+filename+'</font>" not found')
                self.int_send_HEADERS(404,mensaje)
                #self.int_send_BODY(mensaje)

        if Verb!='HEAD':
            self.int_send_BODY(mensaje)


        return

    def svc_hndl_LIB(self,parms,query, Verb=''):
        if DEBUG: self.logger.pdebug("svc_hndl_LIB called with parms: >%s, %s<" % (Verb, parms))
        message = ''

        if DEBUG: self.logger.pdebug("url parms = %s, %s" % (parms,query))
        filename=re.sub(r'[^a-zA-Z0-9]\.[a-zA-Z0-9]', "", parms)
        if os.path.exists('./lib/'+filename):
            tamagno = os.path.getsize('./lib/'+filename)
            self.bodySize= tamagno
            self.code = 200
            self.content_lenght = tamagno

            source = open('./lib/'+filename, 'rb')
            #mensaje = source.read()
            self.int_send_HEADERS_FILETYPE(200,filename, tamagno)
            if Verb!='HEAD':
                while 1:
                    data = source.read(1024)
                    if not data: break
                    self.wfile.write(data)

        else:
            mensaje=self.int_get_html_message('File "<font color="red">'+filename+'</font>" not found')
            self.int_send_HEADERS(404,mensaje)
            #self.int_send_BODY(mensaje)

        return

    def svc_hndl_ULIB(self,parms,query, Verb=''):
        if DEBUG: self.logger.pdebug("svc_hndl_ULIB called with parms: >%s, %s<" % (Verb, parms))

        message = ''

        if DEBUG: self.logger.pdebug("url parms = %s, %s" % (parms,query))
        filename=re.sub(r'[^a-zA-Z0-9]\.[a-zA-Z0-9]', "", parms)
        if os.path.exists('./ulib/'+filename):
            tamagno = os.path.getsize('./ulib/'+filename)
            self.bodySize= tamagno
            self.code = 200
            self.content_lenght = tamagno

            source = open('./ulib/'+filename, 'rb')
            #mensaje = source.read()
            self.int_send_HEADERS_FILETYPE(200,filename, tamagno)
            if Verb!='HEAD':
                while 1:
                    data = source.read(1024)
                    if not data: break
                    self.wfile.write(data)

        else:
            mensaje=self.int_get_html_message('File "<font color="red">'+filename+'</font>" not found')
            self.int_send_HEADERS(404,mensaje)
            #self.int_send_BODY(mensaje)

        return

    def svc_hndl_DB(self, query, parms, Verb=''):
        if DEBUG: self.logger.pdebug("svc_hndl_DB called with parms: >VERB: %r, %r, %r<" % (Verb, query, parms))

        answer = db_handler().handle_request(query, parms)
        ##print("FFFFFFFFFFFFFFFFFFFFFFFFFFFF %s" % answer)

        if answer['typeinfo'] == 'html':
            mensaje= str(answer['answer'])
            self.int_send_HEADERS(200, mensaje)

        elif answer['typeinfo'] == 'json':
            mensaje= str(answer['answer'])
            self.int_send_HEADERS_JSON(200, mensaje)

        #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>> %r" % type(answer['answer']))
        self.int_send_BODY(mensaje)
        return

    def svc_hndl_VIRTUAL(self, query, parms, Verb=''):
        #if DEBUG:
        self.logger.pdebug("VIRTUAL called with parms: >VERB: %r, %r, %r<" % (Verb, query, parms))
        if query == 'revalidate_proxy':
            self.int_HEAD_PROXY_AUTH()
        elif query == 'revalidate_http':
            self.int_HEAD_HTTP_AUTH()
        elif query == 'redirect':
            self.int_send_HEADERS_redirect(location=parms)

        return

    def svc_hndl_CONFIG(self,parms,query, Verb=''):
        if DEBUG: self.logger.pdebug("svc_hndl_CONFIG called with parms: >%s, %s<" % (Verb, parms))
        if Verb=='HEAD':
            mensaje=''
        else:
            mensaje=self.int_get_html_message('CONFIG hndl')
            self.int_send_HEADERS_redirect(301, "/lib/index.html")
        ##HTTP/1.1 301 Moved Permanently
        ##Location: http://www.example.org/index.asp
        #self.send_html_message("CONFIG")
        return

    def svc_hndl_FAVICON(self,parms,query, Verb=''):
        if DEBUG: self.logger.pdebug("svc_hndl_FAVICON called with parms: >%s, %s<" % (Verb, parms))
        if Verb=='HEAD':
            mensaje=''
        else:
            mensaje=self.int_get_html_message('CONFIG hndl')
            self.int_send_HEADERS_redirect(301,'/ulib/images/favicon.ico')
        ##HTTP/1.1 301 Moved Permanently
        ##Location: http://www.example.org/index.asp
        #self.send_html_message("CONFIG")
        return

    def svc_hndl_STOP(self,parms,query, Verb=''):
        if DEBUG: self.logger.pdebug("svc_hndl_STOP called with parms: >%s, %s<" % (Verb, parms))
        if Verb=='HEAD':
            mensaje=''
        else:
            mensaje=self.int_get_html_message('STOP hndl')

        self.int_send_HEADERS(200,mensaje)

        if Verb!='HEAD':
            self.int_send_BODY(mensaje)
            Proxy.threadServer.force_shutdown()

        #self.send_html_message("FORCED SHUTDOWN")
        return

    def svc_hndl_POST(self,parms,query, Verb=''):
        if DEBUG: self.logger.pdebug("svc_hndl_POST called with parms: >%s, %s<" % (Verb, parms))
        if Verb=='HEAD':
            mensaje=''
        else:
            mensaje='<html><head><title>My Page</title></head><body><form name="myform" action="http://localhost/dump.php" method="POST"><div align="center"><br><br><input type="text" size="25" value="Enter your name here!"><br><input type="submit" value="Send me your name!"><br></div></form></body></html>'
            self.int_send_HEADERS(200,mensaje)

        if Verb!='HEAD':
            self.int_send_BODY(mensaje)

        return

    def svc_hndl_NOOP(self,parms,query, Verb=''):
        if DEBUG: self.logger.pdebug("svc_hndl_NOOP called with parms: >%s, %s<" % (Verb, parms))
        if Verb=='HEAD':
            mensaje=''
        else:
            mensaje=self.int_get_html_message('NOOP hndl')
        self.int_send_HEADERS(200,mensaje)

        if Verb!='HEAD':
            self.int_send_BODY(mensaje)

        return


    LocalServices = {
        re.compile(r"/favicon.ico", re.IGNORECASE),
        re.compile(r"/STOP", re.IGNORECASE),
        re.compile(r"/CONFIG", re.IGNORECASE),
        re.compile(r"/POST/", re.IGNORECASE),
        re.compile(r"/VIRTUAL/", re.IGNORECASE),
        re.compile(r"/FILE/", re.IGNORECASE),
        re.compile(r"/LIB/", re.IGNORECASE),
        re.compile(r"/ULIB/", re.IGNORECASE),
        re.compile(r"/DB/", re.IGNORECASE),
        re.compile(r"/NOOP/", re.IGNORECASE)
    }

    ServiceHandle = {
        "FAVICON.ICO": svc_hndl_FAVICON,
        "STOP": svc_hndl_STOP,
        "CONFIG": svc_hndl_CONFIG,
        "POST": svc_hndl_POST,
        "FILE": svc_hndl_FILE,
        "LIB": svc_hndl_LIB,
        "ULIB": svc_hndl_ULIB,
        "DB": svc_hndl_DB,
        "VIRTUAL": svc_hndl_VIRTUAL,
        "NOOP": svc_hndl_NOOP
    }


    def int_get_html_message(self, what):
        content = "<HTML><BODY><H1>"+what+"</H1></BODY></HTML>\n"
        return content


    def map_ext_to_filetype(self, extension):
        return {
            'js': 'application/javascript',
            'txt': 'text/plain',
            'html': 'text/html',
            'htm': 'text/html',
            'css': 'text/css',
            'asc': 'text/plain',
            'bmp': 'image/bmp',
            'class': 'application/octet-stream',
            'doc': 'application/msword',
            'gif': 'image/gif',
            'ico': 'image/x-icon',
            'jpe': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'jpg': 'image/jpeg',
            'pdf': 'application/pdf',
            'png': 'image/png',
            'xht': 'application/xhtml+xml',
            'xhtml': 'application/xhtml+xml',
            'xls': 'application/vnd.ms-excel',
            'xml': 'application/xml',
            'xpm': 'image/x-xpixmap',
            'xsl': 'application/xml',
            'xslt': 'application/xslt+xml'
        }[extension]


    def int_send_HEADERS_JSON(self, code=200, message=''):
        #print("int_send_HEADERS_JSON -> (%r, %r)" % (code, message))
        self.code = code
        if message != '':
            self.bodySize= len(str(message))
            self.content_lenght = self.bodySize

        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        #self.send_header('Content-Type', 'application/json')
        #self.send_header('Content-Length', self.bodySize)
        self.end_headers()
        return

    def int_send_HEADERS_redirect(self, code=301, location=''):
        self.code = code
        self.send_response(code)
        self.send_header('Location', location)
        self.send_header('Content-Length', 0)
        self.end_headers()
        #self.send_header('Content-Length', self.bodySize)
        #self.end_headers()
        return

    def int_send_HEADERS(self, code=200, message=''):
        self.code = code
        if message != '':
            self.bodySize=len(message)
            self.content_lenght = self.bodySize

        #print("int_send_HEADERS -> (%r, %r, %r )" % (code, message, self.bodySize))

        self.send_response(code)
        self.send_header('Content-Type', 'text/html;charset=UTF-8')
        #self.send_header('Content-Length', self.bodySize)
        self.end_headers()
        return

    def int_send_HEADERS_FILETYPE(self, code, filename, tamagno):
        self.code = code
        self.send_response(code)
        ext = filename.rsplit('.', 1)[-1]
        self.send_header('Content-Type', self.map_ext_to_filetype(ext))
        self.send_header('Content-Length', self.bodySize)
        self.end_headers()
        return

    def int_send_BODY(self, message=''):
        #print("int_send_BODY -> (%r)" % (message))

        try:
            if python_OldVersion:
                self.wfile.write(message)
            else:
                self.wfile.write(bytes(message, 'UTF-8'))

        except:
            self.logger.pdebug('excepcion en send_body :%s, %s' % (self.what, self.path))

            pass

        return

    def int_HEAD_PROXY_AUTH(self):
        self.code = 407
        self.send_response(407,"Proxy Authentication Required. "+self.server_version+": Access to the Web Proxy filter is denied.")
        self.send_header('Proxy-Authenticate', 'Basic realm="PROXY autentication required"')
        self.send_header('Proxy-Connection', 'close')
        self.send_header('Connection', 'close')
        self.end_headers()
        return

    def int_HEAD_HTTP_AUTH(self):
        self.code = 401
        self.send_response(401,"HTTP authentication Required. "+self.server_version+": Access to the Web Server is denied.")
        self.send_header('WWW-Authenticate', 'Basic realm="HTTP autentication required"')
        self.send_header('Connection', 'close')
        self.end_headers()
        return

    def parse_query(self):
        if python_OldVersion:
            self.parsed_path = urlparse.urlparse(self.path)
        else:
            self.parsed_path = urllib.parse.urlparse(self.path)
        return

    #TODO: Proxy-Authorization: Basic dXNlcjpwYXNzd29yZA==
    #TODO: dividir en 407 (proxy) y Authentication http

    def handle_PROXY_AUTH(self):

        # Tenemos una cabecera con autenticacion Proxy?

        ## Python 3 => removed self.headers.>has_key<('Proxy-Authorization'):
        ## cambiado por 'in'
        if 'Proxy-Authorization' in self.headers:

            authorization = self.headers.get('Proxy-Authorization')

            if DEBUG: self.logger.pdebug ('Proxy auth string [Proxy-Authorization]: %s ' % authorization)

            authorization = authorization.split()
            # Han usado una autenticación básica?
            if authorization[0].lower() == "basic":
                try:
                    # Sí, intentamos obtener el usuario y passwd
                    if python_OldVersion:
                        authorization = base64.decodestring(authorization[1])
                    else:
                        authorization = base64.decodestring(bytes(authorization[1],'UTF-8')).decode()
                    # bytes(content, 'UTF-8')

                except binascii.Error:
                    # Error, entonces KO
                    return 0

                else:
                    # Tenemos usuario & passwd y lo hemos podido decodificar
                    authorization = authorization.split(':')
                    self.proxy_user=authorization[0]
                    self.proxy_password=authorization[1]

                    if self.theDB.isUserAllowed(self.proxy_user, self.proxy_password):
                        # Usuario autenticado
                        if self.theDB.isUserAdmin(self.proxy_user) or self.theDB.isUserAdvanced(self.proxy_user):
                            #Este usuario [admin|advanced] no tiene restricciones de hora
                            if DEBUG: self.logger.pdebug("Proxy User authorized[1]: %s:%s" % (self.proxy_user, self.proxy_password))
                            return 1
                        elif self.theDB.isUserAllowedNow(self.proxy_user):
                            #Usuario autenticado restringido pero en rango autorizado
                            if DEBUG: self.logger.pdebug("Proxy User authorized[1]: %s:%s" % (self.proxy_user, self.proxy_password))
                            return 1
                        else:
                            #Usuario autenticado restringido pero en rango NO autorizado
                            if DEBUG: self.logger.pdebug("Proxy User NOT authorized[-2] (Rango no autorizado): %s:%s" % (self.proxy_user, self.proxy_password))
                            return -2
                    else:
                        if DEBUG: self.logger.pdebug("Proxy User NOT authorized[-1] (Contraseña): %s:%s" % (self.proxy_user, self.proxy_password))
                        return -1

                    '''
                    if self.proxy_user == 'proxyUser' and self.proxy_password == 'proxyPass':
                        #Autenticacion = OK
                        return 1
                    else:
                        #Autenticacion = KO
                        return 0
                    '''

        # No está autenticado
        else:
            return 0

    def handle_HTTP_AUTH(self):

        # Tenemos una cabecera con autenticacion Proxy?

        ## Python 3 => removed self.headers.>has_key<('Authorization'):
        ## cambiado por 'in'

        if 'Authorization' in self.headers:
            authorization = self.headers.get('Authorization')

            if DEBUG: self.logger.pdebug ('HTTP auth string [Authorization]: %s ' % authorization)

            authorization = authorization.split()

            # Han usado una autenticación básica?
            if authorization[0].lower() == "basic":
                try:
                    # Sí, intentamos obtener el usuario y passwd
                    #authorization = base64.decodestring(authorization[1])

                    if python_OldVersion:
                        authorization = base64.decodestring(authorization[1])
                    else:
                        authorization = base64.decodestring(bytes(authorization[1],'UTF-8')).decode()
                    # bytes(content, 'UTF-8')

                except binascii.Error:
                    # Error, entonces KO
                    return 0

                else:
                    # Tenemos usuario & passwd y lo hemos podido decodificar
                    authorization = authorization.split(':')
                    self.http_user=authorization[0]
                    self.http_password=authorization[1]

                    if self.theDB.isUserAllowed(self.http_user, self.http_password):
                        # Usuario autenticado
                        if self.theDB.isUserAdmin(self.http_user):
                            #Este usuario [admin] puede acceder a la configuración
                            if DEBUG: self.logger.pdebug("Admin User authorized[1]: %s:%s" % (self.http_user, self.http_password))
                            return 1
                        else:
                            # Not admin
                            if DEBUG: self.logger.pdebug("User NOT authorized - not admin[-2]: %s:%s" % (self.http_user, self.http_password))
                            return -2

                    else:
                        # Incorrect password
                        if DEBUG: self.logger.pdebug("User NOT authorized[-1] (Contraseña): %s:%s" % (self.http_user, self.http_password))
                        return -1

                    '''
                    if self.http_user == 'User' and self.http_password == 'Pass':
                        #Autenticacion = OK
                        return 1
                    else:
                        #Autenticacion = KO
                        return 2
                    '''

        # No está autenticado
        else:
            return 0


    def BASIC(self,what):
        self.content = b''
        self.content_lenght = 0
        self.code = 0
        self.processed_headers [:] = []
        #self.processed_headers.clear()
        self.content_cached=False
        self.Allowed = 0
        self.selfquery = False
        if (what==None):
            self.what='GET'
        else:
            self.what=what


        self.parse_query()
        # Comprobamos si nos están pidiendo nuestra URL
        # Por defecto no nos piden a nosotros
        selfquery = False

        ## TODO: aqui hay que cambiar que empiece por la cadena en vez de que sea la cadena
        ## TODO: cuando atacamos localhost:PUERTO (modo proxy), devuelve OK, pero cuando se ataca el servicio
        ## TODO: sin puerto, se devuelve como contenido las cabeceras
        if self.parsed_path.netloc in [ '127.0.0.1' , 'localhost', '', self.myServerAddress]:
            # or '' ]
            selfquery = True
            self.selfquery = True

        # Si es una dirección local, atendemos la petición HTTP
        #######################################################
        if selfquery:
            if DEBUG:
                self.logger.pdebug(self.parsed_path)
                self.logger.pdebug("Local, %s %s" % (selfquery, self.what))

            thePath = ''
            if self.parsed_path.path in ['/favicon.ico']:
                thePath = '/ulib/favicon.ico'
                self.Allowed = 1
            elif re.match('/virtual/', self.parsed_path.path.lower()) != None:
                self.Allowed = 1
            else:
                self.Allowed = self.handle_HTTP_AUTH()

            if DEBUG: self.logger.pdebug("autorizado by HTTP_AUTH: %s " % self.Allowed)

            #autenticacion OK = 1
            if self.Allowed==1:
                # handler por defecto...
                service_handle_value="NOOP"
                service_handle_parms=""

                if self.what in ['GET', 'POST', 'HEAD']:
                    # Para cada uno de los servicios que atenderemos... (LocalServices es una lista de servicios vs handlers)
                    for URL in self.LocalServices:
                        if DEBUG: self.logger.pdebug ("\tm%s" % URL.pattern)
                        if thePath == '':
                            thePath = self.parsed_path.path
                        if URL.match(thePath):
                            # Sustituimos el patron entre "/" y hacemos strip de los caracteres adicionales
                            service_handle_value=re.sub(r"/[.]*$","",re.sub(r"^/+", "", URL.pattern.upper()))
                            service_handle_parms=re.sub(r'(?i)'+URL.pattern, "", thePath)

                    # Llamamos a la funcion que se llame svc_hndl_$(PATRON)
                    # Por defecto, se llama a la funcion NOOP
                    self.ServiceHandle[service_handle_value](self,service_handle_parms,self.parsed_path.query,Verb=self.what)
                    service_handle_value = 'NOOP'

                else:
                    self.do_OTHER()


            elif self.Allowed == -1:  # Contraseña enviada pero incorrecta
                mensaje = 'Usuario o contraseña incorrecto'
                self.int_send_HEADERS(401,mensaje)
                self.int_send_BODY(mensaje)

            elif self.Allowed == -2:  # Usuario not admin
                mensaje = 'El usuario %r no tiene acceso a la configuración del proxy' % (self.proxy_user)
                self.int_send_HEADERS(401,mensaje)
                self.int_send_BODY(mensaje)
            else:
                mensaje = "Autenticacion requerida"
                self.int_HEAD_HTTP_AUTH()
                self.int_send_BODY(mensaje)




        # Tratamos la peticion como PROXY
        # ######################################################
        else:
            if DEBUG: self.logger.pdebug(self.parsed_path)

            # Está autenticado?
            # Habilitamos la autenticacion o forzamos autenticado..
            # TODO:: DESCOMENTAR
            self.Allowed = self.handle_PROXY_AUTH()

            if DEBUG: self.logger.pdebug("autorizado by PROXY_AUTH: %s " % self.Allowed)

            #self.Allowed = 1
            # TODO:: DESCOMENTAR

            #autenticacion OK = 1
            if self.Allowed == 1:
                self.client_headers = {}
                self.client_headers.clear()
                headers_are_text = False
                headers_content_type = ''
                mensaje = ''

                client_headers = Headers.ClientHeaders(self.headers.__str__(),debug=False,
                                                       ip=self.client_address[0],

                                                       port = self.client_address[1])
                new_client_headers = client_headers.parse()


                if DEBUG: self.logger.pdebug('URL: %s: %s' % (self.client_address[1],self.path))
                if DEBUG: self.logger.pdebug ('try request')

                fc = Cache.FileCache()
                # Filtramos el tipo de servicio y llamamos a un bloque o a otro...
                if ( self.what == 'GET' ):

                    cache_content = b''
                    cache_headers = []
                    cache_headers[:] = []
                    #cache_headers.clear()
                    self.content_cached = fc.is_cached(path=self.path, debug=False, ip=self.client_address[0], port=self.client_address[1])
                    if self.content_cached:
                        cache_content, cache_headers = fc.get(path=self.path, debug=True, ip=self.client_address[0], port=self.client_address[1])
                        cache_lenght = len(cache_content)
                        cache_code = 200
                    else:
                        resp = requests.get(self.path, headers=new_client_headers, stream=True, allow_redirects=True)
                        #fc.put(path=self.path, content=resp.content, headers=resp.headers, debug=True, ip=self.client_address[0], port=self.client_address[1])
                elif ( self.what == 'POST' ):
                    resp = requests.post(self.path, headers=new_client_headers, data=self.content, stream=True, allow_redirects=True)
                elif ( self.what == 'HEAD' ):
                    resp = requests.head(self.path, stream=True, allow_redirects=True)


                # Dependiendo de la cache...
                if self.content_cached:
                    self.content = bytes(cache_content)
                    self.content_lenght = cache_lenght
                    self.code = cache_code
                else:
                    self.content = resp.content
                    self.content_lenght = len(resp.content)
                    self.code = resp.status_code


                if  (self.code == requests.codes.ok):
                    # El codigo es OK pero no sabemos si podemos enviar el contenido por las reglas del proxy...
                    # Procesamos las cabeceras
                    self.processed_headers [:] = []
                    #self.processed_headers.clear()
                    parsed_headers = []
                    parsed_headers [:] = []
                    could_cache=True
                    if not self.content_cached:
                        # Procesamos las cabeceras para reescribirlas
                        '''if 'pragma' in resp.headers and resp.headers['pragma'] == 'no-cache':
                            #print('Cache header: pragma ->%s' % resp.headers['pragma'])
                            could_cache=False
                        elif 'expires' in resp.headers and resp.headers['expires'] == '-1':
                            #print('Cache header: expires ->%s' % resp.headers['expires'])
                            could_cache=False
                        #elif 'cache-control' in resp.headers:
                            #print('\tCache header: cache-control ->%s' % resp.headers['cache-control'])
                            #could_cache=False
                        '''
                        parsed_headers = Headers.ServerHeaders(response=resp, debug=False,
                                                               ip=self.client_address[0],
                                                               port = self.client_address[1])
                        self.processed_headers = parsed_headers.parsed_headers()
                        headers_are_text = parsed_headers.is_text()
                        headers_content_type = parsed_headers.get_content_type()

                        if could_cache:
                            #print("............ %r %r " %(headers_are_text, headers_content_type))
                            fc.put(path=self.path, content=resp.content, headers=self.processed_headers, debug=False, strip_text=headers_are_text ,
                                   ip=self.client_address[0], port=self.client_address[1])
                    else:
                        for header in cache_headers:
                            header_key,header_value = str(header).split(': ',1)
                            if header_key.lower() == 'content-type':
                                headers_content_type = header_value

                            self.processed_headers.append([header_key,header_value])


                    if self.theDB.isUserKid(self.proxy_user) or self.theDB.isUserGuest(self.proxy_user):
                        is_blocked = False
                        blocked_DUE_TO = ''

                        if (not is_blocked):
                        #
                        # comprobamos la URI contra las reglas
                        #
                            theURIRules = self.theDB.getRULES('URIS', self.proxy_user)
                            for rule in theURIRules:

                                #print("!!!! %s" % rule)
                                #print(":::: probando por Contenido URI %s - %s" % (rule.rulecontent, self.path))

                                if (not is_blocked):
                                    if re.search(rule.rulecontent, self.path, re.I | re.U):
                                        #print("::::! prohibido por Contenido URI %s - %s" % (rule.rulecontent, self.path))
                                        is_blocked = True
                                        blocked_DUE_TO = rule.__toString__()
                                        # Aqui tenemos match en la URI

                        if not is_blocked:
                        #
                        # comprobamos en 'Content-Type' contra las reglas
                        #
                            theHEADRules = self.theDB.getRULES('MIME', self.proxy_user)

                            for rule in theHEADRules:
                                if (not is_blocked):
                                    if re.search(rule.rulecontent, headers_content_type,  re.I | re.U ):
                                        #print("::::! prohibido por Contenido BODY %s - %s" % (rule.rulecontent, self.path))
                                        # Aqui tenemos match en la URI
                                        is_blocked = True
                                        blocked_DUE_TO = rule.__toString__()



                        if not is_blocked:
                        #
                        # comprobamos el BODY contra las reglas
                        #
                            text_matching = re.compile("(json|xml|text|html|asp|php|^\s*$)", re.I | re.U)
                            match = text_matching.search(headers_content_type)
                            if match:
                                gotText = True
                                #print("\n!GOT text for %s - %s" % (headers_content_type, self.path))
                            else:
                                gotText = False
                                #print("\n!NOT text for %s - %s" % (headers_content_type, self.path))

                            if gotText:
                                #Cache.remove_html_markup(Cache.remove_html_markup(self.content.decode('utf-8')))
                                theBodyText = Cache.remove_html_markup(self.content.decode('utf-8', 'ignore'))
                                theBodyText = html.parser.HTMLParser().unescape(theBodyText)

                                #print(theBodyText)

                                theBODYRules = self.theDB.getRULES('WORD', self.proxy_user)
                                for rule in theBODYRules:
                                    if (not is_blocked):
                                        if re.search(rule.rulecontent, theBodyText,  re.I | re.U ):
                                            #print("::::! prohibido por Contenido BODY %s - %s" % (rule.rulecontent, self.path))
                                            # Aqui tenemos match en la URI
                                            is_blocked = True
                                            blocked_DUE_TO = rule.__toString__()

                        if is_blocked:
                            # Aquí reescribimos el contenido
                            if DEBUG: print("Got blocked by %s - %s" %(blocked_DUE_TO, self.path))
                            message =  '<HTML><BODY><PRE>Contenido bloqueado por %s\n%s</PRE></BODY></HTML>' % (blocked_DUE_TO, self.path)
                            self.content = message.encode('utf-8')
                            self.content_lenght = len(message)
                            self.code = 403



                    if not is_blocked:
                        # Enviamos el código de retorno
                        self.send_response(self.code)
                        # Enviamos todas las cabeceras reescritas
                        for header_key,header_value in self.processed_headers:
                            self.send_header(header_key, str(header_value).rstrip('\n'))
                        # Fin de cabeceras
                        self.end_headers()
                    else:
                        self.int_send_HEADERS(self.code,mensaje)
                        try:
                            self.wfile.write(self.content)
                        except:
                            pass



                    if self.what != 'HEAD' and self.code==200:
                        # Este bloque envia la informacion al cliente.
                        # Si falla el envio por un 'reset by peer' o cierre de la conexion evitamos el error stacktrace
                        # con el bloque except
                        try:
                            self.wfile.write(self.content)
                        except:
                            pass

            elif self.Allowed == 0:  # No tenemos cabeceras autenticacion proxy, las enviamos
                mensaje = "Autenticacion requerida"
                self.int_HEAD_PROXY_AUTH()
                self.int_send_BODY(mensaje)

            elif self.Allowed == -1:  # Contraseña enviada pero incorrecta
                mensaje = "Usuario o contraseña incorrecto"
                self.int_send_HEADERS(401,mensaje)
                self.int_send_BODY(mensaje)

            elif self.Allowed == -2:  # Usuario autenticado pero fuera de horario
                mensaje = 'Acesso de usuario %r fuera de horario' % (self.proxy_user)
                self.int_send_HEADERS(401,mensaje)
                self.int_send_BODY(mensaje)

        if DEBUG: self.logger.pdebug ("end")
        return

    def do_CONNECT(self):
        o_port_default = None
        o_port = 80

        self.parse_query()
        if DEBUG:
            self.logger.pdebug (self.parsed_path)
        self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           'prxUSR: %10s, ' % self.proxy_user[0:9] +
                           'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                           '??? CNT '+ self.path)
        # Tenemos schema? => eso nos fija el puerto por defecto en caso de no
        # venir definido en la cadena CONNECT...
        if self.parsed_path.scheme != '':
            o_port_default = socket.getservbyname(self.parsed_path.scheme)

        destination = self.parsed_path.netloc if (self.parsed_path.netloc!='') else self.parsed_path.path

        try:
            o_dest,o_port = destination.split(':', 1)
        except:
            o_dest = destination
            if (o_port_default!=None): o_port=o_port_default

        try:
            if DEBUG: self.logger.pdebug ('Outbound conection to %s:%s' % (o_dest, o_port))
            self.server_socket = socket.create_connection((o_dest, o_port),timeout=3)

        except (socket.error, socket.herror, socket.gaierror) as e:
            if DEBUG: self.logger.pdebug ("Error %s" % e)
            self.send_response(404,'CONNECT error ['+str(e)+'] to '+o_dest+':'+str(o_port))
            self.end_headers()

        except socket.timeout as e:
            if DEBUG: self.logger.pdebug ("Error %s" % e)
            self.send_response(504,'CONNECT Timeout ['+str(e)+'] to '+o_dest+':'+str(o_port))
            #self.send_header('Content-Length', '0')
            self.end_headers()

        else:
            self.send_response(200,'CONNECT OK -> '+o_dest+':'+str(o_port))
            self.send_header('Content-Length', '0')
            self.end_headers()

            self.server_wfile = self.server_socket.makefile('wb', self.wbufsize)

            #self.logger.pdebug('_Csrc: '+self.client_address[0] +',\tPermit: '+str(self.Allowed)+',\tprxUSR: '+self.proxy_user+',\tPRX: '+self.path)
            self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                               'Allow: %s, ' % self.Allowed +
                               'prxUSR: %10s, ' % self.proxy_user[0:9] +
                               'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                               'PRX CNT '+ self.path)
            salir_bucle = False
            inputs = [self.connection, self.server_socket]
            while (inputs and not salir_bucle):
                # Wait for at least one of the sockets to be ready for processing

                if DEBUG:
                    sys.stderr.write("waiting for the next event")

                #readable, writable, exceptional = select.select(inputs, [], inputs)
                r, w, e = select.select(inputs, [], inputs)
                if DEBUG:
                    sys.stderr.write("select (i:%s, o:%s, e:%s'%(len(r),len(w),len(e))")

                if e != [] and not salir_bucle:
                    # cualquiera que sea el error en los sockets de cliente o servidor, tenemos que salir..

                    if self.connection in e:
                        if DEBUG: self.logger.pdebug("error socket cliente: cerrandolo")
                    if server_socket in e:
                        if DEBUG: self.logger.pdebug("error socket servidor: cerrandolo")
                    if DEBUG: self.logger.pdebug(e)
                    salir_bucle=True

                if r != [] and not salir_bucle:
                    if DEBUG: self.logger.pdebug(r)
                    if (self.connection in r) and not salir_bucle:
                        if DEBUG: self.logger.pdebug('cliente tiene datos: leyendo cliente')
                        try:
                            sockdata = self.connection.recv(4096)
                            if (sockdata):
                                self.server_wfile.write(sockdata)
                            else:
                                if DEBUG: self.logger.pdebug("Cierre de socket cliente ordenado")
                                salir_bucle=True
                        except (socket.timeout, socket.error) as e:
                            if DEBUG: self.logger.pdebug("error socket: %s" % (e))
                            salir_bucle=True

                    if (self.server_socket in r) and not salir_bucle:
                        if DEBUG: self.logger.pdebug('servidor tiene datos: leyendo servidor')
                        try:
                            sockdata = self.server_socket.recv(4096)
                            if (sockdata):
                                self.wfile.write(sockdata)
                            else:
                                if DEBUG: self.logger.pdebug("Cierre de socket servidor ordenado")
                                salir_bucle=True
                        except (socket.timeout, socket.error) as e:
                            if DEBUG: self.logger.pdebug("error socket: %s" % (e))
                            salir_bucle=True

                if w != [] and not salir_bucle:
                    if DEBUG: self.logger.pdebug(w)

        if DEBUG: self.logger.pdebug ("saliendo del bucle del socket...")
        self.server_wfile.close()
        self.server_socket.close()
        return

##     __verbs_supported ='GET, HEAD, POST, PUT, TRACE, OPTIONS, CONNECT'
##                         xxx  xxxx  xxxx              xxxxxxx  xxxxxxx

    def do_OPTIONS(self):
        self.content = ''
        if DEBUG_BEFORE_HANDLING:
            self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           'prxUSR: %10s, ' % self.proxy_user[0:9] +
                           'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                           '??? OPT '+ self.path)
        if (self.path == '*'):
            self.send_response(200)
            self.send_header('Allow',self.__verbs_supported)
            self.send_header('Content-Length', '0')
            self.end_headers
        else:
            self.BASIC(what='OPTIONS')
            # TODO:: OPTIONS de url requiere auth... gestionado en BASIC

        # Aqui discriminamos si era una llamada PROXY o HTTP

        if self.selfquery:
             auth_str = 'httUSR: %10s, ' % self.http_user[0:9]
             req_type = 'HTT OPT '
        else:
            auth_str = 'prxUSR: %10s, ' % self.proxy_user[0:9]
            req_type = 'PRX OPT '


        self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           auth_str+
                           'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                           '%s %s' % (req_type, self.path))
        return

    def do_HEAD(self):
        if DEBUG_BEFORE_HANDLING:
            self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           'prxUSR: %10s, ' % self.proxy_user[0:9] +
                           'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                           '??? HEA '+ self.path)
        self.content = ''
        self.BASIC(what='HEAD')

        if self.selfquery:
            auth_str = 'httUSR: %10s, ' % self.http_user[0:9]
            req_type = 'HTT HEA '
        else:
            auth_str = 'prxUSR: %10s, ' % self.proxy_user[0:9]
            req_type = 'PRX HEA '


        self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           auth_str+
                           'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                           '%s %s' % (req_type, self.path))
        '''
        self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           'prxUSR: %10s, ' % self.proxy_user[0:9] +
                           'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                           'PRX HEA '+ self.path)
        '''
        return

    def do_TRACE(self):
        self.content = ''
        self.BASIC(what='TRACE')

        if self.selfquery:
             auth_str = 'httUSR: %10s, ' % self.http_user[0:9]
             req_type = 'HTT TRC '
        else:
            auth_str = 'prxUSR: %10s, ' % self.proxy_user[0:9]
            req_type = 'PRX TRC '


        self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           auth_str+
                           'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                           '%s %s' % (req_type, self.path))

        '''
        self.logger.pdebug( '%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                            'Allow: %s, ' % self.Allowed +
                            'prxUSR: %10s, ' % self.proxy_user[0:9] +
                            'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                            'PRX TRC '+ self.path)
        '''
        return

    def do_GET(self):

        if DEBUG_BEFORE_HANDLING:
            self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           'prxUSR: %10s, ' % self.proxy_user[0:9] +
                           'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                           '??? GET %s' % (self.path)
                           )
        '''
        parsed_headers = Headers(headers=self.headers.items(), debug=True,
                                ip=self.client_address[0],
                                port = self.client_address[1])
        returned_headers = parsed_headers.input_parsed_headers()
        '''


        if 'Content-Length' in self.headers:
            self.content = self.rfile.read(int(self.headers['Content-Length']))
        else:
            self.content = ''
        self.BASIC(what='GET')
        '''
        msg = "%s:%s: " % (self.client_address[0], self.client_address[1])+
                   'Allow: %s, ' % self.Allowed +
                   'prxUSR: %10s, ' % self.proxy_user[0:9] +
                   'Cod: %3d, Size: %8d,' % (self.code, self.content_lenght) +
                   'PRX GET ' + self.path
        '''
        if self.content_cached:
            self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           'prxUSR: %10s, ' % self.proxy_user[0:9] +
                           'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                           'CAC GET  %s' % (self.path)
                           )
        else:
            if self.selfquery:
                 auth_str = 'httUSR: %10s, ' % self.http_user[0:9]
                 req_type = 'HTT GET '
            else:
                auth_str = 'prxUSR: %10s, ' % self.proxy_user[0:9]
                req_type = 'PRX GET '


            self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                               'Allow: %s, ' % self.Allowed +
                               auth_str+
                               'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                               '%s %s' % (req_type, self.path))

            '''
            self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           'prxUSR: %10s, ' % self.proxy_user[0:9] +
                           'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                           'PRX GET %s' % (self.path)
                           )
            '''
        return


    def do_POST(self):
        if DEBUG_BEFORE_HANDLING:
            self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           'prxUSR: %10s, ' % self.proxy_user[0:9] +
                           'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                           '??? PST %s' % (self.path)
                           )

        if 'Content-Length' in self.headers:
            self.content = self.rfile.read(int(self.headers['Content-Length']))
        else:
            self.content = ''

        if DEBUG: sys.stderr.write('calling BASIC\n')
        self.BASIC(what='POST')

        if self.selfquery:
             auth_str = 'httUSR: %10s, ' % self.http_user[0:9]
             req_type = 'HTT PST '
        else:
            auth_str = 'prxUSR: %10s, ' % self.proxy_user[0:9]
            req_type = 'PRX PST '


        self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           auth_str+
                           'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                           '%s %s' % (req_type, self.path))

        '''
        self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           'prxUSR: %10s, ' % self.proxy_user[0:9] +
                           'Cod: %3d, Size: %8d, ' % (self.code, self.content_lenght) +
                           'PRX PST '+ self.path)
        '''
        return


    def do_OTHER(self):
        self.content = ''
        self.send_response(405)
        self.send_header('Allow',self.__verbs_supported)
        self.end_headers
        self.logger.pdebug('%s:%s, ' % (self.client_address[0], self.client_address[1]) +
                           'Allow: %s, ' % self.Allowed +
                           'prxUSR: %10s, ' % self.proxy_user[0:9] +
                           'Cod: %3d, Size: %8d,' % (self.code, self.content_lenght) +
                           'PRX OTH '+ self.path)

        return
